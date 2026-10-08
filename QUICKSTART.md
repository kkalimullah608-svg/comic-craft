# Run ComicCraft locally

## Start the server

From this project folder in PowerShell:

```powershell
& .\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Or double-click `run_local.bat` to start the same development server without activating the environment.

Open <http://127.0.0.1:8000> in your browser. Press Ctrl+C in the server window to stop it.

## Configure AI generation

The app reads environment variables from the project root `.env`, then falls back to `env.example/.env` for this project's existing setup. Keep valid `GEMINI_API_KEY` and `HF_API_KEY` values there. Gemini creates the outline and story; Hugging Face creates the panel images. Restart the server after changing keys.

The virtual environment is already present. If setting up from scratch, install the dependencies listed in `requirements.txt\requirement` with:

```powershell
python -m pip install -r .\requirements.txt\requirement
```

Generated panels and PDFs are saved under `static/panels` and `static/exports`.
