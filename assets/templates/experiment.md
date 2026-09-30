---
schema_version: 1
id: "{{PROJECT}}-E-{{NUMBER}}"
type: "experiment"
project: "{{PROJECT}}"
title: "{{TITLE}}"
status: "planned"
owner: null
created_at: "{{ISO_TIME}}"
updated_at: "{{ISO_TIME}}"
record_mode: "prospective"
conclusion: "unresolved"
links: []
---

# {{TITLE}}

## 研究问题与主张
关联主张；要区分的解释；不是只写“跑一下模型”。

## 运行前方案
- 对照与实验组、改变与固定的变量：
- 协议 ID/版本、数据/代码/配置版本：
- 指标、seed、重复次数和不确定性：
- 支持/反驳/不足以判断的标准：
- 资源预算、停止条件、重试边界：
- 占用资源（主机/设备/启动者）与释放条件：

## 进度
时间（含时区）｜已完成量｜同阶段实测速度｜剩余量｜预计完成与依据。阶段切换后重新实测，无依据不写预计时间。

## Run 索引
Run ID｜运行状态｜起止时间｜配置/代码/数据｜原始日志与产物｜机器回执。
重跑另建 Run；不覆盖旧结果。历史补录将 record_mode 改 retrospective，缺项写未知。

## 结果与异常
真实数值、波动、无效运行与失败，链接原始记录和聚合脚本。

## 科学判断
运行完成不等于假设支持；区分技术失败、有效负结果、证据不足、有效支持。
列范围、替代解释、反对证据与限制。

## 下一步
接受/限定/反驳主张，或建立有限预算的新验证任务。
