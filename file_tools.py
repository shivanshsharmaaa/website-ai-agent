
from pathlib import Path

# All generated websites must stay inside this workspace.
WORKSPACE = (Path(__file__).resolve().parent / "workspace").resolve()
WORKSPACE.mkdir(parents=True, exist_ok=True)


def safe_path(relative_path: str) -> Path:
    """Resolve a relative path and prevent access outside workspace."""

    target = (WORKSPACE / relative_path).resolve()

    if target != WORKSPACE and WORKSPACE not in target.parents:
        raise ValueError("Access outside workspace is not allowed.")

    return target


def create_directory(path: str) -> dict:
    """Create a directory inside the workspace."""

    try:
        target = safe_path(path)
        target.mkdir(parents=True, exist_ok=True)

        return {
            "success": True,
            "path": str(target.relative_to(WORKSPACE))
        }
    except (ValueError, OSError) as error:
        return {"success": False, "error": str(error)}


def write_file(path: str, content: str) -> dict:
    """Create or update a UTF-8 text file inside the workspace."""

    try:
        target = safe_path(path)

        if not target.parent.exists():
            return {
                "success": False,
                "error": "Parent directory does not exist. Create it first."
            }

        if target.exists() and target.is_dir():
            return {
                "success": False,
                "error": "The target path is a directory, not a file."
            }

        target.write_text(content, encoding="utf-8")

        return {
            "success": True,
            "path": str(target.relative_to(WORKSPACE)),
            "characters_written": len(content)
        }
    except (ValueError, OSError) as error:
        return {"success": False, "error": str(error)}


def read_file(path: str) -> dict:
    """Read a UTF-8 text file inside the workspace."""

    try:
        target = safe_path(path)

        if not target.is_file():
            return {"success": False, "error": "File not found."}

        return {
            "success": True,
            "path": str(target.relative_to(WORKSPACE)),
            "content": target.read_text(encoding="utf-8")
        }
    except (ValueError, OSError) as error:
        return {"success": False, "error": str(error)}


def list_files(path: str = ".") -> dict:
    """List files and directories inside the workspace."""

    try:
        target = safe_path(path)

        if not target.is_dir():
            return {"success": False, "error": "Directory not found."}

        entries = []

        for item in sorted(target.iterdir()):
            entries.append({
                "name": item.name,
                "type": "directory" if item.is_dir() else "file"
            })

        return {
            "success": True,
            "path": str(target.relative_to(WORKSPACE)),
            "entries": entries
        }
    except (ValueError, OSError) as error:
        return {"success": False, "error": str(error)}


