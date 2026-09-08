import re
with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'r', encoding='utf-8') as f:
    c = f.read()
print('Count (功能说明):', c.count('(功能说明)'))
# Find all item-name entries
names = re.findall(r'<span class="item-name">([^<]+)<span class="item-desc">\(功能说明\)', c)
print('Total matches:', len(names))
print('Sample first 20:', names[:20])