import os, re

src = r'D:\demo\202609\vllm-ascend\vllm-ascend-main\vllm_ascend'

# 第二轮描述：补全剩余函数
# 基于平台.py, ascend_config.py, ascend_forward_context.py 等的源码阅读
EXTRA_DESCRIPTIONS = {
    'platform.py': {
        '_ensure_global_patch': '对 vllm.platform 模块做全局补丁替换（适用 RL 场景）',
        'register': 'vllm_ascend 插件入口：按顺序注册 connector、model_loader、service_profiling 等',
        'register_connector': '把自定义 KV connector 子类注册到 vllm 的 connector 注册表',
        'register_model_loader': '注册自定义 model loader（处理 HuggingFace 之外的模型加载）',
        'register_service_profiling': '在配置目录生成 service_profiling_symbols YAML（',
        'register_model': '将模型架构名注册到 vLLM ModelRegistry（供 load 时查找）',
        'NPUPlatform.manual_seed_all': '占位方法，NPU 当前不实现随机种子设置',
        'NPUPlatform.is_sleep_mode_available': 'NPU 平台支持 sleep/wake，返回 True',
        'NPUPlatform.is_cumem_allocator_available': 'NPU 提供 CaMemAllocator，返回 True',
        'NPUPlatform.is_pin_memory_available': 'NPU 支持 pinned memory，返回 True',
        'NPUPlatform.opaque_attention_op': 'NPU 自定义 attention 算子对上游 opaque，返回 True',
        'NPUPlatform.support_hybrid_kv_cache': 'NPU 支持混合 KV cache（全 attn + 线性），），返回 True',
        'NPUPlatform.support_static_graph_mode': 'NPU 支持静态图模式，返回 True',
        'NPUPlatform.use_custom_op_collectives': 'NPU 使用自定义算子实现集合通信，返回 True',
        'NPUPlatform.get_device_capability': 'NPU 无 compute capability，返回 None',
        'NPUPlatform.get_device_name': '返回 torch.npu.get_device_name() 的字符串',
        'NPUPlatform.inference_mode': '上下文管理器：进入 torch.inference_mode()',
        'NPUPlatform.set_device': '调用 torch.npu.set_device() 切换当前 NPU 设备',
        'NPUPlatform.register_custom_kv_cache_specs': '调用 core.register_ascend_kv_cache_specs() 注册 Ascend 特有的 KV cache spec',
        'NPUPlatform.get_pass_manager_cls': '返回 GraphFusionPassManager 的导入路径',
        'NPUPlatform.get_compile_backend': '返回 AscendCompiler 的导入路径',
        'NPUPlatform.get_punica_wrapper': '返回 PunicaWrapperNPU 的导入路径（LoRA 拼接）',
        'NPUPlatform.get_current_memory_usage': '重置 NPU peak 后返回 max_memory_allocated',
        'NPUPlatform.get_device_communicator_cls': '返回 NPUCommunicator 的导入路径',
        'NPUPlatform.get_static_graph_wrapper_cls': '返回 ACLGraphWrapper 的导入路径',
        'NPUPlatform.get_device_uuid': '从 torch.npu 读取 device uuid',
        'NPUPlatform.get_device_total_memory': '占位：torch_npu 不允许重复初始化，返回 NotImplementedError',
        'NPUPlatform.get_attn_backend_cls': '根据 use_mla/use_sparse/use_pcp/use_dcp 返回 attention backend 类',
        'NPUPlatform.import_kernels': '懒注册 vllm_ascend_C 自定义算子（避免 ASCEND_RT_V_V 提前初始化）',
        'NPUPlatform.pre_register_and_update': 'vLLM 启动前调用：应用全局补丁 + 注册 ascend 量化方法到命令行选项',
        'NPUPlatform.apply_config_platform_defaults': '注入 Ascend 特定的 cudagraph 默认值',
        'NPUPlatform.num_compute_units': '返回 Cube Core 数（fallback 到 vector core 或 24）',
        'NPUPlatform.update_block_size_for_backend': '对 mamba block size 进行与 block_size 对齐校验',
        'NPUPlatform._validate_indexer_pp_config': '校验 PP 拆分时 Indexer/IndexCache 是否被不当地跨 stage',
        'NPUPlatform.check_and_update_config': 'vLLM 启动入口：日志、并行、量化、cudagraph、worker、scheduler 链式校验与设置',
        'NPUPlatform.set_additional_forward_context': '为 V2 model runner 计算 moe_comm_type/mc2_mask 等额外 forward 字段',
    },
    'ascend_config.py': {
        'is_mega_moe_supported': '判断当前运行时是否可用 MegaMoe fused MC2（基于环境/import 检查）',
        'validate_additional_config_bool': '在 config 初始化前对 bool 字段做 pydantic 严格校验',
        '_apply_unsupported_hardware_downgrade_and_static_kernel_check': '关闭 npugraph_ex/static_kernel（若硬件不支持）',
        '_validate_config': 'EplbConfig 验证：文件路径、间隔、policy、heat_collection_stage 等',
        '_validate': 'RejectionSamplerConfig 验证：posterior_threshold/alpha 范围',
        'apply': 'RlConfig.apply：开启 RL 时覆盖 weight_nz_mode、关闭 expandable_segments、设置 batch-invariant  ',
        '_validate_user_input_ranges': 'AscendConfig 验证：weight_nz_mode、mega_moe 启用回退、envs  ',
        'derive_and_validate': 'AscendConfig 主校验：mutex、SP、profiling_chunk、PD tp 比例、enable_kv_nz 前置条件等',
        '_validate_mc2_comm_alg': '校验 mc2_comm_alg 选项与硬件、专家数、fused MC2 是否冲突',
        '_validate_sparse_c8_kv_offload_compatibility': '校验 sparse C8 KV cache 与 sparse SFA C8 主 cache 的互斥',
        '_check_mooncake_c8_kv_cache_quant': '校验 MooncakeConnector + C8 KV 量化在 GQA 模型上的不兼容性',
        '_check_mix_placement': '校验 mix_placement 与 shared expert DP / multistream overlap 的互斥',
        '_is_megamoe_supported_by_config': '按 hidden/中间/量化类型判断模型是否能启用 MegaMoe',
        '_materialize_dump_config_to_file': '把 additional_config.dump_config（内联 dict）物化到 msprobe_dump_config.json',
        '_resolve_dump_config_path': '从 additional_config 解析 dump_config_path/dump_config 并检查互斥',
        '_has_sparse_li_c8_layer_config': '判断 quant_description 是否包含 sparse LI C8 索引器字段',
        '_parse_sparse_li_c8_layers_from_quant_config': '从 quant_description 中提取 indexer C8 量化的层 id 与名称',
        'is_sparse_li_c8_layer': '判断某层是否属于已配置的 sparse LI C8 索引器量化层',
        '_get_compile_ranges': '读 compile_ranges_endpoints',
        '_set_compile_ranges': '写 compile_ranges_endpoints',
        'update_compile_ranges_split_points': '占位：当前 Ascend 不自定义 split point',
        'get_mc2_comm_alg': '返回 MC2 通信算法（fullmesh/hierarchy 等），A3 + fullmesh 映射为 fullmesh_v1',
        'AscendCompilationConfig._apply_unsupported_hardware_downgrade_and_static_kernel_check': '关闭不支持的 npugraph_ex / static_kernel 并校验二者一致性',
        'EplbConfig._validate_config': '校验 expert_map_path、间隔、policy、heat_collection_stage、env 变量',
        'RejectionSamplerConfig._validate': '校验 posterior_threshold (0,1]、与 posterior >= >= 0',
        'RlConfig.apply': '开启 RL 时设置 weight_nz_mode=0、关闭 expandable_segments、可选 batch-invariant、',
        'AscendConfig._validate_user_input_ranges': '校验 weight_nz_mode 与 enable_fused_mc2；根据模型架构禁用 MegaMoe',
        'AscendConfig.derive_and_validate': '业务校验：mutex、降级、profile chunk 与 balance 不并存、SP 与 Eplb 互锁等',
        'AscendConfig._validate_mc2_comm_alg': '校验 mc2_comm_alg 硬件支持性与专家数限制',
        'AscendConfig._validate_sparse_c8_kv_offload_compatibility': '校验 sparse C8 KV offload 与 sparse SFA C8 主 cache 不并存',
        'AscendConfig._check_mooncake_c8_kv_cache_quant': 'GQA + Mooncake 禁用 C8 KV 量化（int8 会被当成 bf16 重解释）',
        'AscendConfig._check_mix_placement': 'mix_placement 与 shared-expert-DP/multistream overlap 互斥',
        'AscendConfig._is_megamoe_supported_by_config': '依据 hidden/moe 中间/量化判断 MegaMoe 可用性',
        'AscendConfig._materialize_dump_config_to_file': '把 dump_config 写入 msprobe_dump_config.json',
        'AscendConfig._resolve_dump_config_path': '解析 dump_config_path/dump_config 并检查互斥',
        'AscendConfig._has_sparse_li_c8_layer_config': '判断 quant_description 包含 indexer C8 字段',
        'AscendConfig._parse_sparse_li_c8_layers_from_quant_config': '提取 indexer C8 量化的层 id 与名称',
        'AscendConfig.is_sparse_li_c8_layer': '判断某层是否为 sparse LI C8 量化层',
        'AscendConfig._get_compile_ranges': '读 compile_ranges_endpoints',
        'AscendConfig._set_compile_ranges': '写 compile_ranges_endpoints',
        'AscendConfig.update_compile_ranges_split_points': '占位：不设置 split point',
        'AscendConfig.get_mc2_comm_alg': '返回 MC2 通信算法（fullmesh/hierarchy 等），A3 + fullmesh 映射为 fullmesh_v1',
        'EplbConfig._validate_config': '校验 EPLB 文件、间隔、env 变量',
        'RejectionSamplerConfig._validate': '校验 posterior_threshold / alpha 范围',
        'AscendConfig.__init__': '初始化所有字段与 derived 子（注意 deprecated 警告）',
    },
    'ascend_forward_context.py': {
        '_is_decode_only_node': '判断当前节点是否为 P/D 分离中的 decode-only 节点',
        'check_extra_attr': '校验属性名是否在允许的 extra forward context 字段名单内',
        '_ctx': '获取当前 forward context（内部 helper）',
        '__getattr__': '代理属性访问到 vllm forward context 或 V2 additional_kwargs',
        '_ExtraForwardContextProxy.__getattr__': '读取额外 forward 上下文字段（V2 走 additional_kwargs）',
        '_ExtraForwardContextProxy.__setattr__': '写入额外 forward 上下文字段（V2 走 additional_kwargs）',
        '_ExtraForwardContextProxy.check_extra_attr': '校验属性名是否在合法 extra attrs 名单内',
        '_ExtraForwardContextProxy._ctx': '获取 vllm 的当前 forward context',
    },
    'meta_registration.py': {
        'register_meta_if_necessary': '检查后若 meta 实现尚未注册，则把 Python meta 函数注册到指定命名空间',
        'bgmv_expand_meta': '返回与 y 同形同 dtype 的空张量（bgmv_expand meta 实现）',
        'sgmv_expand_meta': '返回与 y 同形同 dtype 的空张量（sgmv_expand meta 实现）',
    },
    'envs.py': {
        '__getattr__': '懒取值：从 env_variables 字典中读取环境变量并调用对应 lambda',
        '__dir__': '列出全部环境变量名（用于 tab 补全等）',
    },
    'utils.py': {
        'extract_dsv4_layer_index': '提取 DSV4 的 per-layer 数组索引（MTP 层位于主模型层之后）',
        'get_dsv4_spec_layer_idx_from_weight_name': '从权重名（如 mtp.0.weight）中提取 MTP 本地层 idx',
        'get_dsv4_compress_ratio': '返回 DSV4 指定层压缩比（未配置或越界返回 0）',
        'model_uses_sfa_sparse': '判断模型是否使用 SFA 稀疏注意力（带 index_topk 且无 compress_ratios）',
        'enable_sfa_dcp_replicated_indexer': '判断是否启用 SFA DCP 复制 indexer（DCP>1 且 SFA 稀疏模型）',
        'clear_enable_sp': '清空 enable_sp / enable_dsa_cp 等 lru_cache，便于重新读取配置',
        'is_rc_device': '检测 310P NPU 是否在 Root Complex 模式（通过 lspci 输出判断）',
        '_mark_op_side_effectful': '把 torch.ops 节点标记为带副作用，避免 FX / Inductor DCE 或重排',
        '_ensure_device_print_registered': '确保 _C_ascend.device_print 自定义算子已注册 side-effect',
        'device_print': '从 device 回调打印一个标量/字符串/张量（用于 NPU graph 内调试）',
        '_should_trans_nz': '判断是否应把权重转换为 NZ 布局（基于 dtype、硬件 profile、weight_nz_mode）',
        'maybe_trans_nz': '必要时调用 npu_format_cast 把权重转 NZ 布局',
        '_round_up': '把 x 上取整到 align 的倍数',
        '_prepend_env_path': '把路径插入环境变量 PATH 类字段的前面（去重）',
        'bootstrap_custom_op_env': '把 _cann_ops_custom vendor 路径加入 ASCEND_CUSTOM_OPP_PATH（可选 LD_LIBRARY_PATH）',
        '_custom_pad': '对张量按 pad_dims 末尾填充',
        '_custom_reshape': 'reshape 张量到 target_shape',
        '_custom_transpose': 'transpose两个维度',
        'nd_to_nz_2d': '把 2D 张量从 ND 布局转换为 NZ 布局',
        'nd_to_nz_spec': '构造掩码张量并以 NZ 布局返回',
        'aligned_16': '把张量第 0 维向上对齐到 16（310P 专用）',
        'enable_custom_op': '懒加载 vllm_ascend_C 自定义算子（必要时回退到 vendor 路径）',
        'find_hccl_library': '查找 HCCL 库文件（HCCL_SO_PATH 或 torch 自带 libhccl.so）',
        'current_stream': '返回当前 NPU stream（带缓存，避免重复构造）',
        'global_stream': '返回全局 NPU stream（懒初始化）',
        'shared_experts_calculation_stream': '返回 shared experts 计算专用 NPU stream',
        'cp_chunkedprefill_comm_stream': '返回 CP chunked prefill 通信专用 NPU stream',
        'attention_calculation_stream': '返回 attention 计算专用 NPU stream',
        'adapt_patch': '全局或/进程级应用 vllm_ascend 的 monkey-patch',
        'setup_ascend_local_comm_res': '从配置文件加载 A5 endpoint JSON 到 ASCEND_LOCAL_COM_VL_RES',
        'vllm_version_is': '比较当前 vllm 版本是否等于 target（支持 VLLM_VERSION 环境覆盖）',
        'get_max_hidden_layers': '递归查找 hf_config 中所有 num_hidden层，取最大值',
        'update_cudagraph_capture_sizes': '更新 compilation_config 的 cudagraph capture sizes 与 max',
        'dispose_tensor': '释放张量占用的存储（置空为 (0,)）',
        'register_ascend_customop': '把 Ascend 自定义算子映射到 CustomOp.register_oot（可能覆盖 310p 兼容实现）',
        'lmhead_tp_enable': 'lmhead 是否启用细粒度 TP',
        'embedding_tp_enable': 'embedding 是否启用细粒度 TP',
        'oproj_tp_enable': 'o_proj 是否启用细粒度 TP',
        'olora_tp_enable': 'olora 是否启用细粒度 TP（TP size > 1）',
        'mlp_tp_enable': 'mlp 是否启用细粒度 TP',
        'enable_sp': '是否启用 sequence parallel moe',
        'shared_expert_dp_enabled': 'shared expert 是否启用 DP',
        'is_score_encoder_cache_manager': '判断 EC manager 是否为 ScoreEncoderCacheManager',
        'is_moe_model': '判断模型是否是 MoE（递归查找 expert 键）',
        'is_drafter_moe_model': '判断 draft 模型是否 MoE（特判 extract_hidden_states / Eagle3DeepseekV2ForCausalLM / Step3p5MTP）',
        '_is_contain_expert': '递归检查 config 字典是否包含 expert 键',
        'is_vl_model': '判断模型是否是 VL（多模态，hf_config 与 hf_text_config 不同）',
        'is_moe_model': '判断当前模型是否为 MoE（递归扫描 expert 键）',
        'check_kv_extra_config': '校验 P/D 分离下 P/D 的 KV pool 一致性 + engine_id 唯一化',
    },
    'logger.py': {
        '_use_color': '根据 envs 判断是否在控制台启用彩色输出',
        '_is_ascend_module': '判断日志调用的文件路径是否来自 vllm_ascend',
        '_infer_module_name': '从文件路径推断模块名（如 platform.py -> platform）',
        '_format_with_ascend_prefix': '为 ascend 模块日志添加 [vllm-ascend] / [module] 前缀',
        'RotatingAscendFileHandler.__init__': '初始化：生成基于 timestamp+pid 的日志文件名',
        'RotatingAscendFileHandler.emit': '写入前检查文件大小，超过上限则触发 rotate',
        'RotatingAscendFileHandler._rotate': '关闭当前 stream，按序号递增生成新文件',
        '_setup_file_logging': '添加 RotatingAscendFileHandler 到 vllm / vllm_ascend logger',
        'configure_ascend_file_logging': '根据 ascend_config.ascend_log_path 重新设置文件日志',
        'configure_ascend_logging': '为 vllm_ascend logger 添加控制台 handler（带 Ascend 前缀与颜色）',
    },
    'config_utils.py': {
        'config': '构造 vllm 兼容的 config dataclass（避免导入 vllm.config 引发循环）',
    },
    'cpu_binding.py': {
        'is_arm_cpu': '判断当前 CPU 架构是否为 ARM（aarch64/arm64/arm*）',
        'execute_command': '在 C locale 下执行 shell 命令并返回 (output, return_code)',
        'DeviceInfo.__init__': '初始化：从 npu-smi 收集 NPU 拓扑与允许 CPU 列表',
        'DeviceInfo.split_npu_smi_header': '按多个空格分隔 npu-smi 表头',
        'DeviceInfo.is_cpu_list': '判断字符串是否是合法的 CPU 列表格式（"0-3,5,7"）',
        'DeviceInfo.expand_cpu_list': '把 "0-3,5,7" 字符串展开为 [0,1,2,3,5,7] 的 CPU id 列表',
        'DeviceInfo.get_all_logic_npus': '从 npu_map_info 中收集全部逻辑 NPU id',
        'DeviceInfo.get_npu_map_info': '通过 npu-smi info -m 解析 NPU 拓扑映射',
        'DeviceInfo.resolve_logic_id': '根据 npu_id 与可选 chip_id 解析逻辑 NPU id',
        'DeviceInfo.get_running_npus': '从 npu-smi info 解析当前进程使用的 NPU id 列表',
        'DeviceInfo.parse_allowed_cpus': '从 /proc/self/status 读取 Cpus_allowed_list',
        'DeviceInfo.parse_topo_affinity': '从 npu-smi info -t topo 解析每个 NPU 的 NUMA CPU 亲和性',
        'CpuAlloc.__init__': '初始化 CPU 池为 rank_id 分配数据结构',
        'CpuAlloc.cpu_to_mask': '把 CPU id 转换为 smp_affinity 十六进制掩码',
        'CpuAlloc.get_threads_map': '从 ps -Te 输出解析 acl_thread / release_thread',
        'CpuAlloc.bind': '用 taskset 把进程或线程绑定到指定 CPU 列表',
        'CpuAlloc.average_distribute': '在多 NPU 间平均分配一组 CPU',
        'CpuAlloc.extend_numa': '若列表全在同一 NUMA，扩展到下一 NUMA 的允许 CPU',
        'CpuAlloc.build_cpu_node_map': '从 lscpu -e 解析 cpu→numa 节点映射',
        'CpuAlloc.parse_threads_per_core': '从 lscpu 解析 Thread(s) per core',
        'CpuAlloc.get_uvb_poll_window_threads': '从 ps 输出提取 uvb_poll_window 线程 id',
        'CpuAlloc.get_ascend_950_cluster_size': '计算 Ascend 950 集群大小（每 cluster CPU 数）',
        'CpuAlloc.get_single_numa_node': '判断列表中所有 CPU 是否在同一 NUMA 节点',
        'CpuAlloc.bind_uvb_poll_window_threads': '把 uvb_poll_window 线程绑定到 NUM0 上可用 CPU',
        'CpuAlloc.build_ascend_950_cpu_pools': '为 Ascend 950 构建每 NPU 的 CPU 集群池',
        'CpuAlloc.build_global_slice_cpu_pool': '全局按逻辑 NPU id 切片 CPU 池（跨进程不重叠）',
        'CpuAlloc._binding_mode': '返回当前硬件 profile 的 CPU 绑定模式',
        'CpuAlloc._uses_cluster_cpu_topology': '是否使用 Ascend 950 的 cluster CPU 拓扑',
        'CpuAlloc._reserve_irq_cpus': '是否预留 IRQ 绑定所需的 CPU',
        'CpuAlloc._min_cpus_per_npu': '每 NPU 所需最少 CPU 数（含或不含 IRQ）',
        'CpuAlloc.build_cpu_pools': '依据模式构建 CPU 池（cluster topology / global slice / topo affinity）',
        'CpuAlloc._build_topo_affinity_cpu_pool': '基于 npu-smi topo 构建每 NPU CPU 池（按 NUMA 亲和扩展）',
        'CpuAlloc.allocate': '为每 NPU 划分 main/acl/release CPU',
        'CpuAlloc._allocate_ascend_950_roles': 'Ascend 950：所有 CPU 都给 main（无 acl/release 角色）',
        'CpuAlloc._allocate_default_roles': '默认：从尾部预留 acl/release CPU（可选 IRQ 预留 2 个）',
        'CpuAlloc.print_plan': '打印当前 rank 的 CPU 分配计划',
        'CpuAlloc._print_ascend_950_plan': '打印 Ascend 950 模式下 main CPU 列表',
        'CpuAlloc._print_default_plan': '打印 main/acl/release CPU 列表',
        'CpuAlloc.bind_memory': '调用 migratepages 把进程内存迁移到目标 NUMA 节点',
        'CpuAlloc.bind_threads': '绑定主进程与 acl/release 子线程，并迁移内存',
        'CpuAlloc._bind_default_threads': '默认线程绑定：main + acl_thread + release_thread + memory',
        'CpuAlloc.bind_ascend_950_threads': 'Ascend 950 线程绑定：仅 main + memory',
        'CpuAlloc.bind_npu_irq': '把 NPU 的 sq_send_trigger_irq / cq_update_irq 绑定到保留 CPU',
        'CpuAlloc.run_all': '一站式执行：构建池、分配、打印、绑定线程、绑定 IRQ',
        'bind_cpus': '为给定 rank 创建 CpuAlloc 并执行完整绑定流程',
    },
    'profiling_config.py': {
        'get_config_dir': '返回 ~/.config/vllm_ascend/ 目录路径',
        '_cleanup_temp_file': '删除临时文件（若存在）',
        'generate_service_profiling_config': '在 ~/.config/vllm_ascend/ 下生成（若不存在）service_profiling_symbols.<vllm_version>.yaml',
    },
    'batch_invariant.py': {
        'add_rms_norm': '拆分 AddRmsNorm 为 add + rms_norm（保证 batch-invariant）',
        'reduce_sum': '对 NPU 上指定 dim 调用 batch-invariant reduce_sum（CPU 仍走 torch.sum）',
        'override_envs_for_invariance': '设置 batch-invariant 所需环境（HCCL/LCCL deterministic、torch deterministic、weight_nz_mode=0）',
        'enable_batch_invariant_mode': '把 aten::mm/matmul/addmm/bmm/softmax 等注册为 batch-invariant 实现（优先 AscendC，其次 Triton）',
        'init_batch_invariance': '检查 VLLM_BATCH_INVARIANT 后调用 override_envs_for_invariance + enable_batch_invariant_mode',
    },
}

# 读取 panorama-root.html
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

    # 遍历 EXTRA_DESCRIPTIONS 找到匹配项（basename 精确匹配）
    extra = EXTRA_DESCRIPTIONS.get(basename, {})

    def make_replacer(bn, ext_map):
        def replacer(m):
            fname = m.group(1).strip()
            marker_fname = m.group(2).strip()
            desc = ext_map.get(fname, '')
            if not desc:
                # 类名.方法名匹配
                for key, d in ext_map.items():
                    if '.' in key and key.endswith('.' + fname):
                        desc = d
                        break
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

print(f'Replaced (second round): {counts["replaced"]}')
print(f'Unknown remaining: {counts["unknown"]}')
print(f'Sample still-unknown: {unknown_list[:20]}')
print(f'Final ( ( remaining in HTML:', new_html.count('(源码见对应位置:'))
print(f'Final (功能说明) remaining:', new_html.count('(功能说明)'))