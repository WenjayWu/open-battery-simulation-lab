# 工作台状态

更新时间：2026-09-10（Asia/Shanghai）

## 当前阶段

- 规划：已完成。
- 实施：本地交付已完成。
- 当前里程碑：第一阶段验收完成。
- 维护交接：已补充维护手册、仓库级与项目级自动化操作边界，并加入英文路径自动检查。

## 环境与位置

| 项目 | 状态 | 说明 |
| --- | --- | --- |
| Windows 主库 | 已确认 | 当前 Git 工作区；不记录用户目录绝对路径 |
| Windows 系统 Python | 保持不变 | Python 3.12.10；实施前无法导入 PyBaMM |
| Ubuntu 24.04 | 已配置 | WSL2；47 GiB 可见内存、16 GiB swap、28 逻辑处理器、RTX 5070 Ti 可见 |
| Ubuntu 22.04 | 保留闲置 | 未删除、未安装本阶段组件 |
| 项目 `.venv` | 已创建 | Python 3.12.10；PyBaMM 26.6.2.0；由项目内 `uv.lock` 管理 |
| GitHub 仓库 | 已创建 | `WenjayWu/open-battery-simulation-lab`；公开 |

## WSL 变更记录

- 2026-09-09：实施前确认无仿真、训练或交互式长时任务；系统服务与 `hermes` 用户网关在重启后自动恢复。
- 2026-09-09：保留镜像网络模式，设置 `memory=48GB`、`swap=16GB`，未设置 `processors`。
- 2026-09-09：重启后验证为 47 GiB 内存、16 GiB swap、28 个逻辑处理器；GPU 为 NVIDIA GeForce RTX 5070 Ti（16303 MiB）。
- 原配置已在变更前备份到用户配置目录；仓库不记录含用户名的绝对备份路径。

## 验证、风险与阻塞

- 已通过：系统 Python 基线检查、WSL 资源与 GPU 可见性、项目环境导入、两类短求解烟雾测试、完整基线运行、完整五循环退化方法示例。
- 基线结果：完整 5 步实验成功；时间严格递增；电压范围 2.5–3.6 V；输出 manifest、时间序列、逐循环摘要、PNG 与日志。
- 退化示例：10°C、2C 充电 / 1C 放电的 5 个循环全部完成；每循环 5 步；16 项借用参数均属于 SEI 或析锂白名单；结果带 `illustrative_unvalidated` 标签。
- 环境重建：删除项目 `.venv` 后，`uv sync --frozen` 成功恢复 124 个包；系统 Python 仍无法导入 PyBaMM。
- 重复性：两类正式配置各重复运行两次，关键摘要最大相对误差均为 0，小于 `1e-6` 验收限值。
- 自动检查：Ruff 通过；pytest 8 项通过；Notebook 从空内核顺序执行通过；Git 跟踪路径均为英文 ASCII 且不含空格。
- 公开扫描：未发现凭据、私人邮箱、用户目录绝对路径；待提交范围不含 COMSOL 二进制或大型原始结果。
- 远程发布：`main` 已推送到公开仓库；Linux CI 的冻结环境恢复、Ruff、pytest、两类 DFN 烟雾运行与 Notebook 空内核执行全部通过。
- 科学风险：Prada2013 不包含完整的热与老化参数；SEI/析锂案例必须保持 `illustrative_unvalidated` 标签，不得作定量预测声明。
- 当前阻塞：仿真与 Git 推送无阻塞；GitHub CLI 的 API 凭据当前返回 401，后续若使用 `gh` 管理仓库需重新执行 `gh auth login --web`。公开 CI 状态徽章已核对为 passing，未读取或保存明文令牌。

## 下一步

1. 接入真实 LFP/石墨电芯参数与实验数据，单独开展校准和验证。
2. 按路线图逐项引入网格、后处理和 Linux 多物理场求解器。

## 路线图（第一阶段之后）

1. Gmsh 便携版放入项目 `.tools/`。
2. ParaView 使用默认 MSI 安装位置。
3. FEniCSx 使用 Ubuntu 24.04 独立 Conda 环境。
4. OpenFOAM 14 使用 Ubuntu 软件包。
5. MOOSE 使用另一套独立 Conda 环境。

所有 Python 组件均不得安装进 Windows 或 Ubuntu 系统 Python。

## 变更记录

- 2026-09-10：新增 `docs/MAINTENANCE_GUIDE.md`，覆盖项目接管、环境重建、案例运行、结果解释、科学参数变更、测试、Git、COMSOL 存放、WSL 分工、备份与故障恢复。
- 2026-09-10：新增根目录与 PyBaMM 项目的 `AGENTS.md`，将英文路径、虚拟环境隔离、数据保护和模型可信度要求写成自动化操作边界。
- 2026-09-10：新增 Git 跟踪路径检查，并加强 COMSOL 安装介质、许可证和压缩包的忽略规则。
