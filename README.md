# Research Project Governance

轻量科研项目治理 skill：把目标、执行、证据和下一步连起来，用统一记录支持新项目启动、旧项目接入、任务交付、实验汇报与科研周报。

## 从一个项目开始

在能读取本 skill 的 Agent 环境中，提供项目路径及允许操作的范围，再提出：

> 请使用 research-project-governance 为这个项目做轻量接入。先核对最新目标、现有负责人、在途任务和已有记录；复用现有文件，只建立必要记录。选一项已获授权的小任务，记录派发、开工、关键进展和验收。服务器项目的权威记录放对应服务器，本机只保留索引和摘要。不启动额外实验、不重启任务、不创建竞争 writer。最后给出记录位置、完成阶段、验收证据与缺口。

若当前环境无法读取本 skill，先提供或安装整个仓库目录；不要仅凭名称假定远端 Agent 已具备这些规则。安装规范不等于项目已接入或执行者已确认接收。

## 包含什么

- [SKILL.md](SKILL.md)：入口、适用范围和权限边界。
- [任务记录](references/records.md)：派发—进行—完成的统一格式与验收门槛。
- [精简汇报](references/reporting.md)：实验六项格式（背景、设置、分析、demo、结论、TODO）、周二/周五更新的科研周报和有来源的常问问题准备。
- [存量接入](references/intake.md)：先盘点，再渐进建档，不搬动既有产物。
- [过程与算力安全](references/operations.md)：按精确身份停进程、启动核验、非交互环境、共享算力、有依据的预计时间、逐例完成判定。
- [评测公平性](references/evaluation.md)：打分器冻结、链路等价与对照组、条件冻结、补充组单列、结果隔离、受控诊断实验。
- [空模板](assets/templates/)：任务、实验、文献、主张、决策、交接、周报等；[周报示例](assets/examples/weekly-report-example.md)为虚构数据。
- [只读审计工具](scripts/records.py)：检查轻量档事件日志格式、任务卡结构，并生成 TODO 文本。

按风险分级：轻量工作记入项目滚动事件日志；纳入治理的任务（标准档及以上）每项一张权威卡。事件格式为：

`时间｜阶段/事件｜实际变化与结果｜证据/回执｜下一检查点或阻塞`

已发送不等于已开工，运行结束不等于验收完成。无变化不重复记录；历史失败不抹除。详细规则以对应参考文件为准。

## 验证工具

在仓库根目录执行（Python 3，仅标准库）：

```bash
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/records.py log /path/to/project
python3 scripts/records.py audit /path/to/project
python3 scripts/records.py todo /path/to/project
```

工具只读，不启动任务；结构检查通过不证明科学结论、远端证据或交付质量。

## 边界

本仓库不包含私人项目记录、会话、凭据或服务器权限。不提供常驻调度服务，也不会自动新建 Session、恢复任务、启动实验或推送报告。常问问题准备发生在已授权的工作节点，并非独立后台学习服务。

论文写作与审稿可衔接目标环境中可用的 `craft-ccfa-paper`；该技能未随仓库打包，不可用时须明确降级。Jev 参考仅为可选规范，不含客户端、凭据或联调承诺。公开参考与取舍见 [sources.md](references/sources.md)。
