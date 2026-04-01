from typing import Any

import httpx

from neuralflow.tools.base import BaseTool


class HttpRequestTool(BaseTool):
    name = "http_request"
    description = "Make an HTTP GET or POST request and return the response."
    input_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to request"},
            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"], "default": "GET"},
            "headers": {"type": "object", "description": "HTTP headers"},
            "body": {"type": "object", "description": "JSON body for POST/PUT"},
            "timeout": {"type": "number", "description": "Timeout in seconds", "default": 30},
        },
        "required": ["url"],
    }

    async def execute(self, input_data: dict[str, Any]) -> Any:
        url = input_data["url"]
        method = input_data.get("method", "GET").upper()
        headers = input_data.get("headers", {})
        body = input_data.get("body")
        timeout = input_data.get("timeout", 30)

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=body if body else None,
            )
            content_type = response.headers.get("content-type", "")
            try:
                body_out = response.json() if "json" in content_type else response.text
            except Exception:
                body_out = response.text

            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": body_out,
            }
