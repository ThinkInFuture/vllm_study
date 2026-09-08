"""
综合脚本：补全 panorama HTML 中剩余的 (参见源码:xxx) 占位符
- 使用 func_meta.json 中的真实 docstring 描述
- 为每个函数添加代码行数显示
- 保留我的手工描述优先（已存在的）
"""
import os, re, json

# 读取已构建的函数元数据
with open(r'D:\demo\202609\vllm-ascend\func_meta.json', 'r', encoding='utf-8') as f:
    META = json.load(f)

# 规范化路径 - META key 是 "relative/path.py" 用正斜杠
def normalize_path(p):
    return p.replace('\\', '/').lstrip('./')


def get_meta(file_name, fname):
    """从 META 中取 (lines, desc)"""
    candidates = [file_name, normalize_path(file_name)]
    for key in candidates:
        if key in META and fname in META[key]:
            return META[key][fname]
    # 试 basename
    bn = os.path.basename(file_name)
    if bn in META and fname in META[bn]:
        return META[bn][fname]
    return None


# 已知手工描述（保留之前写好的）
MANUAL = {
    'parse': '从 request_id 解析 #job_name[NAME]# 前缀',
    'remove': '从缓存移除一个 request_id',
    'clear': '清空全部缓存',
    'predict': '基于 EWMA 预测下一轮该 job 的 decode token 数',
    'observe': '观测真实 decode 长度，更新 EWMA',
    'get_stats': '返回该 job 的统计信息',
    '_cdiv': '整数上除法',
    'invalidate_cache': '失效 EWMA 缓存 / 失效 best-fit 缓存',
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
    'prepend_requests': '批量将请求插到队列头部（优先调度）',
    'remove_request': '移除指定请求',
    'remove_requests': '批量移除多个请求',
    'peek_request': '查看队首请求但不移除',
    'pop_request': '弹出队首请求',
    '_get_job_name': '取得请求的 job 名称',
    '_track_cold_start_req': '跟踪冷启动请求（首轮）',
    '_get_or_create_job_bucket': '获取或创建 job 桶',
    '_free_blocks': '释放请求占用的 KV block',
    '_admission_budget': '调度准入预算（最大可接纳请求数）',
    'parse': '从 request_id 解析 #job_name[NAME]# 前缀',
    'quantize': '对权重进行 W8A8 量化（PerChannel/PerTensor）',
    'matmul': 'W8A8 量化矩阵乘',
    'weight': '权重属性',
    '__getattr__': '代理属性访问到父类模块',
    'unfold_kvcache': '将 MLA KV cache 拆分为 kc 和 kpe',
    '_build_kv_cache': '构造 MLA 的 KV cache 张量',
    'get_attn_backend': '根据 vllm_config 返回 attention backend 类',
    '_forward_core': '内部前向计算（核心子层）',
    '_stable_argsort_for_npu': 'NPU 友好的稳定 argsort',
    '_treat_single_token_prefills_with_state_as_decodes': '将单 token prefill 视为 decode 路径',
    '_split_decodes_and_prefills': '把 batch 拆为 decode / prefill 子集',
    '_build_backend_metadata': '构造后端 metadata（内部 helper）',
    '_finalize_pcp_metadata': '完成 PCP metadata 的填充',
    '_graph_metadata_layer_name': '返回当前 graph 的 metadata 层名',
    'update_graph_params': 'DCP/PCP 模式下更新 graph 参数',
    'extract_layer_index': '从层名称中提取数字索引',
    'is_direct_target_attn_key': '判断当前 key 是否是直接目标 attention key',
    'full_graph_pa': 'PA 全图 forward',
    '_get_fia_params': '取得 FIA forward 参数',
    '_forward_fia_chunked_prefill_split': 'FIA chunked prefill split forward',
    'forward_fused_infer_attention': 'FIA 融合 forward',
    'forward_paged_attention': 'PA 物理 forward',
    '_forward_encoder_attention': 'encoder 阶段 attention forward',
    'get_cos_and_sin_mla': 'MLA 路径下按 positions 取 cos/sin',
    'get_cos_and_sin_dsa': 'DSA 路径下按 positions 取 cos/sin',
    'get_full_cos_and_sin_dsa': 'DSA 路径下取完整 cos/sin',
    'update_cos_sin': '更新 rotary embedding 的 cos/sin 缓存',
    'full_graph_fia': 'FIA 全图 forward',
    'full_graph_fia_v2': 'FIA 全图 forward (V2)',
    '_uses_causal_draft_attention': '是否使用因果 draft attention',
    'precompute_and_store_context_kv': '预计算并存储 context 阶段 KV',
    'get_draft_attn_causal': '取得 draft attention 是否因果',
    'embed_input_ids': '将 input_ids 嵌入为 hidden states',
    'get_embedding_tensor': '取得 embedding 权重张量',
    '_find_safetensors_weight': '在 safetensors 文件中按 key 查找权重',
    'load_quarot_target_layer': '为 quarot 加载目标层权重',
    'compute_rotation_matrix3': '计算 quarot 旋转矩阵（3 阶）',
    '_linear': '内部线性层调用',
    'combine_hidden_states': '合并 hidden states（Eagle3 等）',
    'compute_logits': '从 hidden states 计算最终 logits',
    'get_input_embeddings': '取得输入 embedding 层',
    'get_multimodal_embeddings': '取得多模态 embedding',
    'propose_draft_token_ids': '生成 draft token id（MTP/DSpark）',
    'forward': '模型前向传播入口',
    'load_weights': '加载权重到模型',
    'get_layer': '按 layer_idx 返回 layer 实例',
    'remap_mixed_gate_weights': '重映射混合 gate 权重到正确的 expert index',
    'set_dspark_aux_capture_materialized': '为 DSpark 附加捕获启用物化',
    '_apply_ascend_attn_res': '应用 Kimi 学习到的残差混合（用原生 NPU ops）',
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
    'process_weights_after_loading': '权重加载后的后处理（如 layout cast、NZ 转换）',
    'register_model': '将模型架构名注册到 vLLM ModelRegistry',
    'dsa_forward': 'DSA NPU 前向实现',
    'dsa_forward_fake': 'DSA NPU forward 的 meta/fake 实现',
    '_probe_fused_chunk': '探测 CANN fused chunk 可用性',
    '_chunk_gated_delta_rule_fused': 'fused chunk 模式 gated delta rule',
    '_split_ba_for_tp': '为 TP 切分 BA（gated delta rule 中间变量）',
    'get_state_shape': '取得 SSM 状态张量形状',
    '_warmup_prefill_kernels': 'warmup prefill 内核',
    '_warmup_prefill_kernels_v0202': 'warmup prefill 内核（v0.20.2）',
    'forward_oot': 'out-of-tree NPU forward 实现',
    'forward_impl': '前向底层实现',
    'forward_native': '原生 reference forward 实现',
    'forward_cuda': 'NPU forward（cuda dispatch key）',
    'exec_kv': 'KV 路径入口',
    'is_applicable_for_range': '判断该 pass 是否在当前 compile_range 生效',
    'pattern': '返回待匹配的模式函数',
    'replacement': '返回替换函数',
    'build': '构造 metadata',
    'build_for_graph_capture': '为 cudagraph 捕获构造 mock metadata',
    'build_for_drafting': '为 draft 模型构造 metadata',
    'reorder_batch': '按 chunked-prefill 需求重排 batch',
    'determine_chunked_prefill_workspace_size': '估算 chunked prefill workspace',
    'set_num_actual_tokens': '写入实际 token 数到 metadata',
    'init_meta_buffers': '初始化 attention 计算所需的 meta 缓冲',
    'free_meta_buffers': '释放 attention meta 缓冲',
    'use_v1': '返回是否走 v1 attention 格式',
    'get_cudagraph_support': '返回 backend 对 CUDA graph 捕获的支持程度',
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
    '__init__': '初始化类实例（绑定配置、参数、模块）',
    '__post_init__': 'dataclass 后置初始化（计算派生字段）',
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
    'apply': '对输入张量应用 Linear 计算',
    'forward_attn': '封装：调用 forward_impl 并合并输出',
    'is_empty': '返回队列是否为空',
    'add_request': '添加新请求到队列',
}


def get_description(file_name, fname):
    """获取函数描述，优先用 META 中的 docstring"""
    meta = get_meta(file_name, fname)
    if meta:
        lines, doc_desc = meta
        if doc_desc:
            return doc_desc
    # 退化到手工描述
    if fname in MANUAL:
        return MANUAL[fname]
    return ''


def get_lines(file_name, fname):
    meta = get_meta(file_name, fname)
    if meta:
        return meta[0]
    return 0


def make_desc(file_name, fname):
    desc = get_description(file_name, fname)
    lines = get_lines(file_name, fname)
    if desc and lines:
        return f'[{lines}行] {desc}'
    elif desc:
        return desc
    elif lines:
        return f'[{lines}行] 见源码:{fname}'
    else:
        return f'见源码:{fname}'


def process_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    counts = {'replaced': 0, 'unknown': 0, 'total': 0}
    unknown_list = []

    # 匹配 参见源码:xxx 占位符
    func_pattern = re.compile(
        r'<span class="item-name">([^<]+)</span><span class="item-desc">\(参见源码:([^<]+)\)</span>'
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

        def make_replacer(fn):
            def replacer(m):
                fname = m.group(1).strip()
                desc = make_desc(fn, fname)
                if desc and '(参见源码:' not in desc:
                    counts['replaced'] += 1
                else:
                    counts['unknown'] += 1
                    if fname not in unknown_list:
                        unknown_list.append(fname)
                return '<span class="item-name">' + fname + '</span><span class="item-desc">' + desc + '</span>'
            return replacer

        new_block = func_pattern.sub(make_replacer(file_name), block)
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
    print(f'  Total placeholders: {counts["total"]}')
    print(f'  Replaced with real desc: {counts["replaced"]}')
    print(f'  Unknown (no desc available): {counts["unknown"]}')
    if unknowns:
        print(f'  Sample unknown: {unknowns[:10]}')