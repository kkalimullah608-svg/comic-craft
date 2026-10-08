"""Load environment settings used by the ComicCraft application."""

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Load the conventional project-root file first, then the checked-in local
# example path for this project. Existing process variables always win.
ROOT_ENV_FILE = BASE_DIR / ".env"
FALLBACK_ENV_FILE = BASE_DIR / "env.example" / ".env"

load_dotenv(ROOT_ENV_FILE, override=False)
load_dotenv(FALLBACK_ENV_FILE, override=False)

ENV_FILE = ROOT_ENV_FILE if ROOT_ENV_FILE.is_file() else FALLBACK_ENV_FILE


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

HF_API_KEY = os.getenv("HF_API_KEY", "")


GEMINI_MODEL = os.getenv(
	"GEMINI_MODEL",
	"gemini-2.5-flash"
)

GEMINI_STORY_MODEL = os.getenv(
	"GEMINI_STORY_MODEL",
	"gemini-2.5-flash"
)


HF_IMAGE_MODEL = os.getenv(
	"HF_IMAGE_MODEL",
	"stabilityai/stable-diffusion-xl-base-1.0"
)


USE_LOCAL_DIFFUSERS = (
	os.getenv(
		"USE_LOCAL_DIFFUSERS",
		"false"
	).lower()
	== "true"
)


LOCAL_IMAGE_MODEL = os.getenv(
	"LOCAL_IMAGE_MODEL",
	"runwayml/stable-diffusion-v1-5"
)


NUM_PANELS = int(
	os.getenv(
		"NUM_PANELS",
		"5"
	)
)

if not 1 <= NUM_PANELS <= 12:
	raise ValueError("NUM_PANELS must be between 1 and 12.")


IMAGE_SIZE = int(
	os.getenv(
		"IMAGE_SIZE",
		"768"
	)
)

if IMAGE_SIZE < 256 or IMAGE_SIZE > 1024 or IMAGE_SIZE % 8:
	raise ValueError("IMAGE_SIZE must be a multiple of 8 between 256 and 1024.")
