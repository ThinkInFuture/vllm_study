import re
for p in ['panorama-attention.html', 'panorama-core.html', 'panorama-models.html', 'panorama-ops.html', 'panorama-root.html']:
    fp = r'D:/demo/202609/vllm-ascend/code-docs/' + p
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    matches = re.findall(r'item-name">([^<]+)</span><span class="item-desc">(\[\d+行\][^<]+)</span>', c)
    print(f'=== {p} ===')
    for fname, desc in matches[:5]:
        print(f'  {fname}: {desc[:120]}')
    print(f'  Total: {len(matches)} with [N行] prefix')
    print()