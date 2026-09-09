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

项目环境建立后，在 `projects/lfp-sei-plating/` 中运行：

```powershell
uv sync --frozen
uv run python -m lfp_lab.run --case baseline
uv run python -m lfp_lab.run --case sei_plating_demo
```

详细说明和可信度边界见项目内文档与 [`STATUS.md`](STATUS.md)。

## 为什么部分工具使用 WSL

PyBaMM 可直接在 Windows 的项目虚拟环境中稳定运行，因此第一阶段不强制使用 WSL。后续的 FEniCSx、OpenFOAM 和 MOOSE 更贴近 Linux 原生的编译、MPI、PETSc、包管理和官方测试环境；放在 WSL 可以减少平台补丁与路径兼容问题。源码仍留在 Windows 主库，小型开发直接在 Windows 完成；未来高 I/O 的大型 Linux 运行目录放在 Ubuntu 的 ext4 文件系统中，避免跨 `/mnt` 边界带来的性能损失。

## 许可证

源代码使用 [BSD 3-Clause License](LICENSE)。第三方软件、参数集与文献各自遵循其原许可证和引用要求。
