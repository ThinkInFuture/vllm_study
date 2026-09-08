import re
with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-ops.html', 'r', encoding='utf-8') as f:
    c = f.read()
# 提取所有 item-name
names = re.findall(r'<span class="item-name">([^<]+)</span>', c)
print(f'Total item-name: {len(names)}')
print(f'Unique: {len(set(names))}')
# 找出重复
from collections import Counter
cnt = Counter(names)
duplicates = [(n, c) for n, c in cnt.items() if c > 1]
print(f'Duplicates: {len(duplicates)}')
for n, c in duplicates[:10]:
    print(f'  {n}: {c}次')