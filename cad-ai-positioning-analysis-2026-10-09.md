# text-to-cad 市场定位分析

| 项目 | 内容 |
|---|---|
| 分析日期 | 2026-10-09 |
| 分析对象 | [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad)（cadgen 0.7.19，MIT） |
| 分析方法 | Agency Agents `Trend Researcher` 人格（`product/product-trend-researcher.md`） |
| 上游依据 | 先前 `Research Synthesist` 四路并行检索的竞品证据库（2026-10-09） |

> **证据提示**：本文中的竞品状态、star 数、融资金额、市场数据均来自检索子代理，**未逐条独立复核**。做决策前请按文中 URL 自行验证关键条目。

---

## 1. 定位声明

text-to-cad 是目前**"安装后完全离线、自包含的 agent-native CAD 生成运行时"中受众最广的开源项目**（18,634 stars @2026-10-09）。

它与主流竞品的根本区别：**不依赖任何外部 CAD 应用（Fusion/SolidWorks/AutoCAD）运行即可生成 STEP/STL/3MF/GLB/DXF**，并附带 12 个覆盖设计→制造的 agent skill。

真实位置是**个人制造者与小型硬件团队的"零门槛 CAD 入口"**，而非企业级参数化 CAD 的替代品。

**核心弱点**：受限于 build123d 内核能力上限（复杂曲面、大型装配体）、Windows 11 Smart App Control 阻断、缺乏企业采购所需的合规与治理能力。

## 2. 竞争地图

**轴线选择理由**——这两条最能预测买方决策路径与防御壁垒：

- **纵轴：几何生成自主性** —— 能否独立生成工程级 B-rep（不依赖外部 CAD 应用运行）。这是与"传统 AI 助手"的分界线。
- **横轴：分发与安装深度** —— 从"需 CAD 应用在线"到"一键安装即用"，决定可达用户基数。

```
                    几何生成自主性（高）
                         │
     text-to-cad ●       │
     build123d-mcp ●     │
                         │
  ───────────────────────┼────────────────────────
                         │         CADAM(Adam) ●
    Svetlana-DAO ●       │         Sloyd ●
                         │         AiCadGen ●
    RhinoAI ●            │         卡伦特 ●
    FreeCAD AI ●         │         gNucleus ●
    GenCAD ●             │
                         │
    Blender MCP ●        │    SW AURA ●    daobataotie ●
    Onshape-MCP ●        │    PTC Advisor ● Fusion360-mcp ●
    NX MCP ●             │    Siemens Copilot ● shapr3d-mcp ●
                  几何生成自主性（低）
          ← 需CAD应用在线          一键安装即用 →
```

### 白地空间：有价值，但也有"未被占据的合理理由"

右上象限（高自主性 + 深度分发）仅 text-to-cad 与 build123d-mcp 占据。三个原因让它空着：

1. 商业 CAD 厂商的 MCP server **全部落在右下**——需 CAD 应用在线，因为它们的核心商业模式是保护许可证收入
2. AI-native 创业公司（Adam、Leo AI）走 SaaS 路线，不进开源免费空间
3. 同内核的 build123d-mcp 分发广度不足

**但空着不全是机会**：企业不会用未经审计的开源工具替代合规的 CAD 许可证；个人制造者市场虽大但付费意愿低。**这块白地的天花板取决于 agent 安装基数能否转化为收入。**

## 3. 关键竞品状态更新（本轮新验证）

| 竞品 | 最新状态 | 验证日期 |
|---|---|---|
| **build123d-mcp** | v0.3.90，**110 stars**（较上轮 86 上升），59 issues。高频迭代中：新增特征识别（quiddity 0.3.5，支持 pockets/slots/ribs/gussets）、通孔编辑、3MF 导出、HTTP 会话隔离。**工程图工具已废弃**，迁往 draftwright | 2026-10-09 |
| **RhinoAI**（McNeel 官方） | **351 stars**，MIT，支持 Claude Desktop/Code/Copilot/Codex/Gemini CLI，含 GH 脚本生成 + AI 命令创建 + 内置 MCP，connector v0.1.6 | 2026-10-09 |
| **SolidWorks LEO** | R2026x FD03（2026-08）：能力仍是装配分析、简化、指令生成、宏生成——**均非几何生成**。Dassault 未宣布 GA 日期 | 2026-08-05 |
| **Autodesk Fusion MCP** | **2026-04 已发布**官方双服务器（本地建模 + 云端查询），Revit MCP tech preview | 2026-10-08 |
| **Adam**（YC W25） | $4.1M 种子（2025-10，TQ Ventures），数万付费用户，年底上 Onshape copilot | 2025-10-31 |
| **Leo AI**（创业公司） | **$9.7M 种子**（2025-09，Flint Capital），50,000+ 工程师在用（HP/Scania/Siemens/Mobileye） | 2025-09-02 |
| **Schneider 收购 PTC** | **$22.6B** 股权 / $23.7B EV，预计 2027 Q3 完成 | 2026-10-05 |

> ⚠️ **命名陷阱**：Leo AI（getleo.ai，独立创业公司）与 SolidWorks 的 LEO（Dassault 嵌入助手）是**完全不同的实体**。两者目前都没做几何生成。

### 来源

- build123d-mcp — https://github.com/pzfreo/build123d-mcp · https://github.com/pzfreo/build123d-mcp/blob/main/CHANGELOG.md
- RhinoAI — https://github.com/mcneel/RhinoAI
- SolidWorks LEO — https://blogs.solidworks.com/products/solidworks/whats-new-in-solidworks-ai-r2026x-fd03/
- Autodesk Fusion MCP — https://www.autodesk.com/products/fusion-360/blog/introducing-the-fusion-mcp-opening-fusion-to-ai-powered-workflows/
- Adam — https://techcrunch.com/2025/10/31/yc-alum-adam-raises-4-1m-to-turn-viral-text-to-3d-tool-into-ai-copilot/
- Leo AI — https://www.unite.ai/leo-ai-raises-9-7m-to-power-a-new-era-of-mechanical-engineering/
- Schneider–PTC — https://beyondplm.com/2026/10/05/schneider-electric-ptc-acquisition-plm-analysis/

## 4. 细分市场

| 细分 | 真实竞品 | text-to-cad 可信度 | 成真条件 |
|---|---|---|---|
| **个人制造者** | Adam（$5.99-17.99/月）、openscad-mcp、Blender MCP、3dp-mcp | ✅ **高（主场）** | 维持零摩擦；扩展制造服务连接 |
| **机器人** | 无直接竞品做 URDF/SRDF/SDF 验证 | ✅ **高（利基）** | 与 ROS 2 深度集成。市场极小 |
| **制造/加工服务** | Xometry、SendCutSend 原生 API、Protolabs | 🟡 **中** | 聚焦 DfAM/DFM 的独立价值，而非做连接器 |
| **初创硬件团队** | Leo AI、Adam、Zoo | 🟠 **中低** | 需要 PLM 集成与可追溯设计历史——**大概率不该投入** |
| **AEC/建筑** | Autodesk Revit MCP、ODA MCP | 🔴 **低** | 核心格式是 IFC/RVT，STEP 触不到 BIM |
| **企业机械工程** | SolidWorks/Siemens/PTC/Autodesk | 🔴 **极低** | **不现实**——需 SOC 2、FedRAMP、供应商审计 |

**企业市场正在垂直整合**：Schneider–PTC $22.6B、Siemens–Altair $10B、Autodesk–MaintainX $3.6B。这个层面上开源 agent skill 根本不在牌桌上。

## 5. 差异化审计（哪些是真壁垒）

### ✅ 防御性

| 优势 | 理由 |
|---|---|
| **自包含 wheel** | 与所有 vendor MCP（需 CAD 应用运行）根本不同。复制需打包整个 build123d + OCP + viewer + 存储——数月工程量 |
| **字节确定性 + 内容寻址存储** | 深度架构决策（设计律 1-6），非 sprint 可补。build123d-mcp 到 v0.3.87 才加 `bank_candidate()` 的 gate-clean 保存——**同行正在往这个方向走** |
| **12 个制造 skill 的覆盖深度** | DfAM（壁厚/悬垂/支撑体积/构建方向）、DFM（钣金/CNC/注塑，每条发现带测量证据）、G-code、Bambu、SendCutSend——**这条链没有竞品完整覆盖** |

### 🟡 瞬态（一个 sprint 就能追赶）

| 优势 | 真实情况 |
|---|---|
| **离线优先** | 半瞬态。任何 build123d MCP 本质也是离线的。真正差异不在"离线"，在"自包含 + 无外部 CAD 依赖" |
| **多宿主分发** | 半瞬态。build123d-mcp 已支持 7+ 宿主；RhinoAI 支持 5 家。**多宿主正在变成桌面赌注** |
| **MIT 许可** | ❌ 纯瞬态。RhinoAI、Blender MCP、openscad-mcp 全是 MIT，build123d-mcp 是 Apache 2.0。**MIT 是加分项，不是壁垒** |

### ⚠️ 盲点（最值得警惕）

**广度 ≠ 深度**：build123d-mcp 在特征识别（quiddity 家族）、事务性几何编辑、设计审计子流程上的工具深度**已经超过 text-to-cad**。12 个 skill 是分发表面，单 skill 能力上限受限于 build123d 内核。

**遥测默认开启**：README 承认——这与"完全离线"的定位叙事**直接冲突**（何况 step-parts 和 sendcutsend 本身需要网络）。对企业采购是红线，对个人用户是隐私顾虑。

## 6. 威胁与时间表

**0-12 个月**

1. **Autodesk Fusion MCP 已落地（2026-04）**——Fusion 用户（据称 50 万+ 订阅）现在有官方 agent 连接，text-to-cad 的"给 agent CAD 超能力"叙事对他们**直接失效**
2. **build123d-mcp 快速追赶**——特征识别、事务性编辑、设计审计、HTTP 会话隔离、公开基准成绩，维度上已超越

**12-24 个月**

3. **SolidWorks LEO 几何生成 GA** — 判断 **2027H2-2028**。理由：Dassault 路线图是 AURA（知识）→ LEO（工作流自动化）→ 几何生成的渐进路径，几何生成需领域训练数据，商业化路径仍早期。一旦 GA，SolidWorks 用户群体上 text-to-cad 毫无竞争力
4. **Schneider–PTC 整合**（2027 Q3 完成）— 可能加速 PTC AI 路线图，也可能因整合期拖延
5. **创业公司企业渗透** — Leo AI 若 12 个月内实现企业级参数化生成，"大机械模型"叙事空间被大幅收窄

**防御空间**：vendor 不愿意进入的地方——**vendor-lock-in-free 的生成**（Autodesk MCP 只能驱动 Fusion，text-to-cad 能驱动任何吃 STEP 的工具）、**制造全链路**（vendor AI 全聚焦设计端）、**离线/隐私敏感场景**。

## 7. 趋势信号

**MCP 标准化**：官方注册表 9,652 条服务器记录、SDK 月下载 97M+，但**企业生产部署仅 45%**（26% 有限生产 + 19% 广泛生产），安全是第一障碍。顺风，但标准化也意味着 **vendor 零成本复制 text-to-cad 核心功能**。

**几何生成仍是全行业真空**：Autodesk AU 2026、Siemens Solid Edge 2026（AI 生成 80% 图纸视图）、SolidWorks LEO——**没有一家在做几何生成**。

**学术前沿正在解决 text-to-cad 也依赖 LLM 猜测的环节**：Pointer-CAD（CVPR 2026，DeepSeek/港大/腾讯）的面/边 pointer 机制直指实体选择与量化误差——一旦开源落地，build123d 命令序列路径可能被端到端 B-rep 生成路径取代。

**资金流向**：$4.1M（Adam）、$9.7M（Leo AI）、$10M（Zoo）——**押注 SaaS 型 vendor-adjacent 创业公司，不是开源 agent skill**。

**市场规模**：3D CAD 软件市场 $17.34B @2030（CAGR 6.7%，Grand View Research）有可靠数据；但**"AI for CAD"/"agentic CAD" 作为独立细分没有可信公开规模数据**——这是真实发现而非搜索遗漏，赛道太新太模糊。

## 8. 三条建议

### ✅ 应该做

**1. 把 DfAM/DFM 产品化为"制造审查即服务"——接受任意 STEP/STL 输入，而非只审自己的产物。**

这是 12 个 skill 里最具防御性的能力，**没有任何竞品**（含 build123d-mcp 的 design_audit、vendor 助手、创业公司）做到这个深度。包装成可被任意 MCP agent 调用的工具，把价值从"生成入口"扩展为"审查节点"，产生跨竞品用户依赖。vendor 不会做跨格式审查——它们只想推自家生成路径。

**2. 在 CADGenBench 上公开跑分并公布成绩。**

build123d-mcp 已经在同一 benchmark 上声称 0.360→0.457。text-to-cad 应公开自己的数字——**赢了直接打击对手核心叙事，输了也比回避诚实**。"我的工具生成更准"比"我分发更广"更有说服力。

**3. 解决 Windows 11 Smart App Control 阻断——这是流量泄漏点，不是边缘 case。**

Win11 新机默认开启 SAC，意味着每个新购 Windows 11 的个人制造者（**正是核心用户**）在第一次 `uvx cadgen` 就撞 `ImportError: DLL load failed`。"用 WSL"不是解——把 1 步安装变成 5 步，对非开发者是劝退级。**此事优先级应高于任何新功能开发。**

### ❌ 不应该做

**不要追求企业机械工程市场——这是虚荣心陷阱。**

- 那个市场正在以 $22.6B 级别的交易垂直整合，开源 agent skill 不在牌桌上
- 企业合规需求（SOX/FedRAMP/审计）不是开源社区项目该满足的
- 追逐它会迫使项目加上多租户/RBAC/审计日志，**稀释最大资产——一键安装、30 秒出第一个 STEP 的零摩擦**
- Adam 和 Leo AI 各有 $4.1M/$9.7M 融资和全职企业销售团队

**反向利用**："企业不可用"应定位为**选择信号**——text-to-cad 是给那些不需要企业 CAD、但需要真几何生成和制造工作流的人。这个用户基数大得多，且 vendor 在这个层面上不会来。

---

## 证据质量与缺口

| 类别 | 内容 |
|---|---|
| **已验证**（带 URL+日期） | star 数/版本/融资金额/MCP 注册表数据/收购交易/论文会议，均附来源 |
| **合理推断** | LEO 几何生成 GA 时间预判（2027H2-2028）；个人制造者市场优势判断 |
| **需验证假设** | **"企业在开源 agent 工具上零渗透"——证据是间接的**（TechDraw AI 综述未提及任何企业部署案例，但没有直接的排除性证据）。这一条若被推翻，整个企业段结论要重写 |
| **证据薄弱** | 中国市场覆盖不足（卡伦特、华天、大腾的实际 AI 能力与市场地位无法验证）；私有公司路线图不可验证 |
| **明确未找到** | "AI for CAD" 细分市场的可信公开规模数据 |

---

## 附：分析所依据的上游报告

本文的竞品证据库来自同日的另一份调研（`Research Synthesist` 人格，4 路并行检索），涵盖：agent/MCP 类、商业 CAD 内嵌 AI、开源学术、中国生态、邻近生成式 3D 五大板块。
