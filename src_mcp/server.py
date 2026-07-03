"""Repo Auditor MCP Server — анализ GitHub-репозиториев."""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from src_mcp.tools import clone_repo, analyze_structure, audit_quality, audit_honesty, generate_report


app = Server("repo-auditor")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="clone_repo",
            description="Клонировать репозиторий для анализа.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_url": {"type": "string", "description": "URL GitHub репо (https://github.com/owner/repo)"},
                    "output_dir": {"type": "string", "default": "/tmp/repo-audit"},
                },
                "required": ["repo_url"],
            },
        ),
        Tool(
            name="analyze_structure",
            description="Анализ структуры: языки, размер, файлы, директории.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                },
                "required": ["repo_path"],
            },
        ),
        Tool(
            name="audit_quality",
            description="Аудит качества кода: тесты, docs, dependencies, CI/CD, типы, security.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                },
                "required": ["repo_path"],
            },
        ),
        Tool(
            name="audit_honesty",
            description="Аудит честности README: что обещает vs что реально есть (TODOs, half-implementations).",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                },
                "required": ["repo_path"],
            },
        ),
        Tool(
            name="generate_report",
            description="Генерация финального отчёта: score 0-100, рекомендации, red flags.",
            inputSchema={
                "type": "object",
                "properties": {
                    "repo_path": {"type": "string"},
                },
                "required": ["repo_path"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    import json
    tools_map = {
        "clone_repo": clone_repo,
        "analyze_structure": analyze_structure,
        "audit_quality": audit_quality,
        "audit_honesty": audit_honesty,
        "generate_report": generate_report,
    }
    try:
        result = await tools_map[name].run(**arguments)
        return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]


async def main():
    async with stdio_server() as (rs, ws):
        await app.run(rs, ws, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
