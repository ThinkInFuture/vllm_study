import json, os

with open('mod_summary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

lines = []
lines.append('<!DOCTYPE html>')
lines.append('<html lang="zh-CN">')
lines.append('<head>')
lines.append('<meta charset="UTF-8">')
lines.append('<title>vLLM Ascend 全景图 - 索引</title>')
lines.append('<style>')
lines.append('body{font-family:Arial,sans-serif;background:#f5f7fa;color:#333;margin:0;padding:20px;}')
lines.append('.h1{color:#667eea;margin-bottom:20px;}')
lines.append('.table{width:100%;border-collapse:collapse;margin:20px 0;}')
lines.append('.table th,.table td{padding:8px 12px;border:1px solid #ddd;text-align:left;font-size:0.9rem;}')
lines.append('.table th{background:#667eea;color:#fff;}')
lines.append('.module{margin:30px 0;padding:20px;border-left:4px solid #667eea;background:#fafbfc;}')
lines.append('.module h2{color:#333;margin-bottom:10px;}')
lines.append('</style>')
lines.append('</head>')
lines.append('<body>')
lines.append('<h1>vLLM Ascend 全景图 - 源码结构索引</h1>')
total_files = sum(v['files'] for v in data.values())
total_funcs = sum(v['functions'] for v in data.values())
total_cls = sum(v['classes'] for v in data.values())
lines.append(f'<p>共 {total_files} 个文件，{total_funcs} 个函数，{total_cls} 个类</p>')

for mod_name, info in data.items():
    lines.append('<div class="module">')
    lines.append(f'<h2>{mod_name}</h2>')
    lines.append(f'<p>文件: {info["files"]} | 类: {info["classes"]} | 函数: {info["functions"]}</p>')
    lines.append('<table class="table"><tr><th>文件相对路径</th><th>类数</th><th>函数数</th></tr>')
    lines.append(f'<tr><td colspan="3">详见对应模块子页面 (panorama-{mod_name}.html)</td></tr>')
    lines.append('</table>')
    lines.append('</div>')

lines.append('<h3>子页面说明</h3>')
lines.append('<p>每个模块对应一个子页面，例如：</p>')
lines.append('<ul>')
links = ['root','core','attention','ops','worker','models','distributed','rest']
for lnk in links:
    lines.append(f'<li><a href="panorama-{lnk}.html">{lnk}</a></li>')
lines.append('</ul>')
lines.append(f'<p>每个子页面将列出该模块下的所有文件、类和函数（共计约 {total_funcs} 个函数）</p>')
lines.append('</body>')
lines.append('</html>')

with open('panorama.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('Generated panorama.html successfully')
print(f'Total: {total_files} files, {total_funcs} functions, {total_cls} classes')