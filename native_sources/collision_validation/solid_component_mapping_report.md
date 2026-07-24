# STEP实体与部件名称映射

- 映射实体数：248
- 参数化源码部件数：194
- STEP包围盒最大匹配误差：0.000000000 mm
- 映射状态：VERIFIED

映射方法是在不修改参数化源码的前提下捕获其有标签的部件列表，按每个部件包含的实体展开，并逐项与导出STEP的实体包围盒核对。只有实体数量一致且六个包围盒坐标最大误差不超过0.001 mm时才写入结果。

`solid_component_map.csv` 现在可把 `solid_index` 追溯到 `component_name`；`overlap_classification_worklist.csv` 也已增加 `component_a` 和 `component_b`，后续干涉整改不再只依赖数字编号。
