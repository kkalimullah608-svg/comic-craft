"""Legacy Gemini story generator retained for root-level imports."""

import json

from google import genai
from google.genai import types

from app.config import (
	GEMINI_API_KEY,
	GEMINI_STORY_MODEL,
)


def get_client():
	if not GEMINI_API_KEY:
		raise RuntimeError(
			"GEMINI_API_KEY is missing. "
			"Please add it to your .env file."
		)

	return genai.Client(api_key=GEMINI_API_KEY)


def generate_story(outline, character_name, tone):
	client = get_client()

	prompt = f"""
Create the complete narration and dialogue
for this comic.

Main character:
{character_name}

Tone:
{tone}

Comic outline:

{json.dumps(outline, ensure_ascii=False, indent=2)}

Return ONLY valid JSON.

Return one object for every panel.

Each object must contain:

panel_number
caption
narration
dialogue

Rules:

1. Do not create extra panels.
2. Keep the story consistent.
3. Make dialogue natural.
4. Keep dialogue reasonably short.
5. Make narration suitable for a comic.
6. Match the requested tone.
"""

	response = client.models.generate_content(
		model=GEMINI_STORY_MODEL,
		contents=prompt,
		config=types.GenerateContentConfig(
			temperature=0.85,
			response_mime_type="application/json",
		),
	)

	data = json.loads(response.text)

	if not isinstance(data, list):
		raise RuntimeError("Gemini returned invalid story data.")

	if len(data) != len(outline):
		raise RuntimeError("Story panel count does not match outline.")

	return data
