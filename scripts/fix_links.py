import os, re

docs = r'D:\demo\202609\vllm-ascend\code-docs'

# 1. detailed/*.html: index.html -> ../index.html, panorama.html -> ../panorama/panorama.html
det = os.path.join(docs, 'detailed')
for fn in os.listdir(det):
    if not fn.endswith('.html'):
        continue
    fp = os.path.join(det, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    orig = c
    c = re.sub(r'href="index\.html(["#])', r'href="../index.html\1', c)
    c = re.sub(r'href="panorama\.html(["#])', r'href="../panorama/panorama.html\1', c)
    # detailed 同级页面在 detailed/ 下，链接保持不变（正确）
    if c != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'fixed: detailed/{fn}')

# 2. panorama/*.html: index.html -> ../index.html, panorama-index.html -> panorama.html
pan = os.path.join(docs, 'panorama')
for fn in os.listdir(pan):
    if not fn.endswith('.html'):
        continue
    fp = os.path.join(pan, fn)
    with open(fp, 'r', encoding='utf-8') as f:
        c = f.read()
    orig = c
    c = re.sub(r'href="index\.html(["#])', r'href="../index.html\1', c)
    c = re.sub(r'href="panorama-index\.html(["#])', r'href="panorama.html\1', c)
    if c != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'fixed: panorama/{fn}')

print('\ndone')
