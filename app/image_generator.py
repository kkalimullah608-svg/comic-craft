"""Generate and save comic panel artwork."""

import io
import re
import uuid
from pathlib import Path

import requests
from PIL import Image

from app.config import (
	HF_API_KEY,
	HF_IMAGE_MODEL,
	IMAGE_SIZE,
	LOCAL_IMAGE_MODEL,
	USE_LOCAL_DIFFUSERS,
)


BASE_DIR = Path(__file__).resolve().parent.parent
PANEL_DIR = BASE_DIR / "static" / "panels"
PANEL_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(text: str) -> str:
	value = re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_")
	return (value or "panel")[:60]


def generate_with_huggingface(prompt: str):
	if not HF_API_KEY:
		raise RuntimeError(
			"HF_API_KEY is missing. Add it to a .env file in the project root."
		)
	url = f"https://router.huggingface.co/hf-inference/models/{HF_IMAGE_MODEL}"
	response = requests.post(
		url,
		headers={"Authorization": f"Bearer {HF_API_KEY}"},
		json={"inputs": prompt},
		timeout=180,
	)
	if response.status_code != 200:
		if response.status_code in (401, 403):
			raise RuntimeError(
				"HF_API_KEY was rejected. Replace the placeholder with a valid Hugging Face token in env.example/.env."
			)
		raise RuntimeError(
			"Hugging Face image generation failed: "
			f"{response.status_code} {response.text[:500]}"
		)
	try:
		return Image.open(io.BytesIO(response.content)).convert("RGB")
	except Exception as exc:
		raise RuntimeError("Hugging Face returned an invalid image.") from exc


def generate_with_local_diffusers(prompt: str):
	try:
		import torch
		from diffusers import StableDiffusionPipeline
	except ImportError as exc:
		raise RuntimeError(
			"Local image generation needs torch, diffusers, transformers, and accelerate."
		) from exc
	dtype = torch.float16 if torch.cuda.is_available() else torch.float32
	pipe = StableDiffusionPipeline.from_pretrained(
		LOCAL_IMAGE_MODEL,
		torch_dtype=dtype,
	)
	if torch.cuda.is_available():
		pipe = pipe.to("cuda")
	return pipe(
		prompt,
		height=IMAGE_SIZE,
		width=IMAGE_SIZE,
		num_inference_steps=25,
	).images[0].convert("RGB")


def generate_image(image_prompt: str, panel_number: int, title: str):
	final_prompt = f"""{image_prompt}

Create a high-quality comic panel illustration with clear composition,
expressive characters, cinematic lighting, a detailed environment, consistent
character appearance, and professional comic artwork. Include no watermark or
readable text.
"""
	image = (
		generate_with_local_diffusers(final_prompt)
		if USE_LOCAL_DIFFUSERS
		else generate_with_huggingface(final_prompt)
	)
	filename = (
		f"{panel_number:02d}_{safe_filename(title)}_"
		f"{uuid.uuid4().hex[:8]}.png"
	)
	image.save(PANEL_DIR / filename, format="PNG")
	return f"/static/panels/{filename}"
