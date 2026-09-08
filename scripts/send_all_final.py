"""
打包所有 8 个 panorama HTML + index 并发送到邮箱
"""
import smtplib, os, zipfile
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

docs_dir = r'D:\demo\202609\vllm-ascend\code-docs'
zip_path = r'D:\demo\202609\vllm-ascend\panorama-all.zip'

pages = [
    'panorama.html',
    'panorama-root.html',
    'panorama-attention.html',
    'panorama-core.html',
    'panorama-models.html',
    'panorama-ops.html',
    'panorama-worker.html',
    'panorama-distributed.html',
    'panorama-rest.html',
]

# 打包
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in pages:
        fp = os.path.join(docs_dir, f)
        sz = os.path.getsize(fp)
        zf.write(fp, f)
        print(f'Added: {f} ({sz/1024:.1f} KB)')

zip_size = os.path.getsize(zip_path)
print(f'\nZip total: {zip_size/1024:.1f} KB')

# 发送
msg = MIMEMultipart()
msg['From'] = '18913980939@163.com'
msg['To'] = '125987347@qq.com'
msg['Subject'] = 'vLLM Ascend 全景图完整包 (8个 HTML + index)'

body_text = f"""vLLM Ascend 全景 API 文档 - 完整打包

附件：panorama-all.zip ({zip_size/1024:.1f} KB)

包内文件清单：
- panorama.html              (总览首页，链接到所有子页面)
- panorama-root.html         (根模块：平台配置、环境变量、工具类、编译器)
- panorama-attention.html    (注意力：MLA/SFA/DSA/FA3/标准、上下文并行)
- panorama-core.html         (核心：KV Cache接口、批处理调度器、动态负载均衡)
- panorama-models.html       (模型：Kimi K3、DeepSeek V4、MiniMax M3、Qwen3、Llama Eagle3)
- panorama-ops.html          (算子：Linear、LayerNorm、RoPE、MLA、GDN、融合算子)
- panorama-worker.html       (Worker：模型运行器、输入批处理、块表、编码器)
- panorama-distributed.html  (分布式：通信器、EP并行、权重传输、KV传输)
- panorama-rest.html         (其他：量化、LoRA、推测解码、补丁、310P适配)

总计：覆盖全部 530+ 源文件，约 4,500 个函数
每个函数格式：[代码行数行] 功能描述

请查收。
"""
msg.attach(MIMEText(body_text, 'plain', 'utf-8'))

with open(zip_path, 'rb') as f:
    attach = MIMEApplication(f.read(), Name='panorama-all.zip')
attach['Content-Disposition'] = 'attachment; filename="panorama-all.zip"'
msg.attach(attach)

server = smtplib.SMTP_SSL('smtp.163.com', 465)
server.login('18913980939@163.com', '<SMTP_PASSWORD>')
server.sendmail('18913980939@163.com', '125987347@qq.com', msg.as_string())
server.quit()
print(f'\n已发送 panorama-all.zip ({zip_size/1024:.1f} KB) 至 125987347@qq.com')
