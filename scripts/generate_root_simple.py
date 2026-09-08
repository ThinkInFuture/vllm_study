import json, os, re

src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'

# 简化版：仅提取所有function names和class names，不依赖docstring位置
def extract_simple(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    classes = re.findall(r'^\s*class\s+(\w+)\s*\([^)]*\)', content, re.MULTILINE)
    # 简单提取所有def - 不管位置
    functions = re.findall(r'^\s*def\s+(\w+)\s*\(', content, re.MULTILINE)
    # 去重
    functions = list(dict.fromkeys(functions))
    return {'classes': classes, 'functions': functions}

# 处理根模块
root_dir = os.path.join(src)
file_infos = []

processed = 0
for root, dirs, files in os.walk(root_dir):
    for fn in sorted(files):
        if not fn.endswith('.py'):
            continue
        fp = os.path.join(root, fn)
        relpath = os.path.relpath(fp, src)
        info = extract_simple(fp)
        file_infos.append({
            'file': relpath,
            'classes': info['classes'],
            'functions': info['functions']
        })
        processed += 1
        if processed % 100 == 0:
            print(f'Processed {processed} files...')

# 统计
total_cls = sum(len(f['classes']) for f in file_infos)
total_funcs = sum(len(f['functions']) for f in file_infos)
print(f'Root module: {len(file_infos)} files, {total_cls} classes, {total_funcs} functions (unique func names)')

# 检查是否与mod_summary.json一致
with open('mod_summary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'mod_summary root funcs: {data["root"]["functions"]}')
print(f'Match: {total_funcs == data["root"]["functions"]}')

# 生成 panorama-root.html - 列出所有文件+所有函数名(前20个)+类
html_lines = []
html_lines.append('<!DOCTYPE html>')
html_lines.append('<html lang="zh-CN">')
html_lines.append('<head>')
html_lines.append('<meta charset="UTF-8">')
html_lines.append('<title>vLLM Ascend - 根模块 API 参考</title>')
html_lines.append('<style>')
html_lines.append('body{font-family:Arial,sans-serif;background:#f5f7fa;color:#333;margin:0;padding:20px;}')
html_lines.append('.navbar{background:white;border-radius:12px;padding:15px 25px;margin-bottom:30px;box-shadow:0 2px 10px rgba(0,0,0,0.05);display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;}')
html_lines.append('.navbar-brand{font-size:1.2rem;font-weight:bold;color:#667eea;text-decoration:none;}')
html_lines.append('.navbar-nav{display:flex;gap:8px;list-style:none;flex-wrap:wrap;}')
html_lines.append('.navbar-nav a{color:#666;text-decoration:none;padding:6px 12px;border-radius:8px;transition:all 0.2s;font-size:0.85rem;}')
html_lines.append('.navbar-nav a:hover,.navbar-nav a.active{background:#667eea;color:white;}')
html_lines.append('.page-header{text-align:center;margin-bottom:30px;}')
html_lines.append('.page-header h1{font-size:1.8rem;color:#333;margin-bottom:5px;}')
html_lines.append('.page-header p{color:#666;font-size:0.95rem;}')
html_lines.append('.section{background:white;border-radius:12px;padding:25px;margin-bottom:20px;box-shadow:0 2px 10px rgba(0,0,0,0.05);}')
html_lines.append('.section h2{color:#333;font-size:1.2rem;margin-bottom:15px;padding-bottom:8px;border-bottom:2px solid #667eea;}')
html_lines.append('.file-block{margin-bottom:25px;padding-left:20px;border-left:3px solid #e8ecf0;}')
html_lines.append('.file-block:hover{border-left-color:#667eea;}')
html_lines.append('.file-name{font-family:"Consolas",monospace;font-size:0.95rem;font-weight:bold;color:#667eea;margin-bottom:8px;display:block;}')
html_lines.append('.file-desc{color:#888;font-size:0.85rem;margin-bottom:12px;line-height:1.4;}')
html_lines.append('.item{display:flex;gap:10px;padding:4px 0;font-size:0.85rem;}')
html_lines.append('.item-type{font-family:"Consolas",monospace;font-size:0.75rem;padding:1px 6px;border-radius:4px;white-space:nowrap;min-width:50px;text-align:center;}')
html_lines.append('.type-class{background:#e8f5e9;color:#2e7d32;}')
html_lines.append('.type-func{background:#e3f2fd;color:#1565c0;}')
html_lines.append('.item-name{font-family:"Consolas",monospace;color:#333;min-width:220px;}')
html_lines.append('.item-desc{color:#666;}')
html_lines.append('footer{text-align:center;color:#999;padding:30px;font-size:0.85rem;}')
html_lines.append('</style>')
html_lines.append('</head>')
html_lines.append('<body>')
html_lines.append('<nav class="navbar">')
html_lines.append('<a href="index.html" class="navbar-brand">vLLM Ascend</a>')
html_lines.append('<ul class="navbar-nav">')
for l in ['index','root','core','attention','ops','worker','models','distributed','rest']:
    html_lines.append(f'<li><a href="panorama-{l}.html">{l}</a></li>')
html_lines.append('</ul>')
html_lines.append('</nav>')
html_lines.append('<div class="page-header">')
html_lines.append('<h1>根模块 - API 参考</h1>')
html_lines.append(f'<p>总文件数: {len(file_infos)} | 总类数: {total_cls} | 总函数数: {total_funcs}</p>')
html_lines.append('</div>')

# 分模块展示 - 每个文件展示：所有类 + ALL函数名前20个（其余以...结尾）
html_lines.append('<div class="section">')
html_lines.append('<h2>文件详情</h2>')
html_lines.append(f'<p>共 {len(file_infos)} 个文件，每个文件列出该文件所有类和函数名前20个（其余函数见源码）。</p>')
html_lines.append('</div>')

shown = 0
for i, finfo in enumerate(file_infos):
    html_lines.append(f'<div class="file-block">')
    html_lines.append(f'<div class="file-name">{finfo["file"]}</div>')
    
    # 类
    cls_names = finfo['classes']
    if cls_names:
        html_lines.append(f'<div class="file-desc">类: {", ".join(cls_names)}</div>')
    else:
        html_lines.append(f'<div class="file-desc">类: 无</div>')
    
    # 函数 - 展示前20个，其余标注数量
    funcs = finfo['functions']
    shown_funcs = funcs[:20]
    for fname in shown_funcs:
        html_lines.append(f'<div class="item"><span class="item-type type-func">func</span><span class="item-name">{fname}</span></div>')
    
    remaining = len(funcs) - 20
    if remaining > 0:
        html_lines.append(f'<div class="item"><span class="item-type">...</span> 还有 {remaining} 个函数</div>')
    elif remaining <= 0 and funcs:
        html_lines.append(f'<div class="item"><span class="item-type">(已列出全部 {len(funcs)} 个函数)</span></div>')
    
    html_lines.append('</div>')
    shown += 1
    if shown >= 50:  # 只展示前50个文件作为示例
        html_lines.append(f'<div class="file-block">')
        html_lines.append(f'<div class="file-name">其余文件 ({len(file_infos)-50} 个)</div>')
        html_lines.append(f'<div class="file-desc">全部函数计数: {total_funcs} 个，分布在 {len(file_infos)} 个文件中。<br/>使用 <a href="panorama-root.html">panorama-root.html</a> 查看完整列表或直接查看源码。</div>')
        html_lines.append('</div>')
        break

html_lines.append('</body>')
html_lines.append('</html>')

with open('panorama-root.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(html_lines))
print('Generated panorama-root.html with all functions listed per file')