import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

files_to_send = [
    r'D:\demo\202609\vllm-ascend\panorama.html',
    r'D:\demo\202609\vllm-ascend\panorama-root.html',
    r'D:\demo\202609\vllm-ascend\panorama-models.html'
]

for i, fpath in enumerate(files_to_send, 1):
    fname = os.path.basename(fpath)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    msg = MIMEMultipart()
    msg['From'] = '18913980939@163.com'
    msg['To'] = '125987347@qq.com'
    msg['Subject'] = f'vLLM Ascend 全景图文件 {i}/3 - {fname}'
    
    fsize = os.path.getsize(fpath)
    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f2:
        first200 = ''.join(f2.readlines()[:20])
    
    body_plain = f'''vLLM Ascend 全景图文件 {i}/3 封。

文件：{fname}
大小：{fsize/1024:.1f} KB
首20行预览：{first200}

完整HTML文件请直接打开：D:\\\\demo\\\\202609\\\\vllm-ascend\\\\{fname}

---
第 {i}/3 封，共 3 封。请查收。
'''
    
    msg.attach(MIMEText(body_plain, 'plain', 'utf-8'))
    
    # 发送HTML正文 - 由于HTML文件较大，显示前2000字符，并注明完整路径
    truncated = content[:2000]
    html_body = f'''<html><head><meta charset="utf-8"></head><body>
<h2>{fname}</h2>
<pre style="white-space:pre;font-family:Consolas,monospace;padding:10px;border:1px solid #ddd;">{truncated}</pre>
<p>内容已截断，显示前2000字符。完整文件请直接打开：D:\\\\demo\\\\202609\\\\vllm-ascend\\\\{fname}</p>
</body></html>'''
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    
    server = smtplib.SMTP_SSL('smtp.163.com', 465)
    server.login('18913980939@163.com', '<SMTP_PASSWORD>')
    server.sendmail('18913980939@163.com', '125987347@qq.com', msg.as_string())
    server.quit()
    print(f'第 {i}/3 封邮件发送成功: {fname}')