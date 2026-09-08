import re
with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'r', encoding='utf-8') as f:
    c = f.read()
print('Total (功能说明) remaining:', c.count('(功能说明)'))
print('Total (源码见对应位置) remaining:', c.count('(源码见对应位置'))
# 看一个替换后的例子
m = re.search(r'item-name">set_ascend_forward_context</span><span class="item-desc">([^<]+)</span>', c)
if m:
    print('set_ascend_forward_context desc:', m.group(1)[:100])
else:
    print('Not found set_ascend_forward_context')

m = re.search(r'item-name">select_moe_comm_method</span><span class="item-desc">([^<]+)</span>', c)
if m:
    print('select_moe_comm_method desc:', m.group(1)[:100])
else:
    print('Not found select_moe_comm_method')