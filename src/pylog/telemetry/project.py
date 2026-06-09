from pathlib import Path
import tomllib


def get_project_name() -> str:
    current = Path.cwd().resolve()

    while current != current.parent:
        pyproject = current / "pyproject.toml"

        if pyproject.exists():
            try:
                with open(pyproject, "rb") as f:
                    data = tomllib.load(f)

                return data.get("project", {}).get("name", "unknown-service")

            except Exception:
                return "unknown-service"

        current = current.parent

    return "unknown-service"
