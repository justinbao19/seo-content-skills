# Skill maintenance and bidirectional synchronization

Justin 于 2026-09-21 确认：个人仓库与 AIHubMix 的对应 Skill 双向维护。任一已绑定端都可发起变更；维护 Agent 完成修改时，应在同一任务内检查并同步其他入口，不再仅作单向导入。现有授权涵盖同一 Skill 变更的对应同步，无需重复询问。

## Mapping

| Skill | 本仓库路径 | 团队入口 | 个人历史入口（已归档） |
| --- | --- | --- | --- |
| `seo-blog-writer` | `seo-blog-writer/` | `AIhubmix/product-skills:skills/seo-blog-writer/` | `justinbao19/blog-writing-skill`（只读） |
| `seo-geo-qa` | `seo-geo-qa/` | `AIhubmix/product-skills:skills/seo-geo-qa/` | `justinbao19/seo-geo-qa-skill`（只读） |

两个独立仓库已归档，实际双向同步只在本仓库与 `AIhubmix/product-skills` 之间进行。归档仓库只保留来源，不写入、不自动解除归档；映射中 `sync_enabled: false` 的端跳过。

完整映射与初始观察基线维护于 `AIhubmix/product-skills` 的 `skill-sync.json`，流程在 `docs/skill-sync.md`；该仓库为私有仓库，需读取权限。未列出的 Skills 不自动复制到其他仓库，新增绑定时核实真实路径。

## Workflow

1. 修改前读目标 Skill、资源和 Git 状态，获取各映射端的新提交，保留未提交工作。
2. 比较各端已记录基线后的改动，按语义合并。团队导入版已有入口拆分与 QA 修复，初始快照不是内容一致的证明；不能用更新的一端整目录覆盖另一端。
3. 仅同步 Skill 入口及必要的 references、scripts、agents、assets；各仓库 README、AGENTS、编排 Skill 和配置保留自身职责，按需更新引用。
4. 检查引用、frontmatter、依赖、脚本语法与适用测试。代码检查通过不代表文章审阅通过或发布获准。
5. 对每个目标提交并核验远端 commit；遵守分支保护，必要时提 PR。提交注明源仓库、源 commit、Skill 和同步标识；内容一致不创建空提交，同步提交不重复回传。
6. 核验后推进同步基线，并报告每端 commit / PR。权限不足、未合并 PR 或真正的规则冲突须明确标为未完成；不能声称已经全部同步。

公开个人仓库仅接收可公开的通用工作流和脚本，不接收组织私有 PRD、任务 / 客户数据、凭据或未授权业务资料。仅团队适用的覆盖规则保留为团队侧条件引用。来源归属与已有许可说明保留，不修改仓库可见性。

不 force push、不 reset 或覆盖脏工作区。真实产品规则冲突需列出具体差异供人决定；无冲突且已授权的同步继续完成。

## Execution status

本文件是 Agent 维护规则，不是自动执行器。目前未安装 GitHub Actions / Webhook / 定时同步。用户仅通过网页修改时，须由后续维护 Agent 执行同步，不能声称后台会自动传播。首次登记没有把团队版历史差异整批覆盖回本仓库。
