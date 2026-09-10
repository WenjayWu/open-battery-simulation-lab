# Maintenance and Handover Guide

本手册用于接管、运行和维护 `open-battery-simulation-lab`。它优先回答四个问题：项目里有什么、怎样复现、怎样安全修改、出了问题怎样恢复。

## 1. Naming Policy

仓库根目录以及仓库内所有文件、文件夹均使用有意义的英文名称：

- 路径只使用 ASCII 字符，不使用中文、空格或特殊标点。
- 普通目录和文档文件优先使用小写 `kebab-case`，例如 `lfp-sei-plating`、`maintenance-guide`。
- Python 包、模块、函数和配置字段使用 `snake_case`，例如 `lfp_lab`、`sei_plating_demo`。
- 约定俗成的仓库文件保持大写，例如 `README.md`、`STATUS.md`、`LICENSE`、`AGENTS.md`。
- 文件内容可以使用中文、英文或双语；英文命名规则只约束路径和程序标识符。
- Git 测试会检查所有已跟踪路径是否为 ASCII 且不含空格。测试不能判断单词语义，因此新增路径仍需人工确认名称确为英文。

## 2. Five-Minute Takeover

在新的 Windows PowerShell 窗口中进入项目：

```powershell
cd D:\Professional\Simulation\Projects\open-battery-simulation-lab\projects\lfp-sei-plating
uv sync --frozen
uv run python -c "import pybamm; print(pybamm.__version__)"
uv run pytest -q
uv run python -m lfp_lab.run --case baseline
```

预期结果：

1. `uv sync --frozen` 根据 `uv.lock` 创建或恢复项目自己的 `.venv`。
2. PyBaMM 版本显示为 `26.6.2.0`。
3. 自动测试全部通过。
4. 基线结果写入 `results/runs/baseline/<run-id>/`，其中至少包含 `manifest.json`、`timeseries.csv`、`summary.csv`、PNG 图表和日志。

不要使用全局 `pip install`，也不要手动把依赖装入 Windows 或 Ubuntu 的系统 Python。

## 3. What This Workbench Does

PyBaMM 是电池机理模型与数值求解框架，不是三维 CAD 或通用三维有限元软件。本项目当前用它完成：

- 用 DFN/P2D 方程描述正极、隔膜、负极方向上的电化学过程。
- 计算电压、电流、浓度、电势、容量以及选定的副反应量随时间的变化。
- 组织可重复的工况、参数、求解、结果导出和质量检查。
- 为后续实验参数标定、退化分析和更复杂耦合建立可信的软件基线。

若研究对象需要真实三维几何、局部热场、结构应力或复杂流场，后续再由 Gmsh、FEniCSx、OpenFOAM、MOOSE 或 COMSOL 承担相应部分。PyBaMM 可以提供电化学源项和电芯尺度结果，但不会自动替代这些三维求解器。

## 4. Repository Map

```text
open-battery-simulation-lab/
├── .github/workflows/ci.yml          # 公开仓库的持续集成检查
├── comsol-projects/                  # COMSOL 项目说明与可公开脚本
├── docs/
│   └── MAINTENANCE_GUIDE.md          # 本手册
├── projects/
│   └── lfp-sei-plating/
│       ├── configs/                  # 工况与参数溯源配置
│       ├── notebooks/                # 调用核心代码的探索入口
│       ├── results/
│       │   ├── reference/            # 少量、已审查、可跟踪的参考结果
│       │   ├── runs/                 # 每次正式运行，默认不进入 Git
│       │   └── tmp/                  # 临时执行产物，默认不进入 Git
│       ├── src/lfp_lab/              # 唯一的求解与导出核心代码
│       ├── tests/                    # 科学约束、重复性和仓库规则检查
│       ├── pyproject.toml            # 直接依赖与工具配置
│       └── uv.lock                   # 完整可复现依赖锁
├── AGENTS.md                         # 自动化助手的仓库级安全边界
├── README.md                         # 项目入口与总体说明
└── STATUS.md                         # 当前状态、风险、验证和路线图
```

目录职责的核心原则是：源码与配置进入 Git，生成结果按价值筛选，虚拟环境与大型原始数据不进入 Git。

## 5. Environment Isolation

### 5.1 Normal Restore

在 `projects/lfp-sei-plating/` 中执行：

```powershell
uv sync --frozen
```

`--frozen` 表示严格使用现有 `uv.lock`，不会偷偷更新版本。`.venv` 可以删除后重建，因此不需要备份，也不应提交到 Git。

### 5.2 Intentional Dependency Update

只有明确计划升级依赖时才执行：

1. 修改 `pyproject.toml` 中的版本范围。
2. 执行 `uv lock` 重新生成锁文件。
3. 执行完整质量检查和两个案例的短求解。
4. 检查关键结果变化，更新 `STATUS.md`。
5. 将 `pyproject.toml` 与 `uv.lock` 放在同一个提交中。

不得只改锁文件或只改依赖声明。PyBaMM 主版本或参数接口变化时，应按科学模型变更处理，而不是普通维护更新。

### 5.3 Confirm System Python Is Untouched

系统 Python 不应能导入项目依赖。检查时直接调用系统 Python，而不是先激活 `.venv`：

```powershell
python -c "import importlib.util; print(importlib.util.find_spec('pybamm'))"
```

若输出 `None`，说明当前终端所指向的 Python 没有全局安装 PyBaMM。项目命令始终优先写成 `uv run ...`，避免混淆解释器。

## 6. Running Cases

### 6.1 Baseline

```powershell
uv run python -m lfp_lab.run --case baseline
```

该案例使用 Prada2013 LFP/石墨参数、等温 25°C、初始 SOC 95%，执行 1C 放电、静置、C/2 恒流恒压充电和再次静置。它是工作台的电化学参考基线，并不代表已经针对本地真实电芯完成标定。

### 6.2 SEI and Plating Methodology Demo

```powershell
uv run python -m lfp_lab.run --case sei_plating_demo
```

该案例保持 Prada2013 主体，只借用 OKane2022 中模型构建所需的 SEI 与析锂专用参数。所有借用项记录在 `configs/sei_plating_parameter_provenance.json`。结果必须保留 `illustrative_unvalidated` 标签，不可用于定量寿命或安全预测。

如果新版本模型需要白名单以外的参数，程序应立即失败。不要通过额外复制其他参数集的值来“让它跑起来”。

### 6.3 Quick Smoke Runs

开发阶段可以使用缩短运行：

```powershell
uv run python -m lfp_lab.run --case baseline --quick
uv run python -m lfp_lab.run --case sei_plating_demo --quick
```

短运行只验证软件链路，不代替正式工况和科学验收。

## 7. Reading the Results

每次运行目录都是独立的，常用文件含义如下：

| File | Purpose |
| --- | --- |
| `manifest.json` | 软件版本、案例、配置哈希、模型选项、运行时间和可信度标签 |
| `timeseries.csv` | 时间、电流、电压、容量和可用的关键副反应变量 |
| `summary.csv` | 按循环汇总容量、LLI、SEI 损失和析锂指标 |
| `*.png` | 便于快速检查趋势的图表 |
| `run.log` | 求解过程、警告和错误记录 |

分析结果时先读 `manifest.json`，确认案例、配置哈希和可信度标签，再看图表和 CSV。不要只凭 PNG 判断参数或工况；PNG 是视图，manifest 和配置才是可追溯依据。

`results/reference/` 只保存少量经过审查、适合公开和持续比较的基准文件。普通运行留在 `results/runs/`，必要时再将选定结果人工整理为参考结果。

## 8. Using the Notebook

```powershell
uv run jupyter lab
```

打开 `notebooks/01_workbench_smoke.ipynb`。Notebook 只应调用 `src/lfp_lab/` 中的核心逻辑，不复制模型构建或求解代码。提交前验证空内核顺序执行：

```powershell
uv run jupyter nbconvert --to notebook --execute notebooks/01_workbench_smoke.ipynb --output-dir results/tmp
```

Notebook 输出属于临时产物；除非它是经过审查的小型展示材料，否则不要提交执行后的副本。

## 9. Safe Ways to Modify the Project

### 9.1 Change an Existing Experiment

1. 复制一个 `configs/*.json` 并使用英文 `snake_case` 文件名。
2. 修改工况，而不是在 Python 源码里硬编码实验步骤。
3. 在 `src/lfp_lab/config.py` 中补充必要校验。
4. 在 `tests/` 中增加正常与异常输入测试。
5. 先做 quick run，再决定是否进行完整运行。

### 9.2 Add a New Case

1. 在 `configs/` 新建配置。
2. 在 `src/lfp_lab/cases.py` 中实现模型或参数装配。
3. 复用 `artifacts.py` 的导出流程，保持结果目录结构一致。
4. 在 `run.py` 中注册入口，不创建第二套运行脚本。
5. 增加测试，并在项目 `README.md` 与根 `STATUS.md` 记录科学边界。

### 9.3 Change Scientific Parameters

每项外部参数必须记录名称、数值、单位、来源、适用体系和使用理由。实验拟合参数还需记录电芯批次、实验条件、拟合方法、误差与版本。未经记录的参数变更不应合并到 `main`。

## 10. Quality Checks

日常修改至少执行：

```powershell
uv run ruff check .
uv run pytest -q
uv run python -m lfp_lab.run --case baseline --quick
uv run python -m lfp_lab.run --case sei_plating_demo --quick
```

涉及 Notebook、求解核心、参数集或依赖版本时，再执行 Notebook 空内核测试和相应完整案例。验收重点包括：

- 时间严格递增，电压、容量和副反应量为有限值。
- 求解达到预期实验终止条件。
- 同一锁文件和配置重复运行时，关键摘要在约定误差内一致。
- 退化示例的参数借用不越过 SEI/析锂白名单。
- 所有已跟踪路径均符合英文 ASCII 命名规则。
- Git 中没有虚拟环境、缓存、令牌、私人路径或大型二进制结果。

公开仓库的 CI 会在 Linux 与 Python 3.12 上重新执行冻结环境恢复、代码检查、测试、短求解和 Notebook 检查。CI 通过表示软件管线可复现，不表示模型已经过实验验证。

## 11. Git Workflow

开始工作前：

```powershell
git status --short --branch
git pull --ff-only
```

完成修改后：

```powershell
git diff --check
git status --short
git add <reviewed-files>
git diff --cached
git commit -m "<type>: <short English description>"
git push origin main
```

只添加已经人工审查的明确文件，不使用可能把大型结果和私人资料一起带入的宽泛操作。提交消息使用英文 Conventional Commit 风格，例如 `docs: update maintenance guide` 或 `feat: add calibrated lfp case`。

发布前检查：

- 是否出现访问令牌、私人邮箱、用户名绝对路径或实验对象身份信息。
- 是否意外跟踪 `.venv`、缓存、`results/runs` 或 `results/tmp`。
- 是否出现 COMSOL 软件、许可证、安装包、恢复文件或二进制模型。
- 参数或结果是否拥有足够的公开许可与引用信息。

## 12. COMSOL Storage Policy

`comsol-projects/` 是仓库中的项目、接口与说明区，不是软件安装目录。Windows 软件本体在仓库外层的 `Software/COMSOL/` 预留位置。可以放入 Git 的内容包括：

- 英文命名的 Markdown 说明。
- 可公开的 Java、MATLAB 或命令行自动化脚本。
- 不含机密参数的小型文本配置、重建步骤和模型索引。
- 经许可、经筛选的小型交换数据。

不得放入 Git 的内容包括：

- COMSOL 软件本体、安装器、ISO、压缩包、补丁或破解文件。
- 许可证文件、密钥、服务器地址和个人凭据。
- `*.mph`、`*.mphbin`、恢复目录以及大型求解结果。
- 未获公开许可的商业模型或合作方数据。

COMSOL 软件应安装在仓库外层预留的 `Software/COMSOL/`，其内部结构由用户未来决定。私人二进制模型应放在单独的本地数据目录并独立备份；仓库只保留可重建说明和公开接口。这样克隆仓库不会复制软件本体，也不会因公开 GitHub 而泄露许可证或模型。

## 13. Windows and WSL Responsibilities

Windows 负责源码、配置、文档、Git 和当前 PyBaMM 项目。未来 FEniCSx、OpenFOAM 与 MOOSE 放在 Ubuntu 24.04，是因为这些软件的官方包、MPI、PETSc、编译链和测试环境以 Linux 为主。

未来大型 Linux 求解的运行目录应放在 Ubuntu 自己的 Linux 文件系统中，而不是直接放在 `/mnt/d/`。版本化源码仍以 Windows 主库为准，可通过明确的同步或导出步骤送入 Linux 运行目录。Ubuntu 22.04 保留闲置，不承载新环境。

每个 Linux 求解器也要使用自己的独立环境，不得把 Python 依赖装进 Ubuntu 系统 Python。

## 14. Data and Backup Policy

Git 不是原始实验数据或大型仿真结果的备份系统。建议将资产分为三类：

| Class | Location | Backup |
| --- | --- | --- |
| 源码、配置、文档、小型参考结果 | 本仓库 | GitHub + 本地 Git |
| 大型运行结果与中间网格 | 项目外的数据区或 Linux 运行区 | 独立版本化备份 |
| 原始实验数据、私人模型、许可证 | 受控私人数据区 | 加密备份与访问控制 |

删除或迁移大型数据前，先列出目标、估算大小、检查引用关系并做 dry run。不要让自动化工具递归整理或删除未知的实验数据目录。

## 15. Troubleshooting

### `uv` Is Not Found

先确认 `uv --version`。若机器尚未安装 `uv`，按 uv 官方方式安装用户级工具；不要用系统 `pip` 安装项目依赖。安装后重新打开 PowerShell。

### PyBaMM Cannot Be Imported

确认当前目录是 `projects/lfp-sei-plating/`，执行 `uv sync --frozen`，随后使用 `uv run python ...`。不要依赖手工激活后遗留的终端状态。

### Locked Environment Cannot Be Restored

记录完整错误和平台信息，不要立即删除 `uv.lock`。先确认 Python 3.12、网络和磁盘空间，再检查锁文件是否被部分修改。只有确认要升级依赖时才重新生成锁文件。

### Solver Fails or Becomes Slow

先保存日志和 `manifest.json`，再缩短为 quick case。检查最近的配置、参数、PyBaMM 版本、终止条件和网格设置。不要通过放宽所有容差来掩盖模型错误。

### Results Differ from the Reference

比较 `manifest.json` 的配置哈希、PyBaMM/Python 版本与模型选项。若版本相同，再定位参数、求解器设置和浮点平台差异。任何有科学意义的变化都要在 `STATUS.md` 记录。

### Accidental Global Installation

先确认是哪一个 Python 解释器安装了包，再使用该解释器对应的包管理方式清理。不要删除系统 Python。完成后重建项目 `.venv` 并重新运行测试。

### GitHub CLI Reports 401

先运行 `gh auth status --hostname github.com`。如果输出同时显示失效的 `GITHUB_TOKEN` 和有效的 keyring 账户，说明环境变量优先覆盖了钥匙串登录；应在干净终端中运行，或只在当前 PowerShell 会话移除失效变量后重试。不要用 `gh auth token` 打印令牌，也不要把令牌写进仓库配置。只有钥匙串账户本身也失效时，才执行 `gh auth login --web`。

## 16. Recovery from a New Machine

恢复公开部分只需要：

1. 安装 Git、Python 3.12 和 uv。
2. 克隆公开仓库。
3. 进入 `projects/lfp-sei-plating/`。
4. 执行 `uv sync --frozen`。
5. 执行测试与 baseline quick run。

私人实验数据、COMSOL 二进制模型和大型运行结果不在公开仓库中，必须从各自的受控备份恢复。`.venv` 不需要恢复，应由锁文件重新生成。

## 17. Routine Maintenance Checklist

### Before Every Work Session

- 阅读 `STATUS.md` 的当前风险与阻塞。
- 检查 Git 状态，确认没有来源不明的未提交修改。
- 用 `uv run` 运行命令。

### Before Every Commit

- 跑 Ruff、pytest 和相关 smoke case。
- 检查路径为英文 ASCII 且无空格。
- 审查差异、输出和敏感信息。
- 科学模型变化同步更新说明与状态。

### Monthly or Before a Milestone

- 在干净环境执行 `uv sync --frozen`。
- 重跑完整基线与退化示例，比较参考摘要。
- 检查 GitHub CI、依赖安全公告与磁盘占用。
- 验证大型数据和私人模型备份可恢复。
- 更新 `STATUS.md` 的版本、验证结果、风险和下一步。

## 18. Responsibility Boundaries

- `README.md` 面向第一次进入仓库的人，提供最短入口。
- 本手册面向项目所有者，提供接管、维护与恢复流程。
- `AGENTS.md` 面向自动化助手，规定命名、隔离、数据安全与验证边界。
- `STATUS.md` 是随项目变化持续更新的事实台账，不应被手册中的历史描述替代。

当手册、实际代码和 `STATUS.md` 不一致时，先停止高风险操作，核对 Git 历史和当前环境，再修正文档；不要默认为代码或文档中的任一方一定正确。
