import os, re

EXTRA_DESCRIPTIONS_2 = {
    'platform.py': {
        'decorator': 'config 装饰器：把方法标记为惰性属性访问的入口',
        'format': '格式化为指定字符串（工具函数）',
        'pass_key': '返回 COMPILATION_PASS_KEY（Inductor PassManager 自定义 pass key）',
        '_ensure_global_patch': '对 vllm.platform 模块做全局补丁替换（适用 RL 场景）',
        'register': 'vllm_ascend 插件入口：按顺序注册 connector、model_loader、service_profiling 等',
        'register_connector': '把自定义 KV connector 子类注册到 vllm 的 connector 注册表',
        'register_model_loader': '注册自定义 model loader（处理 HuggingFace 之外的模型加载）',
        'register_service_profiling': '在配置目录生成 service_profiling_symbols YAML',
        'register_model': '将模型架构名注册到 vLLM ModelRegistry（供 load 时查找）',
    },
    'attention_v1.py': {
        'AscendAttentionState': 'attention 状态枚举（Prefill / Decode / ChunkedPrefill 等）',
        '_generate_attn_mask': '生成 attention mask 张量（依据 prefill / decode 阶段）',
        '__init__': 'Attention 元数据 dataclass 初始化',
        'get_attn_mask': '获取当前 attention 计算所需的 mask',
        'get_splitfuse_attn_mask': '获取 SplitFuse 合并阶段所需的 attention mask',
        'get_attention_mask': '对外统一入口：按当前状态返回 attention mask',
        'AscendAttentionBackend.get_name': '返回后端名（_ASCEND）',
        'AscendAttentionBackend.get_impl_cls': '返回 AscendAttentionBackendImpl',
        'AscendAttentionBackend.get_builder_cls': '返回 AscendAttentionMetadataBuilder',
        'AscendAttentionBackend.get_kv_cache_shape': '返回 KV 缓存张量形状',
        'AscendAttentionBackend.get_supported_kernel_block_sizes': '返回支持的 block size 列表',
    },
    'mla_v1.py': {
        'supports_pcp': '返回 True 表示该 backend 支持 prefill context parallel',
    },
    'mla_v1.py': {
        'AscendMLAMBackendache.get_kv_cache_shape': '返回 MLA KV 缓存形状',
    },
    'indexer.py': {
        'AscendSFAIndexerBackend.supports_pcp': '返回 True 表示 indexer backend 支持 PCP',
    },
    'dsa_v1.py': {
        'AscendDSABackend.swap_blocks': '交换两个 block group 的内容（用于 prefix cache）',
    },
    'acl_graph.py': {
        'format': '简单格式化函数（按需）',
        '_generate_attn_mask': '（见 attention 模块）',
    },
    'cpu_binding.py': {
        'bind_cpus': '为给定 rank_id 创建 CpuAlloc 并执行完整绑定流程',
    },
}

with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'r', encoding='utf-8') as f:
    html = f.read()

counts = {'replaced': 0, 'unknown': 0}
unknown_list = []

func_pattern = re.compile(
    r'<span class="item-name">([^<]+)</span><span class="item-desc">\(源码见对应位置:([^<]+)\)</span>'
)

file_block_starts = [m.start() for m in re.finditer(r'<div class="file-block">', html)]
file_block_pattern = re.compile(r'<div class="file-name">([^<]+)</div>')

new_html_parts = []
last_idx = 0

for i, start in enumerate(file_block_starts):
    new_html_parts.append(html[last_idx:start])
    if i + 1 < len(file_block_starts):
        end = file_block_starts[i + 1]
    else:
        end = len(html)
    block = html[start:end]
    name_match = file_block_pattern.search(block)
    file_name = name_match.group(1) if name_match else ''
    basename = os.path.basename(file_name).replace('\\', '/')

    extra = EXTRA_DESCRIPTIONS_2.get(basename, {})

    def make_replacer(bn, ext_map):
        def replacer(m):
            fname = m.group(1).strip()
            desc = ext_map.get(fname, '')
            if desc:
                counts['replaced'] += 1
            else:
                counts['unknown'] += 1
                if fname not in unknown_list:
                    unknown_list.append(fname)
                desc = '(源码见对应位置:' + fname + ')'
            return '<span class="item-name">' + fname + '</span><span class="item-desc">' + desc + '</span>'
        return replacer

    new_block = func_pattern.sub(make_replacer(basename, extra), block)
    new_html_parts.append(new_block)
    last_idx = end

new_html_parts.append(html[last_idx:])
new_html = ''.join(new_html_parts)

with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f'Round 3 replaced: {counts["replaced"]}')
print(f'Round 3 unknown: {counts["unknown"]}')
print(f'Sample still-unknown: {unknown_list[:15]}')
print(f'Total remaining placeholders:', new_html.count('(源码见对应位置:'))