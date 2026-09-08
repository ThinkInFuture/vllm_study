"""
为 panorama-root.html 的每个函数添加行数前缀
"""
import os, re, json

with open(r'D:\demo\202609\vllm-ascend\func_meta.json', 'r', encoding='utf-8') as f:
    META = json.load(f)


def normalize_path(p):
    return p.replace('\\', '/').lstrip('./')


def get_meta(file_name, fname):
    candidates = [file_name, normalize_path(file_name)]
    for key in candidates:
        if key in META and fname in META[key]:
            return META[key][fname]
    bn = os.path.basename(file_name)
    if bn in META and fname in META[bn]:
        return META[bn][fname]
    return None


def get_lines(file_name, fname):
    meta = get_meta(file_name, fname)
    if meta:
        return meta[0]
    return 0


def process_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    counts = {'processed': 0, 'skipped': 0}

    # 匹配现有 desc span - 在前面加 [N行]
    # 不重复添加：如果已经有 [N行] 前缀则跳过
    func_pattern = re.compile(
        r'(<span class="item-name">)([^<]+)(</span>)(<span class="item-desc">)(?!\[)(\d+行\] )?([^<]+)(</span>)'
    )
    # 更简单的策略：找所有 item-name + item-desc 对，如果 desc 不以 [N行] 开头且有行数，则加前缀

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

        # 对每个 item-name + item-desc 替换
        pattern = re.compile(
            r'(<span class="item-name">)([^<]+)(</span><span class="item-desc">)(?!\[)([^<]+)(</span>)'
        )
        def make_replacer(fn):
            def replacer(m):
                fname = m.group(2).strip()
                desc = m.group(4).strip()
                if not desc or desc.startswith('('):
                    # 跳过 placeholder 或空
                    return m.group(0)
                if desc.startswith('['):
                    # 已有行数前缀
                    return m.group(0)
                lines = get_lines(fn, fname)
                if lines > 0:
                    new_desc = f'[{lines}行] {desc}'
                    counts['processed'] += 1
                else:
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


path = r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html'
counts = process_html(path)
print(f'panorama-root.html: processed={counts["processed"]}')