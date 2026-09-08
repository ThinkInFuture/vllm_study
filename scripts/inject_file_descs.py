import os, re, json

DOCS = r'D:\demo\202609\vllm-ascend\code-docs'
PANO = os.path.join(DOCS, 'panorama')
SRC_REL = '../../vllm-ascend-main/vllm_ascend/'

with open(r'D:\demo\202609\vllm-ascend\scripts\data\file_descs.json', encoding='utf-8') as f:
    DESCS = json.load(f)

CSS_ADD = '''
.file-desc-real{color:#444;font-size:0.88rem;margin-bottom:8px;line-height:1.7;background:#f8f9fc;border-radius:8px;padding:10px 12px;}
.src-link{font-size:0.75rem;color:#fff;background:#667eea;border-radius:4px;padding:1px 8px;margin-left:8px;text-decoration:none;font-weight:normal;vertical-align:middle;}
.src-link:hover{background:#5568d8;}
.file-classes{color:#999;font-size:0.78rem;margin-bottom:10px;line-height:1.5;}
'''

def inject_page(path, src_prefix):
    c = open(path, encoding='utf-8').read()
    # 1. CSS 注入（幂等）
    if '.file-desc-real' not in c:
        c = c.replace('</style>', CSS_ADD + '</style>', 1)

    # 2. 清理假描述：[N行] 见源码:xxx -> [N行]
    c = re.sub(r'(\[\d+行\]) 见源码:[^<]*', r'\1', c)
    # 清理空 item-desc
    c = re.sub(r'<span class="item-desc">\s*</span>', '', c)

    # 3. 每个 file-block：文件名加源码链接 + 注入真实讲解
    blocks = re.split(r'(<div class="file-name">[^<]*</div>)', c)
    out = [blocks[0]]
    injected = 0
    linked = 0
    for seg in blocks[1:]:
        m = re.match(r'<div class="file-name">([^<]*)</div>', seg)
        if not m:
            out.append(seg)
            continue
        rel = m.group(1).strip()
        exists = os.path.exists(os.path.join(
            r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend',
            rel.replace('\\', os.sep)))
        # 文件名加源码链接（幂等：已含 src-link 则跳过）
        if 'src-link' not in seg and exists:
            seg = (f'<div class="file-name">{rel}'
                   f'<a class="src-link" href="{src_prefix}{rel.replace(chr(92), "/")}" target="_blank">查看源码</a></div>')
            linked += 1
        out.append(seg)
    c = ''.join(out)

    # 4. 在 file-name 后插入 file-desc-real（幂等：仅当该 file-block 尚无）
    def repl_fileblock(match):
        nonlocal injected
        head = match.group(0)
        rel = match.group(1).strip()
        desc = DESCS.get(rel)
        if not desc:
            return head
        return head + f'<div class="file-desc-real">{desc}</div>'
    # 先移除已有 file-desc-real，再重新注入，保证更新
    c = re.sub(r'<div class="file-desc-real">.*?</div>', '', c, flags=re.S)
    def inject_after_name(m):
        nonlocal injected
        inner = m.group(1)
        rel = inner.split('<')[0].strip()
        desc = DESCS.get(rel) or DESCS.get(rel.replace('/', '\\')) or DESCS.get(rel.replace('\\', '/'))
        head = m.group(0)
        if not desc:
            return head
        injected += 1
        return head + f'<div class="file-desc-real">{desc}</div>'
    c = re.sub(r'<div class="file-name">(.*?)</div>', inject_after_name, c, flags=re.S)

    # 5. 原有「类: xxx」file-desc 降级为 file-classes 样式
    c = re.sub(r'<div class="file-desc">(类: [^<]*)</div>', r'<div class="file-classes">\1</div>', c)

    open(path, 'w', encoding='utf-8').write(c)
    return injected, linked

for fn in sorted(os.listdir(PANO)):
    if not fn.endswith('.html') or fn == 'panorama.html':
        continue
    inj, lnk = inject_page(os.path.join(PANO, fn), SRC_REL)
    print(f'{fn}: injected {inj} descs, linked {lnk} files')

# panorama.html 索引页：加回首页导航
idx = os.path.join(PANO, 'panorama.html')
c = open(idx, encoding='utf-8').read()
if '../index.html' not in c:
    c = c.replace('<h1>vLLM Ascend 全景图 - 源码结构索引</h1>',
                  '<p><a href="../index.html" style="color:#667eea;text-decoration:none;">← 返回架构总览首页</a></p>\n<h1>vLLM Ascend 全景图 - 源码结构索引</h1>')
    open(idx, 'w', encoding='utf-8').write(c)
    print('panorama.html: added index nav')
