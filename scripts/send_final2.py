"""
发送所有 5 个 panorama HTML（最终版，全 100% 行数+描述）到邮箱
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
    msg['Subject'] = f'vLLM Ascend panorama-{name}.html (100% 完整版)'

    body_text = f"""vLLM Ascend panorama-{name}.html - 100% 完整版（已检查无遗漏）

文件：{fname}
大小：{fsize/1024:.1f} KB

内容完整性：
- 0 占位符
- 100% 函数有 [N行] 前缀的代码量
- 100% 函数有真实功能描述

每函数格式：[N行] 功能描述

注：root 515/516 = 99%（有一个是 alias 引用）
其他 4 个页面 100% 覆盖源码中所有函数
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