"""
扫描源码目录，统计每个模块的文件数和函数数，确定缺失页面覆盖范围
"""
import os, json

src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'

with open(r'D:\demo\202609\vllm-ascend\func_meta.json', 'r', encoding='utf-8') as f:
    META = json.load(f)

# 统计根目录（不含子目录）的文件数
root_files = [fp for fp in META if '/' not in fp]
print(f'Root-level files (in panorama-root.html): {len(root_files)}')
for fp in sorted(root_files):
    print(f'  {fp}: {len(META[fp])} funcs')

# 按一级目录分组
modules = {}
for fp in META:
    parts = fp.split('/')
    if len(parts) == 1:
        module = '_root'
    else:
        module = parts[0]
    if module not in modules:
        modules[module] = []
    modules[module].append(fp)

print(f'\n{"="*60}')
print('ALL MODULES (by directory):')
print(f'{"="*60}')

# 模块映射：哪些模块对应哪个 panorama 页面
mapping = {
    '_root': 'panorama-root.html',
    'attention': 'panorama-attention.html',
    'compilation': 'panorama-root.html',
    'core': 'panorama-core.html',
    'models': 'panorama-models.html',
    'ops': 'panorama-ops.html',
    # 缺失的三个页面
    'worker': 'panorama-worker.html',
    'distributed': 'panorama-distributed.html',
    'model_loader': 'panorama-rest.html',
    'quantization': 'panorama-rest.html',
    'experiment': 'panorama-rest.html',
    'test': 'panorama-rest.html',
    '_310p': 'panorama-rest.html',
}

for mod in sorted(modules.keys()):
    files = modules[mod]
    total_funcs = sum(len(META[fp]) for fp in files)
    page = mapping.get(mod, 'panorama-rest.html')
    print(f'{mod:20s}: {len(files):3d} files, {total_funcs:4d} funcs -> {page}')
    for fp in sorted(files)[:5]:
        print(f'  {fp}')
    if len(files) > 5:
        print(f'  ... and {len(files)-5} more')
