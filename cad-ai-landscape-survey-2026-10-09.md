# CAD × AI 项目全景调研

| 项目 | 内容 |
|---|---|
| 检索日期 | 2026-10-09 |
| 分析方法 | Agency Agents `Research Synthesist` 人格（`research/research-synthesist.md`） |
| 执行方式 | 4 路并行检索（agent/MCP 类、商业 CAD、开源学术、中国生态 + 邻近生成式 3D） |
| 下游文档 | [`cad-ai-positioning-analysis-2026-10-09.md`](./cad-ai-positioning-analysis-2026-10-09.md) |

## ⚠️ 证据边界（先读这段）

- **以下 URL、star 数、发布状态均为检索子代理声称已打开一手来源，未逐条独立复核**。决策前请自行验证关键条目。
- 证据分级：**A** = 已打开项目官网/仓库/论文确认；**B** = 仅第三方报道；**C** = 仅社区提及；**D** = 检索后未找到。
- star 数为检索时点快照，会变。
- 中文源覆盖天然弱于英文源——中国生态部分是本报告最薄的一环。

---

## 一、Agent / MCP 类 —— 与 text-to-cad 同赛道

竞争最激烈的赛道，且**不是空白市场**。

### Tier 1：同内核、同渠道的直接竞品

| 项目 | 内核 | Star | 许可 | 宿主 | 状态 |
|---|---|---|---|---|---|
| **text-to-cad**（基线） | build123d/OCCT 7.9 | ~18,634 | MIT | Claude Code/Codex/Cursor/Gemini/Grok | A · active |
| **build123d-mcp** | build123d/OCCT | 86→110 | Apache 2.0 | Claude Code/Cursor/Codex CLI/Cline/VS Code/Continue | A · active |
| **openscad-mcp** | OpenSCAD（**CSG 非 B-rep**） | 149 | MIT | Claude Code 插件、Claude Desktop、Cursor、Windsurf | A · active |
| **3dp-mcp-server** | build123d | 14 | — | Claude Code 插件 + 6 技能（拓竹向） | A · active |
| **Svetlana-DAO-LLC/cad-agent** | build123d + Docker VTK 渲染 | 48 | PolyForm SBL | Docker 化，含可打印性分析 | A · active |
| **cad3dify** | GPT-5/Claude/Gemini → Python | — | — | CLI + Streamlit | A · active |
| **shapr3d-mcp** | build123d | 28 | MIT | macOS only，靠 STEP 与 Shapr3D 交换 | A · active |
| **CadQuery 官方 mcp-server** | CadQuery/OCCT | — | Apache 2.0 | 任意 MCP 客户端 | A · active |

**最直接对手是 build123d-mcp**：同内核、同 MCP 分发、同受众，工具面高度重叠（执行代码、渲染、测量、校验、导出 STEP/STL/DXF）。它还公开了 CADGenBench 0.360→0.457 的跑分。

text-to-cad 的差异：5+ agent 宿主的插件分发（vs 单 MCP 配置）、12 个技能（vs 纯工具）、制造服务对接、工程图纸、机器人描述文件、自研 Viewer。
build123d-mcp 的差异：公开基准、增量编辑（find_candidates/edit_feature）、设计审计子流程。

**openscad-mcp** 功能面接近且有 Claude Code 插件 + 15 项 eval 套件，但走 CSG 内核，**不产生 B-rep**，不适合制造级 STEP。

### Tier 2：商业桌面 CAD 桥接（需装并运行 CAD）

| 项目 | 对接软件 | Star | 限制 |
|---|---|---|---|
| **fusion360-mcp-server** (faust-machines) | Fusion 360 | 115 | 93 个工具，TCP 桥接，需装 Fusion，Beta |
| **solidworks-skills** (delancy827) | SolidWorks | 123 | Windows + COM，含反幻觉模块 |
| **Andiveli/mcp-cad** | Inventor | 0 | 80+ 原子工具，.NET |
| **daobataotie/cad-mcp** | AutoCAD/中望/浩辰 | 568* | Windows COM，35 工具，2D 制图 |
| **frankhommers/autodesk-fusion-mcp** | Fusion 360 | — | Fusion 内 add-in，Streamable HTTP，14 工具 |
| **AuraFriday/Fusion-360-MCP-Server** | Fusion 360 | — | Fusion 内执行 Python |

*568 这一数字来自单一来源，未交叉验证，可信度存疑。

### Tier 3：厂商官方 MCP（企业内部产品，非开发者分发）

| 厂商 | 产品 | 格式 | 状态 |
|---|---|---|---|
| **Autodesk** | AutoCAD / Civil 3D MCP + Fusion MCP | DWG, Fusion | 已发布（beta/preview） |
| **PTC/Onshape** | FeatureScript MCP Server | Onshape 原生 | 2026-08 发布（Onshape Labs） |
| **Open Design Alliance** | ODA MCP Servers | DWG, STEP, IFC | Pre-release，2026 Q3 |

### 大规模但非 CAD

| 项目 | Star | 说明 |
|---|---|---|
| **ahujasid/blender-mcp** | **30,304** | 全场星数第一，248 个工具。但 Blender 是**网格建模**，非参数化 CAD |
| **carlosh7/blender-mcp** | 9 | 另一分支实现 |
| **MCP CAD Studio** (flujo-app) | 3 | WASM Manifold 内核，**不需要 Python/原生安装** |
| **mattmohandiss/cad-mcp-server** | 4 | 只读 STEP 检查（OCCT 内核），不做生成 |

### 赛道空白点

1. **无人覆盖完整技能广度** —— 生成 + 工程图 + DFM/DfAM + 制造服务 + 机器人描述 + G-code 切片，无第二家
2. **离线能力稀缺** —— 只有 text-to-cad 和 build123d-mcp 完全离线；商业桥接多数需网络/云；Onshape 纯云
3. **STEP-first 罕见** —— 多数工具 STL-first/mesh-first；text-to-cad 与 build123d-mcp 是制造级 B-rep 优先
4. **插件分发是护城河** —— 多数竞品只给 MCP 配置片段
5. **eval/benchmark 正在成为入场门槛** —— openscad-mcp 和 build123d-mcp 都带 eval 套件

---

## 二、商业 CAD 内嵌 AI —— 关键发现：**普遍不做几何生成**

按 **已交付 / 预览 / 预告** 分开，这是本节最有价值的部分。

### 真正做了实质 ML 自动化

| 产品 | 功能 | 状态 |
|---|---|---|
| **Siemens Solid Edge 2026** | AI 磁吸装配约束、**AI 自动生成 80% 图纸视图**、Design Copilot | ✅ 已交付（2025-10） |
| **BricsCAD AI Tools** | AI Predict 命令建议、Drawing Health 自动清理 DWG、Bimify 自动转 BIM | ✅ 已交付 |
| **Altium 365 Engineering Assistant** | 自然语言增删改需求，AI Skills 封装工作流 | ✅ 已交付（需求工程，非布局） |

### 只做「参考馆员」，不做「协作者」

| 产品 | 状态 | 能问答 | 能生成几何 |
|---|---|:-:|:-:|
| Autodesk Assistant（Fusion/Forma/Flow） | ✅ GA 2026-09 | ✅ | ❌（下一代 agentic 排到 2027） |
| SolidWorks **AURA**（Mistral on Outscale） | ✅ 已交付 | ✅ | ❌ |
| Onshape AI Advisor（Amazon Bedrock） | ✅ 已交付 | ✅ | ❌（FeatureScript 生成仅 roadmap） |
| Siemens Design Copilot NX | ✅ 已交付 | ✅ | ❌（但 Select Similar Faces 已 ML 化） |
| PTC Creo AI Assistant | ✅ 已交付 | ✅ | ❌（读模型为 Beta） |
| Shapr3D AI | ✅ 已交付 | 仅帮助中心 | ❌ |
| Autodesk Fusion Generative Design | ✅ 已交付 | — | ❌（拓扑优化，非 LLM 生成代码） |

### 未交付

| 产品 | 状态 |
|---|---|
| **SolidWorks LEO** | 🟡 **Beta** —— 最接近几何生成（从草图学习预测几何规则、生成装配体、图像转网格）。R2026x FD03（2026-08）仍为装配分析/简化/指令生成/宏生成 |
| SolidWorks MARIE（材料科学助手） | ⚪ 预告 |
| Graitec Assistant（AECO） | ⚪ 预告，2027 Release |

### 真正从自然语言生成参数化脚本的，集中在开源

| 项目 | 能做什么 |
|---|---|
| **RhinoAI**（McNeel 官方，开源，351 stars，MIT） | GH1/GH2 脚本生成与转换、AI 创建自定义命令、内置 MCP 服务器（多 Rhino 并行） |
| **FreeCAD AI**（ghbalf） | 50 个结构化工具、21 家 LLM、Skills 系统、MCP 支持 |
| **GenCAD**（freecad.gencad） | 文本→CAD 代码、RAG 上下文、VLM 视觉校验 + 自动重试 |
| **Blender MCP** | 248 工具，自然语言→Blender Python 建模，VLM 反馈闭环 |
| **KiCad ALT TAB Copilot** | 原理图起草（Next Gen）、智能编辑（Live），自训 3B 参数 Ohm 模型 |

**定价模式**：全部含在既有订阅内（Fusion、SOLIDWORKS Design、Onshape、Altium 365）；生成式设计走 token/credit 计费（Fusion Simulation Extension 约 $1,465/年 + Flex tokens）；Siemens 走 value-based token 授权。

---

## 三、开源与学术

### 范式 b：直接生成可脚本化参数化 CAD（更贴近 text-to-cad）

| 项目 | 会议 | Star | 代码状态 |
|---|---|---|---|
| **Text-to-CadQuery** | — | 119 | 完整训练+推理，170K CadQuery 标注 |
| **CAD-Coder**（MIT VLM，图像→代码） | — | 207 | 完整 + GenCAD-Code 数据集 |
| **CAD-Coder**（CoT + 几何奖励 RL） | NeurIPS 2025 | 12 | 权重在 HF，推理脚本已放 |
| **CAD-Recode**（点云→代码） | ICCV 2025 | 268 | 仅推理 demo |
| **CADFusion**（微软研究院） | ICML 2025 | 91 | MIT，完整 |
| **CAD-Assistant**（工具增强 VLLM→FreeCAD 代码） | ICCV 2025 | 83 | 3D 实体识别器 |

### 范式 a：生成构造序列 / B-rep（需自定义解码器）

| 项目 | 会议 | Star | 备注 |
|---|---|---|---|
| **DeepCAD** | ICCV 2021 | 833 | **基础数据集 178K 模型**，下游几乎全建于此 |
| **Text2CAD** | NeurIPS 2024 Spotlight | 483 | 训练+推理已放 |
| **BrepGen**（Autodesk Research） | SIGGRAPH 2024 | 423 | B-rep 扩散，代码+模型+数据集 |
| **CAD-MLLM** | — | 271 | ⚠️ **推理/训练代码未公开**（截至 2025-05） |
| **SketchAgent** | CVPR 2025 | 231 | 完整代码 |
| **CAD-GPT** | AAAI 2025 | 57 | 数据集在 HF，代码部分 |

### 工具与平台

| 项目 | 说明 |
|---|---|
| **CADAM**（Adam, YC W25） | 5,231 star，GPL-3.0，**开源 text-to-CAD Web 应用**，输出 OpenSCAD，含 V8 引擎等 13 个 benchmark 模型 |
| **Zoo**（原 KittyCAD） | 商业，Zookeeper agent + MLephant text-to-CAD，$10M |
| **Adam**（adamcad.com） | YC W25，Onshape + Fusion，REST API + MCP，$4.1M 种子 |
| **Leo AI**（getleo.ai） | $9.7M 种子，机械工程副驾，接 SolidWorks/Onshape/Fusion/Inventor/NX/Teamcenter，50,000+ 工程师 |
| **CAD Arena**（cadarena.dev） | 参数化 CAD 生成的公开 benchmark，20 prompts × 4 tiers，测 Claude/Zoo/Text-to-CadQuery/Gemini/GPT-5 |
| **gNucleus text-to-cad-mcp** | MCP，文本→可编辑 CAD 零件/装配体，18 stars |
| **AiCadGen**（aicadgen.com） | $5/月 Web 应用，STEP/STL/DXF/OBJ/PDF |
| **卡伦特 创模AI** | 中国，文字/图片→**带特征树**的参数化 CAD，导出 CATIA/UG/Creo/SolidWorks |

### ❗ 检索中的证据缺口（重要）

- **"Text2CAD in the Wild"、"AskCAD"、"CADAgent" 作为独立论文标题均未找到**。搜索返回命名冲突（存在**两篇不同的 "Text2CAD" 论文**）和邻近工作。
- **循环引用警示**：DeepCAD 是几乎所有下游 text-to-CAD 论文的基础数据集 —— 大量"独立印证"其实都回溯到同一个 2021 年来源。**引用数不等于证据强度**。
- CAD-MLLM 声称 SOTA 但推理代码未公开，其数字无法独立验证。
- SketchGraphs（NeurIPS 2021，4.7M 参数化草图）与 DeepCAD 共同构成基础层。

---

## 四、中国生态

### 国产 CAD 厂商内嵌 AI（最成熟的一层）

| 厂商 | AI 能力 | 状态 |
|---|---|---|
| **中望软件** | AI 识图模型、3D悟空2027 接 DeepSeek 自动圆角/智能出图（官方称标注准确率 95%）、AI-structure Copilot（与清华陆新征团队，面向结构设计） | ✅ 已发布 |
| **浩辰软件**（A股 688657） | AI 助手：LLM + 垂类模型，自然语言驱动绘图/编辑/标注/批量建层；ScanToCAD 图像转 DWG；GstarRender | ✅ 已交付 |
| **大腾智能CAD** | 华为云商店页明确写"LLM 大模型、智能体 Agent 及 **MCP 框架深度整合**"；百万级零部件库秒级检索 | ✅ 在线 |
| **华天软件 CrownCAD** | 大模型底座—多模态智能体—行业应用三层体系，500,000+ 注册用户，C+ 轮融资 | ✅ 已交付 |
| **开目软件** | AI 智能体"小沐"，覆盖设计/工艺/制造；侧重 CAPP/MPM/PLM 而非几何生成 | ✅ 已发布 |

### 生成式 CAD 新产品 —— 最接近 text-to-cad 范式

**卡伦特 创模AI**（currentcad.com）：文字/图片直接生成**带完整特征树**的参数化 3D CAD，零件→装配体，可导出 CATIA/UG/Creo/SolidWorks。LLM+GNN 生成 + 多模态扩散。国内目前最接近 text-to-cad 范式的产品。

其他：AiCAD 钢结构大模型平台（垂直行业）、创新奇智 × Bentley 的 iPID（P&ID 图像转 CAD，港股"AI+制造"第一股）

### 学术前沿（直接生成参数化命令序列）

| 项目 | 出处 | 会议 |
|---|---|---|
| **Pointer-CAD** | DeepSeek + 港大马毅 + 腾讯 + 北航 | CVPR 2026 |
| **SEEK-CAD** | DeepSeek-R1 本地部署参数化 CAD 自精炼 | ICLR 2026 |
| **CAD-Llama** | LLM 参数化 3D 生成 | CVPR 2025 |
| **Intelligent CAD 2.0 综述** | 浙大 CAD&CG 国家重点实验室 | — |

### 国内开源小项目

| 项目 | Star | 说明 |
|---|---|---|
| HiCAD | 192 | 自然语言 → **JSCAD** 参数化代码（JS 内核，非 B-rep） |
| vjmap/aidraw | 82 | TRAE/Cursor 里生成 CAD 图纸下载 DWG |
| AutoCADMindAI | 8 | 自然语言驱动 AutoCAD 命令，COM+本地 HTTP 桥 |
| HeDouAgent | — | B 站演示，AutoCAD/中望双平台插件，40+ 功能，支持 GPT/DeepSeek |

### ❗ 中国部分的检索缺口

- **TapLogic / 云智造 / 云工厂 / 阿里云天池 CAD 数据集**：检索后未发现相关 AI CAD 产品或数据集。
- **华为云**：提供盘古大模型与 MCP 框架、托管第三方 CAD，但**无自研 AI CAD 产品**。
- **新迪数字（天工CAD）**：官网聚焦国产替代，**未发现 AI 驱动建模功能**。

---

## 五、邻近的生成式 3D —— 它们**不是 CAD 工具**

这一节的目的是划清边界：text-to-3D 资产生成 ≠ text-to-CAD 参数化建模。

**所有下列工具输出均为 mesh 或隐式表征（NeRF / 3D Gaussian），不产生特征树、草图约束、参数化历史或可工程编辑的 STEP/IGES。**

| 项目 | 类型 | Star / 融资 | 活跃度 |
|---|---|---|---|
| TRELLIS (Microsoft) | 研究，CVPR 2025 Spotlight | 13,782 | active |
| TRELLIS.2 (Microsoft) | 研究 | 11,394 | active |
| Shap-E (OpenAI) | 研究，2023-05 | 12,265 | ⚠️ stale |
| InstantMesh (腾讯 ARC) | 研究，2024-04 | 4,554 | active |
| TripoSR | 研究，2024-03 | 6,999 | active |
| Meshy | 商业 | Series B ~$4 亿，估值 $15 亿，173 人 | active |
| Tripo3D AI | 商业 | — | active |
| Hyper3D / Rodin | 商业 | Rodin Gen-2，clean quad topology 但仍是 mesh | active |
| CSM.ai | 商业 | game-ready mesh | active |
| Luma AI / Genie | 商业 | $43M | active |
| **Sloyd** | 商业 | **唯一例外**：保留程序化参数滑块，但无 B-rep/特征树/工程约束 | active |

**AlphaSculpt：检索后完全未找到**（D 级）——搜到的都是牙科产品和 3D 打印用户名，可能名称有误或不存在。

---

## 六、综合判断

**最反直觉的一点**：截至 2026 年 10 月，所有主流商业 CAD 厂商（Autodesk、SolidWorks、Siemens、PTC、Shapr3D）**都交付了 AI 助手，但绝大多数只做文档问答和命令导航**。真正的自然语言→参数化几何生成能力，**集中在开源生态**（RhinoAI、FreeCAD AI、GenCAD、Blender MCP，以及这批 build123d MCP 项目），商业侧只有 SolidWorks LEO 还在 Beta。

**对 text-to-cad 的三点含义**：

1. **同赛道不是空白**。build123d-mcp、openscad-mcp 用同一内核、同一 MCP 分发渠道、同一受众。差异化不在"能建模"，而在暖守护进程、字节确定性缓存、自研 Viewer、制造向技能闭环。
2. **开源反而领先商业**。这是罕见的格局——大厂在路线图上，开源小项目在交付。text-to-cad 站在"离线自包含 + 制造闭环"这个位置上，没有直接对手占住。
3. **真正的护城河可能是离线与企业部署**，而非 AI 能力本身。所有 MCP 竞品都要求本地装 CAD 软件或在线 API。

> 📌 本节结论已被下游的[定位分析](./cad-ai-positioning-analysis-2026-10-09.md)深化并部分修正——尤其是"多宿主分发"和"离线优先"两项，经复核后被判定为**半瞬态优势**，不构成壁垒。
