# P1干涉数字闭环报告

复核日期：2026-07-28

原筛查P1对数：118；数字工程判定关闭：118；未判定：0。

原整机STEP同时包含制造实体、采购件包络和建模辅助实体，因此公共体积不等同于真实装配穿透。本次利用已完成的实体名称映射和36个受控零件资料，将每一对归入包络嵌套、参考构造或设计接触。这些结论关闭的是数字样机筛查项；实机装配擦碰仍归入实机验证。

## 结果

- `ACCEPTED_NONPHYSICAL_ENVELOPE`：25
- `ACCEPTED_REFERENCE_CONSTRUCTION`：62
- `ACCEPTED_INTERFACE_CONTACT`：31

逐项证据见 `p1_digital_closure.csv`。
