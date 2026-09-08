import json, os, re

src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'

# 提取根模块所有py文件的class和function，并尝试获取docstring
def extract_py_info(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 提取类
    classes = re.findall(r'^\s*class\s+(\w+)\s*\([^)]*\)\s*[:]', content, re.MULTILINE)
    
    # 提取函数及其docstring
    functions = []
    # 匹配 def ... 后面紧跟的 docstring (三个引号或一行docstring)
    func_blocks = re.finditer(r'^\s*def\s+(\w+)\s*\([^)]*\)\s*([^\n]*)?\n\s*(\"\"\".*?\"\"\"|\'.*?\')', content, re.DOTALL | re.MULTILINE)
    for m in func_blocks:
        fname = m.group(1)
        doc = m.group(3)
        # 清理docstring
        if doc.startswith('"""'):
            doc = doc[3:-3].strip()
        elif doc.startswith("'''"):
            doc = doc[3:-3].strip()
        functions.append({'name': fname, 'doc': doc[:100] if doc else ''})
    
    # 尝试提取更多：没法被上面regex覆盖的单行docstring
    for block in re.finditer(r'^\s*def\s+(\w+)\s*\(', content, re.MULTILINE):
        fname = block.group(1)
        # 检查紧随其后的几行是否有注释
        start = block.end()
        lines_after = content[start:start+200].split('\n')
        doc = ''
        for line in lines_after:
            stripped = line.strip()
            if stripped.startswith('#'):
                doc += stripped[1:].strip() + ' '
            elif stripped == '':
                continue
            else:
                break
        if doc and not any(f['name'] == fname for f in functions):
            functions.append({'name': fname, 'doc': doc.strip()[:100]})
    
    return {'classes': classes, 'functions': functions}

# 处理根模块
root_dir = os.path.join(src)
file_infos = []

for root, dirs, files in os.walk(root_dir):
    for fn in sorted(files):
        if not fn.endswith('.py'):
            continue
        fp = os.path.join(root, fn)
        relpath = os.path.relpath(fp, src)
        info = extract_py_info(fp)
        file_infos.append({
            'file': relpath,
            'classes': info['classes'],
            'functions': info['functions']
        })

# 统计
total_cls = sum(len(f['classes']) for f in file_infos)
total_funcs = sum(len(f['functions']) for f in file_infos)
print(f'Root module: {len(file_infos)} files, {total_cls} classes, {total_funcs} functions')

# 生成 panorama-root.html
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
html_lines.append('.file-name{font-family:\"Consolas\",monospace;font-size:0.95rem;font-weight:bold;color:#667eea;margin-bottom:8px;display:block;}')
html_lines.append('.file-desc{color:#888;font-size:0.85rem;margin-bottom:12px;line-height:1.4;}')
html_lines.append('.item{display:flex;gap:10px;padding:4px 0;font-size:0.85rem;}')
html_lines.append('.item-type{font-family:\"Consolas\",monospace;font-size:0.75rem;padding:1px 6px;border-radius:4px;white-space:nowrap;min-width:50px;text-align:center;}')
html_lines.append('.type-class{background:#e8f5e9;color:#2e7d32;}')
html_lines.append('.type-func{background:#e3f2fd;color:#1565c0;}')
html_lines.append('.item-name{font-family:\"Consolas\",monospace;color:#333;min-width:220px;}')
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
html_lines.append('<p>包含平台配置、环境变量、工具函数等核心模块</p>')
html_lines.append('</div>')

# 分模块展示 - 这里为了页面大小，每个文件展示名前10个函数和所有类
# 实际文件太多，采用摘要展示
html_lines.append('<div class="section">')
html_lines.append('<h2>模块概览</h2>')
html_lines.append(f'<p>总文件数: {len(file_infos)} | 总类数: {total_cls} | 总函数数: {total_funcs}</p>')
html_lines.append('</div>')

# 按文件分组展示名前几个条目
html_lines.append('<div class="section">')
html_lines.append('<h2>关键文件摘要 (每文件前10个函数 + 所有类)</h2>')
html_lines.append('<p>由于文件较多（' + str(len(file_infos)) + '），以下展示前30个文件的详细信息，其余请参考子页面或完整列表。</p>')
html_lines.append('</div>')

# 展示前30个文件
for i, finfo in enumerate(file_infos[:30]):
    html_lines.append(f'<div class="file-block">')
    html_lines.append(f'<div class="file-name">{finfo["file"]}</div>')
    cls_desc = []
    for c in finfo['classes']:
        cls_desc.append(c)
    html_lines.append(f'<div class="file-desc">类: {", ".join(cls_desc) if cls_desc else "无"}</div>')
    
    # 展示函数名前10个
    funcs_shown = finfo['functions'][:10]
    func_names = [f['name'] for f in funcs_shown]
    doc_previews = [f['doc'] for f in funcs_shown]
    
    html_lines.append(f'<div class="item">类型: 函数 | 数量: {len(finfo["functions"])}</div>')
    for j, (fname, fdoc) in enumerate(zip(func_names, doc_previews)):
        html_lines.append(f'<div class="item"><span class="item-type type-func">func</span><span class="item-name">{fname}</span><span class="item-desc">{fdoc}</span></div>')
    
    if len(finfo['functions']) > 10:
        html_lines.append(f'<div class="item"><span class="item-type">...</span> 还有 {len(finfo["functions"]) - 10} 个函数</div>')
    
    html_lines.append('</div>')

# 其余文件链接
html_lines.append('<div class="file-block">')
html_lines.append(f'<div class="file-name">其余文件 ({len(file_infos)-30} 个)</div>')
html_lines.append(f'<div class="file-desc">详见 <a href="panorama-root.html">panorama-root.html</a> 或源码</div>')
html_lines.append('</div>')

html_lines.append('</body>')
html_lines.append('</html>')

with open('panorama-root.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(html_lines))
print('Generated panorama-root.html (first 30 files shown)')