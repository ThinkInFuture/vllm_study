import os
d = r'D:\demo\202609\vllm-ascend\code-docs'
for f in sorted(os.listdir(d)):
    if f.startswith('panorama-') and f.endswith('.html'):
        fp = os.path.join(d, f)
        with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
            c = fh.read()
        n1 = c.count('(功能说明)')
        n2 = c.count('(源码见对应位置:')
        print(f'{f}: {len(c)/1024:.1f}KB, (功能说明)={n1}, (源码见对应位置:)={n2}')