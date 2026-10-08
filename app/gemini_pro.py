"""Generate comic narration and dialogue with the Gemini API."""

import json

from google import genai
from google.genai import types

from app.config import GEMINI_API_KEY, GEMINI_STORY_MODEL


def get_client():
	if not GEMINI_API_KEY:
		raise RuntimeError(
			"GEMINI_API_KEY is missing. Add it to a .env file in the project root."
		)
	return genai.Client(api_key=GEMINI_API_KEY)


def generate_story(outline, character_name, tone):
	client = get_client()
	prompt = f"""
Create the narration and dialogue for this comic.

Main character: {character_name}
Tone: {tone}
Comic outline:
{json.dumps(outline, ensure_ascii=False, indent=2)}

Return ONLY a JSON array with one object per panel. Each object must contain
panel_number, caption, narration, and dialogue. Do not add panels. Keep dialogue
natural and short, and keep the story consistent with the outline.
"""
	response = client.models.generate_content(
		model=GEMINI_STORY_MODEL,
		contents=prompt,
		config=types.GenerateContentConfig(
			temperature=0.85,
			response_mime_type="application/json",
		),
	)
	if not response.text:
		raise RuntimeError("Gemini returned an empty story response.")
	try:
		data = json.loads(response.text)
	except json.JSONDecodeError as exc:
		raise RuntimeError("Gemini returned invalid story JSON.") from exc
	if not isinstance(data, list) or len(data) != len(outline):
		raise RuntimeError("Story panel count does not match the outline.")
	return data
