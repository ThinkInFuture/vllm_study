import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
<h2>vLLM Ascend 文档优化进展</h2>
<div class="card"><div class="card-title">问题1：死链修复</div>
<div class="card-row"><span class="label">修复前死链数</span><span class="value">40</span></div>
<div class="card-row"><span class="label">修复后死链数</span><span class="value positive">0</span></div>
<div class="card-row"><span class="label">修复内容</span><span class="value">detailed 页 index/panorama 相对路径；panorama 页回首页导航</span></div>
</div>
<div class="card"><div class="card-title">问题2：假描述治理</div>
<div class="card-row"><span class="label">"见源码:xxx" 占位假描述</span><span class="value">652 条已全部清除</span></div>
<div class="card-row"><span class="label">新方案</span><span class="value positive">文件级真实讲解 + 函数仅保留名称与行数</span></div>
</div>
<div class="card"><div class="card-title">文件级讲解进度</div>
<div class="card-row"><span class="label">已完成（真实源码阅读后撰写）</span><span class="value positive">112 / 458 个文件</span></div>
<div class="card-row"><span class="label">attention / core</span><span class="value">18 + 8 全部完成</span></div>
<div class="card-row"><span class="label">worker / models / root</span><span class="value">34 + 26 + 26 全部完成</span></div>
<div class="card-row"><span class="label">待完成</span><span class="value">distributed 51、ops 111、rest 183</span></div>
</div>
<div class="card"><div class="card-title">新增：源码跳转</div>
<div class="card-row"><span class="label">每个文件名旁新增</span><span class="value positive">"查看源码" 链接，直达真实源码文件（共 397 个文件链接）</span></div>
<div class="card-row"><span class="label">panorama 索引页</span><span class="value">新增返回架构总览首页入口</span></div>
</div>
<div class="card"><div class="card-title">下一步</div>
<div class="card-row"><span class="label">计划</span><span class="value">继续完成剩余 345 个文件的讲解后，重新打包发送完整压缩包</span></div>
</div>
</body></html>"""

msg = MIMEMultipart()
msg['From'] = '18913980939@163.com'
msg['To'] = '125987347@qq.com'
msg['Subject'] = 'vLLM Ascend 文档优化进展：死链清零 + 假描述清除 + 112个文件级讲解完成'
msg.attach(MIMEText(html, 'html', 'utf-8'))

server = smtplib.SMTP_SSL('smtp.163.com', 465)
server.login('18913980939@163.com', '<SMTP_PASSWORD>')
server.sendmail('18913980939@163.com', '125987347@qq.com', msg.as_string())
server.quit()
print('progress email sent')
