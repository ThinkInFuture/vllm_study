import os, re

# 综合脚本：处理 attention, core, models, ops 四个 panorama 页面
# 基于已读取的源码撰写真实中文功能描述

DESCRIPTIONS = {
    # ==================== attention ====================
    'dsa_v1.py': {
        'dsa_kv_compress_scatter': '对 DSA KV 压缩 cache 做 scatter',
        'format_dsa_slot_mapping': '按选定格式格式化 DSA slot_mapping',
        'get_dsa_compressor_slot_mapping_format': '取得 compressor slot_mapping 格式',
        'add_dsa_sparse_attn_extra_kwargs': '向 kwargs 添加 DSA 稀疏 attention 专属字段',
        'get_dsa_sparse_attn_base_kwargs': '取得 DSA 稀疏 attention 基础 kwargs',
        'get_dsa_sparse_attn_metadata_kwargs': '取得 DSA 稀疏 attention metadata 算子的 kwargs',
        'is_direct_target_attn_key': '判断当前 key 是否是直接目标 attention key',
        'get_dsa_attn_kv_plan': '返回当前配置对应的 DSA KV cache 布局（layout/dtype/算子）',
        'is_dsa_sparse_layout_supported': '判断 DSA 稀疏布局是否被硬件支持',
        'get_compress_ratio': '返回当前模型/层的压缩比',
        'select_dsa_kv_dtype': '根据硬件与设置选择 DSA KV dtype',
        'validate_dsa_attn_kv_plan': '校验当前 KV plan 与 vllm_config 一致性',
        '_init_hadamard': '初始化 Hadamard 旋转矩阵',
        'get_dspark_sparse_sas_window': '计算 DSpark 稀疏 SAS 窗口大小',
        '_aligned_dspark_index_width': '返回对齐到硬件要求后的 DSpark index 宽度',
        'build_dspark_swa_indices': '构造 DSpark sliding window 索引表',
        '_require_req_metadata': '校验 builder 是否已设置请求级 metadata',
        '_is_w8a8_dynamic': '判断线性层是否使用 AscendW8A8Dynamic 量化方法',
        '_has_weight_scale': '判断线性层是否携带 weight_scale 张量',
        '_dsa_layout_kv': '返回当前 VllmConfig 对应的 KV cache 布局字符串',
        '_dsa_swa_only_cmp_ratio': 'BF16 SWA-only 场景下返回 0，否则保留主模型的压缩比',
        'dsv4_dsa_overlap_stream': '获取 DSV4 与 DSA 重叠计算用的 NPU 流（懒初始化）',
        'AscendDSABackend.get_name': "返回 'ASCEND_DSA'",
        'AscendDSABackend.get_builder_cls': '根据 DSA-CP/PCP 标志返回 metadata builder 类',
        'AscendDSABackend.get_kv_cache_shape': '返回 KV 缓存张量形状',
        'AscendDSABackend.get_scale_shape': '返回 scale 张量形状',
        'AscendDSABackend.get_impl_cls': '返回 attention 实现类',
        'AscendDSABackend.get_supported_kernel_block_sizes': '返回支持的 kernel 块大小',
        'AscendDSABackend.swap_blocks': '交换两组 KV cache 内容（prefix cache）',
        'AscendDSAC4Backend.get_name': "返回 'ASCEND_DSA_C4'",
        'AscendDSAC4Backend.get_supported_kernel_block_sizes': '返回 C4 物理页对应的逻辑块大小',
        'AscendDSAC128Backend.get_name': "返回 'ASCEND_DSA_C128'",
        'AscendDSAC128Backend.get_supported_kernel_block_sizes': '返回 C128 物理页对应的逻辑块大小',
        'AscendDSASWABackend.get_name': "返回 'ASCEND_DSA_SWA'",
        'AscendDSASWABackend.get_supported_kernel_block_sizes': '返回 SWA 支持的块大小',
        'AscendDSAC4StateBackend.get_name': "返回 'ASCEND_DSA_C4_STATE'",
        'AscendDSAC4StateBackend.get_supported_kernel_block_sizes': '返回 C4 STATE 块大小',
        '__init__': '初始化类实例（绑定 vllm_config、layer_names、device）',
        'get_cudagraph_support': '返回 backend 对 CUDA graph 捕获的支持程度',
        'reorder_batch': 'DSA 专用 batch 重排',
        'build': '构造 attention metadata',
        'build_for_drafting': '为 draft 模型构造 metadata',
        'build_for_graph_capture': '为 CUDA graph 捕获构造 mock metadata',
        'forward_impl': 'attention 前向实现',
        'forward': 'attention 前向入口',
        'forward_attn': '封装：调用 forward_impl 并合并输出',
        'process_weights_after_loading': '权重加载后的后处理',
        'init_meta_buffers': '初始化 attention meta 缓冲',
        'use_v1': '返回是否走 v1 attention 格式',
        'free_meta_buffers': '释放 attention meta 缓冲',
        '_attention_compute': 'DSA 注意力内部计算',
    },
    'fa3_v1.py': {
        '__init__': '初始化 AscendFAImpl（校验参数）',
        '_flash_attn_with_kvcache': '调用 flash_attn_npu_v3 的 flash_attn_with_kvcache',
        'forward_impl': '执行 attention 前向（区分 decode/prefill）',
        'AscendFABackend.get_name': "返回 'CUSTOM'",
        'AscendFABackend.get_impl_cls': '返回 AscendFAImpl',
        'AscendFABackend.get_builder_cls': '返回 AscendAttentionMetadataBuilder',
        'AscendFABackend.get_kv_cache_shape': '返回 KV 缓存张量形状 (2, num_blocks, ...)',
        'AscendFABackend.get_supported_kernel_block_sizes': '返回 [128]',
    },
    'indexer.py': {
        'AscendSFAIndexerBackend.get_name': "返回 'ASCEND_SFA_INDEXER'",
        'AscendSFAIndexerBackend.get_impl_cls': '占位实现，返回 None',
        'AscendSFAIndexerBackend.get_builder_cls': '返回 AscendSFAIndexerMetadataBuilder',
        'AscendSFAIndexerBackend.get_kv_cache_shape': '返回 indexer 缓存张量形状',
        'AscendSFAIndexerBackend.get_supported_kernel_block_sizes': '返回 [128]',
        'AscendSFAIndexerBackend.supports_pcp': '返回 True（indexer backend 支持 PCP）',
        'AscendSFAIndexerMetadataBuilder.__init__': '初始化：直接走父类构造',
        'AscendSFAIndexerMetadataBuilder.get_cudagraph_support': '返回支持 CUDA graph 捕获 (UNIFORM_BATCH)',
        'AscendSFAIndexerMetadataBuilder.build': '缓存专用 builder：不构建任何 metadata 直接返回 None',
        '__init__': '初始化元数据构建器',
        'get_cudagraph_support': '返回 backend 对 CUDA graph 捕获的支持程度',
        'build': '构造 attention metadata',
    },
    'mla_v1.py': {
        '__init__': '初始化 MLA backend 或 metadata builder',
        '__post_init__': 'MLA dataclass 后置初始化',
        'get_cudagraph_support': '返回 MLA backend 对 CUDA graph 捕获支持',
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
        '_npu_mla_prolog_v3_no_rope': '调用 AscendC MLA prolog（v3）算子，可省略 RoPE 入参',
        'AscendMLABackend.get_name': "返回 'ASCEND_MLA'",
        'AscendMLABackend.get_builder_cls': '根据 DCP/PCP 标志返回对应的 MLA builder',
        'AscendMLABackend.get_kv_cache_shape': '返回 MLA KV 缓存张量形状',
        'AscendMLABackend.get_impl_cls': '返回 MLA 实现类',
        'AscendMLABackend.get_supported_kernel_block_sizes': '返回 [128]',
    },
    'sfa_kv_offload.py': {
        '_check_device_kv_cache_exist': '检查当前 prefill/mixed 批次是否需要 keep_device_kv_cache',
        'AscendSFAKVOffloadMetadataBuilder.__init__': '初始化：判断是否 PD-decode 消费端',
        'AscendSFAKVOffloadMetadataBuilder._populate_offload_metadata': '填充 offload 专用 metadata',
        'AscendSFAKVOffloadMetadataBuilder.build': '调用父类 build 后填充 offload 专用 metadata',
        'AscendSFAKVOffloadMetadataBuilder.build_for_drafting': '为 draft 模式填充 offload metadata',
        'AscendSFAKVOffloadImpl.__init__': '初始化：禁止 DSA-CP 与 sparse_sfa_c8',
        'AscendSFAKVOffloadImpl._resolve_preprocess_type': '强制使用 native 预处理路径',
        'AscendSFAKVOffloadImpl._cpu_cache_pair': '返回该层的 CPU 端 K/V cache 对',
        'AscendSFAKVOffloadImpl._resident_views': '返回该层 topk 驻留视图',
        'AscendSFAKVOffloadImpl._offload_layer_name': '取得该层在 offload manager 中的逻辑层名',
        'AscendSFAKVOffloadImpl._is_decode_only': '判断该层 forward 阶段是否只做 decode',
        'AscendSFAKVOffloadImpl._pad_to_input_tokens': '将 token 数 padding 到 input_tokens',
        'AscendSFAKVOffloadImpl._in_graph_runtime': '判断是否在 ACL 图 运行时内',
        'AscendSFAKVOffloadImpl.forward': '路由 forward：decode 时只走 offload 路径',
        'AscendSFAKVOffloadImpl._compute_kv_only': '仅计算当前 token 的 K/V',
        'AscendSFAKVOffloadImpl.exec_kv': 'KV 路径入口：prefill 写主 cache 后 D2H 提交',
        'AscendSFAKVOffloadImpl._execute_sparse_flash_attention_process': '执行 sparse flash attention 主计算',
        '__init__': '初始化类实例',
        'build': '构造 metadata',
        'build_for_drafting': '为 draft 模式构造 metadata',
        'forward': '前向计算',
        'exec_kv': 'KV 路径入口',
    },
    'sfa_v1.py': {
        '__init__': '初始化 AscendSFAImpl / Builder',
        '_prepare_parallel_metadata': '为 parallel 模式准备 metadata',
        '_update_parallel_slot_mapping': '更新 parallel slot_mapping（基于 indexer 范围）',
        'determine_chunked_prefill_workspace_size': '估算 SFA chunked prefill workspace',
        'get_cudagraph_support': '返回 SFA backend 对 CUDA graph 的支持',
        'reorder_batch': 'SFA 专用 batch 重排',
        'build': '构造 SFA attention metadata',
        'build_for_drafting': '为 draft 模型构造 SFA metadata',
        '_build_with_metadata_view': '在已有 metadata 视图上填充 SFA 专用字段',
        '_build': '底层构造 SFA metadata',
        'build_for_graph_capture': '为 CUDA graph 捕获构造 mock SFA metadata',
        'kv_cache_indexer_k_idx': '计算 indexer K 缓存的物理 slot 索引',
        '_resolve_topk_indices': '解析 SFA topk 索引到物理 cache 行',
        '_get_indexer_types': '从 config tuple 提取 indexer_types 字段',
        '_has_shared_indexer_layers': '判断是否有 shared 类型的 indexer 层',
        '_get_config_bool': '从 config tuple 中按顺序读取 bool 属性',
        'forward_impl': 'SFA attention 前向实现',
        'forward': 'SFA attention 前向入口',
        'exec_kv': 'KV 路径入口',
        'process_weights_after_loading': '权重加载后 SFA layout cast',
        'init_meta_buffers': '初始化 SFA meta 缓冲',
        '_compute_topk_indices': '计算 topk 索引（SFA 内部）',
        '_get_topk_indices': '取得 topk 索引',
        'prefetch_mlp': 'MLP 预取（sfa 路径）',
        'AscendSFABackend.get_name': "返回 'ASCEND_SFA'",
        'AscendSFABackend.get_builder_cls': '根据是否启用 sparse_kv_offload 返回对应 builder',
        'AscendSFABackend.get_kv_cache_shape': '返回 SFA KV 缓存形状',
        'AscendSFABackend.get_impl_cls': '返回 AscendSFAImpl 或其 KV-offload 变体',
        'AscendSFABackend.get_supported_kernel_block_sizes': '返回 [128]',
    },
    'sparse_flash_mla.py': {
        '_get_sparse_flash_mla_ops': '懒加载 SparseFlashMla 算子',
        '_add_compressed_kv_lengths': '为 kwargs 添加压缩 KV 长度信息',
        'sparse_flash_mla_metadata': '将 DSA metadata 适配到 SparseFlashMla BF16 KV',
        'sparse_flash_mla': '将 DSA attention 适配到 SparseFlashMla BF16 KV 并执行',
    },
    'utils.py': {
        'get_or_register_attention_buffer': '注册跨 attention 层共享的非-persistent 缓冲',
        'build_valid_topk_mask': '生成 top-k 行中的合法位置掩码',
        'get_sfa_qsfa_packed_head_dim': '计算 SFA/QSFA packed KV 缓存的 head_dim 字节数',
        'PagedAttentionGraphParam.__iter__': '解包 params 元组为可迭代子',
        'update_paged_attention_graph_param': '更新 ACL graph 中 PA 参数',
        'cache_graph_workspace': '按 graph 大小缓存 FIA workspace 张量',
        'needs_layer_aware_fia_graph_replay': '是否需要逐层感知的 FIA 图 replay',
        'ascend_chunked_prefill_workspace_size': '计算 chunked prefill 所需的 workspace',
        'using_paged_attention': '判断是否使用 paged attention',
        'enable_dcp': '判断当前配置是否启用 decode context parallel',
        'enable_pcp': '判断当前配置是否启用 prefill context parallel',
        'unpadded': 'dataclass 字段：原始未对齐 KV 长度',
        '_slice_reqs': '按请求 id 切片 metadata',
        'filter_chunked_req_indices': '过滤 chunked prefill 阶段请求索引',
        'split_decodes_and_prefills': '把请求 batch 拆为 decode / prefill 子集',
        'wait_for_kv_layer_from_connector': '从 KV connector 等待指定层 KV',
        'maybe_save_kv_layer_to_connector': '如需 offloading，把层 KV 提交给 connector',
        'notify_kv_cache_written': '通知 connector 当前层 cache 已写入',
        'round_up': '向上取整到对齐单位',
        'trans_rope_weight': '把 RoPE 权重从 (B,A) 转 (A,B) 存储布局',
        'enable_mlapo': '判断是否走 MLAPO 路径',
        'copy_blocks': '拷贝若干 KV cache block',
    },
    'attention_v1.py': {
        'AscendAttentionState': 'attention 状态枚举（Prefill/Decode/ChunkedPrefill 等）',
        '_generate_attn_mask': '生成 attention mask 张量',
        'AscendAttentionBackend.get_name': "返回 'ASCEND'",
        'AscendAttentionBackend.get_impl_cls': '返回 AscendAttentionBackendImpl',
        'AscendAttentionBackend.get_builder_cls': '返回 AscendAttentionMetadataBuilder',
        'AscendAttentionBackend.get_kv_cache_shape': '返回 KV 缓存张量形状',
        'AscendAttentionBackend.get_supported_kernel_block_sizes': '返回支持的 block size 列表',
        'AscendAttentionBackend.swap_blocks': '交换两组 KV cache 内容',
        'AscendAttentionMetadataBuilder.__init__': '初始化元数据构建器',
        'AscendAttentionMetadataBuilder.reorder_batch': '按 chunked-prefill 需求重排 batch',
        'AscendAttentionMetadataBuilder.build': '构造 attention metadata',
        'AscendAttentionMetadataBuilder.build_for_graph_capture': '为 cudagraph 捕获构造 mock metadata',
        'AscendAttentionMetadataBuilder.determine_chunked_prefill_workspace_size': '估算 chunked prefill workspace',
        'AscendAttentionMetadataBuilder.get_cudagraph_support': '返回对 CUDA graph 捕获的支持',
        'AscendAttentionBackendImpl.__init__': '初始化 attention impl',
        'AscendAttentionBackendImpl.forward_impl': '底层 attention 计算实现',
        'AscendAttentionBackendImpl.forward': 'attention 前向入口',
        'AscendAttentionBackendImpl.process_weights_after_loading': '权重加载后的后处理',
        'AscendAttentionBackendImpl.init_meta_buffers': '初始化 attention 计算所需的 meta 缓冲',
        'AscendAttentionBackendImpl.use_v1': '返回是否使用 v1 attention 格式',
        'AscendAttentionBackendImpl.free_meta_buffers': '释放 attention meta 缓冲（sleep 时）',
        'AscendAttentionState.get_attn_state': '返回当前 attention 状态',
        'AscendAttentionState.get_attn_mask': '获取当前 attention 所需的 mask',
        'AscendAttentionState.get_splitfuse_attn_mask': '获取 SplitFuse 阶段的 attention mask',
        'AscendAttentionState.get_attention_mask': '统一入口：按当前阶段返回对应的 attention mask',
        'get_attn_mask': '返回 attention mask',
        'get_splitfuse_attn_mask': '返回 SplitFuse 阶段 attention mask',
        'get_attention_mask': '统一入口返回 attention mask',
    },
    'attention_mask.py': {
        'AttentionMaskBuilder.__init__': '初始化 mask 构造器',
        'get_attn_mask': '对外接口：返回 attention mask',
        'get_splitfuse_attn_mask': '返回 SplitFuse 阶段 attention mask',
        'get_attention_mask': '统一入口：按当前阶段返回对应的 attention mask',
        '_generate_attn_mask': '内部：生成 attention mask 张量',
    },
    'dsa_attn_kv_plan.py': {
        'get_dsa_attn_kv_plan': '返回当前配置对应的 DSA KV cache 布局',
        '_supports_dsv4_compressed_cache': '判断当前硬件是否支持 DSV4 压缩 cache',
        'resolve_dsv4_cache_dtype': '依据模型 dtype 解析 DSV4 cache 实际 dtype',
        'is_a5_bf16_kv_enabled': '判断 A5 设备是否启用 BF16 KV 路径',
        'get_dsv4_attn_kv_dtype': '返回 DSV4 attention KV 的目标 dtype',
        'get_dsa_sparse_attn_metadata_op': '返回 DSA 稀疏 attention metadata 算子',
        'get_dsa_sparse_attn_op': '返回 DSA 稀疏 attention 计算算子',
        'is_dsa_sparse_layout_supported': '判断 DSA 稀疏布局是否被硬件支持',
        'get_compress_ratio': '返回当前模型/层的压缩比',
        'select_dsa_kv_dtype': '根据硬件与设置选择 DSA KV dtype',
        'validate_dsa_attn_kv_plan': '校验当前 KV plan 与 vllm_config 一致性',
    },
    'gdn_attn_builder.py': {
        'AscendGDNAttentionBackend.get_name': "返回 'ASCEND_GDN'",
        'AscendGDNAttentionBackend.get_impl_cls': '返回 GDN impl 类',
        'AscendGDNAttentionBackend.get_builder_cls': '返回 GDN builder 类',
        'AscendGDNAttentionBackend.get_kv_cache_shape': '返回 KV 缓存形状',
        'AscendGDNAttentionBackend.get_supported_kernel_block_sizes': '返回 [128]',
        'AscendGDNAttentionBackend.swap_blocks': '交换 KV cache blocks',
        'AscendGDNAttentionBuilder.__init__': '初始化 GDN metadata builder',
        'AscendGDNAttentionBuilder.reorder_batch': 'GDN 专用 batch 重排',
        'AscendGDNAttentionBuilder.build': '构造 GDN metadata',
        'AscendGDNAttentionBuilder.build_for_graph_capture': '为 cudagraph 捕获构造 mock',
    },
    'gdn.py': {
        'AscendGatedDeltaNetAttention.__init__': '初始化 GatedDeltaNet impl',
        'AscendGatedDeltaNetAttention._probe_fused_chunk': '探测 CANN fused chunk 可用性',
        'AscendGatedDeltaNetAttention.forward_impl': 'GDN 前向实现',
        'AscendGatedDeltaNetAttention.forward': 'GDN 前向入口',
        'AscendGatedDeltaNetAttention.process_weights_after_loading': '权重加载后处理',
    },
    # ==================== core ====================
    'kv_cache_interface.py': {
        'AscendMLAAttentionSpec.merge': '合并同一组内的所有 MLA spec',
        'AscendMLAAttentionSpec.max_memory_usage_bytes': '估算该 spec 最大 KV 缓存占用',
        'get_storage_block_size': '返回 KV cache spec 的物理存储块大小',
        'AscendSFAIndexerCacheSpec.merge': '合并一组内的 SFA indexer spec',
        'register_ascend_kv_cache_specs': '注册 Ascend 自定义 KV cache spec',
        'AscendMLAAttentionSpec.__post_init__': 'MLA spec 后置初始化',
    },
    'batch_job_aware_scheduler.py': {
        'JobNameParser.parse': '从 request_id 解析 #job_name[NAME]# 前缀',
        'JobNameParser.remove': '从缓存移除一个 request_id',
        'JobNameParser.clear': '清空全部缓存',
        'JobDecodeEstimator.predict': '基于 EWMA 预测下一轮该 job 的 decode token 数',
        'JobDecodeEstimator.observe': '观测真实 decode 长度，更新 EWMA',
        'JobDecodeEstimator.get_stats': '返回该 job 的统计信息',
        'JobDecodeEstimator.invalidate_cache': '失效 EWMA 缓存',
        'BatchJobAwareRequestQueue.put': '将请求插入等待队列（按 job 桶）',
        'BatchJobAwareRequestQueue.peek_best_fit_request': '取出 KV 容量最匹配的请求',
        'BatchJobAwareRequestQueue.is_empty': '返回队列是否为空',
        'BatchJobAwareRequestQueue.add_request': '添加新请求到队列',
        'BatchJobAwareRequestQueue.prepend_request': '将请求插到队列头部（优先调度）',
        'BatchJobAwareRequestQueue._finalize_reserve': '完成保留块计数',
        'BatchJobAwareRequestQueue._compute_one': '为单个请求计算所需 KV 块数',
        'BatchJobAwareRequestQueue._compute_all': '为请求列表汇总所需 KV 块数',
        'BatchJobAwareRequestQueue._cdiv': '整数上除法',
        'BatchJobAwareRequestQueue.invalidate_cache': '失效 best-fit 缓存',
        'BatchJobAwareScheduler.schedule': '执行 LPT 调度 + 容量保留（核心入口）',
        'BatchJobAwareScheduler.__init__': '初始化调度器',
        'BatchJobAwareAsyncScheduler.schedule': '异步版本的调度入口',
        'BatchJobAwareAsyncScheduler.__init__': '初始化异步调度器',
    },
    'dyntra_lb_scheduler.py': {
        'get_dyntra_lb_block_size': '返回 DyntraLB 负载均衡用的 KV 块大小',
        'get_dyntra_lb_request_block_num': '估算单个请求占用的 KV 块数',
        'diagnostics_enabled': '读 additional_config 中的诊断开关',
        'print_scheduler_summary': '打印调度器当前状态摘要',
        'DyntraLBPolicyMixin.is_schedulable_waiting': '判断请求是否处于可调度等待态',
        'DyntraLBPolicyMixin._waiting_requests_in_schedule_order': '按调度顺序遍历等待请求',
        'DyntraLBPolicyMixin._refresh_blocked_waiting_requests': '刷新被阻塞的请求列表',
        'DyntraLBPolicyMixin._run_lb_kv_prefetch': '触发 LB 模式 KV 预取',
        'DyntraLBPolicyMixin.prepare_dyntra_lb_step': '为一次 DyntraLB step 做准备',
        'DyntraLBPolicyMixin._apply_load_balance_modifications': '应用 DyntraLB 调整后的队列顺序',
        'DyntraLBPolicyMixin.req_blk_num': '计算请求占用的 KV 块数',
        'DyntraLBPolicyMixin._can_admit_waiting_request': '判断是否允许接纳一个等待请求',
        'DyntraLBPolicyMixin._scheduler_output_supports': '判断调度输出是否支持某项 LB 调整',
        'DyntraLBPolicyMixin._has_pending_deliverable_output': '检查是否有挂起的可交付输出',
        'DyntraLBPolicyMixin._get_connector_computed_blocks': '从 KV connector 取得已计算块',
        'DyntraLBPolicyMixin._record_prefix_cache_stats': '记录 prefix cache 命中统计',
        'DyntraLBPolicyMixin._preempt_request': '抢占一个请求（释放其 KV 块）',
        'DyntraLBPolicyMixin._lb_pause_request': 'DyntraLB 模式下暂停一个请求',
        'DyntraLBPolicyMixin._handle_stopped_request': '清理已停止请求的状态',
        'DyntraLBScheduler.__init__': '初始化 DyntraLBScheduler',
        'DyntraLBScheduler.schedule': 'DyntraLBScheduler 调度入口',
        'AsyncDyntraLBScheduler.schedule': '异步 DyntraLB 调度',
        'AsyncDyntraLBScheduler.__init__': '初始化异步 DyntraLB 调度器',
    },
    'profiling_chunk_predictor.py': {
        '_start_profiling_chunk_timing': '开始计时一次 chunked prefill 的 profiling',
        '_finish_profiling_chunk_timing': '结束计时并返回耗时（毫秒）',
        '_attach_profiling_chunk_execution_time': '把耗时附加到 model runner output',
        'ChunkSizePredictor.__init__': '初始化：a/b/c 系数、目标 latency、min_chunk 等',
        'ChunkSizePredictor.fit': '基于序列长度与延迟采样拟合二次曲线',
        'ChunkSizePredictor.fit_chunk': '拟合 chunk 大小与延迟的关系',
        'ChunkSizePredictor.set_target_latency': '设置目标 latency',
        'ChunkSizePredictor.f': '曲线函数：给定长度 l，返回预测延迟',
        'ChunkSizePredictor.get_time': '基于当前 history 长度预测耗时',
        'ChunkSizePredictor.get_time_with_history': '带历史的预测耗时',
        'ChunkSizePredictor.predict': '给定目标 latency 与 history，预测下一 chunk 大小',
        'ChunkSizePredictor.predict_with_history': '带历史预测下一 chunk 大小',
        'ChunkSizePredictor.is_ready': '模型是否已就绪',
        'ChunkSizePredictor.history_ready': '历史是否足够',
        'ChunkSizePredictor.predict_chunk_size': '预测下一 chunk 大小',
        'ChunkSizePredictor.predict_time': '给定 chunk 大小预测耗时',
        'ChunkSizePredictor.record_batch_execution_time': '记录一次 batch 的真实执行时间',
    },
    'recompute_scheduler.py': {
        'RecomputeSchedulerConfig.initialize_from_config': '从 vllm config 拷贝字段并设置 scheduler_cls',
        'RecomputeSchedulerOutput': '调度器输出：含 preempted_reqs 列表',
        'RecomputeScheduler._get_computed_blocks_for_connector': '取 KV connector 的已计算块',
        'RecomputeScheduler._truncate_computed_blocks_for_connector': '截断已计算块到 KV connector 需要的长度',
        'RecomputeScheduler._truncate_computed_blocks_with_mamba_clamp': '用 Mamba 边界再次截断已计算块',
        'RecomputeScheduler._apply_load_balance_modifications': '应用 DyntraLB 调整后的队列',
        'RecomputeScheduler._can_admit_waiting_request': '判断能否接纳一个等待请求（含重算预算）',
        'RecomputeScheduler._update_waiting_for_remote_kv': '更新等待远程 KV 的请求状态',
        'RecomputeScheduler._finish_recomputed_request': '完成一次重算请求',
        'RecomputeScheduler.schedule': '调度入口：含 recompute 流程的核心循环',
        'RecomputeScheduler._build_kv_connector_meta': '构造 KV connector metadata',
        'RecomputeScheduler._add_recomputed_outputs': '把重算输出加到 SchedulerOutput',
        'RecomputeScheduler.update_from_output': '根据 ModelRunnerOutput 更新调度器状态',
        'RecomputeScheduler.__init__': '初始化调度器',
        'RecomputeScheduler._handle_stopped_request': '处理已停止的请求',
        'RecomputeScheduler._preempt_request': '抢占一个请求',
        'AsyncRecomputeScheduler.schedule': '异步 recompute 调度入口',
        'AsyncRecomputeScheduler.__init__': '初始化异步 recompute 调度器',
    },
    # ==================== models ====================
    '__init__.py': {
        'register_model': '将模型架构名注册到 vLLM ModelRegistry（Kimi/DeepSeek/MiniMax/Qwen等）',
    },
    'kimi_k3.py': {
        '_apply_ascend_attn_res': '应用 Kimi 学习到的残差混合（用原生 NPU ops）',
        'AscendKimiMLAAttention.__init__': '初始化 Kimi MLA 注意力',
        'AscendKimiMLAAttention.forward': 'Kimi MLA 前向传播',
        'AscendKimiMLAAttention.forward_attn': 'Kimi MLA 注意力计算',
        'AscendKimiMoE.__init__': '初始化 Kimi MoE',
        'AscendKimiMoE.forward': 'Kimi MoE 前向',
        'AscendKimiLinearModel.__init__': '初始化 Kimi 线性模型',
        'AscendKimiLinearModel.forward': 'Kimi 线性模型前向',
        'AscendKimiLinearModel.get_input_embeddings': '取得输入 embedding',
        'AscendKimiLinearForCausalLM.__init__': '初始化 Kimi 线性因果模型',
        'AscendKimiLinearForCausalLM.forward': 'Causal LM 前向',
        'AscendKimiLinearForCausalLM.compute_logits': '计算 logits',
        'AscendKimiLinearForCausalLM.get_input_embeddings': '取得输入 embedding',
        'AscendKimiK3ForConditionalGeneration.__init__': '初始化 Kimi K3 多模态生成模型',
        'AscendKimiK3ForConditionalGeneration.forward': '多模态前向',
        'AscendKimiK3ForConditionalGeneration.get_multimodal_embeddings': '取得多模态 embedding',
    },
    'kimi_k3_mtp.py': {
        'AscendKimiK3MTP.__init__': '初始化 Kimi K3 MTP 模型',
        'AscendKimiK3MTP.forward': 'MTP 前向传播',
        'AscendKimiK3MultiTokenPredictor.__init__': '初始化 Kimi K3 MTP 预测器',
        'AscendKimiK3MultiTokenPredictor.propose_draft_token_ids': '生成 draft token id',
    },
    'kimi_k3_dspark.py': {
        'AscendK3DSparkForCausalLM.__init__': '初始化 Kimi K3 DSpark 草稿模型',
        'AscendK3DSparkForCausalLM.forward': 'DSpark 草稿模型前向',
        'AscendK3DSparkModel.__init__': '初始化 DSpark 模型',
        'AscendK3DSparkModel.forward': 'DSpark 模型前向',
    },
    'deepseek_v4/model.py': {
        'AscendDeepseekV4ForCausalLM.__init__': '初始化 Deepseek V4 因果模型',
        'AscendDeepseekV4ForCausalLM.forward': 'Deepseek V4 前向',
        'AscendDeepseekV4ForCausalLM.compute_logits': '计算 logits',
        'AscendDeepseekV4ForCausalLM.get_input_embeddings': '取得输入 embedding',
        'DeepseekV4Model.__init__': '初始化 Deepseek V4 模型',
        'DeepseekV4Model.forward': 'V4 模型前向',
        'DeepseekV4Attention.__init__': '初始化 V4 Attention',
        'DeepseekV4Attention.forward': 'V4 Attention 前向',
        'DeepseekV2DecoderLayer.__init__': '初始化 V2 Decoder Layer',
        'DeepseekV2DecoderLayer.forward': 'V2 Decoder Layer 前向',
    },
    'deepseek_v4/mtp.py': {
        'DeepSeekV4MTP.__init__': '初始化 V4 MTP',
        'DeepSeekV4MTP.forward': 'V4 MTP 前向',
        'DeepSeekMultiTokenPredictor.__init__': '初始化 V4 MTP 预测器',
        'DeepSeekMultiTokenPredictor.propose_draft_token_ids': '生成 draft token ids',
    },
    'deepseek_v4/dspark.py': {
        'DSparkDeepseekV4ForCausalLM.__init__': '初始化 V4 DSpark 草稿模型',
        'DSparkDeepseekV4ForCausalLM.forward': 'V4 DSpark 草稿模型前向',
        'DSparkMarkovHead.__init__': '初始化 Markov 头',
        'DSparkMarkovHead.forward': 'Markov 头前向',
        'DSparkConfidenceHead.__init__': '初始化 confidence 头',
        'DSparkConfidenceHead.forward': 'confidence 头前向',
    },
    'deepseek_v4/indexer.py': {
        'AscendDeepseekV4IndexerCache.__init__': '初始化 V4 indexer 缓存',
        'AscendDeepseekV4IndexerCache.get_storage_block_size': '取得物理块大小',
        'DeepseekV4Indexer.__init__': '初始化 V4 Indexer',
        'DeepseekV4Indexer.forward': 'V4 Indexer 前向',
        'AscendIndexerOps.get_topk_indices': '取得 topk 索引',
    },
    'deepseek_v4/compressor.py': {
        'AscendCompressorStateCache.__init__': '初始化 compressor 状态缓存',
        'AscendCompressorStateCache.get_storage_block_size': '取得物理块大小',
    },
    'minimax_m3/minimax_m3.py': {
        'MiniMaxM3SparseForCausalLM.__init__': '初始化 MiniMax M3 Sparse 因果模型',
        'MiniMaxM3SparseForCausalLM.forward': 'MiniMax M3 前向',
        'MiniMaxM3SparseForCausalLM.compute_logits': '计算 logits',
        'MiniMaxM3MoE.__init__': '初始化 MiniMax M3 MoE',
        'MiniMaxM3MoE.forward': 'MiniMax M3 MoE 前向',
        'MiniMaxM3Attention.__init__': '初始化 MiniMax M3 Attention',
        'MiniMaxM3Attention.forward': 'MiniMax M3 Attention 前向',
        'MiniMaxM3DecoderLayer.__init__': '初始化 MiniMax M3 Decoder Layer',
        'MiniMaxM3DecoderLayer.forward': 'MiniMax M3 Decoder Layer 前向',
    },
    'minimax_m3/minimax_m3_vl.py': {
        'MiniMaxM3SparseForConditionalGeneration.__init__': '初始化 MiniMax M3 多模态生成模型',
        'MiniMaxM3SparseForConditionalGeneration.forward': '多模态前向',
    },
    'minimax_m3/msa_m3.py': {
        'AscendMiniMaxM3IndexerBackend.__init__': '初始化 MiniMax M3 indexer backend',
        'AscendMiniMaxM3SparseBackend.__init__': '初始化 sparse backend',
        'AscendMiniMaxM3SparseImpl.__init__': '初始化 sparse impl',
        'AscendMiniMaxM3SparseImpl.forward': 'sparse impl 前向',
        'AscendMiniMaxM3QKVParallelLinearWithIndexer.__init__': '初始化带 indexer 的 QKV 并行线性层',
        'AscendMiniMaxM3QKVParallelLinearWithIndexer.forward': 'QKV 前向',
    },
    'qwen3_dspark.py': {
        'AscendQwen3DSparkForCausalLM.__init__': '初始化 Qwen3 DSpark 草稿模型',
        'AscendQwen3DSparkForCausalLM.forward': 'Qwen3 DSpark 前向',
    },
    'qwen3_dflash2.py': {
        'DFlash2Qwen3ForCausalLM.__init__': '初始化 DFlash2 Qwen3 草稿模型',
        'DFlash2Qwen3ForCausalLM.forward': 'DFlash2 Qwen3 前向',
    },
    'llama_eagle3.py': {
        'AscendEagle3LlamaForCausalLM.__init__': '初始化 Eagle3 Llama 草稿模型',
        'AscendEagle3LlamaForCausalLM.forward': 'Eagle3 Llama 前向',
        'rotarotate_and_maybe_quantize_eagle3_input': '对 Eagle3 input 做旋转/可能量化',
        'rotarotate_and_maybe_quantize_eagle3_input_quarot': '对 Eagle3 input 做 quarot 旋转/量化',
    },
    'llama_eagle3_vwn.py': {
        'Eagle3VwnLlamaForCausalLM.__init__': '初始化 Eagle3 Vwn Llama',
        'Eagle3VwnLlamaForCausalLM.forward': 'Eagle3 Vwn Llama 前向',
        'VwnLlamaModel.__init__': '初始化 Vwn Llama 模型',
        'VwnLlamaModel.forward': 'Vwn Llama 模型前向',
        'VwnLlamaDecoderLayer.__init__': '初始化 Vwn Llama Decoder Layer',
        'VwnLlamaDecoderLayer.forward': 'Vwn Llama Decoder Layer 前向',
    },
    'layer/attention/layer.py': {
        'get_dsv4_block_sizes': '返回 DSV4 注意力层 block size 配置',
    },
    # ==================== ops ====================
    'linear.py': {
        'unquantized_gemm': '非量化 GEMM：F.linear(x, weight, bias)',
        'unquantized_gemm_fake': 'unquantized_gemm 的 fake 实现（用于 meta tensor）',
        'AscendUnquantizedLinearMethod.process_weights_after_loading': '权重加载后处理（NZ layout cast）',
        'AscendUnquantizedLinearMethod.apply': '前向 linear 计算',
        'AscendUnquantizedLinearMethod.forward_oot': 'NPU out-of-tree 前向',
        'AscendColumnParallelLinear.__init__': '初始化列并行 Linear',
        'AscendColumnParallelLinear.forward': '列并行 Linear 前向',
        'AscendColumnParallelLinear.process_weights_after_loading': '列并行 Linear 权重后处理',
        'AscendRowParallelLinear.__init__': '初始化行并行 Linear',
        'AscendRowParallelLinear.forward': '行并行 Linear 前向',
        'AscendRowParallelLinear.process_weights_after_loading': '行并行 Linear 权重后处理',
        'AscendMergedColumnParallelLinear.__init__': '初始化合并列并行 Linear',
        'AscendMergedColumnParallelLinear.forward': '合并列并行 Linear 前向',
        'AscendQKVParallelLinear.__init__': '初始化 QKV 并行 Linear',
        'AscendQKVParallelLinear.forward': 'QKV 并行 Linear 前向',
        'AscendReplicatedLinear.__init__': '初始化复制 Linear',
        'AscendReplicatedLinear.forward': '复制 Linear 前向',
        '_should_keep_nd_for_compatibility_weight': '判断是否应保持 ND layout（兼容权重）',
    },
    'linear_op.py': {
        'CustomLinearOp.__init__': '初始化 CustomLinearOp',
        'CustomLinearOp.update_attrs': '从 layer 同步 bias、prefix 等属性',
        'CustomLinearOp.apply_impl': '子类实现：实际计算（abstract）',
        'CustomLinearOp.apply': '包装 apply_impl 并处理 bias',
        'CustomLinearOp.comm_group': '返回通信组（默认 TP group）',
        'CustomLinearOp.tp_rank': '返回当前 TP rank',
        'CustomLinearOp.tp_size': '返回 TP 规模',
        'CustomColumnParallelOp.__init__': '初始化列并行 op',
        'CustomColumnParallelOp.apply_impl': '列并行 op 实际计算',
        'CustomRowParallelOp.__init__': '初始化行并行 op',
        'CustomRowParallelOp.apply_impl': '行并行 op 实际计算',
        'CustomReplicatedOp.__init__': '初始化复制 op',
        'CustomReplicatedOp.apply_impl': '复制 op 实际计算',
        'get_column_parallel_op': '按 layer 特征选择合适的列并行 op 类',
        'get_row_parallel_op': '按 layer 特征选择合适的行并行 op 类',
        'get_replicated_op': '按 layer 特征选择合适的复制 op 类',
    },
    'layernorm.py': {
        'AscendRMSNorm.__init__': '初始化 RMSNorm',
        'AscendRMSNorm._bias_weight_loader': '加载 norm bias 权重',
        'AscendRMSNorm.forward_oot': 'NPU out-of-tree 前向',
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
        'AscendRotaryEmbedding.forward_native': '原生 RoPE 前向（reference）',
        'AscendRotaryEmbedding.forward_oot': 'NPU out-of-tree RoPE 前向',
        'AscendRotaryEmbedding.forward_cuda': 'NPU RoPE 前向（cuda dispatch key）',
        'AscendRotaryEmbedding.forward_xpu': 'NPU RoPE 前向（xpu dispatch key）',
        'AscendRotaryEmbedding.forward_hpu': 'NPU RoPE 前向（hpu dispatch key）',
        'AscendMRotaryEmbedding.__init__': '初始化 Multi-modal RoPE',
        'AscendMRotaryEmbedding.forward_oot': 'M-RoPE NPU 前向',
        'AscendApplyRotaryEmb.forward_native': '原生 ApplyRotaryEmb',
        'AscendApplyRotaryEmb.forward_oot': 'ApplyRotaryEmb NPU 前向',
        'AscendYaRNRotaryEmbedding.__init__': '初始化 YaRN RoPE',
        'AscendYaRNRotaryEmbedding.forward_oot': 'YaRN RoPE NPU 前向',
        'AscendDeepseekScalingRotaryEmbedding.__init__': '初始化 Deepseek Scaling RoPE',
        'AscendDeepseekScalingRotaryEmbedding.forward_oot': 'Deepseek Scaling RoPE NPU 前向',
    },
    'rope_dsv4.py': {
        'RopeGlobalState.__init__': '初始化 DSV4 RoPE 全局状态',
        'RopeDataProxy.__init__': '初始化 RoPE 数据代理',
        'RopeDataProxy.pad_to': '把 underlying tensors padding 到 target_len',
        'RopeDataProxy.__getitem__': '按 config_key 或 layername 取 RoPE 数据',
    },
    'mla.py': {
        'IndexerWrapper.__init__': '包装 vllm Indexer，删除未用的 topk_indices_buffer',
        'IndexerWrapper.forward': '占位 forward（实际权重继承自 vllm_indexer）',
        'AscendMultiHeadLatentAttention.__init__': '初始化 Ascend MLA',
        'AscendMultiHeadLatentAttention.forward': 'MLA NPU 前向',
        'AscendMultiHeadLatentAttention.forward_native': '原生 MLA 前向',
    },
    'dsa.py': {
        'DSAModules': 'SFA V2 所需模块集合（wq_a/q_norm/wq_b/wkv/wo_a/wo_b/...）',
        'AscendDeepseekSparseAttention.__init__': '初始化 DSV4 Sparse Attention',
        'AscendDeepseekSparseAttention.forward': 'DSA NPU 前向',
    },
    'gdn.py': {
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
        'unquantized_gemm': '非量化 GEMM（F.linear）',
        'unquantized_gemm_fake': 'unquantized_gemm 的 meta/fake 实现',
        'npu_swiglu': 'NPU SwiGLU 算子（已通过 activation.py 暴露）',
        'muls_add_triton': 'Triton 实现的 mul + add 融合算子',
        'rope_forward_oot': 'Ascend RoPE OOT forward 入口',
    },
    'conv.py': {
        'AscendConv3dLayer.__init__': '初始化 Conv3d（继承 vllm）',
        'AscendConv3dLayer.forward_oot': 'NPU 3D Conv 前向（aclnn BatchMatMulV2）',
    },
    'vocab_parallel_embedding.py': {
        'AscendVocabParallelEmbedding.__init__': '初始化 VocabParallel Embedding',
        'AscendVocabParallelEmbedding.forward': 'embedding 前向（支持 embed/lmhead TP）',
        'AscendVocabParallelEmbedding.forward_native': '原生 embedding 前向',
        'AscendVocabParallelEmbedding.forward_oot': 'NPU out-of-tree embedding',
        'AscendParallelLMHead.__init__': '初始化 Parallel LMHead',
        'AscendParallelLMHead.forward': 'LMHead 前向',
        'AscendLogitsProcessor.__init__': '初始化 LogitsProcessor',
        'AscendLogitsProcessor.forward': 'LogitsProcessor 前向',
    },
    'gdn_attn_builder.py': {
        'AscendGDNAttentionBackend.get_name': "返回 'ASCEND_GDN'",
        'AscendGDNAttentionBackend.get_impl_cls': '返回 GDN impl 类',
        'AscendGDNAttentionBackend.get_builder_cls': '返回 GDN builder 类',
        'AscendGDNAttentionBackend.get_kv_cache_shape': '返回 GDN KV 缓存形状',
        'AscendGDNAttentionBackend.get_supported_kernel_block_sizes': '返回 [128]',
        'AscendGDNAttentionBuilder.__init__': '初始化 GDN metadata builder',
        'AscendGDNAttentionBuilder.reorder_batch': 'GDN 专用 batch 重排',
        'AscendGDNAttentionBuilder.build': '构造 GDN metadata',
        'AscendGDNAttentionBuilder.build_for_graph_capture': '为 cudagraph 捕获构造 mock',
    },
}


def get_desc_for_file(basename_composite, fname):
    """从匹配的最长 basename 开始查找描述"""
    parts = basename_composite.replace('\\', '/').split('/')
    # Try composite keys: full path, then parent/basename, then basename
    candidates = []
    for i in range(len(parts)):
        key = '/'.join(parts[i:])
        candidates.append(key)
    for key in candidates:
        if key in DESCRIPTIONS and fname in DESCRIPTIONS[key]:
            return DESCRIPTIONS[key][fname]
    return ''


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
        basename = os.path.basename(file_name)
        # Use full path with backslash as composite
        composite = file_name

        # Count placeholders in this block
        placeholders = func_pattern.findall(block)
        counts['total_placeholders'] += len(placeholders)

        def make_replacer(bn, comp):
            def replacer(m):
                fname = m.group(1).strip()
                desc = get_desc_for_file(comp, fname)
                if desc:
                    counts['replaced'] += 1
                else:
                    counts['unknown'] += 1
                    if fname not in unknown_list:
                        unknown_list.append(fname)
                    desc = '(参见源码:' + fname + ')'
                return '<span class="item-name">' + fname + '</span><span class="item-desc">' + desc + '</span>'
            return replacer

        new_block = func_pattern.sub(make_replacer(file_name, composite), block)
        new_html_parts.append(new_block)
        last_idx = end

    new_html_parts.append(html[last_idx:])
    new_html = ''.join(new_html_parts)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    return counts, unknown_list


# Process all 4 pages
pages = [
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-attention.html', 'attention'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-core.html', 'core'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-models.html', 'models'),
    (r'D:\demo\202609\vllm-ascend\code-docs\panorama-ops.html', 'ops'),
]

for path, name in pages:
    print(f'\n=== Processing {name} ({os.path.basename(path)}) ===')
    counts, unknowns = process_html(path)
    print(f'  Total placeholders: {counts["total_placeholders"]}')
    print(f'  Replaced with real desc: {counts["replaced"]}')
    print(f'  Unknown (left as placeholder): {counts["unknown"]}')
    if unknowns:
        print(f'  Sample unknown functions: {unknowns[:10]}')