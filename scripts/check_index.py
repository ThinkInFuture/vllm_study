import re

with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 找所有 panorama-*.html 链接
links = re.findall(r'panorama-[a-z]+\.html', c)
for l in sorted(set(links)):
    print(l)
