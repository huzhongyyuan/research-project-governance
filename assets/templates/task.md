---
schema_version: 1
id: "{{PROJECT}}-T-{{NUMBER}}"
type: "task"
project: "{{PROJECT}}"
title: "{{TITLE}}"
status: "todo"
owner: null
created_at: "{{ISO_TIME}}"
updated_at: "{{ISO_TIME}}"
parent: null
depends_on: []
links: []
evidence: []
verified_at: null
---

# {{TITLE}}

## 目标与来源
交付物、所服务的里程碑、要求来源（消息/日期）。

## 范围与权限
可改文件/模块、预算、禁止事项。登记不是写锁。

## 输入与依赖
输入版本、前置条件、关联任务。

## 执行定位与派发
负责人；主机/hostId、Session UUID、cwd（远端适用，未知写待核实）。
派发状态：待发送 / 已发送 / 已接收；回执；首个检查点。

## 验收清单
- [ ] 交付物及版本可定位；证据：待补。
- [ ] 约定验证通过；检查对象、方法和结果：待补。

## 进展与证据
时间（含时区）｜阶段/事件｜实际变化与结果｜证据/回执｜下一检查点或阻塞

## 交付与验收结论
交付物及版本；验收者（或自检）、时间、方法、结果；剩余项（确无才写无）。

## 阻塞与下一步
阻塞、解除条件、责任方、最小下一步。

## 重要变更
目标、权限、负责人或验收变更及来源；取消、暂停、重开的原因。
