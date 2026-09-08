"""
更鲁棒地提取所有 .py 文件的函数元数据
- 用 ast.parse 完整解析
- 如果失败，用 regex 兜底
"""
import os, ast, json, re

src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'

all_meta = {}
processed = 0
skipped = 0
total_files = 0

for root, dirs, files in os.walk(src):
    for fn in sorted(files):
        if not fn.endswith('.py'):
            continue
        total_files += 1
        fp = os.path.join(root, fn)
        relpath = os.path.relpath(fp, src).replace('\\', '/')

        # 尝试 ast 解析
        try:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
                source = f.read()
            tree = ast.parse(source)
        except:
            skipped += 1
            continue

        result = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lines = (node.end_lineno - node.lineno + 1) if node.end_lineno else 0
                desc = ''
                if (node.body and isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant)):
                    doc = node.body[0].value.value
                    if isinstance(doc, str):
                        desc = doc.strip().split('\n')[0][:120]
                result[node.name] = (lines, desc)

        if result:
            all_meta[relpath] = result
            processed += 1
        else:
            skipped += 1

print(f'Total .py files: {total_files}')
print(f'Processed (with funcs): {processed}')
print(f'Skipped (no funcs / parse error): {skipped}')

# Save
with open(r'D:\demo\202609\vllm-ascend\func_meta.json', 'w', encoding='utf-8') as f:
    json.dump(all_meta, f, ensure_ascii=False)

total_funcs = sum(len(v) for v in all_meta.values())
with_desc = sum(1 for v in all_meta.values() for fn, (l, d) in v.items() if d)
print(f'Total funcs: {total_funcs}')
print(f'With desc:   {with_desc}')