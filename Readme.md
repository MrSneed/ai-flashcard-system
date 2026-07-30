# AI Flashcard Generator

An AI-assisted flashcard system designed to help computing students generate and revise flashcards using Google Gemini AI and spaced repetition.

## Requirements

- Python 3.10+
- Google Gemini API key (free)

## Installation

1. Clone the repository

2. Install dependencies:
pip install -r requirements.txt

3. Create a `.env` file and add your environment variables:

```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
```

4. Run the application:

```env
python app.py
```

5. Open the local URL provided in your browser.

## Technologies Used

- Python
- Flask
- Google Gemini API
- SQLite
- Jinja2
- HTML/CSS/JavaScript