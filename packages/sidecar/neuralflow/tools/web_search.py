import os
from typing import Any

import httpx

from neuralflow.tools.base import BaseTool


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web and return top results for a query."
    input_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "num_results": {"type": "integer", "description": "Number of results (default 5)", "default": 5},
        },
        "required": ["query"],
    }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        query = input_data["query"]
        num_results = input_data.get("num_results", 5)

        # Try Serper API first, then DuckDuckGo
        serper_key = os.environ.get("SERPER_API_KEY")
        if serper_key:
            return await self._serper_search(query, num_results, serper_key)

        tavily_key = os.environ.get("TAVILY_API_KEY")
        if tavily_key:
            return await self._tavily_search(query, num_results, tavily_key)

        # DuckDuckGo instant answer (no key needed)
        return await self._ddg_search(query, num_results)

    async def _serper_search(self, query: str, n: int, key: str) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": key, "Content-Type": "application/json"},
                json={"q": query, "num": n},
            )
            r.raise_for_status()
            data = r.json()
            results = [
                {"title": item.get("title"), "url": item.get("link"), "snippet": item.get("snippet")}
                for item in data.get("organic", [])[:n]
            ]
            return {"results": results, "provider": "serper"}

    async def _tavily_search(self, query: str, n: int, key: str) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                "https://api.tavily.com/search",
                json={"api_key": key, "query": query, "max_results": n},
            )
            r.raise_for_status()
            data = r.json()
            results = [
                {"title": item.get("title"), "url": item.get("url"), "snippet": item.get("content")}
                for item in data.get("results", [])[:n]
            ]
            return {"results": results, "provider": "tavily"}

    async def _ddg_search(self, query: str, n: int) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json", "no_redirect": "1"},
                headers={"User-Agent": "NeuralFlow/0.1"},
            )
            r.raise_for_status()
            data = r.json()
            results = []
            for item in data.get("RelatedTopics", [])[:n]:
                if isinstance(item, dict) and "Text" in item:
                    results.append({"title": item.get("Text", ""), "url": item.get("FirstURL", ""), "snippet": item.get("Text", "")})
            return {"results": results, "provider": "duckduckgo"}
