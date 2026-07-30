from dotenv import load_dotenv
load_dotenv()
import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
 
from database import init_db, get_due_cards, get_all_cards, add_card, update_card_sm2, flag_card, unflag_card, delete_card, add_feedback, get_stats
from extractor import allowed_file, extract_text, MAX_FILE_SIZE
from generator import generate_flashcards
from sm2 import sm2

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
 
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
init_db()
 
 
 
@app.route("/")
def index():
    stats = get_stats()
    return render_template("index.html", stats=stats)
 
 

 
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        if "file" not in request.files and not request.form.get("snippet"):
            flash("Please upload a file or enter a text snippet.", "error")
            return redirect(url_for("upload"))
 
        num_cards = int(request.form.get("num_cards", 5))
        text = ""
        error = None
 
        # Handle text snippet
        snippet_input = request.form.get("snippet", "").strip()
        if snippet_input:
            text = snippet_input
 
        # Handle file upload (overrides snippet if both provided)
        file = request.files.get("file")
        if file and file.filename:
            if not allowed_file(file.filename):
                flash("Only PDF and TXT files are supported.", "error")
                return redirect(url_for("upload"))
 
            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)
 
            text, error = extract_text(filepath, file.filename)
 
            # Clean up uploaded file after extraction
            try:
                os.remove(filepath)
            except Exception:
                pass
 
            if error:
                flash(error, "error")
                return redirect(url_for("upload"))
 
        if not text:
            flash("No content to generate flashcards from.", "error")
            return redirect(url_for("upload"))
 
        cards, error = generate_flashcards(text, num_cards)
 
        if error:
            flash(error, "error")
            return redirect(url_for("upload"))
 
        for card in cards:
            add_card(card["question"], card["answer"], card["difficulty"], card["snippet"])
 
        flash(f"Successfully generated {len(cards)} flashcards!", "success")
        return redirect(url_for("cards"))
 
    return render_template("upload.html")
 
 

 
@app.route("/cards")
def cards():
    all_cards = get_all_cards()
    return render_template("cards.html", cards=all_cards)
 
 

 
@app.route("/review")
def review():
    due = get_due_cards()
    if not due:
        return render_template("review_done.html")
    session["review_queue"] = [c["id"] for c in due]
    session["review_index"] = 0
    return redirect(url_for("review_card"))
 
 
@app.route("/review/card")
def review_card():
    queue = session.get("review_queue", [])
    index = session.get("review_index", 0)
 
    if not queue or index >= len(queue):
        return redirect(url_for("review_done"))
 
    due = get_due_cards()
    card_id = queue[index]
    card = next((c for c in due if c["id"] == card_id), None)
 
    if not card:
        session["review_index"] = index + 1
        return redirect(url_for("review_card"))
 
    progress = {"current": index + 1, "total": len(queue)}
    return render_template("review.html", card=card, progress=progress, revealed=False)
 
 
@app.route("/review/reveal/<int:card_id>")
def reveal_card(card_id):
    due = get_due_cards()
    card = next((c for c in due if c["id"] == card_id), None)
    queue = session.get("review_queue", [])
    index = session.get("review_index", 0)
    progress = {"current": index + 1, "total": len(queue)}
    return render_template("review.html", card=card, progress=progress, revealed=True)
 
 
@app.route("/review/submit/<int:card_id>", methods=["POST"])
def submit_review(card_id):
    quality = int(request.form.get("quality", 0))
    flagged = int(request.form.get("flagged", 0))
    comment = request.form.get("comment", "").strip()
 
    # Log feedback
    add_feedback(card_id, quality, flagged, comment)
 
    if flagged:
        flag_card(card_id)
    else:
        # Get current card data
        all_cards = get_all_cards()
        card = next((c for c in all_cards if c["id"] == card_id), None)
        if card:
            new_ef, new_interval, new_reps, new_due = sm2(
                quality, card["easiness"], card["interval"], card["repetitions"]
            )
            update_card_sm2(card_id, new_ef, new_interval, new_reps, new_due)
 
    # Advance queue
    session["review_index"] = session.get("review_index", 0) + 1
    return redirect(url_for("review_card"))
 
 
@app.route("/review/done")
def review_done():
    return render_template("review_done.html")
 
 

 
@app.route("/cards/unflag/<int:card_id>", methods=["POST"])
def unflag(card_id):
    unflag_card(card_id)
    flash("Card restored to review queue.", "success")
    return redirect(url_for("cards"))
 
 
@app.route("/cards/delete/<int:card_id>", methods=["POST"])
def delete(card_id):
    delete_card(card_id)
    flash("Card deleted.", "success")
    return redirect(url_for("cards"))
 
 

 
@app.errorhandler(413)
def too_large(e):
    flash("File too large. Maximum size is 5MB.", "error")
    return redirect(url_for("upload"))
 

if __name__ == "__main__":
    app.run(debug=True)
 