import re
with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-models.html', 'r', encoding='utf-8') as f:
    c = f.read()
print('Total (功能说明):', c.count('(功能说明)'))
# Find first 5 file-blocks
for m in list(re.finditer(r'<div class="file-block">', c))[:3]:
    print('---')
    print(c[m.start():m.start()+400])