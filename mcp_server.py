import requests

from mcp.server.mcpserver import MCPServer


mcp = MCPServer("AudioBook Repository")


GITHUB_API_URL = "https://api.github.com/repos/Python-World/python-mini-projects/contents/projects/AudioBook?ref=master"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Python-World/python-mini-projects/master/projects/AudioBook"


@mcp.tool()
def list_repository_files() -> list[str]:

    response = requests.get(GITHUB_API_URL)
    response.raise_for_status()

    files = []

    for item in response.json():
        if item["type"] == "file":
            files.append(item["name"])

    return files


@mcp.tool()
def read_repository_file(filename: str) -> str:

    url = f"{GITHUB_RAW_URL}/{filename}"

    response = requests.get(url)

    if response.status_code == 404:
        return f"File not found: {filename}"

    response.raise_for_status()

    return response.text


if __name__ == "__main__":
    mcp.run()