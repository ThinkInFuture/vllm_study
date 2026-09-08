import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

files_to_send = [
    r'D:\demo\202609\vllm-ascend\panorama.html',
    r'D:\demo\202609\vllm-ascend\panorama-root.html', 
    r'D:\demo\202609\vllm-ascend\panorama-models.html'
]

for i, fpath in enumerate(files_to_send, 1):
    fname = os.path.basename(fpath)
    fsize = os.path.getsize(fpath)
    
    msg = MIMEMultipart()
    msg['From'] = '18913980939@163.com'
    msg['To'] = '125987347@qq.com'
    msg['Subject'] = f'vLLM Ascend 全景图附件 {i}/3 - {fname}'
    
    # Email body text
    body_text = f'''vLLM Ascend 全景图附件 {i}/3 封。

文件：{fname}
大小：{fsize/1024:.1f} KB

完整HTML文件已附带，请在邮件客户端查看附件。
位置：D:\\demo\\202609\\vllm-ascend\\

这是第 {i}/3 封邮件，共 3 封。
'''
    msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
    
    # Attach the HTML file
    with open(fpath, 'rb') as f:
        attach = MIMEApplication(f.read(), Name=fname)
    attach['Content-Disposition'] = f'attachment; filename="{fname}"'
    msg.attach(attach)
    
    server = smtplib.SMTP_SSL('smtp.163.com', 465)
    server.login('18913980939@163.com', '<SMTP_PASSWORD>')
    server.sendmail('18913980939@163.com', '125987347@qq.com', msg.as_string())
    server.quit()
    print(f'第 {i}/3 封邮件发送成功，附件: {fname} ({fsize/1024:.1f} KB)')