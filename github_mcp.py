import os
import httpx

from mcp import Client
from mcp.client.streamable_http import streamable_http_client


GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"


def extract_text(result):

    for content in result.content:

        if hasattr(content, "resource"):

            resource = content.resource

            if hasattr(resource, "text"):

                return resource.text

        if hasattr(content, "text"):

            return content.text

    return ""


async def list_repository_files(
    owner,
    repo,
    path="/"
):

    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        raise ValueError(
            "GITHUB_TOKEN is not set."
        )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "X-MCP-Tools": "get_file_contents"
    }

    async with httpx.AsyncClient(
        headers=headers
    ) as http_client:

        transport = streamable_http_client(
            GITHUB_MCP_URL,
            http_client=http_client
        )

        async with Client(transport) as client:

            await client.list_tools()

            result = await client.call_tool(
                "get_file_contents",
                {
                    "owner": owner,
                    "repo": repo,
                    "path": path
                }
            )

            if getattr(result, "is_error", False):

                raise RuntimeError(
                    f"GitHub MCP error: {result}"
                )

            return extract_text(result)


async def get_repository_file(
    owner,
    repo,
    path
):

    github_token = os.getenv("GITHUB_TOKEN")

    if not github_token:
        raise ValueError(
            "GITHUB_TOKEN is not set."
        )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "X-MCP-Tools": "get_file_contents"
    }

    async with httpx.AsyncClient(
        headers=headers
    ) as http_client:

        transport = streamable_http_client(
            GITHUB_MCP_URL,
            http_client=http_client
        )

        async with Client(transport) as client:

            await client.list_tools()

            result = await client.call_tool(
                "get_file_contents",
                {
                    "owner": owner,
                    "repo": repo,
                    "path": path
                }
            )

            if getattr(result, "is_error", False):

                raise RuntimeError(
                    f"GitHub MCP error: {result}"
                )

            return extract_text(result)