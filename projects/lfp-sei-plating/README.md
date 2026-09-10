# LFP / SEI / 析锂工作台

本项目使用项目级 `uv` 虚拟环境运行 PyBaMM，不依赖也不修改系统 Python。

完整的接管、维护、依赖升级、结果管理和故障恢复流程见仓库根目录的 [`docs/MAINTENANCE_GUIDE.md`](../../docs/MAINTENANCE_GUIDE.md)。本项目的自动化操作边界见 [`AGENTS.md`](AGENTS.md)。所有新增文件和文件夹必须使用英文 ASCII 名称且不含空格，正文仍可使用中文。

## 环境

```powershell
uv sync --frozen
uv run python -c "import pybamm; print(pybamm.__version__)"
```

锁定运行时为 Python 3.12、PyBaMM 26.6.2.0。依赖安装在本目录的 `.venv/`，该目录不会进入 Git。

测试与质量检查：

```powershell
uv run ruff check .
uv run pytest -q
uv run jupyter nbconvert --to notebook --execute notebooks/01_workbench_smoke.ipynb --output-dir results/tmp
```

## 运行

```powershell
uv run python -m lfp_lab.run --case baseline
uv run python -m lfp_lab.run --case sei_plating_demo
```

每次运行会在 `results/runs/<case>/` 下创建独立目录，包含 manifest、时间序列、逐循环摘要、图表和日志。该目录默认不进入 Git。

退化示例的参数借用边界记录在 [`configs/sei_plating_parameter_provenance.json`](configs/sei_plating_parameter_provenance.json)。当前锁定版本中，所选模型直接或间接需要 16 项 SEI/析锂专用参数；代码会先验证这份白名单并预处理模型。如模型还要求任何未批准参数，运行会立即失败并在根目录 `STATUS.md` 追加阻塞记录。

## 科学边界

- `baseline` 使用 Prada2013 LFP/石墨参数集，只做等温 DFN 电化学基线。
- `sei_plating_demo` 会带上 `illustrative_unvalidated` 标签；其 SEI/析锂参数来自 OKane2022，仅用于展示方法和软件管线。
- 在没有真实电芯参数标定和实验验证前，不应将退化示例用于定量寿命或安全预测。

参数集的能力边界和引用信息以 [PyBaMM 26.6.2.0 参数集文档](https://docs.pybamm.org/en/v26.6.2.0/source/api/parameters/parameter_sets.html) 为准。
