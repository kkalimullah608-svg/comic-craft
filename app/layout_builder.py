"""Assemble story panels, generated images, and text into comic layout data."""

def build_comic_layout(outline, story, image_paths):
	story_by_panel = {
		int(item["panel_number"]): item
		for item in story
		if "panel_number" in item
	}
	layout = []
	for index, panel in enumerate(outline):
		number = int(panel["panel_number"])
		story_data = story_by_panel.get(number, {})
		layout.append({
			"panel_number": number,
			"title": panel.get("title", f"Panel {number}"),
			"scene_description": panel.get("scene_description", ""),
			"image_prompt": panel.get("image_prompt", ""),
			"image_path": image_paths[index],
			"caption": story_data.get("caption", ""),
			"narration": story_data.get("narration", ""),
			"dialogue": story_data.get("dialogue", ""),
		})
	return layout
