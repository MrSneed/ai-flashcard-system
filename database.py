import sqlite3
import os
from datetime import date
 
DB_PATH = os.path.join(os.path.dirname(__file__), "flashcards.db")
 
 
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 
 
def init_db():
    conn = get_db()
    c = conn.cursor()
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            difficulty TEXT DEFAULT 'medium',
            source_snippet TEXT,
            easiness REAL DEFAULT 2.5,
            interval INTEGER DEFAULT 1,
            repetitions INTEGER DEFAULT 0,
            due_date TEXT DEFAULT (date('now')),
            flagged INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
 
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            quality INTEGER,
            flagged INTEGER DEFAULT 0,
            comment TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (card_id) REFERENCES flashcards(id)
        )
    """)
 
    conn.commit()
    conn.close()
 
 
def get_due_cards():
    conn = get_db()
    cards = conn.execute("""
        SELECT * FROM flashcards
        WHERE due_date <= ? AND flagged = 0
        ORDER BY due_date ASC
    """, (date.today().isoformat(),)).fetchall()
    conn.close()
    return [dict(c) for c in cards]
 
 
def get_all_cards():
    conn = get_db()
    cards = conn.execute("SELECT * FROM flashcards ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(c) for c in cards]
 
 
def add_card(question, answer, difficulty, snippet):
    conn = get_db()
    conn.execute("""
        INSERT INTO flashcards (question, answer, difficulty, source_snippet)
        VALUES (?, ?, ?, ?)
    """, (question, answer, difficulty, snippet))
    conn.commit()
    conn.close()
 
 
def update_card_sm2(card_id, easiness, interval, repetitions, due_date):
    conn = get_db()
    conn.execute("""
        UPDATE flashcards
        SET easiness=?, interval=?, repetitions=?, due_date=?
        WHERE id=?
    """, (easiness, interval, repetitions, due_date, card_id))
    conn.commit()
    conn.close()
 
 
def flag_card(card_id):
    conn = get_db()
    conn.execute("UPDATE flashcards SET flagged=1 WHERE id=?", (card_id,))
    conn.commit()
    conn.close()
 
 
def unflag_card(card_id):
    conn = get_db()
    conn.execute("UPDATE flashcards SET flagged=0 WHERE id=?", (card_id,))
    conn.commit()
    conn.close()
 
 
def delete_card(card_id):
    conn = get_db()
    conn.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
    conn.execute("DELETE FROM feedback WHERE card_id=?", (card_id,))
    conn.commit()
    conn.close()
 
 
def add_feedback(card_id, quality, flagged, comment):
    conn = get_db()
    conn.execute("""
        INSERT INTO feedback (card_id, quality, flagged, comment)
        VALUES (?, ?, ?, ?)
    """, (card_id, quality, flagged, comment))
    conn.commit()
    conn.close()
 
 
def get_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0]
    due = conn.execute("SELECT COUNT(*) FROM flashcards WHERE due_date <= ? AND flagged=0",
                       (date.today().isoformat(),)).fetchone()[0]
    flagged = conn.execute("SELECT COUNT(*) FROM flashcards WHERE flagged=1").fetchone()[0]
    mastered = conn.execute("SELECT COUNT(*) FROM flashcards WHERE repetitions >= 3 AND flagged=0").fetchone()[0]
    conn.close()
    return {"total": total, "due": due, "flagged": flagged, "mastered": mastered}

