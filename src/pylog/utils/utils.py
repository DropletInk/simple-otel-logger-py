from pathlib import Path


def get_project_name():
    for path in [Path.cwd(), *Path.cwd().parents]:
        pyproject = path / "pyproject.toml"

        if pyproject.exists():
            in_project_section = False

            with open(pyproject, "r") as f:
                for line in f:
                    line = line.strip()

                    if line == "[project]":
                        in_project_section = True
                        continue

                    if line.startswith("[") and line.endswith("]"):
                        in_project_section = False

                    if in_project_section and line.startswith("name"):
                        return (
                            line.split("=", 1)[1].strip().strip('"').strip("'")
                        )

    return None
