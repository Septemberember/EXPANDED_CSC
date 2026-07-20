"""
Java code compilation and execution utilities.

Handles writing Java source to disk, compiling with javac, executing with java,
and parsing variable type declarations from Java source code.
"""

import re
import os
import subprocess

RUNNABLE_DIR = "dataset/runnable"


def get_class_name(java_code: str) -> str:
    """Extract the class name from Java source code."""
    match = re.search(r'class\s+(\w+)', java_code)
    if match:
        return match.group(1)
    return None


def run_java_code(java_code: str, timeout_seconds=20):
    """Compile and execute a Java program, returning the subprocess result.

    Writes the code to dataset/runnable/<ClassName>.java, compiles it,
    then runs it and returns the CompletedProcess with captured stdout/stderr.
    """
    os.makedirs(RUNNABLE_DIR, exist_ok=True)
    classname = get_class_name(java_code)
    if classname is None:
        print("Error: Could not determine class name from Java source.")
        return ""
    file_path = os.path.join(RUNNABLE_DIR, classname + ".java")
    with open(file_path, "w") as file:
        file.write(java_code)
    try:
        subprocess.run(["javac", file_path], check=True)
    except subprocess.CalledProcessError:
        print("Error during Java compilation.")
        return ""
    try:
        result = subprocess.run(
            ["java", "-cp", RUNNABLE_DIR, classname],
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        return result
    except subprocess.TimeoutExpired:
        print("Java execution timeout!")
        raise
    except subprocess.CalledProcessError:
        print("Error during Java execution.")
        raise


def parse_top_level_md_def(java_code: str) -> dict:
    """Parse the top-level method's variable types from Java code.

    Returns a dict mapping variable names to their Java types,
    including 'return_value' for the return type.
    """
    lines = java_code.splitlines()
    var_types = {}

    main_method_content = []
    in_main_method = False
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("public static void main"):
            in_main_method = True
        elif in_main_method and line_stripped.startswith("}"):
            in_main_method = False
        elif in_main_method:
            main_method_content.append(line_stripped)

    called_method_name = None
    for line in main_method_content:
        method_call_match = re.search(r'(\w+(?:\.\w+)*)\s*\(', line)
        if method_call_match:
            full_match = method_call_match.group(1)
            parts = full_match.split('.')
            called_method_name = parts[-1]
            if called_method_name not in ["main", "System", "out", "println", "print", "printf", "scanf", "format", "readLine"]:
                break

    if called_method_name:
        for line in lines:
            line_stripped = line.strip()
            if (line_stripped.startswith("public") or line_stripped.startswith("private")
                or line_stripped.startswith("protected")) and \
               called_method_name in line_stripped and "(" in line_stripped and ")" in line_stripped:
                method_pattern = rf'\b{called_method_name}\s*\('
                if re.search(method_pattern, line_stripped):
                    parts = line_stripped.split()
                    return_type = None
                    for i, part in enumerate(parts):
                        if called_method_name in part and '(' in part:
                            if i > 0:
                                return_type = parts[i - 1]
                            break
                    if return_type:
                        params_start = line_stripped.find('(') + 1
                        params_end = line_stripped.find(')', params_start)
                        if params_end != -1:
                            params_def = line_stripped[params_start:params_end]
                            var_types["return_value"] = return_type
                            if params_def.strip():
                                params = params_def.split(",")
                                for param in params:
                                    param = param.strip()
                                    if param:
                                        param_parts = param.split()
                                        if len(param_parts) >= 2:
                                            var_types[param_parts[1]] = param_parts[0]
                            return var_types

    # Fallback: first non-main static method
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("public static") and "main" not in line_stripped:
            parts = line_stripped.split()
            if len(parts) >= 3:
                return_type = parts[2]
                params_def = line_stripped.split("(")[1].split(")")[0]
                var_types["return_value"] = return_type
                if params_def.strip():
                    params = params_def.split(",")
                    for param in params:
                        param = param.strip()
                        if param:
                            param_parts = param.split()
                            if len(param_parts) >= 2:
                                var_types[param_parts[1]] = param_parts[0]
            return var_types

    return var_types


def parse_class_name(java_code: str) -> str:
    """Extract class name with access modifiers."""
    m = re.search(r'^\s*(?:public|protected|private)?\s*(?:static\s+)?(?:final\s+)?'
                  r'class\s+([A-Za-z_][A-Za-z0-9_]*)', java_code, re.MULTILINE)
    return m.group(1) if m else "classNameUnknown"
