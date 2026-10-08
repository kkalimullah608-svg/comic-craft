"""Export completed comic layouts as downloadable PDF files."""

from datetime import datetime
from pathlib import Path

from fpdf import FPDF


BASE_DIR = Path(__file__).resolve().parent.parent

EXPORT_DIR = (
	BASE_DIR
	/ "static"
	/ "exports"
)

EXPORT_DIR.mkdir(
	parents=True,
	exist_ok=True
)


def get_local_image_path(
	image_path: str
):

	clean_path = image_path.lstrip(
		"/"
	)

	return (
		BASE_DIR / clean_path
	)


def save_pdf(
	layout,
	character_name
):

	filename = (
		"comic_"
		+ datetime.now().strftime(
			"%Y%m%d_%H%M%S"
		)
		+ ".pdf"
	)

	pdf_path = (
		EXPORT_DIR / filename
	)

	pdf = FPDF()

	pdf.set_auto_page_break(
		auto=True,
		margin=15
	)

	for panel in layout:

		pdf.add_page()

		pdf.set_font(
			"Helvetica",
			"B",
			18
		)

		pdf.cell(
			0,
			12,
			(
				f"Panel "
				f"{panel['panel_number']}: "
				f"{panel['title']}"
			),
			ln=True,
		)

		image_file = (
			get_local_image_path(
				panel["image_path"]
			)
		)

		if image_file.exists():

			pdf.image(
				str(image_file),
				x=15,
				y=30,
				w=180
			)

			pdf.ln(105)

		else:

			pdf.ln(5)

		pdf.set_font(
			"Helvetica",
			"I",
			11
		)

		pdf.multi_cell(
			0,
			7,
			panel.get(
				"scene_description",
				""
			)
		)

		pdf.ln(2)

		pdf.set_font(
			"Helvetica",
			"",
			11
		)

		caption = panel.get(
			"caption",
			""
		)

		narration = panel.get(
			"narration",
			""
		)

		dialogue = panel.get(
			"dialogue",
			""
		)

		if caption:

			pdf.multi_cell(
				0,
				7,
				"Caption: " + caption
			)

		if narration:

			pdf.multi_cell(
				0,
				7,
				"Narration: " + narration
			)

		if dialogue:

			pdf.multi_cell(
				0,
				7,
				"Dialogue: " + dialogue
			)

	pdf.output(
		str(pdf_path)
	)

	return (
		f"/static/exports/{filename}"
	)
