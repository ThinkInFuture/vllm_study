import re
with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'r', encoding='utf-8') as f:
    c = f.read()
print('Total placeholder (功能说明):', c.count('(功能说明)'))
print('Total placeholder (源码见对应位置:):', c.count('(源码见对应位置:'))
print('Total file size:', len(c), 'chars')
# Count real descriptions
descs = re.findall(r'item-desc">([^<]+)</span>', c)
print('Total desc items:', len(descs))
# Count those that are NOT placeholder
real = [d for d in descs if d and not d.startswith('(')]
placeholder = [d for d in descs if d.startswith('(')]
print('Real descriptions:', len(real))
print('Still placeholders:', len(placeholder))
print('Sample real descriptions:')
for d in real[:5]:
    print(' -', d[:80])
print('Sample placeholders:')
for d in placeholder[:5]:
    print(' -', d[:80])