import re

with open('panorama-root.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 在每个 <span class="item-name"> 后面，紧随其后的 </span> 前插入 desc span
# 匹配模式：<span class="item-name">xxx</span>
# 替换为：<span class="item-name">xxx</span><span class="item-desc">(功能说明)</span>

# 使用 regex 替换，但要小心不要替换掉已经有 desc 的情况
# 当前 HTML 中 item-name 后面紧跟的是</div>或</div>的上下文

# 我们查找所有出现的 <span class="item-name"> 并检查它后面是否已经有 item-desc
# 如果没有，则添加

# 简单的方法：直接把所有 <span class="item-name"> 后面的 </span> 改成 </span><span class="item-desc">(功能说明)</span>
# 但要确保只在 item-name 之后，不是已经有 desc 的情况下

# 先找出所有位置
count = 0
positions = []
for m in re.finditer(r'<span class="item-name">', html):
    positions.append(m.start())
    count += 1
print(f'Found {count} occurrences of item-name')

# 从后往前替换，避免位置偏移
html_list = list(html)
for pos in reversed(positions):
    # 在 item-name 的结束位置之后插入
    # 找到这个 <span> 的结束
    end_search = html.find('</span>', pos)
    if end_search > pos:
        # 在 </span> 之前插入 our desc
        desc_span = '<span class="item-desc">(功能说明)</span>'
        # 替换: ...xxx</span> -> ...xxx</span><span class="item-desc">(功能说明)</span>
        before = html[:end_search]
        after = html[end_search:]
        new_html = before + desc_span + after
        html = new_html
        # 更新后面的位置信息（这里我们用了从后往前替换，所以位置是对的）

# 写回文件
with open('panorama-root.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('panorama-root.html updated: added (功能说明) to all function name spans')