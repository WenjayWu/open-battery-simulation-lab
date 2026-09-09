# 工作台状态

更新时间：2026-09-09（Asia/Shanghai）

## 当前阶段

- 规划：已完成。
- 实施：进行中。
- 当前里程碑：可复现性、Notebook、CI 与公开发布。

## 环境与位置

| 项目 | 状态 | 说明 |
| --- | --- | --- |
| Windows 主库 | 已确认 | 当前 Git 工作区；不记录用户目录绝对路径 |
| Windows 系统 Python | 保持不变 | Python 3.12.10；实施前无法导入 PyBaMM |
| Ubuntu 24.04 | 已配置 | WSL2；47 GiB 可见内存、16 GiB swap、28 逻辑处理器、RTX 5070 Ti 可见 |
| Ubuntu 22.04 | 保留闲置 | 未删除、未安装本阶段组件 |
| 项目 `.venv` | 已创建 | Python 3.12.10；PyBaMM 26.6.2.0；由项目内 `uv.lock` 管理 |

## WSL 变更记录

- 2026-09-09：实施前确认无仿真、训练或交互式长时任务；系统服务与 `hermes` 用户网关在重启后自动恢复。
- 2026-09-09：保留镜像网络模式，设置 `memory=48GB`、`swap=16GB`，未设置 `processors`。
- 2026-09-09：重启后验证为 47 GiB 内存、16 GiB swap、28 个逻辑处理器；GPU 为 NVIDIA GeForce RTX 5070 Ti（16303 MiB）。
- 原配置已在变更前备份到用户配置目录；仓库不记录含用户名的绝对备份路径。

## 验证、风险与阻塞

- 已通过：系统 Python 基线检查、WSL 资源与 GPU 可见性、项目环境导入、两类短求解烟雾测试、完整基线运行、完整五循环退化方法示例。
- 基线结果：完整 5 步实验成功；时间严格递增；电压范围 2.5–3.6 V；输出 manifest、时间序列、逐循环摘要、PNG 与日志。
- 退化示例：10°C、2C 充电 / 1C 放电的 5 个循环全部完成；每循环 5 步；16 项借用参数均属于 SEI 或析锂白名单；结果带 `illustrative_unvalidated` 标签。
- 待验证：环境删除/重建、重复性、Notebook、Git 卫生、Linux CI、公开仓库。
- 科学风险：Prada2013 不包含完整的热与老化参数；SEI/析锂案例必须保持 `illustrative_unvalidated` 标签，不得作定量预测声明。
- 当前阻塞：无。GitHub 发布前需要通过 GitHub CLI 重新完成一次网页登录。

## 下一步

1. 完成环境重建、重复性与 Notebook 验证。
2. 完成 CI、公开扫描和 GitHub 发布。

## 路线图（第一阶段之后）

1. Gmsh 便携版放入项目 `.tools/`。
2. ParaView 使用默认 MSI 安装位置。
3. FEniCSx 使用 Ubuntu 24.04 独立 Conda 环境。
4. OpenFOAM 14 使用 Ubuntu 软件包。
5. MOOSE 使用另一套独立 Conda 环境。

所有 Python 组件均不得安装进 Windows 或 Ubuntu 系统 Python。
