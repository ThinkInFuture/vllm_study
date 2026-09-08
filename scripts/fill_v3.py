import os, re

# 继续在 EXTRA 中添加更多细节
EXTRA = {
    'kimi_k3.py': {
        '_apply_ascend_attn_res': '应用 Kimi 学习到的残差混合（用原生 NPU ops）',
        'get_layer': '按 layer_idx 返回 layer 实例',
        'embed_input_ids': '将 input_ids 嵌入为 hidden states',
        'get_embedding_tensor': '取得 embedding 权重张量',
        'remap_mixed_gate_weights': '重映射混合 gate 权重到正确的 expert index',
        'set_dspark_aux_capture_materialized': '为 DSpark 附加捕获启用物化',
        '_uses_causal_draft_attention': '是否使用因果 draft attention',
        'precompute_and_store_context_kv': '预计算并存储 context 阶段 KV',
        'get_draft_attn_causal': '取得 draft attention 是否因果',
        '_find_safetensors_weight': '在 safetensors 文件中按 key 查找权重',
        'load_quarot_target_layer': '为 quarot 加载目标层权重',
        'compute_rotation_matrix3': '计算 quarot 旋转矩阵（3 阶）',
        '_linear': '内部线性层调用',
        'combine_hidden_states': '合并 hidden states（Eagle3 等）',
    },
    'linear.py': {
        'quantize': '对权重进行 W8A8 量化',
        'matmul': 'W8A8 量化矩阵乘',
        'weight': '权重属性',
        'process_weights_after_loading': '权重加载后的后处理（layout cast、NZ 转换）',
        'create_weights': '创建权重参数（初始化）',
        'apply': '对输入张量应用 Linear 计算',
    },
    'mla.py': {
        '__getattr__': '代理属性访问到父类 MLA 模块',
        'unfold_kvcache': '将 MLA KV cache 拆分为 kc 和 kpe',
        '_build_kv_cache': '构造 MLA 的 KV cache 张量',
        'forward_oot': 'NPU out-of-tree 前向',
    },
    'dsa.py': {
        'dsa_forward': 'DSA NPU 前向实现',
        'dsa_forward_fake': 'DSA NPU forward 的 meta/fake 实现',
        'forward_oot': 'NPU out-of-tree 前向',
    },
    'gdn.py': {
        '_probe_fused_chunk': '探测 CANN fused chunk 可用性',
        '_chunk_gated_delta_rule_fused': 'fused chunk 模式 gated delta rule',
        'forward_impl': 'GDN 前向实现',
        'forward': 'GDN 前向入口',
        '_split_ba_for_tp': '为 TP 切分 BA（gated delta rule 中间变量）',
        'get_state_shape': '取得 SSM 状态张量形状',
        '_warmup_prefill_kernels': 'warmup prefill 内核',
        '_warmup_prefill_kernels_v0202': 'warmup prefill 内核（v0.20.2）',
    },
    'rotary_embedding.py': {
        'get_cos_and_sin_mla': 'MLA 路径下按 positions 取 cos/sin',
        'get_cos_and_sin_dsa': 'DSA 路径下按 positions 取 cos/sin',
        'get_full_cos_and_sin_dsa': 'DSA 路径下取完整 cos/sin',
        'update_cos_sin': '更新 rotary embedding 的 cos/sin 缓存',
    },
    'mla_v1.py': {
        'full_graph_fia': 'FIA 全图 forward',
        'full_graph_fia_v2': 'FIA 全图 forward (V2)',
        'full_graph_pa': 'PA 全图 forward',
        '_get_fia_params': '取得 FIA forward 参数',
        'forward_fused_infer_attention': 'FIA 融合 forward',
        '_forward_fia_chunked_prefill_split': 'FIA chunked prefill split forward',
        'forward_paged_attention': 'PA 物理 forward',
        '_forward_encoder_attention': 'encoder 阶段 attention forward',
    },
    'attention_v1.py': {
        'forward_fused_infer_attention': 'FIA 融合 forward',
        'forward_paged_attention': 'PA 物理 forward',
        'full_graph_fia': 'FIA 全图 forward',
        'full_graph_fia_v2': 'FIA 全图 forward (V2)',
    },
    # Batch Job Aware Scheduler 补充
    'batch_job_aware_scheduler.py': {
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
        '__len__': '返回队列长度',
        '__bool__': '返回队列是否非空',
        '__iter__': '迭代队列',
        'invalidate_cache': '失效 best-fit 缓存',
    },
    # Recompute Scheduler 补充
    'recompute_scheduler.py': {
        'schedule': '调度入口',
        'update_from_output': '根据 ModelRunnerOutput 更新调度器状态',
        '_initialize_from_config': '从配置初始化调度器',
    },
    # Dyntra LB
    'dyntra_lb_scheduler.py': {
        'schedule': '调度入口',
        'is_schedulable_waiting': '判断请求是否处于可调度等待态',
        'req_blk_num': '计算请求占用的 KV 块数',
    },
    # Core utility
    'core/utils.py': {
        'predict_chunk_size': '预测下一 chunk 大小',
        'fit': '拟合二次曲线',
    },
    # DSpark
    'deepseek_v4/dspark.py': {
        'forward': '前向传播',
        'compute_logits': '计算 logits',
        'get_input_embeddings': '取得输入 embedding',
    },
    # DeepSeek V4 common
    'deepseek_v4/model.py': {
        'compute_logits': '计算 logits',
        'get_input_embeddings': '取得输入 embedding',
        'forward': '前向传播',
    },
    'deepseek_v4/mtp.py': {
        'propose_draft_token_ids': '生成 draft token id',
        'forward': '前向传播',
    },
    'deepseek_v4/indexer.py': {
        'forward': '前向传播',
    },
    'deepseek_v4/compressor.py': {
        'get_storage_block_size': '取得物理块大小',
    },
    'minimax_m3/minimax_m3.py': {
        'compute_logits': '计算 logits',
        'get_input_embeddings': '取得输入 embedding',
        'forward': '前向传播',
    },
    'minimax_m3/minimax_m3_vl.py': {
        'forward': '多模态前向',
        'get_multimodal_embeddings': '取得多模态 embedding',
    },
    'minimax_m3/msa_m3.py': {
        'forward': '前向传播',
    },
    'kimi_k3_mtp.py': {
        'forward': 'MTP 前向传播',
    },
    'kimi_k3_dspark.py': {
        'forward': 'DSpark 前向',
    },
    'qwen3_dspark.py': {
        'forward': 'Qwen3 DSpark 前向',
    },
    'qwen3_dflash2.py': {
        'forward': 'DFlash2 前向',
    },
    'llama_eagle3.py': {
        'forward': 'Eagle3 前向',
    },
    'llama_eagle3_vwn.py': {
        'forward': 'Eagle3 Vwn 前向',
    },
    'layer/attention/layer.py': {
        'get_dsv4_block_sizes': '返回 DSV4 注意力层 block size 配置',
    },
    'gdn_attn_builder.py': {
        'build': '构造 GDN metadata',
        'build_for_graph_capture': '为 cudagraph 捕获构造 mock',
    },
    'mla.py': {
        'forward_native': '原生 reference forward',
    },
    'rotary_embedding.py': {
        'forward_cuda': 'NPU forward（cuda dispatch key）',
    },
    'context_parallel/attention_cp.py': {
        'forward_impl': 'DCP attention 前向实现',
        'update_graph_params': 'DCP 模式下更新 graph 参数',
    },
    'context_parallel/dsa_cp.py': {
        'forward_impl': 'DSA CP attention 前向实现',
        'build': '构造 DSA CP attention metadata',
    },
    'context_parallel/mla_cp.py': {
        'forward_impl': 'MLA DCP forward 实现',
    },
    'context_parallel/sfa_cp.py': {
        'forward_impl': 'SFA CP forward 实现',
        'exec_kv': 'SFA CP KV 路径入口',
    },
}


def get_desc(file_name, fname):
    basename = os.path.basename(file_name)
    dirname = os.path.basename(os.path.dirname(file_name))
    for key in [file_name, basename, f'{dirname}\\{basename}', f'{dirname}/{basename}']:
        if key in EXTRA and fname in EXTRA[key]:
            return EXTRA[key][fname]
    return ''


def process_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    counts = {'replaced': 0, 'unknown': 0, 'total': 0}
    unknown_list = []

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
        print(f'  Sample unknown: {unknowns[:10]}')