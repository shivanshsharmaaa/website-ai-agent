
import os
import json

from dotenv import load_dotenv
from groq import Groq

from file_tools import (
    create_directory,
    write_file,
    read_file,
    list_files,
)

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
# MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

if not API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY missing. Check your .env file."
    )

client = Groq(api_key=API_KEY)

SYSTEM_PROMPT = """
You are a website-building AI agent.

Your job is to create and update complete static websites by using tools.

Rules:
1. All website files must stay inside the workspace sandbox.
2. Never request or reveal API keys, secrets, or environment files.
3. Never use shell commands or execute arbitrary code.
4. Create a separate folder for each website, such as portfolio/.
5. Use HTML, CSS and vanilla JavaScript.
6. Create a complete, attractive, responsive website.
7. Use create_directory before writing into a new directory.
8. Use read_file and list_files to inspect existing projects before editing.
9. Use write_file to create or update website files.
10. Prefer index.html, style.css and script.js when appropriate.
11. Use relative paths for website assets.
12. If a tool fails, inspect the error and try a safe correction.
13. Do not claim a file was created unless a tool confirms it.
14. Keep responses concise and minimize unnecessary tool calls.
15. Do not output entire source files in the final response.
   Briefly report what was created and where.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Create a directory inside the workspace sandbox.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path, e.g. portfolio"
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or update a text file inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative file path, e.g. portfolio/index.html"
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete text content of the file"
                    }
                },
                "required": ["path", "content"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file that exists inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories inside the workspace.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path; use . for workspace root"
                    }
                },
                "required": ["path"],
                "additionalProperties": False
            }
        }
    }
]

FUNCTIONS = {
    "create_directory": create_directory,
    "write_file": write_file,
    "read_file": read_file,
    "list_files": list_files,
}


def execute_tool(name: str, arguments: dict) -> dict:
    """Execute only explicitly allowed sandbox tools."""
    function = FUNCTIONS.get(name)

    if function is None:
        return {"success": False, "error": "Tool not allowed."}

    try:
        if not isinstance(arguments, dict):
            return {"success": False, "error": "Invalid tool arguments."}

        if name == "create_directory":
            return function(arguments["path"])

        if name == "write_file":
            return function(
                arguments["path"],
                arguments["content"]
            )

        if name == "read_file":
            return function(arguments["path"])

        if name == "list_files":
            return function(arguments.get("path", "."))

        return {"success": False, "error": "Unsupported operation."}

    except (KeyError, TypeError, ValueError) as error:
        return {"success": False, "error": str(error)}


def run_agent(user_message: str) -> str:
    """Run the Groq agent with a bounded tool-calling loop."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    tool_calls_used = 0
    max_tool_calls = 10

    for _ in range(8):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2,
            max_tokens=1800,
        )

        assistant_message = response.choices[0].message
        tool_calls = assistant_message.tool_calls

        if not tool_calls:
            return assistant_message.content or "Task completed."

        # Preserve the model's complete tool-call message.
        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        for tool_call in tool_calls:
            if tool_calls_used >= max_tool_calls:
                messages.append({
                    "role": "user",
                    "content": (
                        "Tool-call limit reached. Stop making tool calls "
                        "and briefly report the current result."
                    ),
                })
                break

            name = tool_call.function.name

            try:
                arguments = json.loads(
                    tool_call.function.arguments or "{}"
                )
                result = execute_tool(name, arguments)
            except (json.JSONDecodeError, TypeError, ValueError) as error:
                result = {
                    "success": False,
                    "error": f"Invalid tool arguments: {error}"
                }

            tool_calls_used += 1

            # Keep tool output small to control token usage.
            result_text = json.dumps(
                result,
                ensure_ascii=False
            )[:12000]

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": name,
                "content": result_text,
            })

        if tool_calls_used >= max_tool_calls:
            break

    return (
        "Tool-call limit reached. Check the workspace files "
        "to see which changes were completed."
    )


if __name__ == "__main__":
    prompt = input("What website should I create? ").strip()

    if prompt:
        try:
            print("\nAgent is working...\n")
            print(run_agent(prompt))
        except Exception as error:
            print(f"\nAgent error: {error}")




