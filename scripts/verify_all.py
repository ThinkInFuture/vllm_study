import os, re

docs_dir = r'D:\demo\202609\vllm-ascend\code-docs'
files = [
    'panorama.html',
    'panorama-root.html',
    'panorama-attention.html',
    'panorama-core.html',
    'panorama-models.html',
    'panorama-ops.html',
    'panorama-worker.html',
    'panorama-distributed.html',
    'panorama-rest.html',
]

for f in files:
    fp = os.path.join(docs_dir, f)
    if not os.path.exists(fp):
        print(f'{f}: NOT FOUND')
        continue
    sz = os.path.getsize(fp)
    with open(fp, 'r', encoding='utf-8') as fh:
        c = fh.read()
    items = len(re.findall(r'item-name', c))
    with_lines = len(re.findall(r'item-desc">\[\d+行\]', c))
    print(f'{f}: {sz/1024:.1f}KB, funcs={items}, with_lines={with_lines}')
