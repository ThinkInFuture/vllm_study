import re
with open(r'D:\demo\202609\vllm-ascend\replace_extra_root_v5.py', 'r', encoding='utf-8') as f:
    c = f.read()
# Find dict keys
keys = re.findall(r"'(attention[^']+|compilation[^']+|core[^']+)':\s*\{", c)
seen = set()
dupes = []
for k in keys:
    if k in seen:
        dupes.append(k)
    seen.add(k)
print('All keys:', len(keys))
print('Duplicates:', dupes)