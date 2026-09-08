import ast
import os
import sys

BASE_DIR = r"D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend"
PREFIX = "vllm_ascend/"

def get_first_comment_or_docstring(node):
    """Get the first comment or docstring for a class or function node."""
    # Check for docstring first
    if (node.body and isinstance(node.body[0], ast.Expr) 
        and isinstance(node.body[0].value, ast.Constant)):
        val = node.body[0].value
        s = val.value
        if isinstance(s, str):
            first_line = s.strip().split('\n')[0].strip()
            return first_line
    
    return ""

def get_function_signature(node):
    """Build function signature string."""
    args = node.args
    params = []
    
    # positional args
    defaults_offset = len(args.args) - len(args.defaults)
    for i, arg in enumerate(args.args):
        if arg.arg == 'self' or arg.arg == 'cls':
            params.append(arg.arg)
            continue
        param = arg.arg
        di = i - defaults_offset
        if di >= 0 and di < len(args.defaults):
            param += "=..."
        params.append(param)
    
    # *args
    if args.vararg:
        params.append("*" + args.vararg.arg)
    
    # keyword-only args
    defaults_kw_offset = len(args.kwonlyargs) - len(args.kw_defaults)
    for i, arg in enumerate(args.kwonlyargs):
        param = arg.arg
        di = i - defaults_kw_offset
        if di >= 0 and args.kw_defaults[di] is not None:
            param += "=..."
        params.append(param)
    
    # **kwargs
    if args.kwarg:
        params.append("**" + args.kwarg.arg)
    
    return "(" + ", ".join(params) + ")"

def extract_from_file(filepath):
    """Extract classes and functions from a Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        return [], []
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return [], []
    
    classes = []
    functions = []
    
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            doc = get_first_comment_or_docstring(node)
            classes.append((node.name, doc, node.lineno))
            
            # Extract methods within the class
            for item in ast.iter_child_nodes(node):
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    sig = get_function_signature(item)
                    mdoc = get_first_comment_or_docstring(item)
                    prefix = "@classmethod " if any(
                        isinstance(d, ast.Name) and d.id == 'classmethod' 
                        for d in item.decorator_list
                    ) else "@staticmethod " if any(
                        isinstance(d, ast.Name) and d.id == 'staticmethod' 
                        for d in item.decorator_list
                    ) else ""
                    methods_sig = f"{item.name}{sig}"
                    if not mdoc:
                        # Try to find inline comment
                        pass
                    functions.append((methods_sig, mdoc, item.lineno, True))
        
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sig = get_function_signature(node)
            doc = get_first_comment_or_docstring(node)
            functions.append((sig, doc, node.lineno, False))
    
    return classes, functions

def main():
    results = {}
    
    for root, dirs, files in os.walk(BASE_DIR):
        py_files = sorted([f for f in files if f.endswith('.py')])
        for f in py_files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, os.path.dirname(BASE_DIR))
            rel_path = rel_path.replace('\\', '/')
            
            classes, functions = extract_from_file(full_path)
            if classes or functions:
                results[rel_path] = (classes, functions)
    
    # Group by module directory
    groups = {}
    for path, (classes, functions) in sorted(results.items()):
        # Remove prefix
        short = path
        if short.startswith(PREFIX):
            short = short[len(PREFIX):]
        
        parts = short.split('/')
        if len(parts) == 1:
            group = "root/"
        else:
            group = parts[0] + "/"
        
        if group not in groups:
            groups[group] = []
        groups[group].append((short, classes, functions))
    
    # Output grouped
    group_order = [
        "root/", "core/", "models/", "attention/", "ops/", "worker/",
        "distributed/", "quantization/", "compilation/", "sample/",
        "lora/", "spec_decode/", "patch/", "device/", "model_loader/",
        "model_executor/", "device_allocator/", "observability/",
        "profiler/", "eplb/", "xlite/", "ec_manager/", "_310p/"
    ]
    
    for grp in group_order:
        if grp not in groups:
            continue
        print(f"\n{'='*80}")
        print(f"## {grp}")
        print(f"{'='*80}")
        
        for short_path, classes, functions in groups[grp]:
            print(f"\n=== FILE: {short_path} ===")
            
            for cls_name, cls_doc, line in classes:
                desc = cls_doc if cls_doc else "(no docstring)"
                print(f"CLASS: {cls_name} - {desc}")
            
            for func_sig, func_doc, line, is_method in functions:
                desc = func_doc if func_doc else "(no docstring)"
                if is_method:
                    print(f"METH: {func_sig} - {desc}")
                else:
                    print(f"FUNC: {func_sig} - {desc}")
    
    # Output any groups not in order
    for grp in sorted(groups.keys()):
        if grp not in group_order:
            print(f"\n{'='*80}")
            print(f"## {grp}")
            print(f"{'='*80}")
            for short_path, classes, functions in groups[grp]:
                print(f"\n=== FILE: {short_path} ===")
                for cls_name, cls_doc, line in classes:
                    desc = cls_doc if cls_doc else "(no docstring)"
                    print(f"CLASS: {cls_name} - {desc}")
                for func_sig, func_doc, line, is_method in functions:
                    desc = func_doc if func_doc else "(no docstring)"
                    if is_method:
                        print(f"METH: {func_sig} - {desc}")
                    else:
                        print(f"FUNC: {func_sig} - {desc}")

if __name__ == "__main__":
    main()
