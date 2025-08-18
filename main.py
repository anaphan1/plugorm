import os


def print_package_source(package_path):
    for root, dirs, files in os.walk(package_path):
        # Skip __pycache__ folders
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        code = f.read()
                    # Format relative filename from package root
                    rel_path = os.path.relpath(filepath, package_path)
                    print(f"[{rel_path}]\n{code}\n")
                except Exception as e:
                    print(f"[{filepath}]\n# Error reading file: {e}\n")


print_package_source("src/coatlorm")