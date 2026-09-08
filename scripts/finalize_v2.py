"""
为所有 5 个 panorama HTML 补充行数前缀（增强版：支持 ClassName.method 形式）
"""
import os, re, json

with open(r'D:\demo\202609\vllm-ascend\func_meta.json', 'r', encoding='utf-8') as f:
    META = json.load(f)


def normalize_path(p):
    return p.replace('\\', '/').lstrip('./')


def get_lines(file_name, fname):
    """支持 'method_name' 或 'ClassName.method_name' 形式"""
    candidates = [file_name, normalize_path(file_name)]
    for key in candidates:
        if key in META:
            # 1) 直接匹配
            if fname in META[key]:
                return META[key][fname][0]
            # 2) 匹配 ClassName.method 形式 - 取最后一段
            short = fname.split('.')[-1]
            if short in META[key]:
                return META[key][short][0]
            # 3) 匹配 xxx_yyy.method 形式（方法中可能嵌套）
            # 找以 fname 结尾的 key
            for k in META[key]:
                if k == fname or k.endswith('.' + fname):
                    return META[key][k][0]
    # 退化：basename
    bn = os.path.basename(file_name)
    if bn in META:
        if fname in META[bn]:
            return META[bn][fname][0]
        short = fname.split('.')[-1]
        if short in META[bn]:
            return META[bn][short][0]
    return 0


def process_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    counts = {'processed': 0, 'skipped': 0, 'no_meta': 0}

    file_block_starts = [m.start() for m in re.finditer(r'<div class="file-block">', html)]
    file_block_pattern = re.compile(r'<div class="file-name">([^<]+)</div>')

    new_html_parts = []
    last_idx = 0

    for i, start in enumerate(file_block_starts):
        new_html_parts.append(html[last_idx:start])
        if i + 1 < len(file_block_starts):
            end = file_block_starts[i + 1]
        else:
            end = len(html)
        block = html[start:end]
        name_match = file_block_pattern.search(block)
        file_name = name_match.group(1) if name_match else ''

        pattern = re.compile(
            r'(<span class="item-name">)([^<]+)(</span><span class="item-desc">)(?!\[)([^<]+)(</span>)'
        )
        def make_replacer(fn):
            def replacer(m):
                fname = m.group(2).strip()
                desc = m.group(4).strip()
                if not desc or desc.startswith('('):
                    return m.group(0)
                if desc.startswith('['):
                    return m.group(0)
                lines = get_lines(fn, fname)
                if lines > 0:
                    new_desc = f'[{lines}行] {desc}'
                    counts['processed'] += 1
                else:
                    counts['no_meta'] += 1
                    return m.group(0)
                return f'{m.group(1)}{fname}{m.group(3)}{new_desc}{m.group(5)}'
            return replacer
        new_block = pattern.sub(make_replacer(file_name), block)
        new_html_parts.append(new_block)
        last_idx = end

    new_html_parts.append(html[last_idx:])
    new_html = ''.join(new_html_parts)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    return counts


pages = [
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'root'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-attention.html', 'attention'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-core.html', 'core'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-models.html', 'models'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-ops.html', 'ops'),
]

for path, name in pages:
    counts = process_html(path)
    print(f'{name}: processed={counts["processed"]}, no_meta={counts["no_meta"]}')