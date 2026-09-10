# Repository Instructions

本文件适用于整个仓库，供自动化助手和维护者执行任务时使用。

## Read First

在修改前阅读：

1. `README.md`
2. `STATUS.md`
3. `docs/MAINTENANCE_GUIDE.md`
4. 目标项目内的 `README.md` 与 `AGENTS.md`

## Naming

- 仓库内所有新文件和文件夹必须使用有意义的英文名称。
- 路径仅使用 ASCII 字符，不含中文或空格。
- 目录和普通文档优先使用 `kebab-case`；Python 标识符与配置字段使用 `snake_case`。
- 约定文件名 `README.md`、`STATUS.md`、`LICENSE`、`AGENTS.md` 可保持大写。
- 中文可以用于 Markdown 正文、注释和面向人的说明。

## Safety and Scope

- 不修改 Windows 或 Ubuntu 系统 Python，不执行全局 `pip install`。
- Python 依赖必须进入对应项目的 `.venv` 或未来明确命名的独立 Linux 环境。
- 将 `results/runs/`、`results/tmp/`、`.venv/`、缓存、网格和日志视为生成内容，除非任务明确要求，否则不提交。
- 将原始实验数据、私人 COMSOL 模型、许可证和合作方资料视为受保护资产，不移动、不删除、不公开。
- 在批量移动、重命名或删除前，先列出精确目标并执行 dry run；不得对仓库根目录或未知数据目录执行递归删除。
- 不读取、写入或提交访问令牌、私人邮箱、绝对用户路径或许可证信息。
- 保留用户已有的未提交修改；不要回滚与当前任务无关的内容。

## Scientific Integrity

- 参数必须有来源、单位、适用体系和理由；不得为消除报错而静默借用其他化学体系参数。
- `sei_plating_demo` 必须保留 `illustrative_unvalidated` 标签。
- 未经真实电芯参数标定和实验验证，不得将示例结果描述为定量寿命或安全预测。
- 科学模型、参数、依赖或验收结果变化时，同步更新 `STATUS.md` 和相关文档。

## Verification

在 `projects/lfp-sei-plating/` 中优先使用：

```powershell
uv sync --frozen
uv run ruff check .
uv run pytest -q
uv run python -m lfp_lab.run --case baseline --quick
uv run python -m lfp_lab.run --case sei_plating_demo --quick
```

涉及 Notebook、依赖、求解核心或参数集时，按维护手册执行扩展验收。报告真实验证结果，不把未运行的检查写成“已通过”。

## Git and Publication

- 只暂存已经审查的明确文件。
- 提交消息使用简短英文 Conventional Commit 风格。
- 推送前检查大文件、凭据、私人路径、COMSOL 二进制文件和原始运行结果。
- `comsol-projects/` 只保存可公开说明、脚本和小型配置；软件本体、安装包、许可证和 `*.mph` 不进入仓库。
