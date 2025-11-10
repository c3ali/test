def generate_frontend_code(plan: dict) -> dict:
    """
    Generates the frontend code based on the project plan.
    For now, returns a placeholder for the frontend.
    """
    return {
        "index.html": "<h1>Welcome to your new application!</h1>",
        "style.css": "body { font-family: sans-serif; }",
        "script.js": "console.log('Hello from your generated frontend!');"
    }
