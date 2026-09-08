# vLLM Ascend 文档系统 · 统一设计文档

> 本文档是 code-docs 文档系统的唯一设计权威。任何页面/样式/布局/打包改动先改本文档，再动代码。
> AGENTS.md 从「设计文档」一节导航到这里。

## 1. 目标与总体结构

为 vLLM-Ascend 源码（`vllm-ascend-main/vllm_ascend/`，530 个 .py 文件）生成两套中文 HTML 文档：

```
code-docs/
├── index.html              # 总览首页：架构讲解（mermaid 图）+ 模块导航 + 专题入口
├── assets/                 # 全局资源
│   ├── styles.css
│   ├── highlight/          # 源码查看器高亮库（本地化）
│   └── navigation.js
├── detailed/               # 详细模块文档（15 页，带 mermaid 图）
│   └── attention/compilation/core/distributed/lora/models/ops/patch/
│       quantization/sample/source-guide/spec-decode/upstream/usage/worker.html
├── panorama/               # 全景 API 参考（9 页，纯文本）
│   ├── panorama.html       # 索引页：每模块一段真实介绍 + 统计 + 跳转按钮
│   └── panorama-{root,core,attention,ops,worker,models,distributed,rest}.html
└── compare/                # ★ 专题深度分析（平台对比系列，按需新增）
    └── kimi-k3-platform-compare.html   # Kimi K3 三平台（NV/AMD/Ascend）对比
└── stories/                # ★ 需求故事（一个 HTML 讲清一个需求，按需新增）
    ├── stories.html                    # 需求故事目录
    └── perf-kda-gate-overlap.html      # 首篇：KDA 门控投影融合与双流重叠（PR #15416）
```

两类页面职责划分：
- **detailed/**：讲「为什么、怎么协作」，用 mermaid 图讲架构与流程。
- **panorama/**：讲「有什么、在哪」，逐文件讲解 + 函数清单（名称+行数），不加 mermaid。
- **compare/**：讲「横向对比」，同一模型/组件跨平台实现差异；入口在 index.html
  导航栏「专题对比」与「专题深度分析」区块。新增专题 = 新 HTML 放 compare/ + index 两处加链接。
- **stories/**：讲「一个需求的来龙去脉」，从 git 提交记录选需求（优先性能优化），按
  「需求背景 → 相关流程（改动前/后图）→ 需求改动（真实 diff+注释）→ 相关链接」四段展开；
  入口在 index 导航「需求故事」+ stories.html 目录。

## 2. mermaid 图布局规范（重要经验）

| 图的内容类型 | 布局 | 原因 |
|---|---|---|
| 目录结构、模块组成、层级分类（硬件家族/后端家族/模型家族）、模块协作关系 | **LR**（`graph LR`） | 这类图节点多、标签长，TD 纵向排列会把字挤成窄条，LR 横向展开可读 |
| 执行流程、决策分支（注册流程、后端选择逻辑） | **TD**（`graph TD`） | 流程有先后语义，纵向符合阅读习惯 |
| sequenceDiagram | 不受影响 | 时序图天然纵向 |

判断口诀：**「分叉展示用 LR，先后动作用 TD」**。

mermaid 引擎用 CDN（`cdn.jsdelivr.net/npm/mermaid@10`）即可，**不做本地化**（已验证可用；
headless 截图偶发加载不出属环境波动，不影响真实浏览）。

### compare/ 专题页规范

- 页面宽度同样 1200px（曾用 1650px 已统一）；mermaid 容器 `overflow-x:auto` 允许大图横向滚动。
- **只有"大且被压缩看不清"的图才配下载按钮**（普通图不需要）；按钮复用页面内
  `bindSvgDownload(btnId, diagramId, filename)` 通用函数。
- 内容要求：函数级调用链必须给**真实文件名+行号**（读源码提取，禁止编造）；
  与底层的关系要讲清三个算子通道（`torch.ops._C_ascend` 自研 AscendC、`torch_npu` aclnn、`triton-ascend`）。

### 需求故事页（stories/）规范

- 选材：从 git 提交记录（`precision-rca/vllm-ascend-git/` 本地克隆，token 见
  `docs/agent-requirements-lessons.md` 第 5 节）选真实需求，**优先性能优化**；
  改动集中、能与文档源码版本对上的优先（文档源码 = 改动前状态时，"改动前流程"可直接链源码查看器）。
- 四段结构（固定）：**需求背景 → 相关流程（改动前/后两张图）→ 需求改动（真实 diff + 行内注释）→ 相关链接**。
- 图：改动前/后各一张时序图（对照读）；改动以表格（# / 改动 / 解决什么）+ 真实代码片段呈现。
- 代码块遵守"逐层展开叙事规范"第 5 条（language-python 高亮、行内注释、独立 hljs script 块）。
- 末尾链接清单必含：GitHub commit/PR、文档源码查看器、panorama 讲解、相关专题页、流水线入口。
- 命名：`perf-<slug>.html` / `feat-<slug>.html`；每加一篇同步更新 stories.html 目录与 index.html。



讲解"某模型怎么实现"类内容时，**聚焦一条主线从粗到细，禁止平均用力**：

### 逐层展开叙事规范（K3 对比页教训沉淀）
1. 抽象流程图先承诺重点（用颜色标出占 95% 计算量的步骤），**后续小节必须只聚焦被标色的步骤**，
 
  其余步骤不展开——否则就是"前后文条约撕了"。
2. "和 AMD/上游的关系"用**时序图**表达（participant 分三列：上游/AMD 基类、Ascend 实现、NPU 算子，
   消息标 ↳来自基类 / ⚡昇腾新实现），不要用纯文字表格；并配"三种继承机制"代码卡（整类继承/继承+覆盖/整组件替换）。
3. 源码片段必须：① highlight.js 语法高亮（引用本地 `assets/highlight/`，见第 4a 节）；
   ② 行内注释标注 ↳/⚡/→NPU 三类关系；③ 每段前挂"对应时序图消息 N"的锚点回链。
4. 章节标题写内容本身（"K3 逐层看：…"），**不要把"先抽象再具体再细节"这类写作方法论暴露成标题/导语**。
5. **页面内全部 Python 代码块统一治理**（教训：只有 9.3 高亮、其余裸文本被批"不好看"）：
   - 纯文本代码块加 `class="language-python"`，页尾独立 `<script>` 块统一 `hljs.highlightElement`；
   - **高亮脚本必须是独立 script 块**（与 mermaid.initialize 同块时，mermaid 报错会中断整块导致高亮失效）；
     且 hljs 的 `<script src>` 必须在调用之前；
   - 带 diff 红绿标色的代码块**不做** hljs 高亮（会破坏 span 标色）；文件清单类非代码块不加；
   - 代码块内的 `<` 等字符必须 HTML 转义（残留裸标签会导致 hljs unescaped-HTML 告警且渲染错乱）；
   - 每个代码块至少一组行内中文注释（⚡昇腾 / ↳上游·AMD / →底层）。

已按此规范落地的图（维护时新增图照此执行）：
- index.html：图1 项目定位、图2 目录结构、图4 引擎分层、图9 后端场景、图11 硬件家族、图13 模块协作 → LR；其余流程图 → TD
- detailed 页：各模块「组成/家族/结构/分类」图 → LR（见 `scripts/fix_td_to_lr.py` 白名单）

## 3. 页面宽度规范（重要经验）

**所有页面统一 1200px 内容宽度且水平居中**，不允许有的页面全屏、有的限宽（曾出现 index 1200px、panorama 多数页面全屏、source-guide 1100px 三种宽度并存的问题）。

实现方式二选一（与页面现有结构匹配）：
1. 页面有 `.container` 包裹 → `.container{max-width:1200px;margin:0 auto;padding:0 20px;}`
2. 内容是 body 直接子元素（panorama 各页）→ `body>*{max-width:1200px !important;margin-left:auto !important;margin-right:auto !important;}`

**居中坑（必读）**：方式 2 不加 `!important` 会被类选择器的 margin 简写覆盖——
如 `.module{margin:18px 0}` 简写把左右 margin 置 0，且类选择器特异度 (0-1-0) 高于 `body>*` (0-0-1)，
结果是"限宽生效但不居中"。所以方式 2 的三条属性必须带 `!important`。

## 4. 文件级讲解与源码跳转

- 讲解数据源：`scripts/data/file_descs.json`（457 条，键 = 相对 vllm_ascend 的路径，`\` 或 `/` 分隔均可，注入器做了归一化）。
- 注入脚本：`scripts/inject_file_descs.py`（幂等，全量重注入；同时负责清理 `见源码:` 假描述、给文件名加「查看源码」链接）。
- 禁止函数级硬凑一句话描述（如「返回注册名称」无信息量）；函数条目只保留 `名称 + [N行]`，信息量放在文件级讲解里。
- 「查看源码」链接指向**源码查看器**（见第 4a 节）。

## 4a. 源码查看器（单 HTML 架构）

「查看源码」不再直指 .py 文件，统一打开**唯一的查看器** `code-docs/src-viewer.html?file=<相对路径>`，
提供语法高亮（highlight.js 本地化 + github 浅色主题）、行号列、面包屑、返回按钮、1200px 居中排版。

```
code-docs/src-viewer.html          # 唯一 HTML 查看器（?file= 入参）
code-docs/src/<path>.py.js         # 每 .py 一个数据文件（window.__SRC_SET(path, 内容)）
code-docs/assets/highlight/        # highlight.min.js + github.min.css（本地化，离线可用）
```

**为什么必须是数据文件而非现场 fetch**：file:// 协议下浏览器禁止 fetch/XHR 读取本地文件（CORS），
而 `<script src>` 加载本地 .js 不受限（JSONP 机制），这是"解压双击即用"约束下的唯一可行方案。

规范：
- 数据文件由 `scripts/gen_source_viewer.py` 生成（JSON ensure_ascii=True 防 `</script>` 注入，幂等可重跑）。
- 文档中的链接格式：panorama/ 页用 `../src-viewer.html?file=x`，detailed/ 页同，index.html 用 `src-viewer.html?file=x`。
- 校验：`scripts/check_viewer_links.py`（457 个链接逐一验证数据文件存在）；`check_links.py` 已支持 `?` query。
- **压缩包必须包含 src/ 与 assets/highlight/**，不再附带原始 .py 目录。

## 4a. panorama 页面主题统一规范

8 个模块子页（root/core/attention/ops/worker/models/distributed/rest）使用**同一份内嵌 CSS 与页面骨架**
（曾出现三代样式并存：导航结构不同、字体不同、宽度不同）：

- 骨架：`nav.navbar`（品牌 vLLM Ascend + ul.navbar-nav 九项菜单，当前页 active）→
  `div.page-header`（h1「vLLM Ascend · <模块中文名> API 参考」+ p 统计行）→ 内容 → footer。
- 统计行格式固定：`文件数: N | 函数条目: M | 每个文件含职责讲解…`，N/M 必须是**页面实际条目数**（不是全包递归数）。
- 字体：正文 Arial，代码 Consolas；主色 #667eea；浅色背景 #f5f7fa + 白卡片。
- panorama.html 索引页风格与上述一致（.nav 顶栏 + .module 卡片）。

## 5. 页面间导航要求

- 所有 panorama 页导航条第一项 = `../index.html`（回总览首页）。
- panorama.html 索引页：每模块一段介绍 + 统计 + `panorama-<mod>.html` 跳转按钮 + 返回首页链接。
- index.html「二、项目文件结构」章节放「全景源码导航」入口卡片 → `panorama/panorama.html`。
- detailed 页之间互链用同目录相对路径；跨目录（去 panorama/index）必须带 `../` 前缀。

## 6. 打包发布设计（重要经验）

**压缩包必须附带源码目录，否则「查看源码」链接全部失效。**

包结构（与解压后的相对关系保持一致）：

```
vllm-ascend-docs-final.zip
├── AGENTS.md
├── docs/                          # 本设计文档
├── code-docs/                     # 文档主体
└── vllm-ascend-main/vllm_ascend/  # 源码（仅此子目录即可，约 530 个 .py）
```

打包脚本：`scripts/send_docs_final.py`（打包 + HTML 卡片邮件一键完成）。
注意：**不要**把整个 vllm-ascend-main 仓库（含 .git、测试、CI，3600+ 文件）塞进包，只带 `vllm_ascend/` 子目录。

## 7. 维护命令与检查清单

改动后必跑（在仓库根目录）：

| 命令 | 作用 | 通过标准 |
|---|---|---|
| `python scripts/check_links.py` | 全量 href/src 死链检查 | 0 死链 |
| `python scripts/quantify_fake2.py` | 「见源码:」假描述检查 | 0 条 |
| `python scripts/inject_file_descs.py` | 重新注入文件讲解（幂等） | 输出与 file_descs.json 条数一致 |

发布前 checklist：
1. 三个检查全过；
2. 新增/修改了 mermaid 图 → 对照第 2 节表格核对布局；
3. 新增页面 → 对照第 3 节统一宽度；
4. 用 `scripts/send_docs_final.py` 打包发送（附件名英文）。

## 8. 历史问题档案（避免复发）

| 问题 | 根因 | 规避 |
|---|---|---|
| 40 个死链 | 目录结构化（子目录化）后未更新跨目录相对路径 | 结构调整后必跑 check_links.py |
| 652 条「见源码:xxx」假描述 | 生成器对无 docstring 函数写了占位 | 已清零；讲解以文件级为准（第 4 节） |
| 图2 目录结构 TD 看不清 | 层级类图用了 TD | 布局规范第 2 节 |
| panorama 宽度不一致 | 各页生成器 CSS 不统一 | 宽度规范第 3 节 |
| panorama 限宽后不居中 | `.module{margin:18px 0}` 简写覆盖 `body>*` 的 auto（特异度更高） | 宽度规范第 3 节居中坑：`body>*` 必须带 `!important` |
| 源码跳转点不开 | 打包未带源码目录 | 已被查看器方案取代（第 4a 节） |
| panorama 三代主题并存 | 不同时期生成器样式不同 | 第 4a 节主题统一规范；改样式八页一起改 |
| panorama 页内 viewer 链接 404 | 子目录页用了同级相对路径 | panorama/ 下必须 `../src-viewer.html` |
| root 页与模块页 24 个文件块重复 | root 页生成时递归收录了子目录 | root 页只保留根级 + compilation/ |
