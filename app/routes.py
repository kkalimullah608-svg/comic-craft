"""Define web pages and API endpoints for creating ComicCraft comics."""

import asyncio

from fastapi import (
	APIRouter,
	Form,
	HTTPException,
	Request,
)
from fastapi.responses import (
	HTMLResponse,
	JSONResponse,
)

from app.schemas import PromptRequest
from app.gemini_flash import (
	generate_outline,
)
from app.gemini_pro import (
	generate_story,
)
from app.image_generator import (
	generate_image,
)
from app.layout_builder import (
	build_comic_layout,
)
from app.exporters import (
	save_pdf,
)


router = APIRouter()


def user_error_message(exc: Exception) -> str:
	"""Return a useful setup hint without exposing provider response details."""
	message = str(exc)
	if "GEMINI_API_KEY" in message:
		return "Gemini is not configured. Add a valid GEMINI_API_KEY to the project .env file and restart the server."
	if "HF_API_KEY" in message:
		return "Image generation is not configured. Add an HF_API_KEY to the project .env file, or enable local Diffusers in settings."
	return message or "Comic generation failed. Check the server terminal for details."


async def create_comic(
	data: PromptRequest
):

	outline = await asyncio.to_thread(
		generate_outline,
		data.story_prompt,
		data.character_name,
		data.setting,
		data.tone,
		data.art_style,
	)

	story = await asyncio.to_thread(
		generate_story,
		outline,
		data.character_name,
		data.tone,
	)

	image_paths = []

	for panel in outline:

		image_path = (
			await asyncio.to_thread(
				generate_image,
				panel["image_prompt"],
				int(
					panel["panel_number"]
				),
				panel["title"],
			)
		)

		image_paths.append(
			image_path
		)

	layout = build_comic_layout(
		outline,
		story,
		image_paths,
	)

	pdf_path = await asyncio.to_thread(
		save_pdf,
		layout,
		data.character_name,
	)

	return (
		layout,
		pdf_path
	)


@router.get(
	"/",
	response_class=HTMLResponse
)
async def home(
	request: Request
):

	return request.app.state.templates.TemplateResponse(
		request,
		"index.html",
		{
			"request": request
		}
	)


@router.post(
	"/generate",
	response_class=HTMLResponse
)
async def generate(
	request: Request,

	story_prompt: str = Form(...),

	character_name: str = Form(...),

	setting: str = Form(...),

	tone: str = Form(...),

	art_style: str = Form(...),
):

	try:

		data = PromptRequest(

			story_prompt=story_prompt,

			character_name=character_name,

			setting=setting,

			tone=tone,

			art_style=art_style,
		)

		layout, pdf_path = (
			await create_comic(
				data
			)
		)

		return (
			request.app.state
			.templates
			.TemplateResponse(
				request,
				"comic_preview.html",
				{
					"request": request,
					"layout": layout,
					"pdf_path": pdf_path,
				},
			)
		)

	except Exception as exc:

		return (
			request.app.state
			.templates
			.TemplateResponse(
				request,
				"index.html",
				{
					"request": request,
					"error": user_error_message(exc),
				},
			)
		)


@router.post(
	"/generate-comic/json"
)
async def generate_json(
	data: PromptRequest
):

	try:

		layout, pdf_path = (
			await create_comic(
				data
			)
		)

		return JSONResponse({

			"success": True,

			"layout": layout,

			"pdf_path": pdf_path,

		})

	except Exception as exc:

		raise HTTPException(
			status_code=500,
			detail=user_error_message(exc),
		)


@router.get(
	"/export-success",
	response_class=HTMLResponse
)
async def export_success(
	request: Request
):

	return (
		request.app.state
		.templates
		.TemplateResponse(
			request,
			"export_success.html",
			{
				"request": request
			},
		)
	)


@router.post(
	"/test-image"
)
async def test_image(
	prompt: str = Form(...)
):

	try:

		image_path = (
			await asyncio.to_thread(
				generate_image,
				prompt,
				0,
				"test"
			)
		)

		return {

			"success": True,

			"image_path": image_path,

		}

	except Exception as exc:

		raise HTTPException(
			status_code=500,
			detail=user_error_message(exc),
		)
