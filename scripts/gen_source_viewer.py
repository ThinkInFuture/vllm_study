"""生成源码查看器的数据文件：vllm_ascend/**/*.py -> code-docs/src/<path>.py.js

数据文件为 JSONP 式：内容加载后调用 window.__SRC_SET(path, source)。
JSON ensure_ascii=True 使全部非 ASCII 转为 \\uXXXX，天然防 </script> 提前闭合。
幂等：可重复执行，全量重新生成。
"""
import os, json

SRC = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'
OUT = r'D:\demo\202609\vllm-ascend\code-docs\src'

count = 0
errors = []
for dirpath, dirs, files in os.walk(SRC):
    dirs[:] = [d for d in dirs if d not in ('__pycache__',)]
    for fn in sorted(files):
        if not fn.endswith('.py'):
            continue
        fp = os.path.join(dirpath, fn)
        rel = os.path.relpath(fp, SRC).replace('\\', '/')
        try:
            code = open(fp, encoding='utf-8', errors='replace').read()
        except OSError as e:
            errors.append((rel, str(e)))
            continue
        out_path = os.path.join(OUT, rel.replace('/', os.sep) + '.js')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        payload = json.dumps(code, ensure_ascii=True)
        with open(out_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(f'window.__SRC_SET({json.dumps(rel)},{payload});')
        count += 1

total_lines = 0
for dirpath, _, files in os.walk(OUT):
    for fn in files:
        total_lines += sum(1 for _ in open(os.path.join(dirpath, fn), encoding='utf-8', errors='ignore'))
size_mb = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs) / 1024 / 1024
print(f'generated {count} .js data files, total {size_mb:.1f} MB, errors: {len(errors)}')
for e in errors[:5]:
    print(' ', e)
