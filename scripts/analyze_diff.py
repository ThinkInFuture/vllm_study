"""
分析为什么 HTML 函数数比 AST 解析的函数数多很多
"""
import os, re, json, ast

src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'

# 重新解析所有源码，统计类方法 + 模块级函数
def count_all_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        src = f.read()
    try:
        tree = ast.parse(src)
    except:
        return 0, 0
    funcs = 0  # 模块级函数
    methods = 0  # 类方法
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if isinstance(getattr(node, 'parent', None), ast.ClassDef):
                methods += 1
            else:
                funcs += 1
    return funcs, methods


# 按模块统计
modules = {
    'all': '',
    'attention': 'attention/',
    'core': 'core/',
    'models': 'models/',
    'ops': 'ops/',
}

print('各模块源码中的实际函数数（类方法 + 模块级）:')
for name, prefix in modules.items():
    funcs = 0
    methods = 0
    files = 0
    for root, dirs, files_list in os.walk(src):
        for fn in files_list:
            if not fn.endswith('.py'):
                continue
            fp = os.path.join(root, fn)
            rel = os.path.relpath(fp, src).replace('\\', '/')
            if name == 'all':
                if '/' in rel:  # 子目录的不算 root
                    continue
            else:
                if not rel.startswith(prefix):
                    continue
            f, m = count_all_in_file(fp)
            funcs += f
            methods += m
            files += 1
    print(f'  {name:12s}: files={files:3d}, module_funcs={funcs:3d}, class_methods={methods:4d}, total={funcs+methods:4d}')