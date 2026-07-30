import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

SYSTEM_PROMPT = """ You are an expert educational flashcard generator. Your task is to generate high-quality flashcards from the provided text.

Rules:
- Generate exactly the number of flashcards requested
- You MUST ONLY use information grounded in the source text.
- Do NOT invent facts not present in the source text
- Output ONLY valid JSON, no premable, no markdown, no backticks
- Each card must have: question, answer, difficulty, snippet

Difficulty levels:
-"easy": factual recall, definitions, straightforward concepts
-"medium" application, relationships between concepts
-"hard": analysis, synthesis, complex reasoning

Output format (strict JSON array):
[
  {
    "question": "...",
    "answer": "...",
    "difficulty": "easy|medium|hard",
    "snippet": "exact quote from source text this card is based on"
  }
]"""

def generate_flashcards(text: str, num_cards: int = 5):
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nGenerate {num_cards} flashcards from this text:\n\n{text}"

        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.3,
                max_output_tokens=2000,
            )
        )

        raw = response.text.strip()

        if raw.startswith("```"):
            raw=raw.split("```")[1]
            if raw.startswith("json"):
                raw=raw[4:]
        raw=raw.strip()

        cards = json.loads(raw)

        validated = []
        for card in cards:
            if all(k in card for k in ("question", "answer", "difficulty")):
                snippet = str(card.get("snippet", ""))
                if snippet  and snippet.lower() not in text.lower():
                    continue
                validated.append({
                    "question": str(card["question"]),
                    "answer": str(card["answer"]),
                    "difficulty": card["difficulty"] if card["difficulty"] in ("easy", "medium", "hard") else "medium",
                    "snippet": str(card.get("snippet", "")) 
                })
        
        if not validated:
            return[], "No valid flashcards could be generated"
        
        return validated, None
    
    except json.JSONDecodeError:
        return[], "Failed to parse flashcard output"
    except Exception as e:
        return[], f"Generation errorL {str(e)}"
    

