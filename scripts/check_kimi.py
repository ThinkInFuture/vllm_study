import re
with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-models.html', 'r', encoding='utf-8') as f:
    c = f.read()
# Find the file-block for kimi_k3
m = re.search(r'<div class="file-name">models\\kimi_k3\.py</div>(.*?)(?=<div class="file-block">|$)', c, re.DOTALL)
if m:
    # Get the unknown funcs in this block
    funcs = re.findall(r'item-name">([^<]+)</span><span class="item-desc">\(参见源码:([^)]+)\)', m.group(1))
    print('kimi_k3.py unknowns:')
    for fname, fdesc in funcs[:20]:
        print(f'  {fname}')
else:
    # try forward slash
    m = re.search(r'<div class="file-name">models/kimi_k3\.py</div>(.*?)(?=<div class="file-block">|$)', c, re.DOTALL)
    if m:
        funcs = re.findall(r'item-name">([^<]+)</span><span class="item-desc">\(参见源码:([^)]+)\)', m.group(1))
        print('kimi_k3.py (fwd slash) unknowns:')
        for fname, fdesc in funcs[:20]:
            print(f'  {fname}')
    else:
        print('not found')