import ast
import re
from flask import Blueprint, request, jsonify

debug_bp = Blueprint('debug_bp', __name__)

def check_brackets(code):
    stack = []
    brackets = {'(': ')', '[': ']', '{': '}'}
    errors = []
    lines = code.split('\n')
    
    for i, line in enumerate(lines):
        for j, char in enumerate(line):
            if char in brackets:
                stack.append((char, i + 1, j + 1))
            elif char in brackets.values():
                if not stack:
                    errors.append(f"Line {i+1}: Unmatched closing bracket '{char}'")
                else:
                    open_char, open_line, open_col = stack.pop()
                    if brackets[open_char] != char:
                        errors.append(f"Line {i+1}: Mismatched bracket '{char}', expected '{brackets[open_char]}'")
    
    for char, line, col in stack:
        errors.append(f"Line {line}: Unclosed bracket '{char}'")
        
    return errors

def check_python_syntax(code):
    errors = check_brackets(code)
    fixes = []
    lines = code.split('\n')
    suggestion_lines = list(lines)
    
    # Missing colons and Python 2 print
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^print\s+["\'].*["\']$', stripped):
            errors.append(f"Line {i+1}: Missing parentheses in call to 'print'")
            fixes.append(f"Add parentheses around print argument on line {i+1}")
            suggestion_lines[i] = re.sub(r'^(.*?)print\s+(["\'].*["\'])(.*)$', r'\1print(\2)\3', line)
        elif stripped.startswith(('if ', 'elif ', 'else', 'for ', 'while ', 'def ', 'class ', 'try', 'except ', 'except:', 'finally')):
            if not stripped.endswith(':'):
                errors.append(f"Line {i+1}: Missing colon at the end of statement")
                fixes.append(f"Add ':' at the end of line {i+1}")
                suggestion_lines[i] = line + ':'

    suggestion_code = '\n'.join(suggestion_lines)
    
    try:
        tree = ast.parse(suggestion_code)
        # very basic undefined variable check
        assigned = set(['print', 'len', 'range', 'int', 'str', 'float', 'list', 'dict', 'set', 'True', 'False', 'None'])
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assigned.add(target.id)
            elif isinstance(node, ast.FunctionDef):
                assigned.add(node.name)
                for arg in node.args.args:
                    assigned.add(arg.arg)
            elif isinstance(node, ast.ClassDef):
                assigned.add(node.name)
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    assigned.add(alias.asname or alias.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id not in assigned and not hasattr(__builtins__, node.id):
                    msg = f"Potential undefined variable '{node.id}'"
                    if msg not in errors:
                        errors.append(msg)
                        fixes.append(f"Define variable '{node.id}' before use")
    except SyntaxError as e:
        err_msg = f"Line {e.lineno}: {e.msg}"
        if err_msg not in errors:
            errors.append(err_msg)
            
    return errors, fixes, suggestion_code

def check_js_syntax(code):
    errors = check_brackets(code)
    fixes = []
    lines = code.split('\n')
    suggestion_lines = list(lines)
    
    for i, line in enumerate(lines):
        if line.count('"') % 2 != 0 and not line.endswith('\\"'):
             errors.append(f"Line {i+1}: Unclosed double quote")
             fixes.append(f"Close double quote on line {i+1}")
             suggestion_lines[i] = line + '"'
        if line.count("'") % 2 != 0 and not line.endswith("\\'"):
             errors.append(f"Line {i+1}: Unclosed single quote")
             fixes.append(f"Close single quote on line {i+1}")
             suggestion_lines[i] = line + "'"
             
    for i, line in enumerate(suggestion_lines):
        stripped = line.strip()
        if re.match(r'^console\.log\s+["\'].*["\']$', stripped):
            errors.append(f"Line {i+1}: Missing parentheses in call to 'console.log'")
            fixes.append(f"Add parentheses on line {i+1}")
            suggestion_lines[i] = re.sub(r'^(.*?)console\.log\s+(["\'].*["\'])(.*)$', r'\1console.log(\2)\3', line)
             
    return errors, fixes, '\n'.join(suggestion_lines)

@debug_bp.route('/api/debug', methods=['POST'])
def debug_code():
    data = request.get_json()
    if not data or 'code' not in data or 'language' not in data:
        return jsonify({"error": "Missing code or language in request"}), 400
        
    code = data['code']
    language = data['language'].lower()
    
    if language == 'python':
        errors, fixes, suggestion_code = check_python_syntax(code)
    elif language in ['javascript', 'js']:
        errors, fixes, suggestion_code = check_js_syntax(code)
    else:
        return jsonify({"error": "Unsupported language"}), 400
        
    valid = len(errors) == 0
    message = "Code looks good!" if valid else "Syntax errors found."
    
    return jsonify({
        "valid": valid,
        "errors": errors,
        "fixes": fixes,
        "suggestion_code": suggestion_code,
        "message": message
    })
