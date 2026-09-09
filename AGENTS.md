# AGENTS.md - vLLM Ascend 文档项目

## 项目目标

为 vLLM-Ascend 源码（华为昇腾 NPU 后端）生成完整的中文 HTML 文档：
1. **详细模块文档**（detailed/）：带 mermaid 图的架构讲解
2. **全景 API 参考**（panorama/）：纯文本函数级 API 参考，每个函数带真实中文描述 + 代码行数

## 目录结构

```
D:\demo\202609\vllm-ascend\
├── AGENTS.md                 # 本文件
├── code-docs\                # ★ 文档输出目录（最终交付物）
│   ├── index.html            # 总览首页（导航入口）
│   ├── assets\
│   │   ├── styles.css        # 全局样式
│   │   └── navigation.js     # 导航高亮脚本
│   ├── detailed\             # 详细模块文档（15 个，带 mermaid 图）
│   │   ├── attention.html    # 注意力机制
│   │   ├── compilation.html  # 图编译
│   │   ├── core.html         # 核心模块
│   │   ├── distributed.html  # 分布式通信
│   │   ├── lora.html         # LoRA 适配
│   │   ├── models.html       # 模型定义
│   │   ├── ops.html          # 自定义算子
│   │   ├── patch.html        # Patch 机制
│   │   ├── quantization.html # 量化
│   │   ├── sample.html       # 采样
│   │   ├── source-guide.html # 源码导读
│   │   ├── spec-decode.html  # 投机解码
│   │   ├── upstream.html     # 上下游衔接
│   │   ├── usage.html        # 使用指南
│   │   └── worker.html       # Worker 执行器
│   └── panorama\             # 全景 API 参考（9 个，纯文本）
│       ├── panorama.html           # 索引页
│       ├── panorama-root.html      # 根模块（515 函数）
│       ├── panorama-attention.html # attention（378 函数）
│       ├── panorama-core.html      # core（136 函数）
│       ├── panorama-models.html    # models（286 函数）
│       ├── panorama-ops.html       # ops（494 函数）
│       ├── panorama-worker.html    # worker（329 函数）
│       ├── panorama-distributed.html # distributed（909 函数）
│       └── panorama-rest.html      # 其余模块（1261 函数）
├── compare\                    # ★ 专题深度分析（平台对比系列，按需新增）
│   └── kimi-k3-platform-compare.html  # Kimi K3 三平台对比（含函数级调用链+软件栈分层）
├── stories\                    # ★ 需求故事（一个 HTML 讲清一个需求，按需新增）
│   ├── stories.html                   # 需求故事目录
│   └── perf-kda-gate-overlap.html     # 首篇：KDA 门控投影融合与双流重叠（PR #15416）
├── scripts\                  # 工具脚本（生成器/检查器/发送器）
│   └── data\
│       ├── func_meta.json    # AST 提取的函数元数据（428 文件 / 4145 函数）
│       ├── mod_summary.json  # 模块摘要
│       └── api_output.txt    # API 提取原始输出
├── archive\                  # 历史打包 ZIP
├── vllm-ascend-main\         # vllm-ascend 源码仓库
│   └── vllm_ascend\          # ★ 文档分析的源码目录（530 .py 文件）
└── vllm\                     # vLLM 上游源码（对照用）
```

## 关键路径

| 用途 | 路径 |
|------|------|
| 源码（文档对象） | `vllm-ascend-main\vllm_ascend\` |
| 函数元数据 | `scripts\data\func_meta.json` |
| 文档输出 | `code-docs\` |
| 全景页生成脚本 | `scripts\generate_*.py`、`scripts\build_func_meta_v2.py` |

## 质量规范（强制）

1. **描述必须真实**：禁止 `见源码:函数名`、`(功能说明)`、`TODO` 等占位符。
   描述必须来自：真实阅读源码 / 函数 docstring 翻译 / 基于代码结构的实际分析。
   函数条目只保留 `名称 + [N行]`，信息量放在**文件级讲解**（不要硬凑「返回注册名称」这类无信息量描述）。
2. **每个函数必须带行数**：格式 `[N行]`。
3. **链接必须可点击**：修改目录结构后必须全量检查 href/src 引用，
   使用 `scripts\check_links.py` 验证 0 死链。
4. **全景页不加 mermaid**：panorama 页面是纯文本 API 参考。
5. **mermaid 图规范**（仅 detailed 与 index 页面）：浅色背景、一图一编号、字体正常大小，
   布局按内容类型选择：
   - **结构/层级/分类类**（目录结构、模块组成、硬件/后端/模型家族、协作关系）→ **LR**
     （TD 会把长标签挤成窄条看不清，如 index 图2 目录结构）；
   - **流程/决策类**（注册流程、选择逻辑、请求处理）→ **TD**；
   - 口诀：**分叉展示用 LR，先后动作用 TD**。
6. **页面宽度统一 1200px 且水平居中**：所有页面内容宽度必须一致，不允许全屏与限宽混用
   （有 .container 用 max-width:1200px + margin:0 auto；body 直接子元素布局用
   `body>*{max-width:1200px !important;margin-left:auto !important;margin-right:auto !important;}`，
   **必须带 !important**，否则会被 `.module{margin:18px 0}` 这类简写覆盖导致限宽不居中）。
7. **打包必须带源码**：否则「查看源码」链接全部失效（见设计文档第 6 节）。

## 设计文档

> 页面布局、mermaid 规范、宽度规范、打包结构、历史问题档案的完整设计：
> **[docs\documentation-design.md](docs\documentation-design.md)** —— 改文档先改设计文档，再动代码。

## Agent 工作要求与经验教训（必读）

> **[docs\agent-requirements-lessons.md](docs\agent-requirements-lessons.md)** —— 2026-09 GLM-5.1 精度定位会话沉淀，任何 CI 排查 / 归因分析 / 专题报告任务开工前必读。核心条款：
> 1. **分析不武断**：先做全局对照矩阵（组网 × 日期、多模型对照组），每个嫌疑逐个验证 diff，不许凭标题排除；
> 2. **推理链可追问**：声称"只差 X"必须核对 commit 区间（双变量要声明）；全零 = 系统性机制、中间分 = 渐进机制，得分形态本身是证据；归因面必须与"谁坏谁不坏"自洽；
> 3. **现象与怀疑分离**：现象页只写事实（日志正常/异常、组网×日期、提交记录、评估链路），归因全部进怀疑页；每方向末尾给小结；
> 4. **表格逐个核实**："测不测精度"等标注必须逐 yaml 审计，不许凭印象；重点对象 ★ 标注并写明对照关系；
> 5. **链接齐全**：commit/PR/run/job/yaml 全部加 GitHub 原始链接（commit 短链注意分仓库）；
> 6. **时间线核对**：每个怀疑对象必须回答"为啥能和现象时间对上"，已排除假设附排除依据；
> 7. CI 排查套路：jobs API 矩阵 → job 日志（curl -L）→ 工件解包 → `vLLM server version` 行确认上游版本 → main2main 指针文件（.github/vllm-main-verified.commit）→ 配置双轨制（OBS ≠ repo yaml）→ 2×2 因子对照；
> 8. 深度排查直接 git clone 完整仓库（token 嵌 URL）本地分析；日志/工件下载用 `curl.exe -sL`；
> 9. 页面写完：语法检查 → 截图 → MiniMax 图片理解逐项验证；
> 10. 任何进展先发邮件归档。

## 环境注意事项

- **Shell 是 PowerShell 5.1**：不支持 `&&`、`||`、heredoc、`head`；
  多行 Python 代码必须写成 .py 文件再执行，不要用 `python -c "多行代码"`（转义会出错）。
- **Python 3.14**：`ast.Str` 已移除，只用 `ast.Constant`。
- **无 rg/grep 命令**：内容搜索用 Python 脚本或 Grep 工具。
- **长任务必须后台运行**（Start-Process），禁止前台跑长任务、禁止 Start-Sleep 串联命令。

## 邮件发送

- 发件：`18913980939@163.com`（SMTP SSL 465，授权码见 scripts\send_*.py）
- 收件：`125987347@qq.com`
- 附件名必须英文；HTML 卡片式布局（一列式，行式展示，无多列表格）
- **任何进展先发邮件，再进行下一步**

## 当前状态（2026-09-04）

- [x] 目录结构化完成（code-docs/assets/detailed/panorama）
- [x] 根目录清理完成（scripts/、archive/ 归位）
- [x] 40 个死链全部修复（0 死链，check_links.py 验证 727 链接）
- [x] 652 条 `见源码:xxx` 假描述全部清除（函数条目只保留名称+行数）
- [x] 457 个文件全部有文件级真实讲解（基于真实源码阅读撰写，
      存于 scripts\data\file_descs.json，注入脚本 inject_file_descs.py）
- [x] 每个文件名旁新增「查看源码」跳转链接（397 个，指向
      vllm-ascend-main\vllm_ascend\ 真实源码）
- [x] panorama-root.html 与模块页重复的 24 个文件块已去重
      （compilation 的 14 个文件保留在 root 页）
- [x] panorama.html 索引页重做：每模块真实介绍 + 统计 + 跳转按钮 + 返回首页导航
- [x] index.html「二、项目文件结构」新增「全景源码导航」入口卡片
- [x] 结构类 mermaid 图 TD→LR（index 6 图 + detailed 16 图，共 22 图）
- [x] 全部页面宽度统一 1200px（8 个无宽度页面修复 + source-guide 1100→1200）
- [x] 统一设计文档建立：docs\documentation-design.md

## 文档维护要点

- 设计文档（先读再改）：`docs\documentation-design.md`
- 文件级讲解 JSON：`scripts\data\file_descs.json`（457 条，键为源码相对路径）
- 修改讲解后重跑：`python scripts\inject_file_descs.py`（幂等，全量重新注入）
- 源码变更后重跑：`python scripts\gen_source_viewer.py`（重新生成 src/*.js 数据文件）
- 修改目录结构后必跑：`python scripts\check_links.py`（要求 0 死链）+
  `python scripts\check_viewer_links.py`（457 个查看链接的数据文件必须齐全）
- 假描述检查：`python scripts\quantify_fake2.py`（要求 0 条「见源码」）
- 打包发送：`python scripts\send_docs_final.py`（包内带 src-viewer.html + src\ 数据 +
  assets\highlight\，不带原始 .py；「查看源码」统一走单 HTML 查看器）

## 远程同步

- 仓库：`github.com/ThinkInFuture/vllm_study`（main 分支，公开）
- 同步范围（保持项目根目录格式）：AGENTS.md + docs\ + code-docs\（含 src\ 数据 + assets\highlight\）+ scripts\ + precision-rca\（分析产物，推前脱敏 token；**不含** vllm-ascend-git\ 克隆）；
  **不推**源码目录与 zip。
- **强制脱敏**：lessons 文档的 GitHub PAT、scripts 的 SMTP 授权码，staging 副本里替换为占位符后才可提交。
- 通道：github.com 主站不可达时走 api.github.com Git Data API（blob→tree→commit→ref；
  空仓库先 Contents API 播种；ref 冲突用 force+完整 40 位 sha）。详见设计文档 7b 节。
