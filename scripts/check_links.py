import os, re, urllib.parse

docs = r'D:\demo\202609\vllm-ascend\code-docs'
broken = []
total_links = 0

for dirpath, _, files in os.walk(docs):
    for fn in files:
        if not fn.endswith('.html'):
            continue
        fp = os.path.join(dirpath, fn)
        rel_dir = os.path.relpath(dirpath, docs)
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for m in re.finditer(r'(?:href|src)="([^"]+)"', content):
            url = m.group(1)
            total_links += 1
            if url.startswith(('http://', 'https://', '#', 'mailto:', 'data:')):
                continue
            # 去掉锚点与 query（如 src-viewer.html?file=xxx.py）
            path_part = url.split('#')[0].split('?')[0]
            if not path_part:
                continue
            target = os.path.normpath(os.path.join(dirpath, path_part))
            if not os.path.exists(target):
                broken.append((os.path.relpath(fp, docs), url))

print(f'Total links checked: {total_links}')
print(f'Broken links: {len(broken)}')
print()
seen = set()
for src, url in broken:
    key = (src.split(os.sep)[0] if os.sep in src else 'root', url)
    if key in seen:
        continue
    seen.add(key)
    print(f'  [{src}] -> {url}')
