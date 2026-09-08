"""
发送 5 个 panorama HTML（最终版，含行数 + 真实描述）到邮箱
"""
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

pages = [
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'root'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-attention.html', 'attention'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-core.html', 'core'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-models.html', 'models'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-ops.html', 'ops'),
]

for fpath, name in pages:
    fname = os.path.basename(fpath)
    fsize = os.path.getsize(fpath)

    msg = MIMEMultipart()
    msg['From'] = '18913980939@163.com'
    msg['To'] = '125987347@qq.com'
    msg['Subject'] = f'vLLM Ascend panorama-{name}.html (含行数 + 真实描述) - 最终版'

    body_text = f"""vLLM Ascend panorama-{name}.html 已最终更新。

文件：{fname}
大小：{fsize/1024:.1f} KB

本次更新：
- 用 AST 解析所有源码，提取每个函数的 docstring 作为功能描述
- 计算每个函数的代码行数（基于 AST 的 lineno/end_lineno）
- 格式：[N行] 功能描述
- 已替换所有 0 占位符
- root 页面保留中文描述 + 行数（前轮手工写）
- 其他 4 个页面使用英文 docstring + 行数（来自源码）

统计：{{root:515, attention:378, core:136, models:286, ops:494}} = 1809 个函数全部有描述。
"""
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

    with open(fpath, 'rb') as f:
        attach = MIMEApplication(f.read(), Name=fname)
    attach['Content-Disposition'] = f'attachment; filename="{fname}"'
    msg.attach(attach)

    server = smtplib.SMTP_SSL('smtp.163.com', 465)
    server.login('18913980939@163.com', '<SMTP_PASSWORD>')
    server.sendmail('18913980939@163.com', '125987347@qq.com', msg.as_string())
    server.quit()
    print(f'已发送 {fname} ({fsize/1024:.1f} KB)')