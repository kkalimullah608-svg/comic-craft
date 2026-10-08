
"""Generate structured comic outlines with the Gemini API."""

import json
import re
from typing import Any

from google import genai
from google.genai import types

from app.config import (
	GEMINI_API_KEY,
	GEMINI_MODEL,
	NUM_PANELS,
)


def get_client():
	if not GEMINI_API_KEY:
		raise RuntimeError(
			"GEMINI_API_KEY is missing. "
			"Please add it to your .env file."
		)

	return genai.Client(api_key=GEMINI_API_KEY)


def extract_json(text: str) -> Any:
	text = text.strip()
	text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
	text = re.sub(r"\s*```$", "", text)

	start = text.find("[")
	end = text.rfind("]")
	if start >= 0 and end > start:
		return json.loads(text[start:end + 1])

	return json.loads(text)


def generate_outline(
	story_prompt: str,
	character_name: str,
	setting: str,
	tone: str,
	art_style: str,
):
	client = get_client()

	prompt = f"""
Create a cohesive {NUM_PANELS}-panel comic story outline.

Story idea:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Return ONLY valid JSON.

The JSON must be an array containing exactly
{NUM_PANELS} objects.

Every object must contain:

panel_number
title
scene_description
image_prompt

Requirements:

1. Keep the story connected from panel to panel.
2. Keep the main character visually consistent.
3. Make each panel different but part of the same story.
4. Image prompts must describe the complete visual scene.
5. Do not include markdown.
6. Do not include explanations outside JSON.
"""

	response = client.models.generate_content(
		model=GEMINI_MODEL,
		contents=prompt,
		config=types.GenerateContentConfig(
			temperature=0.9,
			response_mime_type="application/json",
		),
	)

	if not response.text:
		raise RuntimeError("Gemini returned an empty outline response.")

	try:
		data = extract_json(response.text)
	except (json.JSONDecodeError, TypeError) as exc:
		raise RuntimeError("Gemini returned invalid outline JSON.") from exc

	if not isinstance(data, list):
		raise RuntimeError("Gemini returned an invalid outline.")

	if len(data) != NUM_PANELS:
		raise RuntimeError(
			"Gemini did not generate the required number of panels."
		)

	for index, panel in enumerate(data, start=1):
		if not isinstance(panel, dict):
			raise RuntimeError(f"Gemini returned an invalid panel at position {index}.")
		for key in ("title", "scene_description", "image_prompt"):
			if not isinstance(panel.get(key), str) or not panel[key].strip():
				raise RuntimeError(
					f"Gemini panel {index} is missing required field '{key}'."
				)
		panel["panel_number"] = index

	return data
