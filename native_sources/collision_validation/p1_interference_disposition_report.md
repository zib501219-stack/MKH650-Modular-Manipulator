# P1干涉处理决定

P1总数：118

- CONSTRUCTION_GEOMETRY_REMODEL: 62
- EXPECTED_ENVELOPE_OVERLAP: 25
- EXPECTED_FASTENER_ENGAGEMENT: 1
- MANUAL_SECTION_REVIEW: 30

每个P1对已经有部件名称、工程处理类型、整改动作、责任角色和关闭证据要求。状态统一保留为 `DECISION_RECORDED_OPEN`，因为记录处理决定不等于几何已经修改。

只有满足以下条件才能关闭：

1. 在带零件名称的原生装配中完成剖视确认；
2. 对构造重叠完成修剪、并体或重新定位；
3. 对包络件/紧固件建立明确的干涉排除规则；
4. 重新导出STEP并运行精确共同体积筛查；
5. 保存关闭前后截图和复查报告。
