# Project Instructions

本文件适用于 `projects/lfp-sei-plating/` 及其全部子目录，并继承仓库根目录 `AGENTS.md`。

## Environment

- 所有 Python 命令使用 `uv run ...`。
- 使用项目内 `.venv` 和已提交的 `uv.lock`；不得使用系统 Python 安装依赖。
- 普通恢复使用 `uv sync --frozen`。只有明确的依赖升级任务才能运行 `uv lock`。

## Structure

- `configs/` 保存工况与参数溯源，文件名使用英文 `snake_case`。
- `src/lfp_lab/` 是唯一的模型构建、求解和结果导出实现。
- `notebooks/` 只调用核心代码，不复制求解逻辑。
- `tests/` 覆盖配置、科学约束、重复性和仓库规则。
- `results/reference/` 只接收经过审查的小型基准；`results/runs/` 与 `results/tmp/` 默认不跟踪。

## Scientific Rules

- `baseline` 保持 Prada2013 的等温 DFN 基线语义，除非任务明确要求并同步修改测试与文档。
- `sei_plating_demo` 只能从 `configs/sei_plating_parameter_provenance.json` 的批准白名单借用 SEI/析锂参数。
- 任何白名单外的缺失参数都必须使运行失败，不得静默回退到另一参数集。
- 退化示例的 manifest、摘要与图表必须带 `illustrative_unvalidated` 标签。

## Required Checks

代码或配置修改后至少运行：

```powershell
uv run ruff check .
uv run pytest -q
uv run python -m lfp_lab.run --case baseline --quick
uv run python -m lfp_lab.run --case sei_plating_demo --quick
```

涉及 Notebook 时还要从空内核顺序执行；涉及参数、依赖或核心模型时按 `docs/MAINTENANCE_GUIDE.md` 做完整验收。

## Naming and Generated Files

- 所有新增路径使用有意义的英文 ASCII 名称，不含空格。
- 不提交 `.venv`、缓存、临时 Notebook、普通运行目录、日志或大型结果。
- 不覆盖或删除已有运行结果；新运行使用独立目录。
