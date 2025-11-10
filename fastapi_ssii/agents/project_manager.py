from fastapi_ssii.agents import architect, backend_developer, frontend_developer, qa_engineer

def generate_project(description: str) -> dict:
    """
    Orchestrates the project generation process.
    """
    # 1. Call the architect to design the project
    project_plan = architect.design_project(description)

    # 2. Call the backend developer to generate the code
    backend_code = backend_developer.generate_backend_code(project_plan)

    # 3. Call the frontend developer to generate the code
    frontend_code = frontend_developer.generate_frontend_code(project_plan)

    # 4. Call the QA engineer to generate tests
    tests = qa_engineer.generate_tests(backend_code)

    # 5. Combine all the generated code
    full_code = {**backend_code, **frontend_code, **tests}

    return full_code
