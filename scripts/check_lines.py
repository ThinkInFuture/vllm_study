"""
更彻底的检查：
1. 每个函数是否有行数（[N行] 前缀）？
2. 每个函数是否有真实描述（非占位符）？
3. 总函数计数是否与实际源码一致？
"""
import os, re, json

with open(r'D:\demo\202609\vllm-ascend\func_meta.json', 'r', encoding='utf-8') as f:
    META = json.load(f)

# 各 panorama HTML 对应的源文件模块
MODULES = {
    'panorama-root.html': 'all',  # 根模块
    'panorama-attention.html': 'attention',
    'panorama-core.html': 'core',
    'panorama-models.html': 'models',
    'panorama-ops.html': 'ops',
}

# 计算实际源码中的函数总数（按模块）
def count_funcs_in_module(module):
    """按模块统计实际源码中的函数数"""
    src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'
    total = 0
    if module == 'all':
        # root: 根目录所有 .py
        for fp in META:
            if '/' not in fp:  # 根目录
                total += len(META[fp])
    else:
        prefix = module + '/'
        for fp in META:
            if fp.startswith(prefix):
                total += len(META[fp])
    return total


# 检查 panorama HTML 中的实际函数数
def count_funcs_in_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        c = f.read()
    # 匹配所有 item-name span
    names = re.findall(r'<span class="item-name">([^<]+)</span>', c)
    return len(names), names


print('=' * 70)
print('检查每个 panorama HTML 与源码的函数计数一致性')
print('=' * 70)

for html, module in MODULES.items():
    html_path = r'D:/demo/202609/vllm-ascend/code-docs/' + html
    actual_in_html, names = count_funcs_in_html(html_path)
    actual_in_src = count_funcs_in_module(module)
    print(f'\n{html}:')
    print(f'  HTML 中函数条目数: {actual_in_html}')
    print(f'  源码中函数总数:   {actual_in_src}')

    # 检查有行数前缀的占比
    with open(html_path, 'r', encoding='utf-8') as f:
        c = f.read()
    with_lines = len(re.findall(r'item-name">([^<]+)</span><span class="item-desc">\[\d+行\]', c))
    without_lines = actual_in_html - with_lines
    print(f'  有 [N行] 前缀的: {with_lines} ({with_lines*100//actual_in_html}%)')
    print(f'  没有 [N行] 的:   {without_lines}')

    # 检查 placeholder
    p1 = c.count('(功能说明)')
    p2 = c.count('(参见源码:')
    p3 = c.count('(源码见对应位置:')
    print(f'  占位符 (功能说明):  {p1}')
    print(f'  占位符 (参见源码:): {p2}')
    print(f'  占位符 (源码见对应位置:): {p3}')

    # 描述是否有效（不全是占位符）
    real_descs = re.findall(r'item-desc">([^<]+)</span>', c)
    invalid = [d for d in real_descs if d.startswith('(') and ('参见源码' in d or '源码见对应' in d)]
    print(f'  实际为占位符的描述数: {len(invalid)}')

    # 显示几个没有行数前缀的样本
    if without_lines > 0:
        no_line_names = []
        for m in re.finditer(r'<span class="item-name">([^<]+)</span><span class="item-desc">([^\[<][^<]+)</span>', c):
            no_line_names.append(m.group(1))
            if len(no_line_names) >= 5:
                break
        print(f'  没有 [N行] 的样本: {no_line_names}')