import json
import streamlit as st
from services.ai_service import analyze_with_ai, is_ai_configured
from services.project_store import save_project, load_projects
from services.validators import validate_project

st.set_page_config(page_title="Construction Intelligence", page_icon="🏗️", layout="wide")

st.title("🏗️ Multimodal Construction Intelligence Platform")
st.caption("AI-assisted construction insights from project details, questions, and site images.")

with st.sidebar:
    st.header("Settings")
    st.write("AI status:", "🟢 Gemini API configured" if is_ai_configured() else "🟡 Demo mode — add a Gemini API key for live AI analysis")
    st.info("AI results are preliminary guidance. They do not replace professional structural, safety, legal, or valuation assessments.")
    page = st.radio("Choose a module", [
        "Site Safety Monitoring", "Crack Detection & Analysis", "Real Estate Valuation",
        "Construction Project Planning", "Daily Site Assistant", "Weather-aware Advisory",
        "Construction Knowledge Assistant", "Saved Projects"
    ])

MODULES = {
    "Site Safety Monitoring": "Assess visible site hazards, unsafe practices, PPE concerns, and practical mitigation steps.",
    "Crack Detection & Analysis": "Review a photo for visible crack patterns and describe uncertainty, possible causes, and recommended professional follow-up. Never certify structural safety.",
    "Real Estate Valuation": "Create a rough, assumption-based property value estimate from the supplied data. Clearly state that this is not a formal valuation.",
    "Construction Project Planning": "Build a practical project plan with phases, dependencies, approximate durations, resources, and risks.",
    "Daily Site Assistant": "Provide a daily construction site checklist, coordination priorities, and progress-report template.",
    "Weather-aware Advisory": "Give general weather-aware site precautions using the weather details supplied by the user. Do not invent live weather data.",
    "Construction Knowledge Assistant": "Answer construction-related questions in clear, practical language and identify when a licensed professional is needed."
}

if page == "Saved Projects":
    st.subheader("Saved project records")
    records = load_projects()
    if not records:
        st.write("No projects saved yet. Use a module and select **Save project record** after an analysis.")
    else:
        for record in reversed(records):
            with st.expander(f"{record.get('project_name', 'Untitled project')} — {record.get('module', 'Unknown module')} — {record.get('created_at', '')}"):
                st.json(record)
else:
    st.subheader(page)
    st.write(MODULES[page])
    with st.form("analysis_form"):
        project_name = st.text_input("Project name", placeholder="e.g. Green Valley Residential Building")
        location = st.text_input("Project location (optional)", placeholder="City / region")
        context = st.text_area("Project details / question", height=150, placeholder="Describe the site, building, issue, dimensions, materials, budget, schedule, or question...")
        image_file = None
        if page in ("Site Safety Monitoring", "Crack Detection & Analysis"):
            image_file = st.file_uploader("Upload a site image (optional)", type=["png", "jpg", "jpeg", "webp"])
        if page == "Real Estate Valuation":
            c1, c2 = st.columns(2)
            with c1:
                area = st.number_input("Built-up area (sq ft)", min_value=0.0, value=1000.0, step=50.0)
                age = st.number_input("Property age (years)", min_value=0, value=0, step=1)
            with c2:
                rate = st.number_input("Local rate per sq ft (optional)", min_value=0.0, value=0.0, step=100.0)
                condition = st.selectbox("Property condition", ["Not specified", "New", "Good", "Needs repair"])
            context += f"\nProperty data: area_sq_ft={area}; age_years={age}; user_supplied_local_rate_per_sq_ft={rate}; condition={condition}. If no reliable local rate is supplied, do not invent a precise market value."
        if page == "Weather-aware Advisory":
            weather = st.text_input("Current/forecast weather (enter it yourself)", placeholder="e.g. heavy rain expected this afternoon")
            context += f"\nUser-provided weather information: {weather or 'Not provided'}. Do not claim to have fetched live weather."
        submitted = st.form_submit_button("Generate analysis", type="primary", use_container_width=True)

    if submitted:
        errors = validate_project(project_name, context)
        if errors:
            for error in errors:
                st.error(error)
        else:
            with st.spinner("Preparing construction insights..."):
                image_bytes = image_file.getvalue() if image_file else None
                image_mime = image_file.type if image_file else None
                result = analyze_with_ai(module=page, project_name=project_name, location=location, context=context,
                                         image_bytes=image_bytes, image_mime=image_mime)
            st.markdown("### Analysis")
            st.markdown(result.get("summary", "No summary returned."))
            if result.get("key_findings"):
                st.markdown("### Key findings")
                for item in result["key_findings"]:
                    st.markdown(f"- {item}")
            if result.get("recommended_actions"):
                st.markdown("### Recommended actions")
                for item in result["recommended_actions"]:
                    st.markdown(f"- {item}")
            if result.get("risks_or_uncertainties"):
                st.markdown("### Risks and uncertainties")
                for item in result["risks_or_uncertainties"]:
                    st.markdown(f"- {item}")
            with st.expander("View structured JSON response"):
                st.json(result)
            st.download_button("Download analysis as JSON", data=json.dumps(result, indent=2),
                               file_name="construction_analysis.json", mime="application/json")
            if st.button("Save project record"):
                saved = save_project({"project_name": project_name, "location": location, "module": page,
                                      "context": context, "analysis": result})
                st.success("Project record saved." if saved else "Could not save this record in the current environment.")
