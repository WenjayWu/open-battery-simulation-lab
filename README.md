# 开源电池仿真工作台

这是一个面向锂离子电池退化与多物理场研究的可复现仿真主库。第一阶段聚焦于 PyBaMM：建立 LFP/石墨 DFN 基线，并提供一个明确标注为方法演示、尚未校准的 SEI 与析锂案例。

> English summary: A reproducible, open-source workbench for battery degradation and multiphysics simulation. Phase 1 provides a PyBaMM-based LFP/graphite DFN baseline and an explicitly unvalidated SEI/lithium-plating methodology demo.

## 当前范围

- Windows 保存源码、配置、锁文件、测试和少量基准结果。
- 每个 Python 项目使用自己的 `.venv`；不修改 Windows 或 Ubuntu 系统 Python。
- Ubuntu 24.04 作为未来 Linux 求解器和大型计算的主要运行环境。
- `COMSOL/` 保留用于已有商业软件资产；第一阶段不安装 FEniCSx、MOOSE、OpenFOAM、Gmsh GUI 或 ParaView。

## 目录

```text
Simulation/
├── COMSOL/                         # 保留的 COMSOL 工作区（大型二进制不入 Git）
├── projects/
│   └── lfp-sei-plating/            # 第一阶段 PyBaMM 项目
├── README.md
└── STATUS.md                       # 环境、验证、风险和变更台账
```

## 第一阶段入口

先安装 [`uv`](https://docs.astral.sh/uv/)，然后在 `projects/lfp-sei-plating/` 中运行：

```powershell
uv sync --frozen
uv run python -m lfp_lab.run --case baseline
uv run python -m lfp_lab.run --case sei_plating_demo
```

两个入口使用同一套核心代码；Notebook 也只调用该入口。每次正式运行都会创建独立目录，并输出 `manifest.json`、`timeseries.csv`、`summary.csv`、PNG 图表和日志。

| 案例 | 主体参数 | 工况 | 可信度 |
| --- | --- | --- | --- |
| `baseline` | Prada2013 | 25°C，95% SOC，1C 放电与 C/2 CC-CV 充电 | 参数集参考基线，尚未针对本地电芯校准 |
| `sei_plating_demo` | Prada2013 主体 + 16 项 OKane2022 副反应专用参数 | 10°C，2C 充电 / 1C 放电，5 循环 | `illustrative_unvalidated`，只作方法演示 |

详细说明、参考摘要和可信度边界见[项目文档](projects/lfp-sei-plating/README.md)与 [`STATUS.md`](STATUS.md)。

## 为什么部分工具使用 WSL

PyBaMM 可直接在 Windows 的项目虚拟环境中稳定运行，因此第一阶段不强制使用 WSL。后续的 FEniCSx、OpenFOAM 和 MOOSE 更贴近 Linux 原生的编译、MPI、PETSc、包管理和官方测试环境；放在 WSL 可以减少平台补丁与路径兼容问题。源码仍留在 Windows 主库，小型开发直接在 Windows 完成；未来高 I/O 的大型 Linux 运行目录放在 Ubuntu 的 ext4 文件系统中，避免跨 `/mnt` 边界带来的性能损失。

当前 WSL2 保留 Ubuntu 24.04 与闲置的 Ubuntu 22.04。Ubuntu 24.04 的资源上限为 48 GB 内存、16 GB swap，CPU 数量保持默认；这也与 [OpenFOAM 14 的 Ubuntu 24.04 官方支持](https://openfoam.org/download/14-ubuntu/)相衔接。

## 后续路线

第一阶段不顺带安装其他求解器。后续按 Gmsh 便携版、ParaView、FEniCSx 独立 Conda 环境、OpenFOAM 14、MOOSE 独立 Conda 环境的顺序推进；所有 Python 依赖继续与系统 Python 隔离。

## 许可证

源代码使用 [BSD 3-Clause License](LICENSE)。第三方软件、参数集与文献各自遵循其原许可证和引用要求。
