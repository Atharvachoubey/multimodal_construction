def validate_project(project_name: str, context: str) -> list[str]:
    errors = []
    if not project_name.strip():
        errors.append("Enter a project name.")
    if not context.strip():
        errors.append("Enter project details or a question before generating analysis.")
    if len(context) > 12000:
        errors.append("Please keep the project details under 12,000 characters.")
    return errors
