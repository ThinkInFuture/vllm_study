import os, re

# 补全剩余描述 - 使用带子目录的完整 basename
EXTRA_3 = {
    '__init__.py': {
        '_ensure_global_patch': '应用所有 vllm_ascend 顶层全局 patch',
        'register': 'vllm_ascend 插件入口：依次注册 connector、model_loader、service_profiling',
        'register_connector': '把自定义 KV connector 子类注册到 vllm 的 connector 注册表',
        'register_model_loader': '注册自定义 model loader（处理非 HuggingFace 模型）',
        'register_service_profiling': '注册 service profiling 配置到 ~/.config/vllm_ascend/',
        'register_model': '把模型架构名注册到 vLLM ModelRegistry',
    },
    'config_utils.py': {
        'decorator': 'config 装饰器：内部包装函数，把 dataclass config 装饰为 vllm 兼容',
    },
    'logger.py': {
        'format': 'LogRecord 格式化（带 [vllm-ascend] 模块名前缀与颜色）',
    },
    'attention/attention_mask.py': {
        '_generate_attn_mask': '根据序列位置与 KV cache 长度生成 attention 掩码',
        '__init__': 'AttentionMaskBuilder 初始化（构造预计算表）',
        'get_attn_mask': '对外接口：返回 (1,1,seqlen,total_kv_len) 的 attention mask',
        'get_splitfuse_attn_mask': '返回 SplitFuse 合并阶段的 attention mask',
        'get_attention_mask': '统一入口：按当前阶段返回对应的 attention mask',
    },
    'attention/attention_v1.py': {
        'get_name': '返回后端名 ASCEND',
        'get_impl_cls': '返回 AscendAttentionBackendImpl',
        'get_builder_cls': '返回 AscendAttentionMetadataBuilder',
        'supports_pcp': '当前基础后端是否支持 PCP',
        'get_kv_cache_shape': '返回 KV 缓存张量形状',
        'get_supported_kernel_block_sizes': '返回支持的 block size 列表',
        'swap_blocks': '交换两组 KV cache 内容（prefix cache 场景）',
        '__init__': '初始化 attention metadata builder / impl',
        'reorder_batch': '按 chunked-prefill 调度需求重排 batch',
        'build': '根据 common metadata 构建 attention metadata',
        'build_for_graph_capture': '为 cudagraph 捕获阶段构造 mock metadata',
        'determine_chunked_prefill_workspace_size': '估算 chunked prefill 的 workspace 大小',
        'get_cudagraph_support': '返回对 CUDA graph 捕获的支持程度',
        'forward_impl': '底层 attention 计算实现（区分 prefill / decode）',
        'forward': 'attention 前向入口（具体后端各异）',
        'forward_attn': '封装：调用 forward_impl 并合并输出',
        'process_weights_after_loading': '权重加载后的后处理（如 layout cast）',
        'init_meta_buffers': '初始化 attention 计算所需的 meta 缓冲',
        'use_v1_attn_format': '返回是否使用 v1 attention 格式',
        'free_meta_buffers': '释放 attention meta 缓冲（sleep 时）',
    },
    'attention/dsa_attn_kv_plan.py': {
        '_supports_dsv4_compressed_cache': '判断当前硬件是否支持 DSV4 压缩 cache',
        'resolve_dsv4_cache_dtype': '依据模型 dtype 解析 DSV4 cache 实际 dtype',
        'is_a5_bf16_kv_enabled': '判断 A5 设备是否启用 BF16 KV 路径',
        'get_dsv4_attn_kv_dtype': '返回 DSV4 attention KV 的目标 dtype',
        'get_dsa_sparse_attn_metadata_op': '返回 DSA 稀疏 attention metadata 算子',
        'get_dsa_sparse_attn_op': '返回 DSA 稀疏 attention 计算算子',
        'get_dsa_attn_kv_plan': '返回当前配置对应的 DSA KV cache 布局（layout/dtype/算子）',
        'is_dsa_sparse_layout_supported': '判断 DSA 稀疏布局是否被硬件支持',
        'get_compress_ratio': '返回当前模型/层的压缩比',
        'select_dsa_kv_dtype': '根据硬件与设置选择 DSA KV dtype',
        'validate_dsa_attn_kv_plan': '校验当前 KV plan 与 vllm_config 一致性',
    },
    'attention/dsa_v1.py': {
        '_require_req_metadata': '校验 builder 是否已设置请求级 metadata',
        'get_dspark_sparse_sas_window': '计算 DSpark 稀疏 SAS 窗口大小',
        '_aligned_dspark_index_width': '返回对齐到硬件要求后的 DSpark index 宽度',
        'build_dspark_swa_indices': '构造 DSpark sliding window 索引表',
        '__init__': '初始化 AscendDSAImpl / Builder（绑定 vllm_config、layer_names、device）',
        'get_cudagraph_support': '返回对 CUDA graph 捕获的支持程度',
        'reorder_batch': 'DSA 专用 batch 重排（按 chunked-prefill 需求）',
        'build': '构造 DSA attention metadata',
        'forward_impl': 'DSA attention 前向实现',
        '_attention_compute': 'DSA 注意力计算（区分 sparse attn 与基础）',
        'init_meta_buffers': '初始化 DSA meta 缓冲',
        'use_v1': '返回是否走 v1 attention 格式',
        'free_meta_buffers': '释放 DSA meta 缓冲',
    },
    'attention/indexer.py': {
        'supports_pcp': 'indexer backend 是否支持 PCP',
    },
    'attention/mla_v1.py': {
        '__post_init__': 'MLA dataclass 后置初始化',
        '__init__': 'MLA backend 或 metadata builder 初始化',
        'determine_chunked_prefill_workspace_size': '估算 MLA chunked prefill workspace  ',
        'get_cudagraph_support': '返回 MLA backend 对 CUDA graph 捕获的支持程度',
        'reorder_batch': 'MLA 专用 batch 重排',
        'pad_actual_seq_len_q_mtp_enable_pad': 'MTP 启用 padding 时 pad 实际序列长度',
        'pad_actual_seq_len_q_mtp_disable_pad': 'MTP 禁用 padding 时直接使用原长度',
        'set_num_actual_tokens': '写入实际 token 数到 metadata',
        'build': '构造 MLA attention metadata',
        'build_chunked_metadata': '为 chunked prefill 构造 MLA metadata',
        'get_block_table_size': '返回 block table 大小',
        'build_prefill_metadata': '构造 MLA prefill metadata',
        'build_decode_metadata': '构造 MLA decode metadata',
        'build_for_graph_capture': '为 CUDA graph 捕获构造 mock MLA metadata',
        'forward_impl': 'MLA attention 前向实现',
        'forward': 'MLA attention 前向入口',
        'process_weights_after_loading': '权重加载后的 MLA layout cast',
        'init_meta_buffers': '初始化 MLA meta 缓冲',
    },
    'attention/sfa_v1.py': {
        '__init__': '初始化 AscendSFAImpl / Builder',
        '_prepare_parallel_metadata': '为 parallel 模式准备 metadata（slot_mapping、actual_seq）',
        '_update_parallel_slot_mapping': '更新 parallel slot_mapping（基于 indexer 范围）',
        'determine_chunked_prefill_workspace_size': '估算 SFA chunked prefill workspace',
        'get_cudagraph_support': '返回 SFA backend 对 CUDA graph 的支持',
        'reorder_batch': 'SFA 专用 batch 重排',
        'build': '构造 SFA attention metadata',
        'build_for_drafting': '为 draft 模型构造 SFA metadata',
        '_build_with_metadata_view': '在已有 metadata 视图上填充 SFA 专用字段',
        '_build': '底层构造 SFA metadata',
        'build_for_graph_capture': '为 CUDA graph 捕获构造 mock SFA metadata',
        'kv_cache_indexer_k_idx': '计算 indexer K 缓存的物理 slot索引',
        '_resolve_topk_indices': '解析 SFA topk_indices 逻辑索引到物理 cache 行',
        'forward_impl': 'SFA attention 前向实现',
        'forward': 'SFA attention 前向入口',
        'exec_kv': 'KV 路径入口：写主 cache + 写 indexer cache',
        'process_weights_after_loading': '权重加载后 SFA layout cast',
        'init_meta_buffers': '初始化 SFA meta 缓冲',
    },
    'attention/utils.py': {
        'using_paged_attention': '判断是否使用 paged attention（非 paged 时改走 FIA）',
        'enable_dcp': '判断当前配置是否启用 decode context parallel',
        'enable_pcp': '判断当前配置是否启用 prefill context parallel',
        'unpadded': 'dataclass 字段：原始（未对齐）KV cache长度',
        '_slice_reqs': '按请求 id 切片 metadata（dump_profile 等调试用）',
        'filter_chunked_req_indices': '过滤掉处于 chunked prefill 阶段的请求索引',
        'split_decodes_and_prefills': '把请求 batch 拆为 decode / prefill 子集',
        'wait_for_kv_layer_from_connector': '从 KV connector 等待指定层的 KV',
        'maybe_save_kv_layer_to_connector': '如需 offloading，把层 KV 提交给 connector',
        'notify_kv_cache_written': '通知 connector 当前层 cache 已写入',
        'round_up': '向上取整到对齐单位',
        'trans_rope_weight': '把 RoPE 权重从 (B,A) 转 (A,B) 存储布局',
        'enable_mlapo': '判断是否走 MLAPO 路径（MLA + A2/A3 满足条件下）',
    },
    'attention/context_parallel/attention_cp.py': {
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
    },
    'attention/context_parallel/common_cp.py': {
        'get_dcp_local_seq_lens': '读取当前 rank 的 DCP 本地序列长度',
        '__init__': 'DCP 通用 helper 初始化',
        '_require_dcp_metadata': '校验 DCP metadata 是否已就绪',
        '_get_dcp_context_lens': '获取 DCP context 长度',
        '_get_dcp_rank_context_lens': '获取当前 rank 的 DCP context 长度',
        '_dcp_all_gather': 'DCP 内部 all-gather 操作',
        '_dcp_all_gather_fragments': 'DCP 内部分片 all-gather',
        '_merge_dcp_attention_output': '合并 DCP attention 输出',
        '_process_attn_out_lse': '处理 attention 输出与 lse',
        '_npu_attention_update': '调用NPU attention update 算子更新输出',
        '_npu_attn_out_lse_update': '调用NPU attn out + lse update 算子',
        '_out_lse_reshape': 'reshape out 与 lse 到更新调用期望的形状',
        '_update_out_and_lse': '合并 out 与 lse 更新',
    },
    'attention/context_parallel/dsa_cp.py': {
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
        'process_weights_after_loading': '权重加载后的 layout cast',
        '_get_tp_weight_switch_method': '取得 TP 权重切换方法（full weight switch）',
        '_enable_linear_tp_weight_switch': '为该线性层启用 TP full weight switch',
        'forward_impl': 'DSA CP attention 前向实现',
        'init_meta_buffers': '初始化 DSA CP meta 缓冲',
    },
    'attention/context_parallel/mla_cp.py': {
        '__init__': 'MLA CP builder / impl 初始化',
        'build_chunked_metadata': '为 chunked prefill 构造 MLA CP metadata',
        'build_decode_metadata': '为 decode 构造 MLA CP metadata',
        'update_graph_params': 'MLA CP 模式下更新 graph 参数',
        'get_context_seq_len_npu': '取得当前 rank 的 context seq len（NPU 张量）',
        'reorg_decode_q': 'decode Q 重组（MLA CP 路径）',
        '_forward_decode': 'MLA CP decode 前向内部实现',
        '_reorg_kvcache': 'MLA CP 模式下重组 KV cache',
    },
    'attention/context_parallel/sfa_cp.py': {
        '_get_sfa_kv_slot_mapping': '构造 SFA 的 KV slot_mapping',
        'exec_kv': 'SFA CP 模式下的 KV 路径入口',
        '_write_indexer_cache': '写 indexer K cache（CP 路径）',
        '__init__': 'SFA CP builder / impl 初始化',
        '_prepare_parallel_metadata': 'CP 模式下准备 parallel metadata',
        '_update_parallel_slot_mapping': 'CP 模式下更新 slot_mapping',
        'process_weights_after_loading': '权重加载后 layout cast',
        '_get_fused_type_unsunsupported_reasons': '取得不支持 fused 类型的理由列表',
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
        '_get_dcp_local_block_table': '取得 DCP 本地 block table  ',
        '_ensure_replicated_view_buffers': '确保 replicated view 缓冲已分配',
    },
    'compilation/compiler_interface.py': {
        'compile_inner': '实际执行当前 PassManager 并返回 graph（fusion_pass_compile 内部 helper）',
    },
    'compilation/passes/allgather_chunk_noop_pass.py': {
        'pattern': '返回待匹配的 all_gather + sequence_parallel_chunk 模式',
        'replacement': '返回把上述模式折叠为恒等映射的替换函数',
    },
    'compilation/passes/muls_add_pass.py': {
        'pattern': '返回待匹配的 x*scale + y 模式',
        'replacement': '返回替换为 muls_add 算子的函数',
        'is_applicable_for_range': '判断该 pass 是否在当前 compile_range 生效',
    },
    'compilation/passes/norm_quant_fusion_pass.py': {
        'pattern': '返回待匹配的 add+rms_norm+quant 模式',
        'replacement': '返回替换为 npu_add_rms_norm_quant 的函数',
        'is_applicable_for_range': '判断该 pass 是否在当前 compile_range 生效',
    },
    'compilation/passes/qknorm_rope_fusion_pass.py': {
        'pattern': '返回待匹配的 QK rms_norm + RoPE 模式',
        'replacement': '返回替换为 split_qkv_rmsnorm_rope 算子的函数',
        'is_applicable_for_range': '判断该 pass 是否在当前 compile_range 生效',
    },
    'core/dyntra_lb_scheduler.py': {
        '__init__': 'DyntraLBScheduler 初始化（继承 AsyncScheduler + DyntraLBPolicyMixin）',
    },
    'core/kv_cache_interface.py': {
        '__post_init__': 'AscendMLAAttentionSpec 后置初始化（计算派生字段）',
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
    # 转 basename（包含子目录）
    basename = file_name.replace('\\', '/').split('/')[-2] + '/' + os.path.basename(file_name) if '/' in file_name.replace('\\', '/') else os.path.basename(file_name)
    # 如果 basename 在 EXTRA_3 里找不到，尝试纯文件名
    if basename not in EXTRA_3:
        basename = os.path.basename(file_name)

    extra = EXTRA_3.get(basename, {})

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

print(f'Round 4 replaced: {counts["replaced"]}')
print(f'Round 4 unknown: {counts["unknown"]}')
print(f'Sample still-unknown: {unknown_list[:15]}')
print(f'Total remaining placeholders:', new_html.count('(源码见对应位置:'))