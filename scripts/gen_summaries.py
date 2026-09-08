import os, ast, json

SRC = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'
OUT_DIR = r'D:\demo\202609\vllm-ascend\scripts\data\file_summaries'
os.makedirs(OUT_DIR, exist_ok=True)

# panorama 页面 -> 文件列表映射
import re
PANO = r'D:\demo\202609\vllm-ascend\code-docs\panorama'
page_files = {}
for fn in sorted(os.listdir(PANO)):
    if not fn.endswith('.html') or fn == 'panorama.html':
        continue
    c = open(os.path.join(PANO, fn), encoding='utf-8').read()
    files = re.findall(r'<div class="file-name">([^<]+)</div>', c)
    page_files[fn] = [f for f in files if os.path.exists(os.path.join(SRC, f.replace('\\', os.sep)))]

def first_line(doc):
    if not doc:
        return ''
    return doc.strip().splitlines()[0].strip()

def summarize(rel_file):
    path = os.path.join(SRC, rel_file.replace('\\', os.sep))
    try:
        tree = ast.parse(open(path, encoding='utf-8', errors='ignore').read())
    except SyntaxError as e:
        return f'!! PARSE ERROR: {e}'
    lines = []
    mod_doc = first_line(ast.get_docstring(tree))
    n_lines = len(open(path, encoding='utf-8', errors='ignore').read().splitlines())
    lines.append(f'[{n_lines}行] module doc: {mod_doc}' if mod_doc else f'[{n_lines}行]')
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            doc = first_line(ast.get_docstring(node))
            methods = []
            for m in node.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    methods.append(m.name)
            lines.append(f'class {node.name}: {doc} | methods: {", ".join(methods[:15])}{" ..." if len(methods) > 15 else ""}')
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = first_line(ast.get_docstring(node))
            sig = []
            for a in node.args.args[:6]:
                sig.append(a.arg)
            lines.append(f'def {node.name}({", ".join(sig)}): {doc}')
    return '\n'.join(lines[:40])

total = 0
for page, files in page_files.items():
    out_path = os.path.join(OUT_DIR, page.replace('.html', '') + '_summary.txt')
    with open(out_path, 'w', encoding='utf-8') as f:
        for rel in files:
            f.write(f'===== FILE: {rel} =====\n')
            f.write(summarize(rel))
            f.write('\n\n')
            total += 1
    print(f'{out_path}: {os.path.getsize(out_path)/1024:.0f} KB, {len(files)} files')

print(f'\nTotal files summarized: {total}')
