"""Legacy comic image generation module retained for root-level imports."""

import io
import re
import uuid
from pathlib import Path

import requests
from PIL import Image

from app.config import (
	HF_API_KEY,
	HF_IMAGE_MODEL,
	USE_LOCAL_DIFFUSERS,
	LOCAL_IMAGE_MODEL,
	IMAGE_SIZE,
)


BASE_DIR = Path(__file__).resolve().parent.parent

PANEL_DIR = (
	BASE_DIR
	/ "static"
	/ "panels"
)

PANEL_DIR.mkdir(
	parents=True,
	exist_ok=True
)


def safe_filename(text: str):

	value = re.sub(
		r"[^a-zA-Z0-9_-]+",
		"_",
		text
	)

	value = value.strip("_")

	if not value:

		value = "panel"

	return value[:60]


def generate_with_huggingface(
	prompt: str
):

	if not HF_API_KEY:

		raise RuntimeError(
			"HF_API_KEY is missing. "
			"Please add it to your .env file."
		)

	url = (
		"https://router.huggingface.co/"
		f"hf-inference/models/{HF_IMAGE_MODEL}"
	)

	response = requests.post(
		url,
		headers={
			"Authorization":
			f"Bearer {HF_API_KEY}"
		},
		json={
			"inputs": prompt
		},
		timeout=180,
	)

	if response.status_code != 200:

		raise RuntimeError(
			"Hugging Face image generation failed: "
			f"{response.status_code} "
			f"{response.text[:500]}"
		)

	image = Image.open(
		io.BytesIO(
			response.content
		)
	)

	return image.convert("RGB")


def generate_with_local_diffusers(
	prompt: str
):

	try:

		import torch

		from diffusers import (
			StableDiffusionPipeline
		)

	except ImportError as exc:

		raise RuntimeError(
			"Install torch, diffusers, "
			"transformers and accelerate "
			"for local image generation."
		) from exc

	dtype = (
		torch.float16
		if torch.cuda.is_available()
		else torch.float32
	)

	pipe = (
		StableDiffusionPipeline
		.from_pretrained(
			LOCAL_IMAGE_MODEL,
			torch_dtype=dtype,
		)
	)

	if torch.cuda.is_available():

		pipe = pipe.to("cuda")

	image = pipe(
		prompt,
		height=IMAGE_SIZE,
		width=IMAGE_SIZE,
		num_inference_steps=25,
	).images[0]

	return image.convert("RGB")


def generate_image(
	image_prompt: str,
	panel_number: int,
	title: str,
):

	final_prompt = f"""
{image_prompt}

Create a high-quality comic panel illustration.

Visual requirements:
- clear composition
- expressive characters
- cinematic lighting
- detailed environment
- consistent character appearance
- professional comic artwork
- no watermark
- no readable text
"""

	if USE_LOCAL_DIFFUSERS:

		image = generate_with_local_diffusers(
			final_prompt
		)

	else:

		image = generate_with_huggingface(
			final_prompt
		)

	filename = (
		f"{panel_number:02d}_"
		f"{safe_filename(title)}_"
		f"{uuid.uuid4().hex[:8]}.png"
	)

	output_path = (
		PANEL_DIR / filename
	)

	image.save(
		output_path,
		format="PNG"
	)

	return (
		f"/static/panels/{filename}"
	)
