"""Create and configure the ComicCraft FastAPI application."""

import pathlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes import router


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

app = FastAPI(
	title="ComicCraft",
	description="AI Comic Story Creator using Gemini and Hugging Face",
	version="1.0.0",
)

app.mount(
	"/static",
	StaticFiles(directory=str(BASE_DIR / "static")),
	name="static",
)

app.state.templates = Jinja2Templates(
	directory=str(BASE_DIR / "templates")
)

app.include_router(router)
