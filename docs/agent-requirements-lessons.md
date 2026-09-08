# Agent 工作要求与经验教训（2026-09 GLM-5.1 精度定位会话沉淀）

> 来源：用户在 vllm-ascend CI 精度问题定位过程中的多次纠偏与要求。
> 后续同类任务（CI 排查 / 分析报告 / 归因文档）开工前先读本文。

---

## 一、用户明确的工作要求（违者必被纠正）

### 1. 分析不武断，先全局再聚焦
- 不许"逮着一个嫌疑就下结论"。先做**全局对照**（组网 × 日期成败矩阵、多模型对照组），用矩阵界定问题边界，再谈归因。
- 每个嫌疑对象都要**逐个看 diff / 逐个验证**，不能只看标题就排除。

### 2. 推理链条必须经得起追问（实际被追问过的四个问题）
- **"能这么推理吗？commit id 一致吗？"** —— 声称"两次运行只差 X"之前，必须核对 head_sha / commit 区间。两个变量同时变化时要**声明双变量**，不能只强调其中一个。
- **"截断会让 30 题全错吗？"** —— 全零（0/30）与截断（应得中间分）矛盾。得分形态本身就是证据：严格全零 = 系统性/确定性机制；中间分 = 渐进/波动机制。
- **"vLLM 出问题不该所有模型都挂吗？"** —— 全局性质疑。归因面必须与"谁坏了谁没坏"的观察自洽：只有特定开关组合坏 → 归因收窄到该路径，而非整个上游。
- **"开关 false 的组网也红了，跟你说的冲突吧？"** —— 混入无关证据会削弱论证。吞吐失败与精度失败是两种症状，必须分开归档。

### 3. 现象与怀疑严格分离（两个 HTML 的分工）
- **现象页**：只陈述事实 —— 日志正常面/异常面、组网 × 成功失败日期矩阵、提交记录与版本切换、评估链路。**不许出现"嫌疑/怀疑/指向"等归因字样**。
- **怀疑页**：所有归因假设、嫌疑排序、时间对齐论证、判决实验集中在此。
- 页面结构按**方向组织**（方向一 日志正常/异常；方向二 组网 × 日期；方向三 提交记录；方向四 评估链路/取证缺口），内容要细致，但不许堆料到看不懂。

### 4. 表格与事实必须逐个核实
- "哪些测精度、哪些只测吞吐"这类标注**必须逐个 yaml 审计**（看 benchmarks 段），凭印象写错会误导整个归因方向（实际发生过：把带精度 case 的组网标成"只测吞吐"）。
- 矩阵重点对象要 **★ 标注**，并写清"谁是重点、谁是近亲、谁是对照"。
- 手抄矩阵容易错位——能脚本生成的不手抄。

### 5. 链接齐全（含日志入口）
- commit → `https://github.com/<org>/<repo>/commit/<hash>`
- PR → `/pull/<n>`；run → `/actions/runs/<id>`；job → `/actions/runs/<run_id>/job/<job_id>`
- 配置 yaml / 指针文件 → `/blob/main/<path>`
- vLLM 上游 hash 链到 `vllm-project/vllm`，别混仓库。
- **日志证据行必须带"日志入口"链接**：现象页/证据表里的每一行结论（如"31 个请求全部 200 OK""plog 干净"），都要在行内给出可点击的 job 页或 artifact 页链接，做到"每个论断一键可达原始日志"；工件用 `/actions/runs/<run_id>/artifacts/<artifact_id>`。不许只给结论不给证据入口。

### 6. 表达要求
- "讲人话"：先直接回答问题，再展开；推理过程不要绕。
- 每个怀疑对象必须回答 **"为啥能和现象时间对上"**（时间线核对表：事件→时刻→与回归的关系）。
- 已排除的假设保留在"已排除"表里，每条附排除依据。

---

## 二、vllm-ascend CI 排查方法论（本项目沉淀）

### 定位与矩阵
1. 任务定位：`GET /actions/jobs/{job_id}` 拿 job 名/所属 run/步骤列表。
2. 矩阵法：拉 workflow 全量 runs（`/workflows/{id}/runs?created=>=日期`），**每日定时 run 按 created_at 的 HH:mm 识别**（如 15:45），逐个 `/runs/{id}/jobs?per_page=100` 抓目标 job 结论，构建组网 × 日期矩阵。
3. 区分四种状态：**没跑到出分（部署/aisbench 失败）≠ 0 分 ≠ 吞吐失败 ≠ 未安排**。四者混写会污染归因。

### 日志与工件
- 单 job 日志：`curl -sL -H "Authorization: Bearer <TOKEN>" https://api.github.com/repos/<org>/<repo>/actions/jobs/{job_id}/logs -o job.log`（文本，可直接 grep）。
- 工件：`/actions/artifacts/{id}/zip` 下载后 tar 解包；内含 NPU plog、双节点容器日志、engine 日志。
- 判分行特征：`Task vllm-api-general-chat/aime2025: {'accuracy': x}` 与表格行 `aime2025 | <hash> | accuracy | gen | <分>`。
- 注意：`/tmp/benchmark_results/` 与 `output_accuracy.txt`（每题模型原始回答）目前**不在收集范围**——这是定案缺口，需要 CI 侧补收集。

### 关键事实确认手段
- 部署一致性：在 job 日志中比对 `vllm serve ...` 完整命令行与 `vLLM server version` 行。
- 上游版本机制：nightly 镜像经 **main2main** 升级，指针文件 `.github/vllm-main-verified.commit`（git log 该文件即版本切换史）；但镜像也可能装 vLLM main 最新（版本跳变不一定有对应 commit）。
- **配置双轨制**：nightly 实际生效的 case 清单来自 OBS 侧配置，**repo 里的 yaml ≠ 当晚生效配置**（0990fc08 案例）。
- 因子对照：找"部署逐项相同、仅差一个开关"的组网对（如 128k_90_50 vs 198k 的 sfa_c8），做 2×2 表（开关 × 版本），唯一坏格即交互回归。

### 归因纪律
- 时间线排除法有效但要配合矩阵：**"晚于首个坏例的 commit 全部排除"**（08-30 已 0 分 → 09-05/09-06 的提交不可能为首因）。
- "变好再变坏"的波动指向**版本切换/环境变化**，而非单向累积的代码腐化。
- 对照组要求：同模型不同开关（收窄到开关）、同版本不同模型（收窄到模型专属面）、非 GLM 精度 job（排除全局回归）。

---

## 三、工具与环境经验

- **API 限额**：未认证 GitHub API 60 次/小时，`/rate_limit` 端点查余量；用户提供 token 后走 `Authorization: Bearer`，5000 次/小时。
- **git clone 优先**：深度排查直接 clone 完整仓库（token 可嵌 URL），本地 `git log/show/diff/rev-list` 比 API 强得多；本项目分析仓库在 `precision-rca/vllm-ascend-git/`。
- **下载**：`Invoke-WebRequest` 对 github.com 主站间歇失败；工件/日志下载用 `curl.exe -sL`（注意 PowerShell 里必须 `curl.exe`，`curl` 是别名）。
- **PS 5.1**：多行逻辑写 `.ps1`/`.py` 文件执行；`Out-File` 默认 UTF-16（读回时注意编码）；`Start-Process ... -WindowStyle Hidden` 跑长任务，轻量命令轮询产物文件。
- **Playwright**：机器上有 Python 版（无 node 版）；截图验证用 `executable_path=Edge` + `headless=True`；CDN 资源（mermaid）可能拖垮 `networkidle`，用 `domcontentloaded` + 固定等待。
- **页面验证闭环**：语法检查（标签闭合/锚点数）→ 截图 → MiniMax 图片理解逐项问答 → 不合格重改。

---

## 四、本项目分析页面规范（precision-rca/ 模式）

### 4.1 三页分工（2026-09 定稿，违者重写）

> 用户最终定稿：**三个 HTML，职责严格分离，不许合并、不许互相越界**：

| 页面 | 文件 | 职责 | 红线 |
|------|------|------|------|
| ① 现象 | `phenomena.html` | **从多个维度找现象**：方向一 日志（正常面+异常面）；方向二 组网 × 成功失败日期矩阵；方向三 提交记录与版本切换；方向四 评估链路与取证缺口 | 只陈述事实，**无任何归因/推理/嫌疑字样** |
| ② 分析 | `analysis.html` | **基于现象的分析**：同日对照逐项排除推理、时间线对齐论证、矩阵归纳（开关分化）、评估链排除 —— 从现象**直接可推**的结论 | 只做"从现象到结论"的推演，不点名可疑 commit |
| ③ 可疑点 | `suspects.html` | **可疑点清单**：候选对象（是什么/改了什么/为什么可疑/时间对齐核对/如何证实/链接）、已排除假设（附依据）、判决树、实验清单、issue 模板 | 只放归因与验证 |

### 4.2 页面内容规范
1. 结论前置：顶部横幅先给一句话；现象页横幅措辞不得含归因。
2. 每张表一个明确标题；重点对象 ★ + 高亮行；**每个数字/论断可回溯到日志链接**（job 页 / artifact 页）。
3. 分析页每个结论要写清推理链（对照设定 → 逐项排除 → 夹逼结论），不跳步。
4. 可疑点页每个候选必须回答 **"为啥能和现象时间对上"**（时间线核对），已排除假设附排除依据。
5. 页面宽 1200px 居中、浅色背景；mermaid 一图一编号。
6. 归档产物：`benchmarks_audit.json`（yaml 审计）、`configs_extract.json`（开关提取）、日志快照。
7. 任何进展先发邮件归档（SMTP 163 → QQ，HTML 卡片式，附件名英文）。

### 4.3 工作方式要求（用户多次纠偏）
- **不许跳跃**：结构/方案变化先说明计划、更新要求文档，再动手；多步任务按部就班，每步完成后确认。
- 写页面前先列结构大纲给用户对齐，避免整页重写返工。
- 手抄矩阵必错位——数据表用脚本生成或逐格核对。

---

## 五、速查手册：token / 流水线 / commit / 代码拉取

### 5.1 访问 token（用户提供）
- GitHub PAT：`<YOUR_GITHUB_PAT>`
- 用法：REST 头 `"Authorization" = "Bearer <TOKEN>"`；clone 时嵌 URL `https://<TOKEN>@github.com/vllm-project/vllm-ascend.git`
- 限额：认证后 5000 次/小时（未认证仅 60 次/小时，`/rate_limit` 端点查余量且不消耗配额）

### 5.2 流水线地址（workflow id 与文件）
仓库：`vllm-project/vllm-ascend` → API 前缀 `https://api.github.com/repos/vllm-project/vllm-ascend`

| 流水线 | workflow id | 文件 |
|---|---|---|
| **Nightly-A3**（每日 15:45 全量，本案对象） | `228664976` | `.github/workflows/schedule_nightly_test_a3.yaml` |
| **Weekly-A3**（每周全量） | `278657002` | `.github/workflows/schedule_weekly_test_a3.yaml` |
| Nightly-A2 | `228664975` | `.github/workflows/schedule_nightly_test_a2.yaml` |
| Weekly-A2 | `291327544` | `.github/workflows/schedule_weekly_test_a2.yaml` |
| Weekly-310P | `308395150` | `.github/workflows/schedule_weekly_test_310p.yaml` |
| Nightly（旧版 A3，可能仍被触发） | `215695701` | `.github/workflows/nightly_test_a3.yaml` |

常用 API：
- run 列表：`GET /actions/workflows/{id}/runs?created=>=YYYY-MM-DD&per_page=100`（每日定时 run 按 created_at 的 HH:mm=15:45 识别）
- run 详情：`GET /actions/runs/{run_id}`（**head_sha = 该次运行的代码版本**）
- job 列表：`GET /actions/runs/{run_id}/jobs?per_page=100`
- job 日志（文本直接下载）：`GET /actions/jobs/{job_id}/logs`（用 `curl.exe -sL -o`）
- 工件：`GET /actions/runs/{run_id}/artifacts` → `/actions/artifacts/{artifact_id}/zip`
- 网页入口：`https://github.com/vllm-project/vllm-ascend/actions/workflows/<文件名>`

### 5.3 commit id 在哪查
1. **某次 run 跑的代码版本**：run 详情的 `head_sha`（如 run#15540 → `219a7e7e`，run#15521 → `354635783`）；也会出现在该 run 上传工件的 meta JSON（`"sha": "..."`）里
2. **两次 run 之间代码变了什么**：compare API `.../compare/{shaA}...{shaB}`，或本地 git `git log --oneline A..B`
3. **vLLM 上游版本**：job 日志行 `vLLM server version 0.27.1`（**main2main 机制**：指针文件 `.github/vllm-main-verified.commit`，`git log -p -- .github/vllm-main-verified.commit` 即上游版本切换史）
4. **注意**：同 workflow 不同 run 的 head_sha 不同 → 分析"回归窗口"必须用两次运行的 head_sha 做 rev-list，不能想当然

### 5.4 代码拉取与本地分析
``powershell
# 完整 clone（token 嵌 URL）
git clone https://<YOUR_GITHUB_PAT>@github.com/vllm-project/vllm-ascend.git D:\demo\202609\vllm-ascend\precision-rca\vllm-ascend-git
``
本项目已有克隆：`precision-rca/vllm-ascend-git/`。常用命令：
- `git rev-list A..B --count` —— 两 run 之间提交数
- `git log --oneline A..B -- vllm_ascend/` —— 只看运行时代码变更
- `git show <hash> -- <path>` —— 单 commit 的 diff
- `git diff --stat A B -- <path>` —— 区间改动统计
- 上游 vLLM 仓库（bisect 0.26.0..0.27.1 用）：`github.com/vllm-project/vllm`（尚未 clone）