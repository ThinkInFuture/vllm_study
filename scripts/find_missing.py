"""
检查 META 中漏掉了哪些源码文件
"""
import os, json

src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'

# 所有源码文件
all_py_files = set()
for root, dirs, files in os.walk(src):
    for fn in files:
        if fn.endswith('.py'):
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, src).replace('\\', '/')
            all_py_files.add(rel)

with open(r'D:\demo\202609\vllm-ascend\func_meta.json', 'r', encoding='utf-8') as f:
    M = json.load(f)

meta_files = set(M.keys())

missing = all_py_files - meta_files
extra = meta_files - all_py_files

print(f'Total .py files: {len(all_py_files)}')
print(f'In META:         {len(meta_files)}')
print(f'Missing from META: {len(missing)}')
print(f'\nFirst 20 missing:')
for f in sorted(missing)[:20]:
    print(f'  {f}')
print(f'\nFirst 20 extra (in META but not on disk):')
for f in sorted(extra)[:20]:
    print(f'  {f}')