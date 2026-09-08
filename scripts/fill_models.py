import os, re

# 为 models 模块添加描述
MODELS_DESCRIPTIONS = {
    '__init__.py': {
        'register_model': '将模型架构名注册到 vLLM ModelRegistry（Kimi/DeepSeek/MiniMax/Qwen等）',
    },
    'kimi_k3.py': {
        '_apply_ascend_attn_res': '应用 Kimi 学习到的残差混合（用原生 NPU ops）',
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
    'kimi_k3.py': {
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
}


def process_html(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    counts = {'replaced': 0, 'unknown': 0, 'total_placeholders': 0}
    unknown_list = []

    func_pattern = re.compile(
        r'<span class="item-name">([^<]+)<span class="item-desc">\(功能说明\)</span>'
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
        dirname = os.path.basename(os.path.dirname(file_name))

        placeholders = func_pattern.findall(block)
        counts['total_placeholders'] += len(placeholders)

        def make_replacer(fn, ext):
            def replacer(m):
                fname = m.group(1).strip()
                desc = ext.get(fname, '')
                if desc:
                    counts['replaced'] += 1
                else:
                    counts['unknown'] += 1
                    if fname not in unknown_list:
                        unknown_list.append(fname)
                    desc = '(参见源码:' + fname + ')'
                return '<span class="item-name">' + fname + '</span><span class="item-desc">' + desc + '</span>'
            return replacer

        # Try composite key
        keys_to_try = [file_name, basename, f'{dirname}\\{basename}', f'{dirname}/{basename}']
        merged = {}
        for k in keys_to_try:
            if k in MODELS_DESCRIPTIONS:
                merged.update(MODELS_DESCRIPTIONS[k])

        new_block = func_pattern.sub(make_replacer(file_name, merged), block)
        new_html_parts.append(new_block)
        last_idx = end

    new_html_parts.append(html[last_idx:])
    new_html = ''.join(new_html_parts)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    return counts, unknown_list


path = r'D:\demo\202609\vllm-ascend\code-docs\panorama-models.html'
counts, unknowns = process_html(path)
print(f'panorama-models.html: Total={counts["total_placeholders"]}, Replaced={counts["replaced"]}, Unknown={counts["unknown"]}')
if unknowns:
    print(f'Sample unknown: {unknowns[:15]}')