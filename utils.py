import os
import jedi





def list_files_and_folders(start_dir="./", prefix=""):
    al = []
    for item in os.listdir(start_dir):
        item_path = os.path.join(start_dir, item)
        if os.path.isdir(item_path):
            al.append("{prefix}{item}/")
            list_files_and_folders(item_path, prefix + item + "/")
        else:
            al.append(f"{prefix}{item}")
    return al


def prefixer(prefixes):
    lst = list_files_and_folders()
    new = []
    for i in prefixes:
        for j in lst:
            new.append(f"{i} {j}")
    return new
import re

def get_required_indentation(code_text: str, line_number: int) -> str:
    """
    Returns the required indentation for the new line based on the previous line's indentation.
    
    :param code_text: The entire code text.
    :param line_number: The current line number (before adding the new line).
    :return: The required indentation as a string of spaces.
    """
    # Split the code into lines
    lines = code_text.split("\n")
    
    # Ensure we're not at the first line (no previous line)
    if line_number == 0:
        return ""
    
    # Get the previous line's indentation
    prev_line = lines[line_number - 1]
    
    # Check how much indentation is in the previous line
    indent_type = get_indent_type(prev_line)
    
    # Check if the previous line opens a block (increase indentation)
    if is_block_opener(prev_line):
        return indent_type + "    "  # Add one level of indentation (4 spaces)
    
    # Check if the previous line closes a block (decrease indentation)
    if is_block_closer(prev_line):
        return indent_type[:-4]  # Remove one level of indentation (4 spaces)
    
    # If it's neither, just match the previous indentation level
    return indent_type

def get_indent_type(line: str) -> str:
    """ Returns the indent type (spaces or tabs). """
    match = re.match(r"^[ \t]*", line)
    return match.group(0) if match else ""

def is_block_opener(line: str) -> bool:
    """ Determines if the line opens a block. """
    return line.strip().endswith(":") or line.strip().endswith("{")

def is_block_closer(line: str) -> bool:
    """ Determines if the line closes a block. """
    return line.strip() == "}" or line.strip().endswith("end")

def remove_one_indent(line: str) -> str:
    leading_spaces = count_leading_spaces(line)
    indent_to_remove = 4
    if leading_spaces < indent_to_remove:
        indent_to_remove = leading_spaces
    return line[indent_to_remove:] if leading_spaces >= indent_to_remove else line

def count_leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(' '))

def get_comp(code, line):
    script = jedi.Script(code)
    completions = script.complete(line)
    return [completion.name for completion in completions]

