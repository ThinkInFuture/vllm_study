import re
with open(r'D:\demo\202609\vllm-ascend\replace_extra_root_v5.py', 'r', encoding='utf-8') as f:
    c = f.read()
keys = re.findall(r"^\s*'(attention[^']+|compilation[^']+|core[^']+|context_parallel[^']+)':\s*\{", c, re.MULTILINE)
print('Keys in order:')
for k in keys:
    print('  ', k)