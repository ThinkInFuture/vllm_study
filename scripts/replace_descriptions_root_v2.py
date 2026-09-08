import os, re, json

src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'

# 真实的功能描述（基于源码阅读）
DESCRIPTIONS = {
    'ascend_forward_context.py': {
        'override_mrv2_in_profile_run': '上下文管理器：在一次 forward 中临时设置 MRV2 额外 profile-run 标记',
        'get_mrv2_in_profile_run': '读取当前 forward 是否处于 MRv2 的 profile-run 标记下',
        'use_cann_megamoe': '判断当前配置是否启用 CANN MegaMoe fused MC2',
        'set_ascend_forward_context': '上下文管理器：注入 MoE 通信类型、mmrs 融合、layer_idx、mc2_mask 等 forward 状态',
        'set_mc2_tokens_capacity': '根据 max_num_batched_tokens 与 TP 规模计算并锁定 MC2 通信每 rank token 上限',
        'get_mc2_tokens_capacity': '返回当前全局 MC2 通信容量',
        'set_mc2_mask': '预分配 MC2 mask 缓冲区（仅 MoE 模型）',
        'get_mc2_mask': '读取已预分配的 MC2 mask 张量',
        '_select_a2_moe_comm_method': '在 A2 设备上选择 MoE 通信方式（MC2 或 AllGather）',
        '_select_a3_moe_comm_method': '在 A3 设备上选择 MoE 通信方式',
        '_select_a5_moe_comm_method': '在 A5 设备上选择 MoE 通信方式',
        'select_moe_comm_method': '统一入口：根据设备型号、并行配置、token 数返回 MoE 通信方法',
    },
    'dsa_v1.py': {
        'dsv4_dsa_overlap_stream': '获取 DSV4 与 DSA 重叠计算用的 NPU 流（懒初始化）',
        '_is_w8a8_dynamic': '判断线性层是否使用 AscendW8A8Dynamic 量化方法',
        '_has_weight_scale': '判断线性层是否携带 weight_scale 张量',
        '_dsa_layout_kv': '返回当前 VllmConfig 对应的 KV cache 布局字符串',
        '_dsa_swa_only_cmp_ratio': 'BF16 SWA-only 场景下返回 0，否则保留主模型的压缩比',
        'AscendDSABackend.get_name': "返回后端名称 'ASCEND_DSA'",
        'AscendDSABackend.get_builder_cls': '根据 DSA-CP/PCP 标志返回对应的 metadata builder 类',
        'AscendDSABackend.get_kv_cache_shape': '返回 KV 缓存张量形状',
        'AscendDSABackend.get_scale_shape': '返回 scale 张量形状',
        'AscendDSABackend.get_impl_cls': '返回 attention 实现类',
        'AscendDSABackend.get_supported_kernel_block_sizes': '返回支持的 kernel 块大小列表',
    },
    'fa3_v1.py': {
        'AscendFABackend.get_name': "返回后端名称 'CUSTOM'",
        'AscendFABackend.get_impl_cls': '返回 AscendFAImpl',
        'AscendFABackend.get_builder_cls': '返回 AscendAttentionMetadataBuilder',
        'AscendFABackend.get_kv_cache_shape': '返回 KV 缓存张量形状',
        'AscendFABackend.get_supported_kernel_block_sizes': '返回支持的 block 大小 [128]',
        'AscendFAImpl.__init__': '初始化：校验不支持 sliding window、FULL_DECODE_ONLY 图模式',
        'AscendFAImpl._flash_attn_with_kvcache': '调用 flash_attn_npu_v3 的 flash_attn_with_kvcache',
        'AscendFAImpl.forward_impl': '执行 attention 前向：分别处理 decode 和 prefill',
    },
    'indexer.py': {
        'AscendSFAIndexerBackend.get_name': "返回后端名称 'ASCEND_SFA_INDEXER'",
        'AscendSFAIndexerBackend.get_impl_cls': '占位实现，返回 None',
        'AscendSFAIndexerBackend.get_builder_cls': '返回 AscendSFAIndexerMetadataBuilder',
        'AscendSFAIndexerBackend.get_kv_cache_shape': '返回 indexer 缓存张量形状',
        'AscendSFAIndexerBackend.get_supported_kernel_block_sizes': '返回支持的 block 大小 [128]',
        'AscendSFAIndexerMetadataBuilder.__init__': '初始化：直接走父类构造',
        'AscendSFAIndexerMetadataBuilder.get_cudagraph_support': '返回支持 CUDA graph 捕获 (UNIFORM_BATCH)',
        'AscendSFAIndexerMetadataBuilder.build': '缓存专用 builder：不构建任何 metadata 直接返回 None',
    },
    'mla_v1.py': {
        '_npu_mla_prolog_v3_no_rope': '调用 AscendC MLA prolog（v3）算子，可省略 RoPE 入参',
        'AscendMLABackend.get_name': "返回 'ASCEND_MLA'",
        'AscendMLABackend.get_builder_cls': '根据 DCP/PCP 标志返回对应的 MLA builder',
        'AscendMLABackend.get_kv_cache_shape': '返回 MLA KV 缓存张量形状',
        'AscendMLABackend.get_impl_cls': '返回 MLA 实现类',
        'AscendMLABackend.get_supported_kernel_block_sizes': '返回支持的 block 大小 [128]',
    },
    'sfa_kv_offload.py': {
        '_check_device_kv_cache_exist': '检查当前 prefill/mixed 批次是否需要 keep_device_kv_cache',
        'AscendSFAKVOffloadMetadataBuilder._populate_offload_metadata': '填充 offload 专用 metadata',
        'AscendSFAKVOffloadMetadataBuilder.build': '调用父类 build 后填充 offload 专用 metadata',
        'AscendSFAKVOffloadMetadataBuilder.build_for_drafting': '调用父类 build_for_drafting 后填充 offload metadata',
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
    },
    'sfa_v1.py': {
        '_get_indexer_types': '从若干 config 中提取 indexer_types 字段',
        '_has_shared_indexer_layers': '判断任一层是否使用 shared 类型的 indexer',
        '_get_config_bool': '从若干 config 中按顺序读取 bool 属性',
        'AscendSFABackend.get_name': "返回 'ASCEND_SFA'",
        'AscendSFABackend.get_builder_cls': '根据是否启用 sparse_kv_offload 返回对应 builder',
        'AscendSFABackend.get_kv_cache_shape': '返回 SFA KV 缓存形状',
        'AscendSFABackend.get_impl_cls': '返回 AscendSFAImpl 或其 KV-offload 变体',
        'AscendSFABackend.get_supported_kernel_block_sizes': '返回 [128]',
    },
    'sparse_flash_mla.py': {
        '_get_sparse_flash_mla_ops': '懒加载 SparseFlashMla 算子（来自 CANN 9.2 toolkit）',
        '_add_compressed_kv_lengths': '为 kwargs 添加压缩 KV 长度信息',
        'sparse_flash_mla_metadata': '将 DSA metadata 参数适配到 SparseFlashMla BF16 KV',
        'sparse_flash_mla': '将 DSA attention 参数适配到 SparseFlashMla BF16 KV 并执行',
    },
    'utils.py': {
        'get_or_register_attention_buffer': '注册跨 attention 层共享的非-persistent 缓冲',
        'build_valid_topk_mask': '生成 top-k 行中的合法位置掩码',
        'get_sfa_qsfa_packed_head_dim': '计算 SFA/QSFA packed KV 缓存的 head_dim 字节数',
        'PagedAttentionGraphParam.__iter__': '解包 params 元组为可迭代子',
        'update_paged_attention_graph_param': '更新 ACL graph 中 PA 参数',
        'cache_graph_workspace': '按 graph 大小缓存/工作图 空间张量',
        'needs_layer_aware_fia_graph_replay': '是否需要逐层感知的 FIA 图 replay',
        'ascend_chunked_prefill_workspace_size': '计算 chunked prefill 所需的 workspace',
    },
    'acl_graph.py': {
        '_is_stream_resource_capture_error': '判断 RuntimeError 是否为 NPU 流资源不足导致的 capture 错误',
        '_is_old_hdk_capture_error': '判断 RuntimeError 是否为旧版 HDK 的 capture 错误',
        'ACLGraphEntry': '每个 (batch_descriptor, captured_graph) 对应的数据条目',
        'ACLGraphWrapper.__init__': '初始化：记录 runnable 与 runtime_mode，按需初始化 graph_pool',
        'ACLGraphWrapper.__getattr__': '转发属性访问到底层 runnable',
        'ACLGraphWrapper.unwrap': '返回底层 runnable 引用',
        'ACLGraphWrapper.__call__': 'dispatch：根据 runtime_mode 决定 capture/replay/直接调用',
        'weak_ref_workspaces': '将所有 workspaces 张量替换为 weakref，延长 graph 生命周期',
        'update_full_graph_params': '更新 FULL 图注意力所需的 graph params',
        'set_graph_params': '注册 graph params（context manager 内绑定到当前 forward）',
        'update_graph_params_workspaces': '根据新输入更新 graph workspaces',
        'get_graph_params': '读取当前 forward context 关联的 graph params',
        'set_draft_graph_params': '注册 draft 模型（EAGLE）的 graph params',
        'update_draft_graph_params_workspaces': '更新 draft graph 的 workspaces',
        'get_draft_graph_params': '读取 draft graph params',
        'set_draft_graph_prefill_params': '注册 draft prefill 阶段的 graph params',
        'update_draft_graph_prefill_params_workspaces': '更新 draft prefill graph workspaces',
        'get_draft_graph_prefill_params': '读取 draft prefill graph params',
    },
    'breakable_aclgraph.py': {
        'BreakableACLGraphWrapper.__init__': '初始化：记录 use_eagle、enable_enpu 标志',
        'BreakableACLGraphWrapper._capture': '执行 capture：FULL 图模式时设置 capturing=True 与 workspace weakref',
        'BreakableACLGraphWrapper._replay': '执行 replay：FULL 图模式时按 use_eagle/enpu 同步当前 stream',
    },
    'compiler_interface.py': {
        'compile_fx': '编译 FX 图：递归调用 inner_compile，必要时 make_graph_return_tuple',
        'fusion_pass_compile': '用当前 GraphFusionPassManager 跑一遍图融合 pass 再编译',
        '_compute_decode_cudagraph_batch_sizes': '计算 decode-only 阶段可捕获的 cuda graph 批次大小',
        '_configure_backend': '配置 npugraph_ex/torchair 后端选项',
        'npugraph_ex_compile': '主编译入口：调用 npugraph_ex 编译 FX 图，含 Triton 内核时跳过缓存',
        'patched_get_compiled_gm': 'monkey patch：把编译出的 py_code 写入磁盘缓存',
        'compute_hash': '基于 graph 与 example_inputs 计算编译缓存的 hash',
        'initialize_cache': '初始化 FX graph 缓存目录',
        'compile': '入口：根据 cache miss/调用 inner_compile 并写入缓存',
        'load': '根据 hash 从磁盘读取已编译的图',
        'compiled_fn': '返回编译产物 callable',
    },
    'graph_fusion_pass_manager.py': {
        'GraphFusionPassManager.__init__': '初始化空 pass 列表',
        'GraphFusionPassManager.__call__': '执行所有通过的 pass 后 recompile 图',
        'GraphFusionPassManager.add': '添加一个 VllmInductorPass 到 pass 列表',
        'GraphFusionPassManager.configure': '根据 Ascend 编译开关加载各种融合 pass',
    },
    'base_pattern.py': {
        'BasePattern.__init__': '初始化：保存 vllm_config、dtype、eps',
        'BasePattern.get_inputs': '抽象方法：返回示例输入张量',
        'BasePattern.get_pattern': '抽象方法：返回待匹配的模式函数',
        'BasePattern.get_replacement': '抽象方法：返回替换函数',
        'BasePattern.get_extra_stream_scope_check': '返回流作用域检查器',
        'BasePattern.register': '同时注册到 torch inductor 与 npugraph_ex 的 pattern matcher',
    },
    'allgather_chunk_noop_pass.py': {
        'AllGatherChunkNoOpCleanupPass.__init__': '初始化：注册 all_gather + sequence_parallel_chunk 折叠规则',
        'AllGatherChunkNoOpCleanupPass._all_gather': '调用 vllm.all_gather 算子（TP 集合）',
        'AllGatherChunkNoOpCleanupPass._empty': '构造模型 dtype 的示例空张量',
        'AllGatherChunkNoOpCleanupPass._register_patterns': '注册 all_gather→sequence_parallel_chunk 折叠为恒等映射',
        'AllGatherChunkNoOpCleanupPass.__call__': '在 FX 图中应用该 pass',
    },
    'muls_add_pass.py': {
        'MulsAddPattern.__init__': '初始化：保存 vllm_config 与缩放因子 scale',
        'MulsAddPattern.get_inputs': '返回示例输入（x, y）',
        'MulsAddPattern.get_pattern': '返回 x*scale + y 的模式函数',
        'MulsAddPattern.get_replacement': '返回替换为 muls_add 算子的函数',
        'MulsAddFusionPass.__init__': '初始化：根据支持的 dtype 注册 muls_add pattern',
        'MulsAddFusionPass.__call__': '在 FX 图中应用 muls_add 融合',
    },
    'noop_elimination.py': {
        'NoOpEliminationPass.__call__': '移除 FX 图中形状不变的 view/reshape 节点',
        'NoOpEliminationPass._is_view_like': '判断节点是否为 view/reshape 类',
        'NoOpEliminationPass._dims_equivalent': '符号化判断两个维度是否相等',
        'NoOpEliminationPass._all_dims_equivalent': '判断两个 shape 是否所有维度相等',
    },
    'norm_quant_fusion_pass.py': {
        'AddRMSNormQuantFusionPass.__init__': '初始化：注册多种 norm+quant 模式',
        'AddRMSNormQuantFusionPass.__call__': '在 FX 图中应用 norm+quant 融合',
        'AddRMSNormQuantFusionPass._model_uses_w4a4_quant': '判断模型是否使用 w4a4 量化',
        'AddRMSNormQuantPattern.__init__': '初始化：继承 BasePattern，记录 eps',
        'AddRMSNormQuantPattern.get_inputs': '返回示例输入张量',
        'AddRMSNormQuantPattern.get_pattern': '返回 add_rms_norm_bias + quantize 模式',
        'AddRMSNormQuantPattern.get_replacement': '返回融合 npu_add_rms_norm_quant 算子的替换',
        'AddRMSNormQuantPatternWithBias.__init__': '初始化：带 bias 的 norm+quant 模式',
        'AddRMSNormDynamicQuantPattern.__init__': '初始化：动态量化 norm+quant 模式',
        'AddRMSNormDynamicQuantPatternWithBias.__init__': '初始化：动态量化带 bias 模式',
        'AddRMSNormDynamicMXQuantPattern.__init__': '初始化：MX 动态量化模式',
        'RMSNormDynamicMXQuantPattern.__init__': '初始化：仅 RMSNorm+MX 动态量化模式',
    },
    'qknorm_rope_fusion_pass.py': {
        'QKNormRopeFusionPattern.__init__': '初始化：保存 head_dim/num_heads/num_kv_heads/rope_dim',
        'QKNormRopeFusionPattern.get_inputs': '返回示例输入（qkv、q/k 权重、cos_sin、positions）',
        'QKNormRopeFusionPattern.get_pattern': '返回 Q/K 各自 rms_norm + RoPE 拼接模式',
        'QKNormRopeFusionPattern.get_replacement': '返回 split_qkv_rmsnorm_rope 算子调用',
        'QKNormRopeFusionPatternWithBias.__init__': '初始化：带 bias 的 QK-Norm+RoPE 融合模式',
        'QKNormRopeFusionPass.__init__': '初始化：注册 QK-Norm+RoPE 融合 pattern',
        'QKNormRopeFusionPass.__call__': '在 FX 图中应用 QK-Norm+RoPE 融合',
    },
    'npugraph_ex_utils_check.py': {
        'extra_stream_scope_check': '检查被匹配节点是否全部在同一 stream（排除跨流模式匹配）',
        'check_and_register_fusion_pass': '全局注册单个融合 pass（避免重复注册）',
    },
    'kv_cache_interface.py': {
        'get_storage_block_size': '返回 KV cache spec 的物理存储块大小',
        'AscendMLAAttentionSpec.storage_block_size': '返回 Ascend MLA 物理块大小（block_size//compress_ratio）',
        'AscendMLAAttentionSpec.real_page_size_bytes': '返回每个物理页占用的字节数（含 scale_dim）',
        'AscendMLAAttentionSpec.unpadded_page_size_bytes': '等同 real_page_size_bytes（未 padding）',
        'AscendMLAAttentionSpec.merge': '合并同一组内的所有 MLA spec，校验布局一致',
        'AscendMLAAttentionSpec.max_memory_usage_bytes': '估算该 spec 最大 KV 缓存占用（按 max_model_len 与 DCP）',
        'AscendSFAIndexerCacheSpec.page_size_bytes': '返回 indexer 页字节数',
        'AscendSFAIndexerCacheSpec.real_page_size_bytes': '返回 indexer 实际页字节数（含 DCP 复制份数）',
        'AscendSFAIndexerCacheSpec.merge': '合并一组内的 SFA indexer spec，校验 dtype/layout',
        'register_ascend_kv_cache_specs': '注册 Ascend 自定义 KV cache spec',
    },
    'batch_job_aware_scheduler.py': {
        'JobNameParser.parse': '从 request_id 解析 #job_name[NAME]# 前缀，含 LRU 缓存',
        'JobNameParser.remove': '从缓存移除一个某请求_id',
        'JobNameParser.clear': '清空全部缓存',
        'JobDecodeEstimator.predict': '基于 EWMA 预测下一轮该 job 的 decode token 数',
        'JobDecodeEstimator.observe': '观测真实 decode 长度，更新 EWMA',
        'JobDecodeEstimator.get_stats': '返回该 job 的统计信息',
        'BatchJobAwareRequestQueue._cdiv': '整数上除法（调度块容量计算用）',
        'BatchJobAwareRequestQueue.invalidate_cache': '失效 best-fit 缓存',
        'BatchJobAwareRequestQueue._finalize_reserve': '完成保留块计数',
        'BatchJobAwareRequestQueue._compute_one': '为单个请求计算所需 KV 块数',
        'BatchJobAwareRequestQueue._compute_all': '为请求列表汇总所需 KV 块数',
        'BatchJobAwareRequestQueue.put': '将请求插入等待队列',
        'BatchJobAwareRequestQueue.peek_best_fit_request': '取出 KV 容量最匹配的请求',
        'BatchJobAwareRequestQueue.is_empty': '返回队列是否为空',
        'BatchJobAwareRequestQueue.__len__': '返回队列长度',
        'BatchJobAwareRequestQueue.__bool__': '返回队列是否非空',
        'BatchJobAwareRequestQueue.__iter__': '迭代队列',
        'BatchJobAwareRequestQueue.add_request': '添加新请求到队列',
        'BatchJobAwareRequestQueue.prepend_request': '将请求插到队列头部',
        'BatchJobAwareScheduler.__init__': '初始化调度器：建等待队列与 job 状态缓存',
        'BatchJobAwareScheduler.schedule': '执行 LPT 调度 + 容量保留（核心入口）',
        'BatchJobAwareAsyncScheduler.schedule': '异步版本的调度入口',
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
        'RecomputeScheduler.__init__': '初始化调度器（含 DyntraLB mixin）',
    },
}


def get_desc(basename, fname):
    """Get description for a function in a file."""
    if basename not in DESCRIPTIONS:
        return ''
    descs = DESCRIPTIONS[basename]
    # 直接匹配
    if fname in descs:
        return descs[fname]
    # 类名.方法名匹配（如 AscendDSABackend.get_name -> get_name）
    for key, d in descs.items():
        if '.' in key and key.endswith('.' + fname):
            return d
    return ''


# 读取 panorama-root.html 并替换占位符
with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 函数匹配模式：实际HTML结构为 <span class="item-name">func_name<span class="item-desc">(功能说明)</span>
func_pattern = re.compile(
    r'<span class="item-name">([^<]+)<span class="item-desc">\(功能说明\)</span>'
)

counts = {'replaced': 0, 'unknown': 0}
unknown_list = []

# 我们需要根据当前所在的 file-block 来确定 basename
# 按 file-block 切片处理
# 找到所有 file-block 的位置
file_block_starts = [m.start() for m in re.finditer(r'<div class="file-block">', html)]
file_block_pattern = re.compile(r'<div class="file-name">([^<]+)</div>')

new_html_parts = []
last_idx = 0

for i, start in enumerate(file_block_starts):
    # 把前面的原文加入
    new_html_parts.append(html[last_idx:start])

    # 找到这个 file-block 的结束
    if i + 1 < len(file_block_starts):
        end = file_block_starts[i + 1]
    else:
        end = len(html)

    block = html[start:end]

    # 提取 basename
    name_match = file_block_pattern.search(block)
    file_name = name_match.group(1) if name_match else ''
    basename = os.path.basename(file_name).replace('\\', '/')

    # 局部替换函数 - 在闭包内捕获 basename
    def make_replacer(bn):
        def replacer(m):
            fname = m.group(1).strip()
            desc = get_desc(bn, fname)
            if desc:
                counts['replaced'] += 1
            else:
                counts['unknown'] += 1
                if fname not in unknown_list:
                    unknown_list.append(fname)
                desc = '(源码见对应位置:' + fname + ')'
            return '<span class="item-name">' + fname + '</span><span class="item-desc">' + desc + '</span>'
        return replacer

    new_block = func_pattern.sub(make_replacer(basename), block)
    new_html_parts.append(new_block)

    last_idx = end

new_html_parts.append(html[last_idx:])
new_html = ''.join(new_html_parts)

with open(r'D:\demo\202609\vllm-ascend\code-docs\panorama-root.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f'Replaced: {counts["replaced"]}')
print(f'Unknown (left as placeholder): {counts["unknown"]}')
print(f'Sample unknown functions: {unknown_list[:30]}')
print(f'Final HTML length: {len(new_html)}')