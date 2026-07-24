# 实体交叠分类与整改清单

## 当前统计

- 精确交叠对：465
- P1（共同体积不小于100,000 mm3）：118
- P2（5,000至100,000 mm3）：174
- P3（小于5,000 mm3）：173

## 使用方法

`overlap_classification_worklist.csv` 按共同体积从大到小排列，并根据实体空间中心推测所在机构区域。`category_inference` 是几何启发式判断，不是最终审批结论。

整改时应先处理 P1：在原生装配中给 `solid_a`、`solid_b` 对应组件分配名称，打开剖视图，判断是预期配合、焊接/并体构造还是实际穿透。完成后将 `review_status` 改为 `ACCEPTED_INTERFACE`、`FIXED` 或 `FALSE_POSITIVE`，重新导出 STEP 并运行 `run_collision_screening.py`。只有所有真实干涉关闭后，才能声明装配通过干涉检查。
