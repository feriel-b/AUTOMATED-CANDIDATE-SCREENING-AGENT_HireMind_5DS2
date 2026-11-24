"""
Reusable tools for all agents.
"""

from langchain.tools import Tool
from typing import Dict, Any
import json

def create_json_parser_tool():
    """Tool to parse JSON strings."""
    def parse_json(json_str: str) -> Dict[str, Any]:
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Invalid JSON"}
    
    return Tool(
        name="parse_json",
        func=parse_json,
        description="Parse JSON string into dictionary"
    )

def create_text_formatter_tool():
    """Tool to format text output."""
    def format_text(text: str, max_length: int = 500) -> str:
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text
    
    return Tool(
        name="format_text",
        func=format_text,
        description="Format and truncate text to specified length"
    )