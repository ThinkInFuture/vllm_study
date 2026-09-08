"""
扫描所有 .py 源码，构建每个 (file, func_name) -> {lines, desc} 的元数据。
- lines: 函数代码行数（通过 ast 解析）
- desc: 函数功能描述（基于源码内容生成）
"""
import os, ast, json, re

src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'

# 函数描述规则：
# 1. docstring 第一行
# 2. 文件路径 + 函数名启发
# 3. 类成员（self.xxx 调用）启发

def extract_func_info(filepath, relpath):
    """提取文件中所有函数/方法的行数和描述"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            source = f.read()
    except:
        return {}
    try:
        tree = ast.parse(source)
    except:
        return {}

    result = {}  # fname -> (lines, desc, is_method)

    # 遍历 AST
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            lines = (node.end_lineno - node.lineno + 1) if node.end_lineno else 0
            # 提取 docstring
            desc = ''
            if (node.body and isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant)):
                doc = node.body[0].value.value
                if isinstance(doc, str):
                    desc = doc.strip().split('\n')[0][:120]
            # 跳过空描述
            fname = node.name
            # 只保留前两层
            if desc:
                result[fname] = (lines, desc)
    return result


def main():
    all_meta = {}  # basename -> {fname: (lines, desc)}
    for root, dirs, files in os.walk(src):
        for fn in sorted(files):
            if not fn.endswith('.py'):
                continue
            fp = os.path.join(root, fn)
            relpath = os.path.relpath(fp, src).replace('\\', '/')
            info = extract_func_info(fp, relpath)
            if info:
                all_meta[relpath] = info
    # Save
    with open(r'D:\demo\202609\vllm-ascend\func_meta.json', 'w', encoding='utf-8') as f:
        json.dump(all_meta, f, ensure_ascii=False)
    # Summary
    total_files = len(all_meta)
    total_funcs = sum(len(v) for v in all_meta.values())
    with_desc = sum(1 for v in all_meta.values() for fn, (l, d) in v.items() if d)
    print(f'Total files: {total_files}')
    print(f'Total funcs: {total_funcs}')
    print(f'With docstring desc: {with_desc}')

if __name__ == '__main__':
    main()