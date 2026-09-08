import smtplib, os, zipfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

root = r'D:\demo\202609\vllm-ascend'
zip_path = os.path.join(root, 'vllm-ascend-docs-final.zip')

# 打包：code-docs（含 src-viewer.html + src/ 数据 + assets/highlight）+ docs + AGENTS.md
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for top in ('code-docs', 'docs'):
        d = os.path.join(root, top)
        for dirpath, _, filenames in os.walk(d):
            for fn in sorted(filenames):
                fp = os.path.join(dirpath, fn)
                zf.write(fp, os.path.relpath(fp, root))
    zf.write(os.path.join(root, 'AGENTS.md'), 'AGENTS.md')

n_src = sum(1 for dp, _, fs in os.walk(os.path.join(root, 'code-docs', 'src')) for _ in fs)
zip_size = os.path.getsize(zip_path)
print(f'Zip: {zip_size/1024:.1f} KB, viewer data files: {n_src}')

html = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
body{font-family:Arial;margin:20px;background:#f5f5f5;}
.card{background:white;border-radius:10px;padding:15px;margin:10px 0;box-shadow:0 2px 5px rgba(0,0,0,0.1);}
.card-title{font-size:18px;font-weight:bold;color:#333;margin-bottom:10px;}
.card-row{padding:8px 0;border-bottom:1px solid #eee;display:flex;justify-content:space-between;}
.card-row:last-child{border-bottom:none;}
.label{color:#666;}
.value{font-weight:bold;}
.positive{color:#28a745;}
</style></head><body>
<h2>vLLM Ascend 文档 · 源码查看器版</h2>
<div class="card"><div class="card-title">新增：单页源码查看器</div>
<div class="card-row"><span class="label">「查看源码」全新体验</span><span class="value positive">457 个链接统一打开同一 HTML 查看页（不再直接打开 .py 文件）</span></div>
<div class="card-row"><span class="label">查看页能力</span><span class="value">语法高亮（highlight.js 浅色主题）+ 行号列 + 面包屑 + 返回按钮 + 1200px 居中</span></div>
<div class="card-row"><span class="label">离线可用</span><span class="value">高亮库本地化，解压双击 index.html 即完整使用，无需联网/无需本地服务器</span></div>
</div>
<div class="card"><div class="card-title">修复：panorama 主题统一</div>
<div class="card-row"><span class="label">8 个模块子页</span><span class="value positive">统一导航条/页头/字体/配色/页脚（原三代样式并存）</span></div>
<div class="card-row"><span class="label">统计行修正</span><span class="value">按页面实际条目数展示（root 页不再误显全包数字）</span></div>
</div>
<div class="card"><div class="card-title">质量验证（截图 + 大模型图片理解逐项核验）</div>
<div class="card-row"><span class="label">查看器</span><span class="value positive">面包屑/行号/高亮/居中/行数 五项全过（含 5368 行大文件与错误页兜底）</span></div>
<div class="card-row"><span class="label">主题统一</span><span class="value positive">core 与 distributed 两类页面四项核验全过</span></div>
<div class="card-row"><span class="label">死链</span><span class="value positive">735 链接 / 0 死链；457 个查看链接数据文件全部存在</span></div>
</div>
<div class="card"><div class="card-title">包内容</div>
<div class="card-row"><span class="label">附件</span><span class="value">vllm-ascend-docs-final.zip</span></div>
<div class="card-row"><span class="label">结构</span><span class="value">code-docs/（含 src-viewer.html + src/ 数据 + assets/highlight/）+ docs/ + AGENTS.md</span></div>
<div class="card-row"><span class="label">设计文档</span><span class="value">docs/documentation-design.md 已沉淀查看器架构与主题规范</span></div>
</div>
</body></html>"""

msg = MIMEMultipart()
msg['From'] = '18913980939@163.com'
msg['To'] = '125987347@qq.com'
msg['Subject'] = 'vLLM Ascend 文档：单页源码查看器（高亮+居中）+ panorama主题统一'
msg.attach(MIMEText(html, 'html', 'utf-8'))

with open(zip_path, 'rb') as f:
    attach = MIMEApplication(f.read(), Name='vllm-ascend-docs-final.zip')
attach['Content-Disposition'] = 'attachment; filename="vllm-ascend-docs-final.zip"'
msg.attach(attach)

server = smtplib.SMTP_SSL('smtp.163.com', 465)
server.login('18913980939@163.com', '<SMTP_PASSWORD>')
server.sendmail('18913980939@163.com', '125987347@qq.com', msg.as_string())
server.quit()
print('sent')
