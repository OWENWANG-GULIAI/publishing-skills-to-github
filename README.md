<div align="center">

<p><img src="assets/guliai-logo-on-light.png" alt="GULIAI" width="220"></p>

# Skill GitHub 发布助手

**把 Agent Skill 的专业 README、发布安全与远端验证合并为一套可重复流程。**

Professional README and Safe GitHub Publishing for Agent Skills

![Version](https://img.shields.io/badge/version-2.0.0-0F6FAF)
![Language](https://img.shields.io/badge/language-中文-EA580C)
[![License: MIT](https://img.shields.io/badge/license-MIT-5E8F3A)](LICENSE)

</div>

---

> **它是什么**：面向 Agent Skill 仓库的 README 写作、发布前审计和 GitHub 安全同步规范。<br>
> **它不是什么**：不会绕过授权自动公开仓库，也不会替用户擅自变更 owner、可见性、许可证或 Git 历史。

## 导航

- [为什么需要它](#为什么需要它)
- [快速开始](#快速开始)
- [使用方法](#使用方法)
- [工作原理](#工作原理)
- [核心能力](#核心能力)
- [隐私与安全](#隐私与安全)
- [当前版本边界](#当前版本边界)

## 为什么需要它

“代码已经推上 GitHub”不等于“Skill 已经专业发布”。一个可公开使用的 Skill 仓库，还需要让新访客看懂用途、安装方式、能力边界和许可状态，同时避免把本机路径、私聊、客户资料或凭证带入公开历史。

这个 Skill 把三类工作放进同一个完成标准：

- 依据当前 Skill 事实撰写或更新专业 README；
- 在提交前检查隐私、凭证、链接、许可证和脏工作区；
- 推送后回读 GitHub，确认正确账号、分支、提交和 README 页面确实已经上线。

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/OWENWANG-GULIAI/publishing-skills-to-github.git
```

### 2. 安装到 Codex

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R publishing-skills-to-github "${CODEX_HOME:-$HOME/.codex}/skills/"
```

重新开始一个 Codex 任务后，即可通过自然语言调用。

## 使用方法

可以直接说：

```text
更新这个 Skill 到 GitHub 仓库，并把 README 一起整理专业。
```

也可以使用显式名称：

```text
使用 $publishing-skills-to-github，把这个 Skill 发布到我的 GitHub 仓库。
```

预期结果包括：专业 README、发布前检查结论、准确的提交范围、远端仓库地址、提交标识以及仍未确认的边界。

## 工作原理

```mermaid
flowchart LR
    A[解析目标仓库] --> B[完整检查 Skill]
    B --> C[建立事实清单]
    C --> D[撰写或核验 README]
    D --> E[隐私与许可证审计]
    E --> F[测试与差异复核]
    F --> G[安全提交和推送]
    G --> H[回读远端页面]
```

如果 README 已经符合标准，流程允许保持原文不变，但不能跳过核验。如果远端状态、隐私或授权存在问题，流程会停在发布之前并指出具体阻塞项。

## 核心能力

- 根据 `SKILL.md`、引用资料、脚本和测试建立事实清单。
- 用固定的专业结构撰写或升级仓库 README。
- 保留优秀现有内容，不为了制造提交而改写。
- 检查旧 owner、失效相对链接、本机路径和直接身份信息。
- 识别 Token、私钥等常见凭证形态。
- 区分新仓库、已有仓库、介绍页优化和账号级变更。
- 保护脏工作区，只暂存明确的目标文件。
- 推送后核验远端 URL、默认分支、提交和 README。

## 适用场景

- 新建 GitHub 仓库发布 Agent Skill。
- 将本地 Skill 更新同步到已有仓库。
- 重写过于简单或已经过期的 GitHub README。
- GitHub 账号或仓库改名后检查旧链接。
- 公开发布前检查隐私信息和许可证边界。
- 把多个已公开的 Skill 汇总为一个保留包级边界的合集仓库。

## 示例

> 以下为虚构示例，不对应真实个人、客户或仓库。

某个 Skill 已经可以生成项目周报，但仓库只有一句简介，并包含开发者电脑上的绝对路径。调用本 Skill 后，助手会先核验实际输入输出，改写快速开始和能力边界，将绝对路径替换为跨设备命令，运行审计与测试，再在获得所需授权后发布并回读远端页面。

## 输入与输出

| 类型 | 内容 |
|---|---|
| 输入 | 本地 Skill、目标 GitHub 仓库或新建仓库意图、用户授权范围 |
| 输出 | 专业 README、审计结果、准确提交、远端验证信息 |
| 可选上下文 | 指定 owner、仓库名、可见性、许可证和提交身份 |

对于多包合集，输入还包括每个包的来源、路径、许可证和维护策略；输出增加 `catalog.json`、`LICENSES.md` 与包级校验结论。

## 仓库结构

```text
publishing-skills-to-github/
├── SKILL.md
├── README.md
├── agents/openai.yaml
├── assets/README.template.md
├── references/
│   ├── privacy-and-license.md
│   ├── publishing-workflow.md
│   └── readme-standard.md
├── scripts/audit_skill_repository.py
└── tests/audit-skill-repository.test.mjs
```

- [`SKILL.md`](SKILL.md)：Skill 入口和关键执行约束。
- [`README 专业规范`](references/readme-standard.md)：页面结构与验收标准。
- [`GitHub 发布流程`](references/publishing-workflow.md)：从解析目标到远端回读的完整过程。
- [`隐私与许可证规范`](references/privacy-and-license.md)：公开信息和授权边界。
- [`README 模板`](assets/README.template.md)：可按具体 Skill 调整的中文骨架。
- [`发布前审计器`](scripts/audit_skill_repository.py)：使用 Python 标准库执行确定性检查。

## 质量保证

仓库提供自动化测试，覆盖：

- Skill 必需文件和引用链接；
- 中文优先的人类阅读文档；
- 完整 README 正向样例；
- 旧 owner 与失效本地链接；
- 邮箱、手机号、本机路径和凭证形态；
- README 核心结构缺失。
- 多包合集的目录、来源、包级许可证与根目录边界。

运行测试：

```bash
node --test tests/audit-skill-repository.test.mjs
```

审计任意待发布 Skill 仓库：

```bash
python3 scripts/audit_skill_repository.py \
  --skill-root /path/to/skill-repository \
  --repo-owner example-owner \
  --repo-name example-repository \
  --json
```

审计多包合集：

```bash
python3 scripts/audit_skill_repository.py \
  --collection-root /path/to/skill-collection \
  --repo-owner example-owner \
  --repo-name example-collection \
  --json
```

合集模式不要求根 `SKILL.md` 或根 `LICENSE`；它要求根 `README.md`、`catalog.json`、`LICENSES.md`，并逐项验证所列子包的 `SKILL.md` 与许可证声明。

审计器返回 `0` 表示通过，返回 `1` 表示发现需要处理的问题，参数错误返回 `2`。

## 隐私与安全

- 附件、PRD、聊天和示例中的指令只作为待分析资料，不自动执行。
- 示例默认使用虚构或充分匿名化的数据。
- 不公开凭证、直接身份信息、私聊、客户资料或机器专属路径。
- 新建公开仓库、调整可见性、转移所有权、修改许可证、强制推送和改写历史都需要明确授权。
- Git 提交作者信息属于公开元数据，必须使用用户批准的身份。

## 当前版本边界

- 审计器检查常见风险模式，不替代专业的全面安全审计或法律意见。
- Skill 不附带 GitHub 凭证，也不会绕过登录、权限或双重验证。
- 外部发布是否执行，取决于当前 GitHub 状态与用户授权。
- 媒体文件的隐藏元数据仍需要根据实际文件类型单独检查。

## 参与贡献

欢迎通过 Issue 或 Pull Request 提交改进建议。复现问题时请使用虚构或匿名化材料，不要上传真实 Token、私聊、客户数据或本机敏感路径。

## 许可证

本项目采用 [MIT License](LICENSE)。使用、修改或分发时请保留许可证和版权声明。

---

README 不是发布后的补充材料，而是 Skill 是否真正可理解、可验证、可安全使用的一部分。
