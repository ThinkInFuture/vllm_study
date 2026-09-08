import re
with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'r', encoding='utf-8') as f:
    c = f.read()
matches = re.findall(r'<span class="item-name">([^<]+)</span><span class="item-desc">([^\[<][^<]+)</span>', c)
print('No line count:')
for n, d in matches:
    print(f'  {n}: {d[:80]}')