import os, re

# 第四轮：补全剩余 ~90 个函数
# 使用 immediate parent + basename 作为 key（如 context_parallel\\attention_cp.py）
EXTRA_4 = {
    'context_parallel\\attention_cp.py': {
        '_split_decodes_and_prefills': 'DCP 模式：把 batch 拆为 decode / prefill 子集',
        '_get_chunked_req_mask': '为 chunked prefill 请求生成 mask',
        '_build_backend_metadata': '在 DCP 路径下构造 backend metadata',
        'update_graph_params': 'DCP 模式下更新 graph 参数',
        '_forward_decode_dcp': 'DCP decode 前向内部实现',
        '_update_chunk_attn_out_lse_with_current_attn_out_lse': '用当前 chunk 输出与 lse 更新累计值',
        '_prefill_query_all_gather': 'prefill query 在 DCP 内部 all-gather',
        '_compute_prefill_context': 'prefill context 计算（DCP 路径）',
        '_load_kv_for_chunk': '为当前 chunk 加载 KV',
        '_gather_global_context_output': '把全局 context 输出 gather 起来',
        '_update_global_context_output': '用当前 chunk 更新全局 context 输出',
        'forward_impl': 'DCP attention 前向实现',
        '_finalize_pcp_metadata': '完成 PCP metadata 的填充',
        '_graph_metadata_layer_name': '返回当前 graph 的 metadata 层名',
    },
    'context_parallel\\common_cp.py': {
        'get_dcp_local_seq_lens': '读取当前 rank 的 DCP 本地序列长度',
        '__init__': 'DCP 通用 helper 初始化',
        '_require_dcp_metadata': '校验 DCP metadata 是否已就绪',
        '_get_dcp_context_lens': '获取 DCP context 长度',
        '_get_dcp_rank_context_lens': '获取当前 rank 的 DCP context 长度',
        '_dcp_all_gather': 'DCP 内部 all-gather 操作',
        '_dcp_all_gather_fragments': 'DCP 内部分片 all-gather',
        '_merge_dcp_attention_output': '合并 DCP attention 输出',
        '_process_attn_out_lse': '处理 attention 输出与 lse',
        '_npu_attention_update': '调用 NPU attention update 算子更新输出',
        '_npu_attn_out_lse_update': '调用 NPU attn out + lse update 算子',
        '_out_lse_reshape': 'reshape out 与 lse 到更新调用期望的形状',
        '_update_out_and_lse': '合并 out 与 lse 更新',
        'extract_layer_index': '从层名称中提取数字索引',
    },
    'context_parallel\\dsa_cp.py': {
        'hadamard_transform_ref': 'Hadamard 变换的参考实现（用于数值验证）',
        'rotate_activation': '对 activation 做 Hadamard 旋转',
        '__init__': 'DSA CP builder / impl 初始化',
        'get_cudagraph_support': '返回 DSA CP backend 对 CUDA graph 捕获的支持',
        'build': '构造 DSA CP attention metadata',
        'build_for_drafting': '为 draft 模型构造 DSA CP metadata',
        'build_req_metadata_for_drafting': '为 draft 模型构造请求级 DSA CP metadata',
        '_num_compressor_metadata_rows': '计算 compressor metadata 行数',
        '_ensure_device_local_metadata': '确保 device-local metadata 已分配',
        'build_req_metadata': '构造请求级 DSA CP metadata',
        '_build_local_token_metadata': '构造 local token metadata',
        '_get_cmp_seqlens_for_metadata': '取得压缩 cache 的序列长度用于 metadata',
        '_build_sas_metadata': '构造 SAS attention metadata',
        '_build_qli_metadata': '构造 QLI metadata',
        'build_for_graph_capture': '为 CUDA graph 捕获构造 mock metadata',
        '_get_layer_metadata': '取得当前层的 metadata',
        '_compute_compressor_metadata': '计算 compressor 相关 metadata',
        'process_weights_after_loading': 'DSA CP 权重加载后处理',
        '_get_tp_weight_switch_method': '取得 TP 权重切换方法（full weight switch）',
        '_enable_linear_tp_weight_switch': '为该线性层启用 TP full weight switch',
    },
    'context_parallel\\mla_cp.py': {
        '__init__': 'MLA CP builder / impl 初始化',
        'build_chunked_metadata': '为 chunked prefill 构造 MLA CP metadata',
        'build_decode_metadata': '为 decode 构造 MLA CP metadata',
        'update_graph_params': 'MLA CP 模式下更新 graph 参数',
        'get_context_seq_len_npu': '取得当前 rank 的 context seq len（NPU 张量）',
        'reorg_decode_q': 'decode Q 重组（MLA CP 路径）',
        '_forward_decode': 'MLA CP decode 前向内部实现',
        '_reorg_kvcache': 'MLA CP 模式下重组 KV cache',
    },
    'context_parallel\\sfa_cp.py': {
        '_get_sfa_kv_slot_mapping': '构造 SFA 的 KV slot_mapping',
        'exec_kv': 'SFA CP 模式下的 KV 路径入口',
        '_write_indexer_cache': '写 indexer K cache（CP 路径）',
        '__init__': 'SFA CP builder / impl 初始化',
        '_prepare_parallel_metadata': 'CP 模式下准备 parallel metadata',
        '_update_parallel_slot_mapping': 'CP 模式下更新 slot_mapping',
        '_get_fused_type_unsupported_reasons': '取得不支持 fused 类型的理由列表',
        '_parallel_query_gather_dim': '决定 parallel query gather dim',
        '_prepare_native_hidden_states': 'CP 路径下准备 native hidden states',
        '_get_parallel_forward_context': '取得当前 parallel forward context',
        '_prepare_kv_for_parallel': '准备 parallel 路径下的 KV',
        '_store_parallel_kv': '存储 parallel KV 到主 cache',
        '_enable_o_proj_tp_full_weight_switch': '为 o_proj 启用 TP full weight switch',
        '_get_o_proj_linear_method': '取得 o_proj 的 LinearMethod',
        '_apply_o_proj_full_weight': '应用 o_proj full weight（一次完成 TP 切分）',
        '_finalize_o_proj': '完成 o_proj 切分后的聚合',
        '_get_dcp_local_seq_lens': '取得 DCP 本地序列长度',
        '_get_dcp_local_block_table': '取得 DCP 本地 block table',
        '_ensure_replicated_view_buffers': '确保 replicated view 缓冲已分配',
        'process_weights_after_loading': '权重加载后 SFA CP layout cast',
    },
    'attention\\attention_v1.py': {
        'copy_blocks': '拷贝若干 KV cache block（prefix cache 等场景）',
        '_split_decodes_and_prefills': '把 batch 拆分为 decode / prefill 子集（内部 helper）',
        '_build_backend_metadata': '构造后端 metadata（内部 helper）',
        '_finalize_pcp_metadata': '完成 PCP metadata 的填充',
        '_graph_metadata_layer_name': '返回当前 graph 的 metadata 层名',
        'update_graph_params': 'DCP/PCP 模式下更新 graph 参数',
        'extract_layer_index': '从层名称中提取数字索引',
        'is_direct_target_attn_key': '判断当前 key 是否是直接目标 attention key',
    },
    'attention\\utils.py': {
        'copy_blocks': '拷贝若干 KV cache block（prefix cache 等场景）',
        '_split_decodes_and_prefills': '把 batch 拆分为 decode / prefill 子集（内部 helper）',
        '_build_backend_metadata': '构造后端 metadata（内部 helper）',
    },
    'attention\\dsa_v1.py': {
        '_get_indexer_types': '从 config 提取 indexer 类型',
        '_has_shared_indexer_layers': '判断是否有共享 indexer 层',
        '_get_config_bool': '从 config tuple 中读 bool 属性',
        '_init_hadamard': '初始化 Hadamard 旋转矩阵',
        'set_num_actual_tokens': '写入实际 token 数到 DSA metadata',
    },
    'attention\\dsa_attn_kv_plan.py': {
        'is_direct_target_attn_key': '判断当前 key 是否是直接目标 attention key',
        'get_dsa_sparse_attn_metadata_kwargs': '取得 DSA 稀疏 attention metadata 算子的 kwargs',
        'get_dsa_sparse_attn_base_kwargs': '取得 DSA 稀疏 attention 基础 kwargs',
        'add_dsa_sparse_attn_extra_kwargs': '向 kwargs 添加 DSA 稀疏 attention 专属字段',
        'get_dsa_compressor_slot_mapping_format': '取得 compressor slot_mapping 格式',
        'format_dsa_slot_mapping': '按选定格式格式化 DSA slot_mapping',
        'dsa_kv_compress_scatter': '对 DSA KV 压缩 cache 做 scatter',
        '_init_hadamard': '初始化 Hadamard 旋转矩阵',
    },
    'attention\\sfa_v1.py': {
        '_resolve_topk_indices': '解析 SFA topk 索引到物理 cache 行',
        'kv_cache_indexer_k_idx': '计算 indexer K cache 的物理 slot',
        '_compute_topk_indices': '计算 topk 索引（SFA 内部）',
        '_get_topk_indices': '取得 topk 索引',
        'prefetch_mlp': 'MLP 预取（sfa 路径）',
    },
    'attention\\mla_v1.py': {
        '__post_init__': 'MLA dataclass 后置初始化',
        'get_cudagraph_support': '返回 MLA backend 对 CUDA graph 捕获支持',
    },
    'compilation\\passes\\allgather_chunk_noop_pass.py': {
        'pattern': '返回待匹配的 all_gather + sequence_parallel_chunk 模式',
        'replacement': '返回把上述模式折叠为恒等映射的替换函数',
    },
    'compilation\\passes\\muls_add_pass.py': {
        'pattern': '返回待匹配的 x*scale + y 模式',
        'replacement': '返回替换为 muls_add 算子的函数',
        'is_applicable_for_range': '判断该 pass 是否在当前 compile_range 生效',
    },
    'compilation\\passes\\norm_quant_fusion_pass.py': {
        'pattern': '返回待匹配的 add+rms_norm+quant 模式',
        'replacement': '返回替换为 npu_add_rms_norm_quant 的函数',
        'is_applicable_for_range': '判断该 pass 是否在当前 compile_range 生效',
    },
    'compilation\\passes\\qknorm_rope_fusion_pass.py': {
        'pattern': '返回待匹配的 QK rms_norm + RoPE 模式',
        'replacement': '返回替换为 split_qkv_rmsnorm_rope 算子的函数',
        'is_applicable_for_range': '判断该 pass 是否在当前 compile_range 生效',
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
    basename_only = os.path.basename(file_name)
    # Try multiple key formats: full path, immediate parent + basename, just basename
    extra = EXTRA_4.get(file_name, {})  # full path with backslash
    if not extra:
        dirname = os.path.basename(os.path.dirname(file_name))
        composite = dirname + '\\' + basename_only
        extra = EXTRA_4.get(composite, {})
    if not extra:
        # Try also with two levels up
        dirname2 = os.path.dirname(file_name)
        if '\\' in dirname2:
            second = os.path.basename(os.path.dirname(dirname2))
            composite2 = second + '\\' + dirname + '\\' + basename_only
            extra = EXTRA_4.get(composite2, {})
    if not extra:
        extra = EXTRA_4.get(basename_only, {})

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

    new_block = func_pattern.sub(make_replacer(file_name, extra), block)
    new_html_parts.append(new_block)
    last_idx = end

new_html_parts.append(html[last_idx:])
new_html = ''.join(new_html_parts)

with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f'Round 5 replaced: {counts["replaced"]}')
print(f'Round 5 unknown: {counts["unknown"]}')
print(f'Sample still-unknown: {unknown_list[:15]}')
print(f'Total remaining placeholders:', new_html.count('(源码见对应位置:'))