# text-to-cad 使用手册

装好之后你只有两个入口，正常情况下你只会用到第一个：

| 入口 | 形式 | 什么时候用 |
| --- | --- | --- |
| 模型脚本 | `python <model>.py` | 造零件、造 DXF 图纸。**所有生成都走这里** |
| `cadgen` 命令 | `cadgen <格式> <动作> 输入 [输出]` | 处理已经存在的文件：转格式、渲染快照、校验 URDF/SDF/SRDF |

`cadgen` 命令**只吃文件和字节，从不吃脚本**。它的动作是固定的那些：

```
cadgen stl|3mf|glb build <in.step> [out.<ext>]   # STEP 文档 → 网格
cadgen step|stl|3mf|glb|dxf|urdf|sdf snapshot <file> [out.png]
cadgen urdf|srdf|sdf validate <file> [--strict] [--json]
cadgen snapshot <file> [out.png]                   # 按后缀自动路由
cadgen viewer --host 127.0.0.1 --json --detach
cadgen doctor <skill-dir>
cadgen telemetry status|on|off
cadgen store why <model.py>
cadgen daemon status
```

> 文档里写 `cadgen` 和 `python`，指的是技能文件里钉死的同一条启动命令，
> 技能实际执行的是 `uvx --no-config --managed-python --python 3.13 --from cadgen==0.7.19 cadgen`
> （`python` 把结尾的 `cadgen` 换成 `python`）。**版本号跟着技能走**，你不用自己敲 uvx。
> 你的机器上需要 Python ≥ 3.11，技能实际跑在 uvx 拉下来的 3.13 上。

---

## 1. 先花 30 秒确认安装是好的

让 agent 跑这条（把 `<skill-dir>` 换成你某个技能的安装目录）：

```bash
cadgen doctor ~/.claude/plugins/cache/.../skills/cad
```

它会打印：装的是哪个 cadgen、Python 版本、安装路径、共享的守护进程、**内核（OCP）能不能加载**、以及**这个技能钉的版本和你装的对不对得上**。

- `kernel OK — OCP at ...` → 一切正常。
- `kernel FAILED` → 见 [第 6 节](#6-陷阱与修复)，Windows 上大概率是 Smart App Control。

**遥测默认是开的。** 关掉：

```bash
uvx cadgen telemetry off          # 或者直接跟 agent 说"关掉遥测"
DO_NOT_TRACK=1 / CADGEN_TELEMETRY=0   # 只对这一个进程生效
```

**首次运行要联网**：第一次调用会下载 cadgen 运行时，第一次渲染快照还会下载无头浏览器。之后都走缓存（`uv cache prune` 清）。

---

## 2. 能力矩阵

「内核」= 需要 OCP/OpenCascade CAD 内核。12 个技能里只有 4 个绕不开它。

| 我想做的是 | 用哪个技能 | 产物 | 内核 | 网络 | 还得自己装什么 |
| --- | --- | --- | --- | --- | --- |
| 用一句话造一个 3D 零件 / 装配体 | `cad` | `.step`，可加 `.stl` / `.3mf` / `.glb` | ✅ | 首次下载 | — |
| 改现有零件、改尺寸、导出网格 | `cad` | 同上 | ✅ | 首次下载 | — |
| 看已有的 STEP/STL/3MF/GLB | `cad` | 浏览器里的查看器链接 | ✅（渲染） | — | — |
| 拍一张照片/草图让我照着建模 | `cad` | 同上 | ✅ | 首次下载 | — |
| 出带尺寸的工程图 | `engineering-drawing` | **一个 PDF** | ✅ | 首次下载 | — |
| 切激光/等离子/水刀用的展开图、垫片、模板 | `dxf` | `.dxf` | ✅（约 2.5s 冷启动，热守护进程吸收） | 首次下载 | — |
| 把 vendor 的 STEP 展平成下料图 | `dxf` | `.dxf` | ✅ | 首次下载 | — |
| 找标准件：螺丝、轴承、电机、连接器、舵机 | `step-parts` | 目录记录 + 下载的 `.step` | ❌ | ✅ 必需 | — |
| 这零件能打印吗 / 壁厚够吗 / 要多少支撑 | `dfam-check` | 可打印性报告 | ❌ | — | 技能的 `requirements.txt` |
| 推荐摆放方向省支撑 | `dfam-check` | 候选方向 + 支撑面积 | ❌ | — | 同上 |
| 能不能折弯 / 加工 / 注塑 | `dfm` | DFM 审查报告 | ❌ | — | 注塑才需要 `requirements.txt` |
| 切片成 G-code | `gcode` | `.gcode` + `.gcode.3mf` | ❌ | — | **OrcaSlicer（必装）** |
| 发到拓竹打印机 | `bambu-labs` | 在 App 里打开文件 | ❌ | 打印机/云 | **Bambu Connect 或 Bambu Studio（必装）** |
| 这个文件能传 SendCutSend 吗 | `sendcutsend` | 上线前审查报告 | ✅（用 `$cad` 量 STEP 时） | ✅ 必需 | — |
| 写 / 改机器人结构文件 | `urdf` | `.urdf` + 校验报告 | 校验 ❌ / 快照 ✅ | — | — |
| 给 URDF 加 MoveIt 规划语义 | `srdf` | `.srdf` + 校验报告 | 校验 ❌ / 快照 ✅ | — | — |
| 写 Gazebo 模型 / 世界 | `sdf` | `.sdf` + 校验报告 | 校验 ❌ / 快照 ✅ | — | `gz`（可选，装了会自动跑 `gz sdf --check`） |

关于内核那一列：`urdf` / `srdf` / `sdf` 的**校验只用 Python 标准库**，不加载 OCP；但它们的快照和 CAD 查看器要画模型，那条路会碰内核。所以 Windows 上你可能看到「validate 过了、snapshot 挂了」，这是正常的，不是安装坏了。

---

## 3. 四个真实任务走一遍

### 3.1 "帮我做一个 L 形安装支架"

> 你说：`帮我做一个 L 形支架，40mm 宽、20mm 深、壁厚 4mm，上面四个 M5 孔，孔距 30mm 再给我一份 STL`

**发生了什么。** agent 用 `cad` 技能，在项目里写一个 Python 模型脚本 —— 不是一个"配置文件"，是真正的 build123d 代码：

```python
# src/bracket.py
from cadgen import build123d as bd
from cadgen import step, stl, threemf

WIDTH, DEPTH, HEIGHT, THICK = 40.0, 20.0, 24.0, 4.0

@step(out="../STEP/bracket.step")
@stl(out="../STL/bracket.stl")
@threemf(out="../3MF/bracket.3mf")
def bracket():
    base = bd.Box(WIDTH, DEPTH, THICK)
    # 立板底边坐在底板上表面（z = THICK/2），故整体平移到 HEIGHT/2
    wall = bd.Pos(0, DEPTH / 2 - THICK / 2, HEIGHT / 2) * bd.Box(WIDTH, THICK, HEIGHT - THICK)
    body = base + wall
    # 底板上四个 M5 通孔（Ø5.5 让位孔），横向 30mm、纵向 9mm，全部避开立板一侧
    for x in (-15.0, 15.0):
        for y in (-6.5, 2.5):
            body -= bd.Pos(x, y, 0) * bd.Cylinder(2.75, THICK * 2)
    body.label = "bracket"
    return body

if __name__ == "__main__":
    bracket()
```

然后跑：

```bash
python src/bracket.py        # 打印 built STEP/bracket.step（没改动时打印 current ...）
cadgen step snapshot STEP/bracket.step tmp/review.png
```

**你拿回来的东西：**
- `STEP/bracket.step`、`STL/bracket.stl`、`3MF/bracket.3mf`
- 会话里一个能旋转缩放的查看器卡片（在终端、Cursor 这类不能内嵌视图的 app 里，是一个浏览器链接）
- 一份**它实际跑过的检查清单**：单位、阈值、选了哪些几何、哪些要求没验
- 它自己生成并读过的快照图 —— 快照是它给自己的自检，不是给你看的

**注意**：默认毫米、XY 平面、+Z 朝上。几何不能依赖时间、随机数、环境变量或当前工作目录。下次你改尺寸，它改脚本重跑，输出自动跟上。

**接着出工程图：**

> 你说：`给这个支架出一份带尺寸的工程图，A3`

`engineering-drawing` 技能的产物是**一个 PDF**（车间收的就是这个，系统也都能打开）。它不写 DXF，没有配套文件，也没有 CLI —— 脚本本身就是接口：

```bash
python src/bracket_drawing.py      # 打印它写出的 PDF
```

它会打印 PDF 路径，**以及它画图时注意到的问题**，这两个要最先读：

- `measures blank paper` → 你的尺寸点没落在视图的几何上，通常是零件从角点建的、脚本却假设它居中。查一下零件的包围盒。
- `annotation overlaps` → 两个标注压在一起了。把 `sheet.three_views(part, gap=...)` 的间距调大，或者给某个标注传 `offset=`。

**容差不会自己出现。** 只有你在脚本里写了 `tol=` / `fit=` / `general_tolerance=` 才有公差值，而且值必须来自设计要求或你 —— 没给的尺寸就是名义尺寸。

### 3.2 "我有张 vendor 的板子 STEP，要送激光切割"

> 你说：`我有个 vendor_panel.step，想送去激光切割，帮我出展开图，再看看能不能直接传 SendCutSend`

**发生了什么。** `dxf` 技能。关键点：**你项目自己生成的 STEP 绝不能被读取来做展开图** —— 输入和输出是同一个文件，每次跑都会变，永远判不出"最新"，而且展开图会依赖上一次跑剩下在磁盘上的东西。

正确做法有两种。这是**导入一个没有 Python 源的外购 STEP**：

```python
# panel_flat.py，与 imported/vendor_panel.step 同目录
from pathlib import Path
from cadgen import dxf, flatten, read_step

_HERE = Path(__file__).resolve().parent
KERF = 0.15

@dxf
def panel_flat():
    panel = read_step(_HERE / "imported" / "vendor_panel.step")   # 被记为输入
    return flatten.flat_pattern(panel, coordinate=3.0, kerf=KERF)

if __name__ == "__main__":
    panel_flat()
```

```bash
python panel_flat.py                  # 打印 built panel_flat.dxf
cadgen dxf snapshot panel_flat.dxf review.png --appearance dark
```

如果零件是你自己的模型写的，用**另一种**：建一个自己的文件 `bracket_drawing.py`（和 `bracket.py` 并列），`from bracket import bracket` 然后调用它 —— 按结果追踪，改注释不改几何就不会误触发重建。

**契约要记住：**
- `@dxf` 函数**不接参数**，返回 build123d 的二维几何，**引擎负责写文件**。你不用建文档、不用命名实体。
- 返回一个裸 shape → 全部进 `CUT` 层。返回 `{图层: shape}` → 命名图层。
- 几何**必须在 XY 平面上**。从实体上取的面带着实体的 Z 高度，要 `flatten.flatten_face(face)` 压平。引擎会**直接拒绝**平面外的几何，而不是偷偷写它的 XY 投影。
- 文字用 `bd.Text(...)` 雕成**轮廓**，不要用 DXF 的 `TEXT` 实体 —— 切割和打标工具链吃的是几何。
- **曲线保持曲线。** 圆角导出成 `ARC`、孔导出成 `CIRCLE`。如果你的轮廓变成几百条短 `LINE`，说明某处退化成了采样路径，去查，别将就。

**校验是在生成过程中做的**，不是事后补：cut 图层的轮廓必须闭合、不许零长度实体、不许重复几何、modelspace 不许为空。有 error 的构建直接失败。开头的轮廓只允许出现在 bend / engrave / reference 这类图层的图层名里。

**接着跑 SendCutSend 上线前审查：**

> 你说：`SendCutSend 能收吗？`

`sendcutsend` 技能会去抓 SendCutSend **官网当前的**订购指南、目录 JSON、规格 JSON 当证据源（不是稳定 API，字段会变），然后量你那个确切的文件：

- DXF 量：单位、尺寸、图层、实体类型、开口/重复几何、不支持的标注、候选孔和圆、折弯线候选、折弯到切割的距离、折弯两侧的局部折边深度、零面积轮廓
- STEP 量：可解析性、单位提示、实体/曲面信号、包围盒、厚度、折弯面半径

**它只在每一项引用的检查都通过了，才会说这个文件"SendCutSend ready"。** 源数据抓不到、缺字段、字段是 `N/A`、源之间冲突 —— 一律报 `❓ need more info`，绝不替你猜一个 pass。

DXF 单位特别注意：`$INSUNITS` 必须是 `1`（英寸）或 `4`（毫米）。不是这两个值就按比例错误处理，让你重新导出或确认，**它不会偷偷缩放几何**。

### 3.3 "这个零件能打印吗？能的话给我切了"

> 你说：`这个件能直接打印吗？不行的话告诉我怎么改`

**第 1 步 —— 先要一个网格。** DfAM 量的是网格，不是 B-rep。你手上是 STEP 的话，用 `cad` 技能导一个 STL 边车文件：

```bash
cadgen stl build STEP/part.step STL/part.stl
```

直接把 STEP 喂给 `dfam_tool.py measure` 会退出 1 并返回 `{"error": "failed to load mesh: ..."}` —— 那是**喂错了输入**的信号，不是缺依赖，**不要去装别的网格库绕过它**。

**第 2 步 —— 装依赖再量。**

```bash
python scripts/dfam_tool.py measure part.stl --angle-limit 45
python scripts/dfam_tool.py orientations part.stl --angle-limit 45
```

`--angle-limit` 是目标工艺的自支撑角，量之前就要定下来，工艺变了要重量（支撑面积的分箱是按它来的）。

**第 3 步 —— 拿实测值比工艺限值**（内置默认值；你手上的机床/材料数据表优先级更高）：

| 限值 | FDM/FFF | SLS (PA12) | SLA/DLP | PBF-LB 金属 | MJF |
| --- | --- | --- | --- | --- | --- |
| 最小支撑壁厚 (mm) | 1.2 | 0.7 | 0.5 | 0.4 | 0.5 |
| 最小悬空壁厚 (mm) | 1.6 | 0.7 | 1.0 | 0.5 | 0.5 |
| 自支撑角 (°) | 45 | 不适用 | 30 | 45 | 不适用 |
| 最小孔径 (mm) | 2.0 | 1.5 | 0.5 | 1.5 | 1.0 |
| 最小正特征 (mm) | 0.8 | 0.8 | 0.2 | 0.4 | 0.5 |

**读结果时：**

- 状态只有三种：`✅ pass` / `❌ fail` / `❓ need more info`。**没有"差不多"。**
- 命令退出码：**0** = 完整报告，**2** = 部分报告（某个测量族算不出来，比如依赖不全时的 `wall_thickness`，或没有凸包时的 `support_volume`）。部分报告里的族一律当 `❓` 读，**绝不是测出来是 0**。
- `p05_mm` 低于壁厚限值就算违规，哪怕 `min_mm` 看着像采样离群点。两个值都报。
- 装配体上的薄壁会给出 `body_count` 和 `per_body` 拆分，违规要归到具体那个零件上，不能把整机混在一起算。
- **粉末工艺（SLS、MJF）不要套支撑角结论** —— 粉末本身就支撑。相关的检查是困粉排逸，**这个工具现在测不了**，有封闭空腔就报 `❓`。
- `scale.units_suspect` 为 `true`（从包围盒对角线判断）说明源文件可能是米或英寸：所有朝下的面都被当成贴在板上，支撑和悬垂数字全是 0.0，**这时什么都别比**，先回去问用户单位。

**第 4 步 —— 改。** 每个 `❌ fail` 都会带一句带数字的改法，比如"把 [12.4, 3.0, 8.1] 处的壁厚从 0.6 mm 加到 ≥1.2 mm"。你可以直接说"照这个改"，`cad` 技能改完重新生成，再回来重量，直到没有 `❌ fail`。

**第 5 步 —— 切片。这需要你自己先装 OrcaSlicer。**

```bash
brew install --cask orcaslicer      # macOS；Windows/Linux 从 orcaslicer.com 的 releases 装
```

OrcaSlicer 的命令行**不会替你填父级预设**，必须给全：

```bash
python scripts/orca_presets.py --list machine --match "MK4S"
python scripts/orca_presets.py --printer "Prusa MK4S 0.4 nozzle" \
  --process "0.20mm SPEED @MK4S 0.4" --filament "Prusa Generic PLA @MK4S" --out presets

<orca> model.stl --load-settings "presets/process.json;presets/printer.json" \
  --load-filaments presets/filament-1.json \
  --arrange 1 --slice 0 --outputdir /绝对路径/out --export-3mf model.gcode.3mf
```

**它只用你自己的预设，不会替你发明一个** —— 热床尺寸或温度猜错会损坏打印机。

打印前自己确认一遍切片设置（OrcaSlicer 写在 G-code 末尾）：

```bash
grep -E '^; (printer_model|nozzle_diameter|filament_type|nozzle_temperature|hot_plate_temp|bed_temperature) =|printing time' out/plate_1.gcode
```

**第 6 步 —— 发到打印机。** `gcode` **从不接触打印机**。拓竹机器要走 `bambu-labs`，它把文件在 App 里打开，**你自己选打印机、你自己按打印**：

> 你说：`把这个发到我的 X1C`

- 已切片的 `.gcode.3mf` → 打开在 **Bambu Connect** 里
- 没切片的 `.3mf` / `.stl` / `.step` → 打开在 **Bambu Studio** 里，让它自己切

它**永远不会报告"打印开始了"** —— 它看不见打印机。也不会向你要 access code。Bambu Connect 还需要 Windows 10+ 或 macOS 13+，并且你的打印机在该账号下或处于 LAN 模式；**Linux 上 Bambu Connect 还在开发中，用 Bambu Studio**。

其他品牌的打印机：`gcode` 给你 `.gcode` 文件，你用打印机的官方软件 / PrusaLink / OctoPrint / Mainsail / Fluidd 或者 SD 卡自己打。

### 3.4 "给我的六轴机械臂写 URDF 和 MoveIt 配置"

> 你说：`我有一台六轴机械臂，帮我写 URDF，然后配一个 MoveIt 的 SRDF`

**URDF（`urdf` 技能）。** 源文件就是 `.urdf` 本身 —— **直接写 XML，不要造 Python 生成管线，也不存在 `gen_urdf()` 这种东西。**

它会在 `.urdf` 顶部写一段**设计台账**注释块：坐标系、关节、几何、单位、每一条假设。改正则、原点、轴向、网格比例、限位、惯量之前，先读它。

- 惯量张量、质心、多连杆单位换算、镜像变换这些**算出来的数字，不许手敲** —— 原始体用闭式公式，网格来的值用一次性脚本算。
- `visual` / `collision` / `inertial` 分开建模（目标消费者需要时才分开），纯坐标系链接可以故意不写质量和几何。

```bash
cadgen urdf validate path/to/robot.urdf --strict
cadgen urdf validate path/to/robot.urdf --json          # 一行 JSON：ok / path / issues / summary
cadgen urdf validate path/to/robot.urdf --packages robot_description=/path/to/pkg
cadgen urdf snapshot path/to/robot.urdf review.png --joint-values '{"elbow_joint": 45}'
```

**校验过了不等于空间上是对的。** 一个 URDF 可以结构全对，关节却装在错的位置 —— 台账和查看器里逐关节摆一遍就是为了这个。

> 你说：`URDF 没问题了，写 SRDF`

**SRDF（`srdf` 技能）。** 先有一条**有效的 URDF** —— SRDF 只加规划语义，不定义物理结构。同样直接写 XML，没有 `gen_srdf()`。

分工记牢，别放错地方：

| 文件 | 管什么 |
| --- | --- |
| URDF | 物理结构：link、joint、几何、惯量、限位、mimic、transmission |
| SRDF | MoveIt 语义：virtual joint、passive joint、planning group、group state、end effector、禁用碰撞对 |
| SDF | 仿真与场景：物理、传感器、灯光、插件、world |

**几何、惯量、joint origin、link 位姿、网格引用、物理限位、transmission、`ros2_control` 接口，一律不进 SRDF。**

流程上必须先**把 URDF 的 link/joint 表列出来，把名字从表里抄进去** —— 不要凭记忆敲任何一个名字。配对方式只有一个：`.srdf` 和它的 `.urdf` **同目录、同 `<robot name>`**，一个名字在一个目录里只能有一个 URDF。没有元数据元素可以连它们。

group state 用 **URDF 原生单位**：revolute / continuous 用**弧度**，prismatic 用**米**。不要在 SRDF 里存角度。禁用碰撞对必须有真实的 reason 和出处，不能编一张宽泛的禁用表。

```bash
cadgen srdf validate path/to/robot.srdf --strict
cadgen snapshot path/to/robot.srdf review.png     # 按后缀路由到配对的 URDF 几何
```

**渲染好看证明不了规划正确。** 名字对得上、链条解得开，不等于 MoveIt 会按你想的方式规划。

**SDF（`sdf` 技能）** 同理，直接写 XML。注意：这里说的是 SDFormat 仿真格式，**不是有符号距离场几何**。新文件默认 `version="1.12"`，用 SI 单位，每个非平凡的 pose 和轴都要**显式**写 `relative_to` / `expressed_in` —— 隐式坐标系默认值是 SDF 的头号故障来源。

```bash
cadgen sdf validate path/to/model.sdf --gz-check required   # 默认 auto：gz 在 PATH 上就跑
```

---

## 4. 它做不到的事（直说）

| 你可能会想 | 事实 |
| --- | --- |
| `cadgen step inspect` | **已经删除了。** 现在跑它会得到一条教学错误：`cadgen step inspect has been removed`。要检查几何就写 Python：`from cadgen import read_scene`，`scene.resolve(ref).shape()`，需要的话用 `from cadgen.geometry import closest_points, overlap_volume, topology_errors`。检查项和阈值由你在脚本里定。 |
| `cadgen dxf build` | **不存在这个命令。** DXF 只能由 `@dxf` 装饰器 + `python <drawing>.py` 生成。`cadgen dxf snapshot` **只接受 `.dxf` 文件**，传脚本进去会被指名拒绝。 |
| 让它生成 / 参数化 URDF、SRDF、SDF | **没有生成 CLI，没有 `gen_urdf()` / `gen_srdf()` / `gen_sdf()`。** 这三种格式只有**校验 + 快照 + 查看**：直接手写 XML，源文件即真理。 |
| 工程图的剖视图、局部放大图、辅助视图 | **没有。** 视图是从内核投影出来的**正交投影视图 + 隐藏线 + 中心标记**。图纸上没画的东西，图上就没有 —— 它会在交付时说明视图不显示什么。 |
| 工程图出 DXF / CAD 图层 / 配对文件 | **不出。** 输出就是**一个 PDF**，没有 DXF，没有配对，没有关联。用 `$dxf` 做的是切割图和展开图 —— 那是刀路，不是图纸。 |
| 让工程图自动带公差 | **不会。** 公差只来自你写的 `tol=` / `fit=` / `general_tolerance=`。没写的尺寸就是名义尺寸。 |
| 钣金和 CNC 的自动几何测量 | **没有测量脚本。** `dfm` 只有注塑有 `scripts/mold_tool.py`（量拔模角、倒扣、投影面积）。钣金和 CNC 的参考文档**没有对应的几何分析器**，那两条流程靠 CAD 检查或你提供的尺寸，量不到就标 `unverified`。 |
| DFM 制造可行性认证 | **不是。** 这是**有引导的审查**，不是自动特征识别或认证引擎。没有发现 ≠ 全面可行。 |
| 粉末工艺的困粉排逸检查 | **测不了。** SLS / MJF 的相关风险一律 `❓ need more info`。 |
| DfAM 切片 / 上传 / 起打印任务 | **不做。** 切片归 `gcode`，发送归 `bambu-labs`。 |
| 混合工艺后处理器 | 不做。陶瓷、冷萃、金属打印不在列。 |
| DfAM 量 STEP | **不行，喂错输入了。** 导出 STL 边车文件再量。 |
| 在 DXF 图纸上摆相机、剖切、渲染模式、视图标签 | **这些 flag 不存在。** 图纸不是场景，`--camera` / `--display` / `--mode` / `--view-labels` 在 `cadgen dxf snapshot` 上不存在（传进去会被指名拒绝）。只有 `--appearance`、`--size-profile`、`--width`/`--height`。 |
| CLI 检查一个已有的 `.dxf` | **没有这个 CLI。** 用 `ezdxf` 自己读实体/图层，`cadgen.drawing_checks.validate_dxf_file` 跑绘图检查，几何在查看器里目视。 |
| 启动 / 暂停 / 取消打印，读打印机状态 | **不行。** 拓竹的固件只通过 Bambu Connect（或 LAN-only 的开发者模式）接受这些。 |
| 拿 DfAM / DFM / SendCutSend 的结论当最终签核 | **不要。** 报告里会写清楚哪些检查跑了、哪些没跑、缺什么证据。 |

---

## 5. 命名与文件约定（少踩坑）

- **一个模型一个入口文件，脚本和它声明的输出共用一个文件名主干。** `bracket.py` → `bracket.step`。
- DXF 图纸有自己的主干，和模型并排：`bracket_drawing.py` 放在 `bracket.py` 旁边。
- 装饰器上的 `out=` 是**相对脚本自身**的路径；CLI 的路径是**相对当前工作目录**的。
- 默认毫米、XY 平面、+Z 朝上。CAD 项目的惯例是 `src/` 放脚本，`STEP/`、`STL/`、`3MF/`、`GLB/`、`DXF/` 放输出。
- 一个模型读到的**每一个文件都是它自己的输入**：`json.load`、`np.load`、`import_step`、项目字体文件，无一例外。**模型绝不读自己的输出。**
- 探索性检查脚本放 `tmp/`（或系统 `/tmp/`），要留的放 `checks/`。

---

## 6. 陷阱与修复

### 6.1 Windows 11 Smart App Control —— 头号激活阻塞 ⚠️

**症状**：每个 `cadgen` 命令和每次 `import build123d` 都失败，报

```
ImportError: DLL load failed while importing OCP
```

事件查看器 → `CodeIntegrity › Operational`，**事件 ID 3077**。`cadgen doctor` 会直接点名这一条。

**原因**：CAD 内核 OCP（OpenCascade 的 Python 绑定）是一个**未签名的原生模块**，而 Windows 11 的 Smart App Control 会拦截未签名的原生代码。**全新安装的机器上它默认是开的。**

**Smart App Control 没有逐应用的例外机制。** 两条路：

| 方案 | 做法 | 代价 |
| --- | --- | --- |
| 关掉它 | 设置 → 隐私和安全性 → Windows 安全中心 → 应用和浏览器控制 → Smart App Control 设置 → 关 | **一旦关掉，只能重装 Windows 才能重新打开。** 想清楚。 |
| 走 WSL | 在 WSL 里跑 CAD 技能 | 该设置对 WSL 不适用，CAD 全套可用 |

wheel 是 cadquery-ocp 项目构建的，**签名不是本仓库能做的事**，所以只能走上面两条。

### 6.2 其他会绊你的

| 现象 | 原因 | 怎么办 |
| --- | --- | --- |
| `cadgen step inspect ...` 报"has been removed" | 该命令已删除 | 改用 `read_scene` + `cadgen.geometry` 的 Python 脚本，见第 4 节 |
| DXF 每次都全量重建，从来不显示 `current` | 读了本项目自己生成的 STEP 当输入，循环了 | 换成 `import` 模型脚本调用它；外购 STEP 单独放 `imported/` 目录并提交 |
| DXF 构建报平面外几何 | 面是从实体上取的，带着实体的 Z 高度 | `flatten.flatten_face(face)` 压平，或 `bd.Location((0,0,-z)) * face` |
| 轮廓导出成几百条短 `LINE` | 有东西退化成了采样路径，不是精确 OCC 运算 | 去查，不要将就 |
| DfAM 报 `{"error": "failed to load mesh"}` | 喂了 STEP，B-rep 不是网格 | 先 `cadgen stl build` 导出 STL。**不要去装别的网格库。** |
| DfAM 退出码 2，报告里 `"partial": true` | 某个测量族算不出来（依赖不全 / 无凸包） | 那些族当 `❓` 读；重装 `requirements.txt` 后再比壁厚 |
| DfAM 悬垂和支撑全是 0.0 | `scale.units_suspect` 为 true，源文件可能是米或英寸 | 先跟用户确认单位，别比任何限值 |
| 第一次跑很慢 | 首次下载运行时；首次快照还要下载无头浏览器 | 之后走缓存。冷启动加载内核约 2.5s，热守护进程吸收 |
| 版本对不上 / 文档和实际行为不符 | 装了旧版 cadgen | `cadgen doctor <skill-dir>`，它会核对技能钉的版本 |
| 机器人链接的网格加载失败（"No link mesh loaded for robot"） | Git LFS 指针没展开 | `git lfs checkout <mesh dir>` |
| 遥测一直开着 | 默认开 | `uvx cadgen telemetry off`，或 `DO_NOT_TRACK=1` |
| DXF 单位检查直接报比例错误 | `$INSUNITS` 不是 `1`（英寸）也不是 `4`（毫米） | 重新导出或确认单位。它不会偷偷缩放 |
| 工程图打印 `measures blank paper` | 尺寸点没落在视图几何上，零件多半是从角点建的 | 查零件包围盒 |
| 工程图打印 `annotation overlaps` | 两个标注压在一起 | 调大 `three_views(gap=...)` 或给标注传 `offset=`，重跑 |

---

## 7. 外部依赖清单（都得你自己装）

| 依赖 | 谁需要 | 怎么装 |
| --- | --- | --- |
| [uv](https://docs.astral.sh/uv/) | **全部** | `uv --version`，没有就装它的安装器 |
| OrcaSlicer | `gcode` | macOS：`brew install --cask orcaslicer`；Windows/Linux：[releases](https://github.com/OrcaSlicer/OrcaSlicer/releases) |
| Bambu Connect / Bambu Studio | `bambu-labs` | 官网；需要 Win10+ / macOS 13+，Linux 用 Bambu Studio |
| SendCutSend 官网可访问 | `sendcutsend` | 无需安装，技能直接抓官方来源 |
| `api.step.parts` 可访问 | `step-parts` | 无需安装 |
| `gz`（Gazebo） | `sdf` | 可选。装了就自动跑 `gz sdf --check`；`--gz-check required` 可把它变成必需 |
| `requirements.txt` | `dfam-check`、`dfm`（仅注塑） | 装在项目 Python 环境里 |