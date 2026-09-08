import re
for p in ['panorama-attention.html', 'panorama-core.html', 'panorama-models.html', 'panorama-ops.html', 'panorama-root.html']:
    fp = r'D:/demo/202609/vllm-ascend/code-docs/' + p
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    descs = re.findall(r'item-desc">([^<]+)</span>', c)
    real = [d for d in descs if d and not d.startswith('(')]
    placeholder = [d for d in descs if d.startswith('(')]
    print(f'{p}: real={len(real)}, placeholder={len(placeholder)}')