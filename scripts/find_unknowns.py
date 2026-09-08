import re
with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'r', encoding='utf-8') as f:
    c = f.read()
# Find each file-block and the unknown functions within
for m in re.finditer(r'<div class="file-block">\s*<div class="file-name">([^<]+)</div>(.*?)(?=<div class="file-block">|$)', c, re.DOTALL):
    file_name = m.group(1)
    content = m.group(2)
    unknowns = re.findall(r'\(源码见对应位置:(\w+)\)', content)
    if unknowns:
        print(f'{file_name} ({len(unknowns)} unknowns): {unknowns[:5]}')