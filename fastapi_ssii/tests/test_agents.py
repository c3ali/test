import pytest
from unittest.mock import AsyncMock
from fastapi_ssii.agents.architect_agent import ArchitectAgent
from fastapi_ssii.agents.business_analyst_agent import BusinessAnalystAgent
import json

@pytest.fixture
def mock_llm_client():
    client = AsyncMock()
    client.generate_with_gemini_async = AsyncMock()
    return client

# ... (Tests pour ArchitectAgent restent les mêmes)

class TestBusinessAnalystAgent:
    @pytest.mark.asyncio
    async def test_generate_returns_valid_tech_spec(self, mock_llm_client):
        # Arrange
        agent = BusinessAnalystAgent(mock_llm_client)
        spec = {"description": "un blog simple"}
        mock_response = json.dumps({
            "project_summary": "API de blog",
            "main_features": ["créer des articles"],
            "data_entities": [{"name": "Post", "fields": ["id", "title"]}]
        })
        mock_llm_client.generate_with_gemini_async.return_value = mock_response

        # Act
        tech_spec = await agent.generate(spec)

        # Assert
        assert "project_summary" in tech_spec
        assert "main_features" in tech_spec
        assert "data_entities" in tech_spec
        assert tech_spec["data_entities"][0]["name"] == "Post"
        mock_llm_client.generate_with_gemini_async.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_generate_handles_invalid_json(self, mock_llm_client):
        agent = BusinessAnalystAgent(mock_llm_client)
        spec = {"description": "test"}
        mock_llm_client.generate_with_gemini_async.return_value = "json invalide"

        with pytest.raises(json.JSONDecodeError):
            await agent.generate(spec)

    def test_validate_output_raises_error_on_missing_keys(self):
        agent = BusinessAnalystAgent(None)
        with pytest.raises(ValueError):
            agent.validate_output({"project_summary": "test"})
