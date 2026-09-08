import os, re

pano = r'D:\demo\202609\vllm-ascend\code-docs\panorama'
print('=== 各 panorama 页面描述质量统计（修正版）===')
total_fake = 0
total_all = 0
for fn in sorted(os.listdir(pano)):
    if not fn.endswith('.html'):
        continue
    with open(os.path.join(pano, fn), 'r', encoding='utf-8') as f:
        c = f.read()
    descs = re.findall(r'<span class="item-desc">([^<]*)</span>', c)
    fake = sum(1 for d in descs if '见源码' in d)
    total_all += len(descs)
    total_fake += fake
    print(f'  {fn:40s} 总:{len(descs):5d}  假(见源码):{fake:5d}  ({fake*100//max(len(descs),1)}%)')
print(f'\n  TOTAL: {total_all} 条描述, 其中 {total_fake} 条是假的 "见源码:函数名"')
