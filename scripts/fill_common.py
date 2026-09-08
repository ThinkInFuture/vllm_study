import os, re

# 通用模式描述 - 用于处理大量通用的 attention backend / builder / impl / linear 等类方法
COMMON_DESCRIPTIONS = {
    # AttentionBackend 类
    'get_name': '返回后端的注册名称',
    'get_impl_cls': '返回 attention 实现类',
    'get_builder_cls': '返回 attention metadata builder 类',
    'get_kv_cache_shape': '返回 KV 缓存张量形状',
    'get_scale_shape': '返回 scale 张量形状',
    'get_supported_kernel_block_sizes': '返回支持的 kernel 块大小列表',
    'get_supported_head_sizes': '返回支持的 head 大小列表',
    'supports_pcp': '返回是否支持 prefill context parallel',
    'swap_blocks': '交换两个 block group 的内容（prefix cache）',
    'copy_blocks': '拷贝若干 KV cache block',
    'get_cudagraph_support': '返回 backend 对 CUDA graph 捕获的支持程度',
    # AttentionMetadataBuilder 类
    'build': '构造 attention metadata',
    'build_for_graph_capture': '为 cudagraph 捕获构造 mock metadata',
    'build_for_drafting': '为 draft 模型构造 metadata',
    'reorder_batch': '按 chunked-prefill 需求重排 batch',
    'determine_chunked_prefill_workspace_size': '估算 chunked prefill workspace 大小',
    'set_num_actual_tokens': '写入实际 token 数到 metadata',
    'init_meta_buffers': '初始化 attention 计算所需的 meta 缓冲',
    'free_meta_buffers': '释放 attention meta 缓冲',
    'use_v1': '返回是否走 v1 attention 格式',
    'use_v1_attn_format': '返回是否使用 v1 attention 格式',
    # AttentionImpl 类
    'forward_impl': 'attention 前向底层实现',
    'forward': 'attention 前向入口',
    'forward_attn': '封装：调用 forward_impl 并合并输出',
    'forward_oot': 'out-of-tree NPU forward 实现',
    'forward_native': '原生 reference forward 实现',
    'forward_cuda': 'NPU forward（cuda dispatch key）',
    'forward_xpu': 'NPU forward（xpu dispatch key）',
    'forward_hpu': 'NPU forward（hpu dispatch key）',
    'process_weights_after_loading': '权重加载后的后处理（如 layout cast、NZ 转换）',
    # Common
    '__init__': '初始化类实例（绑定配置、参数、模块）',
    '__post_init__': 'dataclass 后置初始化（计算派生字段）',
    # Linear 类
    'apply': '对输入张量应用 Linear 计算',
    # MLA
    'build_chunked_metadata': '为 chunked prefill 构造 MLA metadata',
    'build_prefill_metadata': '构造 MLA prefill metadata',
    'build_decode_metadata': '构造 MLA decode metadata',
    'get_block_table_size': '返回 block table 大小',
    'pad_actual_seq_len_q_mtp_enable_pad': 'MTP 启用 padding 时 pad 实际序列长度',
    'pad_actual_seq_len_q_mtp_disable_pad': 'MTP 禁用 padding 时直接使用原长度',
    # GQA base attention
    'get_attn_mask': '返回 attention mask',
    'get_splitfuse_attn_mask': '返回 SplitFuse 阶段 attention mask',
    'get_attention_mask': '统一入口返回 attention mask',
    'get_attn_state': '返回当前 attention 状态',
    'split_decodes_and_prefills': '把 batch 拆为 decode/prefill 子集',
    # 模型类
    'compute_logits': '从 hidden states 计算最终 logits',
    'get_input_embeddings': '取得输入 embedding 层',
    'get_multimodal_embeddings': '取得多模态 embedding',
    'propose_draft_token_ids': '生成 draft token id（MTP/DSpark）',
    # Fused MoE
    'forward_native': '原生 forward（reference）',
    'forward_fake': 'fake forward（meta tensor）',
    # Config
    'is_applicable_for_range': '判断该 pass 是否在当前 compile_range 生效',
    'pattern': '返回待匹配的模式函数',
    'replacement': '返回替换函数',
    # RoPE
    'update_cos_sin': '更新 rotary embedding 的 cos/sin 缓存',
    # linear
    'process_weights_after_loading': '权重加载后的后处理（layout cast、NZ 转换）',
}


# 已读取并写过的文件具体描述（之前没写够的部分）
EXTRA = {
    'attention_v1.py': {
        'get_attn_state': '返回当前 attention 状态',
    },
    'attention_mask.py': {
        '__init__': 'AttentionMaskBuilder 初始化：构造预计算表',
    },
    'dsa_attn_kv_plan.py': {
        'is_dsa_sparse_layout_supported': '判断 DSA 稀疏布局是否被硬件支持',
    },
    'gdn_attn_builder.py': {
        '__init__': '初始化 GDN metadata builder',
    },
    'gdn.py': {
        'AscendGatedDeltaNetAttention.__init__': '初始化 GatedDeltaNet impl',
    },
    'mla_v1.py': {
        'AscendMLABackend.__init__': 'MLA backend 初始化（不执行）',
        'AscendMLAMetadataBuilder.__init__': 'MLA metadata builder 初始化',
        'AscendMLAPrefillMetadata.__init__': 'MLA prefill metadata 初始化',
        'AscendMLADecodeMetadata.__init__': 'MLA decode metadata 初始化',
        'AscendMLAImpl.__init__': '初始化 AscendMLA impl',
    },
    'sfa_v1.py': {
        'AscendSFABackend.__init__': 'SFA backend 初始化',
        'AscendSFAMetadataBuilder.__init__': 'SFA metadata builder 初始化',
        'AscendSFAImpl.__init__': '初始化 AscendSFA impl',
    },
    'dsa_v1.py': {
        'AscendDSABackend.__init__': 'DSA backend 初始化',
        'AscendDSAMetadataBuilder.__init__': 'DSA metadata builder 初始化',
        'AscendDSAImpl.__init__': '初始化 AscendDSA impl',
    },
    'indexer.py': {
        'AscendSFAIndexerMetadataBuilder.__init__': 'indexer metadata builder 初始化（继承父类）',
    },
    'sfa_kv_offload.py': {
        'AscendSFAKVOffloadMetadataBuilder.__init__': '初始化 KV-offload metadata builder',
        'AscendSFAKVOffloadImpl.__init__': '初始化 KV-offload SFA impl',
    },
    'fa3_v1.py': {
        'AscendFABackend.__init__': 'FA3 backend 初始化',
    },
    'context_parallel/attention_cp.py': {
        'AscendAttentionDCPMetadataBuilder.__init__': '初始化 DCP metadata builder',
        'AscendAttentionDCPImpl.__init__': '初始化 DCP impl',
    },
    'context_parallel/dsa_cp.py': {
        'AscendDSACPMetadataBuilder.__init__': '初始化 DSA CP metadata builder',
        'AscendDSACPImpl.__init__': '初始化 DSA CP impl',
        'AscendDSAPCPMetadataBuilder.__init__': '初始化 DSA PCP metadata builder',
        'AscendDSAPCPImpl.__init__': '初始化 DSA PCP impl',
    },
    'context_parallel/mla_cp.py': {
        'AscendMlaDCPMetadataBuilder.__init__': '初始化 MLA DCP metadata builder',
        'AscendMlaDCPImpl.__init__': '初始化 MLA DCP impl',
    },
    'context_parallel/sfa_cp.py': {
        'AscendSFADCPMetadataBuilder.__init__': '初始化 SFA DCP metadata builder',
        'AscendSFADCPImpl.__init__': '初始化 SFA DCP impl',
        'AscendSFADSADCPMetadataBuilder.__init__': '初始化 SFA DSA DCP metadata builder',
        'AscendSFADSADCPImpl.__init__': '初始化 SFA DSA DCP impl',
        'AscendSFADSACPMetadataBuilder.__init__': '初始化 SFA DSA CP metadata builder',
        'AscendSFADSACPImpl.__init__': '初始化 SFA DSA CP impl',
        'AscendSFAPCPImpl.__init__': '初始化 SFA PCP impl',
    },
    'context_parallel/common_cp.py': {
        'DCPGatherContext.__init__': '初始化 DCP gather context',
    },
    # Core 补充
    'batch_job_aware_scheduler.py': {
        '__init__': '初始化：构造等待队列与 job 状态缓存',
        'parse': '从 request_id 解析 #job_name[NAME]# 前缀',
        'remove': '从缓存移除一个 request_id',
        'clear': '清空全部缓存',
        'predict': '基于 EWMA 预测下一轮该 job 的 decode token 数',
        'observe': '观测真实 decode 长度，更新 EWMA',
        'get_stats': '返回该 job 的统计信息',
        '_cdiv': '整数上除法',
        'invalidate_cache': '失效 EWMA 缓存',
        '_finalize_reserve': '完成保留块计数',
        '_compute_one': '为单个请求计算所需 KV 块数',
        '_compute_all': '为请求列表汇总所需 KV 块数',
        'put': '将请求插入等待队列',
        'peek_best_fit_request': '取出 KV 容量最匹配的请求',
        'is_empty': '返回队列是否为空',
        'add_request': '添加新请求到队列',
        'prepend_request': '将请求插到队列头部（优先调度）',
    },
    'dyntra_lb_scheduler.py': {
        '__init__': '初始化 DyntraLB 调度器',
        'schedule': 'DyntraLB 调度入口',
    },
    'profiling_chunk_predictor.py': {
        '__init__': 'ChunkSizePredictor 初始化：a/b/c 系数、目标 latency、min_chunk 等',
        'fit': '基于序列长度与延迟采样拟合二次曲线',
        'fit_chunk': '拟合 chunk 大小与延迟的关系',
        'set_target_latency': '设置目标 latency',
        'f': '曲线函数：给定长度 l，返回预测延迟',
        'get_time': '基于当前 history 长度预测耗时',
        'get_time_with_history': '带历史的预测耗时',
        'predict': '给定目标 latency 与 history，预测下一 chunk 大小',
        'predict_with_history': '带历史预测下一 chunk 大小',
        'is_ready': '模型是否已就绪',
        'history_ready': '历史是否足够',
        'predict_chunk_size': '预测下一 chunk 大小',
        'predict_time': '给定 chunk 大小预测耗时',
        'record_batch_execution_time': '记录一次 batch 的真实执行时间',
    },
    'recompute_scheduler.py': {
        'RecomputeSchedulerConfig.__init__': '初始化 recompute scheduler config',
        '__init__': '初始化调度器',
        'schedule': '调度入口',
        'update_from_output': '根据 ModelRunnerOutput 更新调度器状态',
    },
    # Models
    'kimi_k3.py': {
        '_apply_ascend_attn_res': '应用 Kimi 学习到的残差混合（用原生 NPU ops）',
    },
    # Ops
    'linear.py': {
        'AscendUnquantizedLinearMethod.forward_oot': 'NPU out-of-tree 前向（线性）',
        'AscendColumnParallelLinear.__init__': '初始化列并行 Linear',
        'AscendColumnParallelLinear.forward': '列并行 Linear 前向',
        'AscendRowParallelLinear.__init__': '初始化行并行 Linear',
        'AscendRowParallelLinear.forward': '行并行 Linear 前向',
        'AscendMergedColumnParallelLinear.__init__': '初始化合并列并行 Linear',
        'AscendMergedColumnParallelLinear.forward': '合并列并行 Linear 前向',
        'AscendQKVParallelLinear.__init__': '初始化 QKV 并行 Linear',
        'AscendQKVParallelLinear.forward': 'QKV 并行 Linear 前向',
        'AscendReplicatedLinear.__init__': '初始化复制 Linear',
        'AscendReplicatedLinear.forward': '复制 Linear 前向',
    },
    'linear_op.py': {
        'CustomLinearOp.__init__': '初始化 CustomLinearOp',
        'CustomColumnParallelOp.__init__': '初始化列并行 op',
        'CustomColumnParallelOp.apply_impl': '列并行 op 实际计算',
        'CustomRowParallelOp.__init__': '初始化行并行 op',
        'CustomRowParallelOp.apply_impl': '行并行 op 实际计算',
        'CustomReplicatedOp.__init__': '初始化复制 op',
        'CustomReplicatedOp.apply_impl': '复制 op 实际计算',
    },
    'layernorm.py': {
        'AscendRMSNorm.__init__': '初始化 RMSNorm',
        'AscendRMSNorm.forward_oot': 'NPU out-of-tree RMSNorm 前向',
        'AscendGemmaRMSNorm.__init__': '初始化 Gemma RMSNorm',
        'AscendGemmaRMSNorm.forward_oot': 'Gemma RMSNorm NPU 前向',
        'AscendRMSNormGated.__init__': '初始化 Gated RMSNorm',
        'AscendRMSNormGated.forward_oot': 'Gated RMSNorm NPU 前向',
        'AscendFusedRMSNormGated.__init__': '初始化 Fused Gated RMSNorm',
        'AscendFusedRMSNormGated.forward_oot': 'Fused Gated RMSNorm NPU 前向',
    },
    'rotary_embedding.py': {
        'set_cos_and_sin': '按模型需要分配并初始化 cos/sin 缓存',
        'get_cos_and_sin_mla': 'MLA 路径下按 positions 取 cos/sin',
        'get_cos_and_sin_dsa': 'DSA 路径下按 positions 取 cos/sin',
        'get_full_cos_and_sin_dsa': 'DSA 路径下取完整 cos/sin',
        'update_cos_sin': '更新 rotary embedding 的 cos/sin 缓存',
        'AscendRotaryEmbedding.__init__': '初始化 Ascend RotaryEmbedding',
        'AscendRotaryEmbedding.forward_oot': 'NPU out-of-tree RoPE 前向',
        'AscendMRotaryEmbedding.__init__': '初始化 Multi-modal RoPE',
        'AscendMRotaryEmbedding.forward_oot': 'M-RoPE NPU 前向',
        'AscendApplyRotaryEmb.forward_oot': 'ApplyRotaryEmb NPU 前向',
        'AscendYaRNRotaryEmbedding.__init__': '初始化 YaRN RoPE',
        'AscendYaRNRotaryEmbedding.forward_oot': 'YaRN RoPE NPU 前向',
        'AscendDeepseekScalingRotaryEmbedding.__init__': '初始化 Deepseek Scaling RoPE',
        'AscendDeepseekScalingRotaryEmbedding.forward_oot': 'Deepseek Scaling RoPE NPU 前向',
    },
    'mla.py': {
        'IndexerWrapper.__init__': '包装 vllm Indexer，删除未用的 topk_indices_buffer',
        'IndexerWrapper.forward': '占位 forward（实际权重继承自 vllm_indexer）',
        'AscendMultiHeadLatentAttention.__init__': '初始化 Ascend MLA',
        'AscendMultiHeadLatentAttention.forward': 'MLA NPU 前向',
    },
    'dsa.py': {
        'AscendDeepseekSparseAttention.__init__': '初始化 DSV4 Sparse Attention',
        'AscendDeepseekSparseAttention.forward': 'DSA NPU 前向',
    },
    'gdn.py': {
        'AscendGatedDeltaNetAttention.__init__': '初始化 GatedDeltaNet impl',
        'AscendGatedDeltaNetAttention._probe_fused_chunk': '探测 CANN fused chunk 可用性',
        'AscendGatedDeltaNetAttention.forward_impl': 'GDN 前向实现（chunk 规则）',
        'AscendGatedDeltaNetAttention.forward': 'GDN 前向入口',
    },
    'activation.py': {
        'AscendQuickGELU.forward_oot': 'NPU QuickGELU（fast_gelu）',
        'AscendSiluAndMul.forward_oot': 'NPU SwiGLU 激活',
        'AscendSiluAndMulWithClamp.forward_oot': 'NPU SwiGLU + clamp',
        'AscendSwigluOAIAndMul.swiglu_oai_forward': 'OAI 版 SwiGLU 前向',
        'AscendSwigluStepAndMul.swiglustep_forward': 'Step 版 SwiGLU 前向（带 limit）',
    },
    'register_custom_ops.py': {
        '_get_ep_local_sizes': '返回 SP token layout（仅 MoE runner 安装时）',
        '_pad_to_ep_local_size': '把 EP all-gather 输入 pad 到相同第一维',
        '_maybe_all_gather_and_maybe_unpad_impl': 'EP all-gather + 按 DP token 分布 unpad',
    },
    'conv.py': {
        'AscendConv3dLayer.__init__': '初始化 Conv3d（继承 vllm）',
        'AscendConv3dLayer.forward_oot': 'NPU 3D Conv 前向（aclnn BatchMatMulV2）',
    },
    'vocab_parallel_embedding.py': {
        'AscendVocabParallelEmbedding.__init__': '初始化 VocabParallel Embedding',
        'AscendVocabParallelEmbedding.forward': 'embedding 前向（支持 embed/lmhead TP）',
        'AscendVocabParallelEmbedding.forward_oot': 'NPU out-of-tree embedding',
        'AscendParallelLMHead.__init__': '初始化 Parallel LMHead',
        'AscendParallelLMHead.forward': 'LMHead 前向',
        'AscendLogitsProcessor.__init__': '初始化 LogitsProcessor',
        'AscendLogitsProcessor.forward': 'LogitsProcessor 前向',
    },
}


def get_desc(file_name, fname):
    """Return description for (file, func)"""
    basename = os.path.basename(file_name)
    dirname = os.path.basename(os.path.dirname(file_name))
    # Try multiple keys
    for key in [file_name, basename, f'{dirname}\\{basename}', f'{dirname}/{basename}']:
        if key in EXTRA and fname in EXTRA[key]:
            return EXTRA[key][fname]
    # Fallback to common patterns
    return COMMON_DESCRIPTIONS.get(fname, '')


def process_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    counts = {'replaced': 0, 'unknown': 0, 'total_placeholders': 0}
    unknown_list = []

    func_pattern = re.compile(
        r'<span class="item-name">([^<]+)</span><span class="item-desc">\(功能说明\)</span>'
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

        placeholders = func_pattern.findall(block)
        counts['total_placeholders'] += len(placeholders)

        def make_replacer(fn, ext):
            def replacer(m):
                fname = m.group(1).strip()
                desc = get_desc(fn, fname)
                if desc:
                    counts['replaced'] += 1
                else:
                    counts['unknown'] += 1
                    if fname not in unknown_list:
                        unknown_list.append(fname)
                    desc = '(参见源码:' + fname + ')'
                return '<span class="item-name">' + fname + '</span><span class="item-desc">' + desc + '</span>'
            return replacer

        new_block = func_pattern.sub(make_replacer(file_name, EXTRA), block)
        new_html_parts.append(new_block)
        last_idx = end

    new_html_parts.append(html[last_idx:])
    new_html = ''.join(new_html_parts)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    return counts, unknown_list


pages = [
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-attention.html', 'attention'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-core.html', 'core'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-ops.html', 'ops'),
]

for path, name in pages:
    print(f'\n=== {name} ===')
    counts, unknowns = process_html(path)
    print(f'  Total: {counts["total_placeholders"]}, Replaced: {counts["replaced"]}, Unknown: {counts["unknown"]}')
    if unknowns:
        print(f'  Sample unknown: {unknowns[:10]}')