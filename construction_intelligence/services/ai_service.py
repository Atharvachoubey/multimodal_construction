import json
import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
except ImportError:
    st = None


def _get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if key:
        return key
    if st is not None:
        try:
            return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        except Exception:
            return ""
    return ""


def is_ai_configured() -> bool:
    return bool(_get_api_key())


def _demo_response(module: str, project_name: str, context: str, has_image: bool) -> dict[str, Any]:
    image_note = " An image was supplied, but demo mode cannot inspect it." if has_image else ""
    if module == "Crack Detection & Analysis":
        summary = "Demo mode only: no image model was run, so no crack characteristics or structural conclusions can be drawn."
        findings = ["Upload an image with the Gemini API configured to request a visual review.", "A photograph alone cannot establish structural safety or the cause/depth of a crack."]
        actions = ["Document crack location, approximate width and length, and whether it is changing.", "If cracks are widening, diagonal near supports, accompanied by sagging, or associated with unusual sounds/movement, restrict access as appropriate and contact a qualified structural engineer promptly."]
        risks = ["This is not an actual image assessment or a structural diagnosis."]
    elif module == "Site Safety Monitoring":
        summary = "Demo mode: provide a Gemini API key for AI review of the description and any site image."
        findings = ["No site-specific hazards have been verified."]
        actions = ["Use a site-specific safety checklist and have a competent safety professional inspect the site.", "Check PPE, edge protection, scaffolding, lifting operations, electrical hazards, housekeeping, and access routes."]
        risks = ["This demo has not inspected the site." ]
    elif module == "Real Estate Valuation":
        summary = "Demo mode: no market valuation was generated. A credible estimate needs local comparable sales, location, property condition, and other relevant details."
        findings = ["No independent market data was consulted."]
        actions = ["Collect recent comparable transactions and confirm the area, tenure/title, age, condition, amenities, and local market context.", "Use a qualified local valuer for formal valuation needs."]
        risks = ["Do not use this demo output for lending, legal, tax, or purchase decisions."]
    else:
        summary = "Demo mode: the backend is running, but live AI is disabled until GEMINI_API_KEY is configured."
        findings = ["Your request has been received.", f"Project: {project_name or 'Not specified'}."]
        actions = ["Add a Gemini API key in Streamlit Secrets to enable model-generated responses.", "Provide project-specific measurements, constraints, and local requirements for more useful recommendations."]
        risks = ["No live AI reasoning or external data lookup was performed."]
    return {"module": module, "project_name": project_name, "mode": "demo", "summary": summary + image_note,
            "key_findings": findings, "recommended_actions": actions, "risks_or_uncertainties": risks,
            "user_context": context[:2000], "disclaimer": "AI guidance is not a substitute for qualified professional assessment."}


def analyze_with_ai(module: str, project_name: str, location: str, context: str,
                    image_bytes: bytes | None = None, image_mime: str | None = None) -> dict[str, Any]:
    api_key = _get_api_key()
    if not api_key:
        return _demo_response(module, project_name, context, bool(image_bytes))

    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        system_prompt = """You are a cautious construction decision-support assistant. Respond only with valid JSON using this schema:
{"module": string, "project_name": string, "mode": "ai", "summary": string, "key_findings": [string], "recommended_actions": [string], "risks_or_uncertainties": [string], "professional_follow_up": [string], "disclaimer": string}
Be practical, explicit about assumptions, and avoid inventing facts or live data. If details are missing, say so. Never claim certification or certainty from an image. For cracks, describe only visible characteristics, not hidden depth or structural capacity; recommend a qualified structural engineer when warranted. For safety, do not declare a site safe based only on an image. For valuation, do not fabricate market comparables or rates; provide calculations only from user-supplied figures and label them illustrative. Weather advice must use only weather information supplied by the user. Include a disclaimer that this is not a substitute for a qualified professional."""
        user_prompt = f"Module: {module}\nProject name: {project_name}\nLocation: {location or 'Not provided'}\nUser input: {context}\nReturn useful, specific guidance without unsupported claims."
        parts: list[Any] = [system_prompt, user_prompt]
        if image_bytes:
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type=image_mime or "image/jpeg"))
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=parts,
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.2)
        )
        parsed = json.loads(response.text)
        parsed.setdefault("module", module)
        parsed.setdefault("project_name", project_name)
        parsed["mode"] = "ai"
        parsed.setdefault("disclaimer", "AI guidance is not a substitute for qualified professional assessment.")
        return parsed
    except Exception as exc:
        return {"module": module, "project_name": project_name, "mode": "error",
                "summary": "The AI request could not be completed. Check the API key, model availability, network connection, and quota.",
                "key_findings": [], "recommended_actions": ["Verify GEMINI_API_KEY in Streamlit Secrets and check the application logs."],
                "risks_or_uncertainties": [f"Technical error: {type(exc).__name__}: {str(exc)[:300]}"],
                "disclaimer": "AI guidance is not a substitute for qualified professional assessment."}
