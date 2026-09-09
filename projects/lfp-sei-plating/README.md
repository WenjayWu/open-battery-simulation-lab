# LFP / SEI / 析锂工作台

本项目使用项目级 `uv` 虚拟环境运行 PyBaMM，不依赖也不修改系统 Python。

## 环境

```powershell
uv sync --frozen
uv run python -c "import pybamm; print(pybamm.__version__)"
```

锁定运行时为 Python 3.12、PyBaMM 26.6.2.0。依赖安装在本目录的 `.venv/`，该目录不会进入 Git。

## 运行

```powershell
uv run python -m lfp_lab.run --case baseline
uv run python -m lfp_lab.run --case sei_plating_demo
```

每次运行会在 `results/runs/<case>/` 下创建独立目录，包含 manifest、时间序列、逐循环摘要、图表和日志。该目录默认不进入 Git。

## 科学边界

- `baseline` 使用 Prada2013 LFP/石墨参数集，只做等温 DFN 电化学基线。
- `sei_plating_demo` 会带上 `illustrative_unvalidated` 标签；其 SEI/析锂参数来自 OKane2022，仅用于展示方法和软件管线。
- 在没有真实电芯参数标定和实验验证前，不应将退化示例用于定量寿命或安全预测。
