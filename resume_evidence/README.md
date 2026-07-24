# 简历项目证据索引

对应简历项目：**MKH-650模块化四轴搬运机械手**

## 简历表述与仓库证据

| 简历内容 | 直接证据 |
|---|---|
| 20 kg负载、1180 mm工作半径 | `docs/parameters.csv`、`docs/assumptions.md` |
| 连杆自重、末端负载和关节扭矩 | `docs/preliminary_calculations.md`、`docs/shaft_bearing_connection_checks.md` |
| 电机、减速器和夹持机构初步选型 | `docs/BOM.csv`、`docs/preliminary_calculations.md` |
| 底座、回转关节、连杆、夹具、轴承与连接件 | `models/mkh650_manipulator.step`、`docs/shaft_bearing_connection_checks.md` |
| 整机建模、总装图、零件图与BOM | `models/mkh650_manipulator.step`、`drawings/二维工程图册_2D_Engineering_Drawings.pdf`、`docs/BOM.csv` |
| 制造工艺和装配维护考虑 | `docs/manufacturing_plan.md`、`docs/shaft_bearing_connection_checks.md` |
| 装配结构复核 | `validation/`、本目录的最新装配体复核视图、`project-validation-summary.md` |

## 本次几何复核

- STEP SHA256：`a06eea65eeb4381c836ad7f970558f52d16f34cc8d5cc70425e1a9197b4832d5`
- 类型：装配体
- 装配节点：303
- 叶节点/实体：248
- 面数量：1047
- 包围盒：`1886.2 × 744.8 × 916.6 mm`
- 复核工具：CAD几何引用检查与ISO快照

## 使用边界

仓库能够证明总体结构、轴系与夹持方案、参数化模型、工程图、BOM和制造计划。额定寿命、结构应力、动态性能和实际搬运节拍没有求解器或实体设备记录时，不作为实测结果。
