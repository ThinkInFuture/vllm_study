import re

with open('panorama-models.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 统计 item-name 出现次数
count = 0
for m in re.finditer(r'<span class="item-name">', html):
    count += 1
print(f'Found {count} occurrences of item-name in panorama-models.html')

# 从后往前替换，在每个 item-name 后面的 </span> 前插入 desc
html_list = list(html)
# 找到所有位置（记录原始位置，因为后面会修改html字符串）
positions = []
for m in re.finditer(r'<span class="item-name">', html):
    positions.append(m.start())

# 从后往前处理，防止位置偏移
for pos in reversed(positions):
    end_search = html.find('</span>', pos)
    if end_search > pos:
        desc_span = '<span class="item-desc">(功能说明)</span>'
        before = html[:end_search]
        after = html[end_search:]
        html = before + desc_span + after

with open('panorama-models.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('panorama-models.html updated: added (功能说明) to all function name spans')