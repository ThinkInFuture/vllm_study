import os, re

# 这个脚本会替换所有的 "(参见源码:xxx)" 为真实描述
# 策略：对每个文件，按 file-block 解析，并基于：
# 1. EXTRA 中的 file -> function 描述
# 2. COMMON_DESCRIPTIONS 中的常见函数名描述
# 3. 如果都没有，保留 "(参见源码:xxx)" 但改进文本

COMMON_DESCRIPTIONS = {
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
    'forward_impl': 'attention 前向底层实现',
    'forward': 'attention 前向入口',
    'forward_attn': '封装：调用 forward_impl 并合并输出',
    'forward_oot': 'out-of-tree NPU forward 实现',
    'forward_native': '原生 reference forward 实现',
    'forward_cuda': 'NPU forward（cuda dispatch key）',
    'forward_xpu': 'NPU forward（xpu dispatch key）',
    'forward_hpu': 'NPU forward（hpu dispatch key）',
    'process_weights_after_loading': '权重加载后的后处理（如 layout cast、NZ 转换）',
    '__init__': '初始化类实例（绑定配置、参数、模块）',
    '__post_init__': 'dataclass 后置初始化（计算派生字段）',
    'apply': '对输入张量应用 Linear 计算',
    'build_chunked_metadata': '为 chunked prefill 构造 MLA metadata',
    'build_prefill_metadata': '构造 MLA prefill metadata',
    'build_decode_metadata': '构造 MLA decode metadata',
    'get_block_table_size': '返回 block table 大小',
    'pad_actual_seq_len_q_mtp_enable_pad': 'MTP 启用 padding 时 pad 实际序列长度',
    'pad_actual_seq_len_q_mtp_disable_pad': 'MTP 禁用 padding 时直接使用原长度',
    'get_attn_mask': '返回 attention mask',
    'get_splitfuse_attn_mask': '返回 SplitFuse 阶段 attention mask',
    'get_attention_mask': '统一入口返回 attention mask',
    'get_attn_state': '返回当前 attention 状态',
    'split_decodes_and_prefills': '把 batch 拆为 decode/prefill 子集',
    'compute_logits': '从 hidden states 计算最终 logits',
    'get_input_embeddings': '取得输入 embedding 层',
    'get_multimodal_embeddings': '取得多模态 embedding',
    'propose_draft_token_ids': '生成 draft token id（MTP/DSpark）',
    'is_applicable_for_range': '判断该 pass 是否在当前 compile_range 生效',
    'pattern': '返回待匹配的模式函数',
    'replacement': '返回替换函数',
    'load_weights': '加载权重到模型',
    'impl': 'impl 实例变量',
    'layer_name': '当前层的名称',
    'kv_cache': 'kv cache 实例变量',
    'kv_cache_dtype': 'kv cache dtype',
    '_k_scale': 'K cache 缩放因子',
    '_run_self_attn': '运行 self-attention 子层',
    'forward_attn_residual': '应用 attention residual 块（Kimi 特有）',
    'is_vl_first_layer': '判断是否是 VL 的第一层',
    '_maybe_set_own_lm_head': '条件性设置自定义 lm_head',
    '_rewrite_spec_layer_name': '重写 spec 层的名称',
    '_attention_layer': 'attention 层实例',
    '_prefill_and_mix_infer': 'prefill 与混合推理入口',
    '_decode_infer': 'decode 推理入口',
    '_forward': '内部前向实现',
    '_detect_w8a8_dynamic': '检测是否 w8a8 dynamic 量化',
    '_detect_communication': '检测通信方式（allgather/all2all）',
    '_init_hadamard': '初始化 Hadamard 旋转矩阵',
    'register_dummy_fusion_op': '注册 dummy fusion op（用于占位）',
    'get_attr': '获取属性',
    'set_attr': '设置属性',
    'from_module': '从模块导入',
    'swiglu_oai_forward': 'OAI 版 SwiGLU 前向',
    'swiglustep_forward': 'Step 版 SwiGLU 前向',
    'prepare_dummy_fusion_pass': '准备 dummy 融合 pass',
}


EXTRA = {
    'kimi_k3.py': {
        'AscendKimiMoE': 'Kimi MoE 模型层（继承自 vLLM KimiMLP）',
        'AscendKimiMLAAttention': 'Kimi MLA 注意力层',
        'AscendKimiDecoderLayer': 'Kimi Decoder Layer',
        'AscendKimiLinearModel': 'Kimi 线性模型（无 MoE）',
        'AscendKimiLinearForCausalLM': 'Kimi 线性因果模型（包装 LinearModel）',
        'AscendKimiK3ForConditionalGeneration': 'Kimi K3 多模态条件生成模型',
    },
    '__init__.py': {
        'register_model': '将模型架构名注册到 vLLM ModelRegistry',
    },
    'deepseek_mtp.py': {
        'AscendDeepSeekMTP': 'DeepSeek MTP 投机解码模型',
        'AscendGlmMoeDsaForCausalLM': 'GLM MoE DSA 因果模型',
    },
    'deepseek_v4/model.py': {
        'AscendDeepseekV4ForCausalLM': 'Deepseek V4 因果 LM 入口类',
        'DeepseekV4Model': 'Deepseek V4 主模型',
        'DeepseekV4Attention': 'Deepseek V4 注意力',
        'DeepseekV2DecoderLayer': 'Deepseek V2 风格 Decoder Layer',
    },
    'deepseek_v4/mtp.py': {
        'DeepSeekV4MTP': 'Deepseek V4 MTP 模型',
        'DeepSeekMultiTokenPredictor': 'V4 多 token 预测器',
    },
    'deepseek_v4/dspark.py': {
        'DSparkDeepseekV4ForCausalLM': 'V4 DSpark 草稿模型',
        'DSparkMarkovHead': 'DSpark Markov 头',
        'DSparkConfidenceHead': 'DSpark 置信度头',
    },
    'deepseek_v4/indexer.py': {
        'AscendDeepseekV4IndexerCache': 'V4 indexer cache 描述',
        'DeepseekV4Indexer': 'V4 indexer 主体',
        'AscendIndexerOps': 'V4 indexer 算子集合',
    },
    'deepseek_v4/compressor.py': {
        'AscendCompressorStateCache': 'V4 compressor state 缓存描述',
    },
    'minimax_m3/minimax_m3.py': {
        'MiniMaxM3SparseForCausalLM': 'MiniMax M3 稀疏因果 LM',
        'MiniMaxM3MoE': 'MiniMax M3 MoE 层',
        'MiniMaxM3Attention': 'MiniMax M3 Attention 层',
        'MiniMaxM3DecoderLayer': 'MiniMax M3 Decoder Layer',
    },
    'minimax_m3/minimax_m3_vl.py': {
        'MiniMaxM3SparseForConditionalGeneration': 'MiniMax M3 多模态生成模型',
    },
    'minimax_m3/msa_m3.py': {
        'AscendMiniMaxM3IndexerBackend': 'MiniMax M3 indexer backend',
        'AscendMiniMaxM3SparseBackend': 'MiniMax M3 sparse backend',
        'AscendMiniMaxM3SparseImpl': 'MiniMax M3 sparse impl',
        'AscendMiniMaxM3QKVParallelLinearWithIndexer': 'MiniMax M3 带 indexer 的 QKV 线性',
    },
    'kimi_k3_mtp.py': {
        'AscendKimiK3MTP': 'Kimi K3 MTP 投机解码模型',
        'AscendKimiK3MultiTokenPredictor': 'Kimi K3 多 token 预测器',
    },
    'kimi_k3_dspark.py': {
        'AscendK3DSparkForCausalLM': 'Kimi K3 DSpark 草稿模型',
        'AscendK3DSparkModel': 'Kimi K3 DSpark 模型',
    },
    'qwen3_dspark.py': {
        'AscendQwen3DSparkForCausalLM': 'Qwen3 DSpark 草稿模型',
    },
    'qwen3_dflash2.py': {
        'DFlash2Qwen3ForCausalLM': 'DFlash2 Qwen3 草稿模型',
    },
    'llama_eagle3.py': {
        'AscendEagle3LlamaForCausalLM': 'Eagle3 Llama 草稿模型',
    },
    'llama_eagle3_vwn.py': {
        'Eagle3VwnLlamaForCausalLM': 'Eagle3 VWN Llama 草稿模型',
        'VwnLlamaModel': 'VWN Llama 模型',
        'VwnLlamaDecoderLayer': 'VWN Llama Decoder Layer',
    },
    'layer/attention/layer.py': {
        'DSAAttention': 'DSA 注意力层（DeepSeek V3.2 / V4）',
    },
    'kv_cache_interface.py': {
        'AscendMLAAttentionSpec': 'Ascend MLA 缓存 spec（带 layout 元数据）',
        'AscendSFAIndexerCacheSpec': 'SFA indexer 缓存 spec',
    },
    'batch_job_aware_scheduler.py': {
        'JobNameParser': '从 request_id 解析 #job_name[]# 前缀（含 LRU 缓存）',
        'JobDecodeEstimator': '基于 EWMA 的 per-job decode 长度估计器',
        'BatchJobAwareRequestQueue': '按 job 桶的请求队列（含 best-fit 搜索）',
        'BatchJobAwareScheduler': 'LPT + 容量保留的批量作业感知调度器',
        'BatchJobAwareAsyncScheduler': '异步版本的批量作业感知调度器',
    },
    'dyntra_lb_scheduler.py': {
        'DyntraLBPolicyMixin': 'DyntraLB 负载均衡策略 mixin',
        'DyntraLBScheduler': 'DyntraLB 调度器',
        'AsyncDyntraLBScheduler': '异步 DyntraLB 调度器',
    },
    'profiling_chunk_predictor.py': {
        'ChunkSizePredictor': '基于二次曲线的动态 chunk size 预测器',
    },
    'recompute_scheduler.py': {
        'RecomputeSchedulerConfig': 'Recompute scheduler 配置',
        'PreemptedRequestData': '被抢占的请求数据',
        'RecomputeReqInfo': 'Recompute 请求信息',
        'RecomputeSchedulerOutput': 'Recompute scheduler 输出',
        'RecomputeScheduler': 'Recompute scheduler（重算式调度）',
        'AsyncRecomputeScheduler': '异步 Recompute scheduler',
        'DyntraLBRecomputeScheduler': 'DyntraLB Recompute scheduler',
        'AsyncDyntraLBRecomputeScheduler': '异步 DyntraLB Recompute scheduler',
    },
    'linear.py': {
        'AscendUnquantizedLinearMethod': '非量化 Linear 算子实现',
        'AscendColumnParallelLinear': '列并行 Linear 层',
        'AscendRowParallelLinear': '行并行 Linear 层',
        'AscendMergedColumnParallelLinear': '合并列并行 Linear 层',
        'AscendQKVParallelLinear': 'QKV 并行 Linear 层',
        'AscendReplicatedLinear': '复制 Linear 层',
    },
    'linear_op.py': {
        'CustomLinearOp': '可定制通信组与 forward 的 Linear op 基类',
        'CustomColumnParallelOp': '可定制列并行 op',
        'CustomRowParallelOp': '可定制行并行 op',
        'CustomReplicatedOp': '可定制复制 op',
    },
    'layernorm.py': {
        'AscendRMSNorm': 'NPU 上 RMSNorm 实现',
        'AscendGemmaRMSNorm': 'NPU 上 Gemma RMSNorm 实现',
        'AscendRMSNormGated': 'NPU 上 Gated RMSNorm 实现',
        'AscendFusedRMSNormGated': 'NPU 上 Fused Gated RMSNorm 实现',
    },
    'rotary_embedding.py': {
        'AscendRotaryEmbedding': 'NPU 上 Rotary Embedding 实现',
        'AscendMRotaryEmbedding': 'NPU 上 Multi-modal RoPE 实现',
        'AscendApplyRotaryEmb': 'NPU 上 ApplyRotaryEmb 实现',
        'AscendYaRNRotaryEmbedding': 'NPU 上 YaRN RoPE 实现',
        'AscendDeepseekScalingRotaryEmbedding': 'NPU 上 Deepseek Scaling RoPE',
    },
    'mla.py': {
        'IndexerWrapper': 'vllm Indexer 的 wrapper（删除 topk_indices_buffer）',
        'AscendMultiHeadLatentAttention': 'Ascend MLA 实现',
    },
    'dsa.py': {
        'DSAModules': 'SFA V2 所需模块集合',
        'AscendDeepseekSparseAttention': 'DSV4 Sparse Attention 实现',
    },
    'gdn.py': {
        'AscendGatedDeltaNetAttention': 'GatedDeltaNet 注意力实现',
    },
    'activation.py': {
        'AscendQuickGELU': 'NPU 上 QuickGELU 激活',
        'AscendSiluAndMul': 'NPU 上 SwiGLU 激活',
        'AscendSiluAndMulWithClamp': 'NPU 上 SwiGLU + clamp 激活',
        'AscendSwigluOAIAndMul': 'OAI 版 SwiGLU 实现',
        'AscendSwigluStepAndMul': 'Step 版 SwiGLU 实现',
    },
    'register_custom_ops.py': {
        'register_custom_op': '注册自定义算子到 vllm',
    },
    'conv.py': {
        'AscendConv3dLayer': 'NPU 上 Conv3d 实现',
    },
    'vocab_parallel_embedding.py': {
        'AscendVocabParallelEmbedding': 'NPU 上并行 Embedding',
        'AscendParallelLMHead': 'NPU 上并行 LMHead',
        'AscendLogitsProcessor': 'NPU 上 LogitsProcessor',
    },
    'gdn_attn_builder.py': {
        'AscendGDNAttentionBackend': 'GDN 注意力 backend',
        'AscendGDNAttentionBuilder': 'GDN metadata builder',
    },
    'attention_v1.py': {
        'AscendAttentionBackend': 'NPU 基础 attention backend',
        'AscendAttentionMetadataBuilder': 'NPU 基础 attention metadata builder',
        'AscendAttentionBackendImpl': 'NPU 基础 attention impl',
    },
    'attention_mask.py': {
        'AttentionMaskBuilder': 'NPU attention mask 构造器',
    },
    'dsa_v1.py': {
        'AscendDSABackend': 'DSA 注意力 backend',
        'AscendDSAC4Backend': 'DSA C4 布局 backend',
        'AscendDSAC128Backend': 'DSA C128 布局 backend',
        'AscendDSASWABackend': 'DSA SWA 滑动窗口 backend',
        'AscendDSAC4StateBackend': 'DSA C4 状态 backend',
        'AscendDSAMetadataBuilder': 'DSA metadata builder',
        'AscendDSAImpl': 'DSA impl',
    },
    'fa3_v1.py': {
        'AscendFABackend': 'FA3 注意力 backend',
        'AscendFAImpl': 'FA3 attention impl',
    },
    'indexer.py': {
        'AscendSFAIndexerBackend': 'SFA indexer backend',
        'AscendSFAIndexerMetadataBuilder': 'SFA indexer metadata builder',
    },
    'mla_v1.py': {
        'AscendMLABackend': 'MLA 注意力 backend',
        'ChunkedContextMetadata': 'MLA chunked context 元数据',
        'AscendMLAPrefillMetadata': 'MLA prefill 元数据',
        'AscendMLADecodeMetadata': 'MLA decode 元数据',
        'AscendMLAMetadata': 'MLA 通用元数据',
        'AscendMLAPCPMetadata': 'MLA PCP 元数据',
        'AscendMLAMetadataBuilder': 'MLA metadata builder',
        'AscendMLAPCPMetadataBuilder': 'MLA PCP metadata builder',
        'AscendMLAImpl': 'MLA impl',
        'AscendMLAPCPImpl': 'MLA PCP impl',
    },
    'sfa_v1.py': {
        'AscendSFABackend': 'SFA 注意力 backend',
        'AscendSFAMetadata': 'SFA 通用元数据',
        'SFAForwardContext': 'SFA forward context',
        'AscendSFAMetadataBuilder': 'SFA metadata builder',
        'AscendSFAImpl': 'SFA impl',
    },
    'sfa_kv_offload.py': {
        'AscendSFAKVOffloadMetadataBuilder': 'SFA KV-offload metadata builder',
        'AscendSFAKVOffloadImpl': 'SFA KV-offload impl',
    },
    'context_parallel/attention_cp.py': {
        'AscendAttentionDCPMetadata': 'Attention DCP 元数据',
        'AscendAttentionDCPMetadataBuilder': 'Attention DCP metadata builder',
        'AscendAttentionDCPImpl': 'Attention DCP impl',
    },
    'context_parallel/dsa_cp.py': {
        'AscendDSACPMetadataBuilder': 'DSA CP metadata builder',
        'AscendDSACPImpl': 'DSA CP impl',
        'AscendDSAPCPMetadata': 'DSA PCP 元数据',
        'AscendDSAPCPMetadataBuilder': 'DSA PCP metadata builder',
        'AscendDSAPCPImpl': 'DSA PCP impl',
    },
    'context_parallel/mla_cp.py': {
        'DCPChunkedContextMetadata': 'DCP chunked context 元数据',
        'AscendMLADCPDecodeMetadata': 'MLA DCP decode 元数据',
        'AscendMlaDCPMetadataBuilder': 'MLA DCP metadata builder',
        'AscendMlaDCPImpl': 'MLA DCP impl',
    },
    'context_parallel/sfa_cp.py': {
        'AscendSFAPCPImpl': 'SFA PCP impl',
        'AscendSFADSACPMetadata': 'SFA DSA CP 元数据',
        'DCPGatherContext': 'DCP gather context',
        'AscendSFADCPMetadata': 'SFA DCP 元数据',
        'AscendSFADSADCPMetadata': 'SFA DSA DCP 元数据',
        'AscendSFADSACPMetadataBuilder': 'SFA DSA CP metadata builder',
        'AscendSFADSACPImpl': 'SFA DSA CP impl',
        'AscendSFADCPMetadataBuilder': 'SFA DCP metadata builder',
        'AscendSFADCPImpl': 'SFA DCP impl',
        'AscendSFADSADCPMetadataBuilder': 'SFA DSA DCP metadata builder',
        'AscendSFADSADCPImpl': 'SFA DSA DCP impl',
    },
    'context_parallel/common_cp.py': {
        'DCPGatherContext': 'DCP gather context',
    },
    'dsa_attn_kv_plan.py': {
        'get_dsa_attn_kv_plan': 'DSA KV cache 布局规划函数',
    },
}


def get_desc(file_name, fname):
    """Get description for (file, func)"""
    basename = os.path.basename(file_name)
    dirname = os.path.basename(os.path.dirname(file_name))

    # Try multiple keys for file-specific
    for key in [file_name, basename, f'{dirname}\\{basename}', f'{dirname}/{basename}']:
        if key in EXTRA and fname in EXTRA[key]:
            return EXTRA[key][fname]

    # Fallback to common
    return COMMON_DESCRIPTIONS.get(fname, '')


def process_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    counts = {'replaced': 0, 'unknown': 0, 'total': 0}
    unknown_list = []

    # Match either (功能说明) or (参见源码:xxx) placeholders
    func_pattern = re.compile(
        r'<span class="item-name">([^<]+)</span><span class="item-desc">(\(功能说明\)|\(参见源码:[^)]+\))</span>'
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
        counts['total'] += len(placeholders)

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
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-models.html', 'models'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-ops.html', 'ops'),
]

for path, name in pages:
    print(f'\n=== {name} ===')
    counts, unknowns = process_html(path)
    print(f'  Total: {counts["total"]}, Replaced: {counts["replaced"]}, Unknown: {counts["unknown"]}')
    if unknowns:
        print(f'  Sample unknown: {unknowns[:15]}')