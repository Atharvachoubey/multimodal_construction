# Multimodal Construction Intelligence Platform

A Streamlit-deployable Python application for AI-assisted construction workflows. It accepts text and optional site images, routes requests through modular backend services, and returns structured JSON results.

## Modules

- Site safety monitoring (preliminary visual/text review)
- Visible crack analysis (not a structural diagnosis)
- Illustrative real-estate valuation support
- Construction project planning
- Daily site assistance
- Weather-aware advisory based only on weather details the user provides
- Construction knowledge assistant
- Saved project records

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\\Scripts\\activate     # Windows PowerShell
pip install -r requirements.txt
streamlit run app.py
```

The app runs in demo mode without an API key. For live multimodal AI, create `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-real-key"
```

Get a key from Google AI Studio. Keep the key private and never upload `secrets.toml` to GitHub. You can optionally set `GEMINI_MODEL` in secrets or environment variables.

Alternatively, for local development, copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

The application loads `.env` automatically at startup. Supported variables are:

- `GEMINI_API_KEY` (required for live AI)
- `GEMINI_MODEL` (optional; defaults to `gemini-2.5-flash`)

Keep `.env` private and never commit it. Environment variables and Streamlit
Secrets take precedence over values loaded from `.env`.

## Deploy to Streamlit Community Cloud

1. Create a GitHub repository and upload the contents of this folder (not the parent folder).
2. Open Streamlit Community Cloud and create a new app from that repository.
3. Set the main file path to `app.py`.
4. In the app's **Settings → Secrets**, add:

   ```toml
   GEMINI_API_KEY = "your-real-key"
   ```

5. Deploy. Streamlit installs dependencies from `requirements.txt`.

## Important deployment notes

- Streamlit Community Cloud filesystems are not durable storage. This app's JSON saved-project feature is a simple demo and saved records may disappear after restarts/redeployments. Use a hosted database/object store for persistent multi-user storage.
- Do not upload private construction/site images or sensitive project information unless authorized.
- This application does not fetch live weather, inspect building internals, verify regulatory compliance, or provide certified engineering/valuation reports.
- Before production use, add authentication, access controls, rate limiting, robust logging, tests, and a persistent database.
