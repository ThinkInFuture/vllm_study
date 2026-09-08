import os, re

docs = r'D:\demo\202609\vllm-ascend\code-docs'
missing = []
checked = 0
for dirpath, _, files in os.walk(docs):
    if os.sep + 'src' in dirpath:
        continue
    for fn in files:
        if not fn.endswith('.html'):
            continue
        c = open(os.path.join(dirpath, fn), encoding='utf-8').read()
        for m in re.finditer(r'src-viewer\.html\?file=([^"&\']+)', c):
            rel = m.group(1)
            checked += 1
            # 数据文件统一在 code-docs/src/ 下
            data = os.path.join(docs, 'src', rel.replace('/', os.sep) + '.js')
            if not os.path.exists(data):
                missing.append((os.path.relpath(os.path.join(dirpath, fn), docs), rel))

print(f'viewer links checked: {checked}')
print(f'missing data files: {len(missing)}')
for s, r in missing[:10]:
    print(' ', s, '->', r)
