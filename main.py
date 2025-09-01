import os
import re


def clean_code(source: str, no_triples=False, no_comments=False) -> str:
    """
    Remove triple-quoted strings and/or comments from source code,
    and clean up extra blank lines.
    """
    if no_triples:
        pattern_triple = r'(\'\'\'(.*?)\'\'\'|"""(.*?)""")'
        source = re.sub(pattern_triple, '', source, flags=re.DOTALL)

    if no_comments:
        # Remove single-line comments
        source = re.sub(r'#.*', '', source)

    # Remove leading/trailing whitespace on each line
    lines = [line.rstrip() for line in source.splitlines()]
    # Remove consecutive blank lines
    cleaned_lines = []
    previous_blank = False
    for line in lines:
        if line.strip() == '':
            if not previous_blank:
                cleaned_lines.append('')
            previous_blank = True
        else:
            cleaned_lines.append(line)
            previous_blank = False
    return '\n'.join(cleaned_lines)


def print_package_source(package_path, no_triples=False, no_comments=False):
    for root, dirs, files in os.walk(package_path):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        code = f.read()
                    code_cleaned = clean_code(code, no_triples=no_triples, no_comments=no_comments)
                    rel_path = os.path.relpath(filepath, package_path)
                    print(f"[{rel_path}]\n{code_cleaned}\n")
                except Exception as e:
                    print(f"[{filepath}]\n# Error reading file: {e}\n")


# Example usage
print_package_source("src/plugorm", no_triples=True, no_comments=True)