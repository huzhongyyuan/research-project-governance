# 开源参考与取舍

查阅日期：2026-09-29。以下为实际读到的公开源文件/节选，分支内容可能变化；不是安装、运行或性能背书。本 skill 是针对用户需求独立编写的整合，不复制这些项目的代码或整套文案。未克隆、安装其 hooks、服务或自动派发器。

| 来源 | 实际查看范围 | 采用 | 不采用 |
|---|---|---|---|
| [Planning with Files](https://github.com/OthmanAdi/planning-with-files) | [SKILL.md](https://github.com/OthmanAdi/planning-with-files/blob/master/skills/planning-with-files/SKILL.md) 中任务目录、持久计划和 owner 段落；[task_plan.md](https://github.com/OthmanAdi/planning-with-files/blob/master/skills/planning-with-files/templates/task_plan.md) 全文 | 任务绑定正确目录；持久记录；清晰下一步；共享计划有维护责任 | 不每两次浏览强制写日志；不安装 hooks 或自动续接；不要求每个简单任务三份文件 |
| [Superpowers](https://github.com/obra/superpowers) | [verification-before-completion](https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md) 全文；brainstorming 中分解、隔离与既有代码库段落 | 完成声明与核验证据绑定；小而清晰的工作边界 | 不把每个状态都变成重新运行生产命令；不自动 commit；不把软件测试通过当科学主张成立 |
| [Edict 三省六部](https://github.com/cft0808/edict) | README 前部和 [任务流转架构](https://github.com/cft0808/edict/blob/main/docs/task-dispatch-architecture.md) 前 180 行 | 策划/审查/执行分离，职责、任务状态与可追踪记录 | 不照搬不可越级和每事必审；不启动常驻角色、自动派发/重试/回滚；不引用其框架对比营销表为客观评测 |
| [OpenAI 官方 Skills 文档](https://developers.openai.com/codex/skills/) | 技能结构、渐进披露、调用与发现段落 | 短入口、按需参考、标准元数据与模板/脚本分离 | 不把 skill 当独立调度服务或强制全局授权机制 |

科研方法沿用本机 `craft-ccfa-paper` 的主张—证据流程与存量项目可保留结构原则；这是本地现有依赖，不冒充本轮验证过的外部开源来源。

## 可选外部模型（不是开源框架依赖）

2026-09-30 阅读 TypeSafe AI 官方 [Models](https://docs.typesafe.ai/models)，核对 Jev 的文本输入、版本/别名和语言限制，用于 [Jev 辅助审查](jev-review.md) 的使用边界。这里只新增规范；未安装客户端、配置密钥、向服务上传项目资料或进行模型效果验证。Jev 不取代实际证据或最终验收。

## 与用户需求的适配

- 直接与任意 Agent 交流：责任明确但不垄断沟通。
- 并行讨论：独立意见文件，汇总保留分歧，科学结论不投票。
- 存量项目：先只读盘点和映射，不强迁目录、不重启任务。
- 文献/实验/讨论/图表：模板分开，稳定 ID 链接，不复制事实。
- 持续改进：有假设、预算、验收和停止条件，不无限循环。
- 低管理开销：按事件写入，按需建文件，派生看板不多头维护。
