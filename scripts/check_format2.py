import re
for p in ['panorama-attention.html', 'panorama-core.html', 'panorama-models.html', 'panorama-ops.html']:
    with open(r'D:/demo/202609/vllm-ascend/code-docs/' + p, 'r', encoding='utf-8') as f:
        c = f.read()
    n3 = c.count('(功能说明)')
    # Find first 100 chars around any (功能说明)
    idx = c.find('(功能说明)')
    if idx >= 0:
        print(f'{p}: count={n3}, first at {idx}: {c[max(0,idx-50):idx+50]}')
    else:
        print(f'{p}: no (功能说明)')