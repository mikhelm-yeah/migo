"""Arena PLM API client for querying product and BOM data."""

import requests
import logging
from typing import Dict, List, Optional, Any
from config import Config

logger = logging.getLogger(__name__)


class ArenaClientError(Exception):
    """Custom exception for Arena API errors."""

    pass


class ArenaClient:
    """Client for interacting with Arena PLM REST API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize Arena client.

        Args:
            api_key: Arena API key (defaults to config)
            base_url: Arena API base URL (defaults to config)
        """
        self.api_key = api_key or Config.ARENA_API_KEY
        self.base_url = base_url or Config.ARENA_API_URL
        self.timeout = Config.ARENA_TIMEOUT
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _make_request(
        self, method: str, endpoint: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Arena API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            ArenaClientError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method,
                url,
                headers=self.headers,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Arena API request failed: {e}")
            raise ArenaClientError(f"Failed to query Arena: {str(e)}") from e

    def get_product(self, sku: str) -> Dict[str, Any]:
        """Retrieve product details by SKU.

        Args:
            sku: Product SKU

        Returns:
            Product data dictionary
        """
        logger.info(f"Fetching product: {sku}")
        return self._make_request("GET", f"/products/{sku}")

    def get_products_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Retrieve all products in a category.

        Args:
            category: Product category

        Returns:
            List of product data dictionaries
        """
        logger.info(f"Fetching products in category: {category}")
        response = self._make_request(
            "GET", "/products", params={"category": category}
        )
        return response.get("data", [])

    def get_bom(self, sku: str, revision: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve bill of materials for a product.

        Args:
            sku: Product SKU
            revision: Product revision (defaults to latest)

        Returns:
            BOM data dictionary with components
        """
        logger.info(f"Fetching BOM for: {sku} (revision: {revision or 'latest'})")
        endpoint = f"/products/{sku}/bom"
        params = {}
        if revision:
            params["revision"] = revision
        return self._make_request("GET", endpoint, params)

    def get_part_details(self, part_id: str) -> Dict[str, Any]:
        """Retrieve details for a specific part.

        Args:
            part_id: Part ID or number

        Returns:
            Part data dictionary
        """
        logger.info(f"Fetching part details: {part_id}")
        return self._make_request("GET", f"/parts/{part_id}")

    def search_products(self, query: str) -> List[Dict[str, Any]]:
        """Search for products by name or SKU.

        Args:
            query: Search query string

        Returns:
            List of matching products
        """
        logger.info(f"Searching for products: {query}")
        response = self._make_request("GET", "/products", params={"search": query})
        return response.get("data", [])

    def get_product_revisions(self, sku: str) -> List[Dict[str, Any]]:
        """Retrieve all revisions of a product.

        Args:
            sku: Product SKU

        Returns:
            List of revision data
        """
        logger.info(f"Fetching revisions for: {sku}")
        response = self._make_request("GET", f"/products/{sku}/revisions")
        return response.get("data", [])

    def get_change_orders(self, sku: str) -> List[Dict[str, Any]]:
        """Retrieve engineering change orders for a product.

        Args:
            sku: Product SKU

        Returns:
            List of change order data
        """
        logger.info(f"Fetching change orders for: {sku}")
        response = self._make_request("GET", f"/products/{sku}/change-orders")
        return response.get("data", [])
