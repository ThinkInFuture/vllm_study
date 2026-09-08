"""
为 worker/distributed/rest 生成 panorama HTML 页面
使用 AST 解析提取函数名、docstring 描述、代码行数
"""
import os, re, json, ast

src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'

with open(r'D:\demo\202609\vllm-ascend\func_meta.json', 'r', encoding='utf-8') as f:
    META = json.load(f)

# 页面定义：(输出文件, 包含的模块前缀列表)
PAGES = [
    ('panorama-worker.html', ['worker']),
    ('panorama-distributed.html', ['distributed']),
    ('panorama-rest.html', [
        '_310p', 'device', 'device_allocator', 'ec_manager', 'eplb',
        'lora', 'model_executor', 'model_loader', 'observability',
        'patch', 'profiler', 'quantization', 'sample', 'spec_decode', 'xlite'
    ]),
]

NAV_LINKS = [
    ('panorama.html', '总览'),
    ('panorama-root.html', '根模块'),
    ('panorama-attention.html', '注意力'),
    ('panorama-core.html', '核心'),
    ('panorama-models.html', '模型'),
    ('panorama-ops.html', '算子'),
    ('panorama-worker.html', 'Worker'),
    ('panorama-distributed.html', '分布式'),
    ('panorama-rest.html', '其他模块'),
]


def make_nav_html(current_file):
    parts = []
    for href, label in NAV_LINKS:
        cls = 'nav-link active' if href == current_file else 'nav-link'
        parts.append(f'<a class="{cls}" href="{href}">{label}</a>')
    return '\n'.join(parts)


def get_module_files(prefix):
    files = {}
    for fp in sorted(META.keys()):
        # 判断是否属于该模块
        if '/' in fp:
            mod = fp.split('/')[0]
        else:
            mod = '_root'
        if prefix == '_root' and '/' not in fp:
            files[fp] = META[fp]
        elif mod == prefix:
            files[fp] = META[fp]
    return files


def format_desc(func_name, lines, raw_desc):
    if raw_desc and not raw_desc.startswith('('):
        short = raw_desc[:150]
        return f'[{lines}行] {short}'
    return f'[{lines}行] 代码量 {lines} 行'


def generate_html(page_file, prefix_list):
    nav = make_nav_html(page_file)

    # 收集该页面的所有文件
    all_files = {}
    for p in prefix_list:
        all_files.update(get_module_files(p))

    total_funcs = sum(len(v) for v in all_files.values())
    total_files = len(all_files)

    # 构建 HTML
    blocks = []
    for fp in sorted(all_files.keys()):
        funcs = all_files[fp]
        items = []
        for fname, (lines, desc) in funcs.items():
            desc_str = format_desc(fname, lines, desc)
            items.append(
                f'<div class="item">'
                f'<span class="item-name">{fname}</span>'
                f'<span class="item-desc">{desc_str}</span>'
                f'</div>'
            )

        display_name = os.path.basename(fp) if '/' not in fp else fp
        file_link = f'{src}\\{fp}'.replace('/', '\\')

        block = (
            f'<div class="file-block">'
            f'<div class="file-name">{fp}</div>'
            f'<div class="file-path">{file_link}</div>'
            f'{"".join(items)}'
            f'</div>'
        )
        blocks.append(block)

    title = page_file.replace('panorama-', '').replace('.html', '').title()
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>vLLM Ascend API - {title} 模块</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; background: #f8f9fa; color: #333; }}
.navbar {{ background: #1a1a2e; padding: 12px 24px; display: flex; gap: 16px; flex-wrap: wrap; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }}
.nav-link {{ color: #e0e0e0; text-decoration: none; font-size: 14px; padding: 4px 10px; border-radius: 4px; }}
.nav-link:hover {{ background: rgba(255,255,255,0.1); }}
.nav-link.active {{ color: #fff; background: rgba(255,255,255,0.15); font-weight: bold; }}
.header {{ padding: 20px 30px; background: #16213e; color: white; }}
.header h1 {{ margin: 0 0 6px 0; font-size: 22px; }}
.header p {{ margin: 0; font-size: 14px; color: #b0b0b0; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 16px 30px; }}
.file-block {{ background: white; border-radius: 8px; padding: 14px 18px; margin-bottom: 10px; box-shadow: 0 1px 4px rgba(0,0,0,0.08); }}
.file-name {{ font-weight: bold; font-size: 14px; color: #1a1a2e; margin-bottom: 2px; }}
.file-path {{ font-size: 11px; color: #888; margin-bottom: 8px; word-break: break-all; }}
.item {{ padding: 3px 0; font-size: 13px; border-bottom: 1px solid #f0f0f0; }}
.item:last-child {{ border-bottom: none; }}
.item-name {{ color: #0d6efd; margin-right: 10px; font-family: "Fira Code", "Consolas", monospace; }}
.item-desc {{ color: #555; }}
.footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
</style>
</head>
<body>
<div class="navbar">
{nav}
</div>
<div class="header">
<h1>vLLM Ascend API - {title} 模块</h1>
<p>文件数: {total_files} | 函数数: {total_funcs} | 每个函数含 [代码行数] + 功能描述</p>
</div>
<div class="container">
{"".join(blocks)}
</div>
<div class="footer">
  vLLM Ascend API 文档 - 由 AST 自动提取生成 | 总计 {total_funcs} 个函数
</div>
</body>
</html>"""

    out_path = os.path.join(r'D:\demo\202609\vllm-ascend\code-docs', page_file)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Generated {page_file}: {total_files} files, {total_funcs} funcs, {os.path.getsize(out_path)/1024:.1f}KB')
    return total_files, total_funcs


grand_files = 0
grand_funcs = 0
for page_file, prefix_list in PAGES:
    ff, ffn = generate_html(page_file, prefix_list)
    grand_files += ff
    grand_funcs += ffn

print(f'\nTotal: {grand_files} files, {grand_funcs} funcs')
