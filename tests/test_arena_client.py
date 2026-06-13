"""Tests for Arena client."""

import pytest
from unittest.mock import Mock, patch
from arena_client import ArenaClient, ArenaClientError


@pytest.fixture
def arena_client():
    """Create arena client for testing."""
    return ArenaClient(api_key="test-key", base_url="https://api.test.com")


def test_client_initialization(arena_client):
    """Test client initialization."""
    assert arena_client.api_key == "test-key"
    assert arena_client.base_url == "https://api.test.com"


@patch("requests.request")
def test_get_product(mock_request, arena_client):
    """Test get_product method."""
    mock_response = Mock()
    mock_response.json.return_value = {"sku": "SKU-123", "name": "Test Product"}
    mock_request.return_value = mock_response
    
    result = arena_client.get_product("SKU-123")
    
    assert result["sku"] == "SKU-123"
    mock_request.assert_called_once()


@patch("requests.request")
def test_get_bom(mock_request, arena_client):
    """Test get_bom method."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "sku": "SKU-123",
        "components": [{"part_number": "PART-001"}]
    }
    mock_request.return_value = mock_response
    
    result = arena_client.get_bom("SKU-123")
    
    assert result["sku"] == "SKU-123"
    assert len(result["components"]) == 1
