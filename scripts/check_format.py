import re
for p in ['panorama-attention.html', 'panorama-core.html', 'panorama-models.html', 'panorama-ops.html']:
    with open(r'D:/demo/202609/vllm-ascend/code-docs/' + p, 'r', encoding='utf-8') as f:
        c = f.read()
    n1 = len(re.findall(r'<span class="item-name">([^<]+)<span class="item-desc">\(功能说明\)', c))
    n2 = len(re.findall(r'<span class="item-name">([^<]+)</span><span class="item-desc">\(功能说明\)', c))
    n3 = c.count('(功能说明)')
    print(f'{p}: format1={n1}, format2={n2}, total={n3}')