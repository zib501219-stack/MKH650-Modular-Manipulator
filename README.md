# MKH-650 Modular Four-Axis Manipulator

20 kg 额定负载、1180 mm 最大工作半径的模块化四轴工业搬运机械手。项目覆盖总体方案、关节驱动与轴承包络、重载箱式连杆、平衡机构、夹紧力、工程材料、制造装配和维护设计。

## Detailed CAD content

- 16 点基础锚固、J1 回转支承和大型肩部塔架
- J2/J3 复合载荷关节、减速器/轴承/中空轴包络及 12 点法兰连接
- 双侧板箱式大臂/小臂、七道内部筋板、检修环和服务盖板
- 平衡连杆/气弹簧、双段拖链、集中润滑接口
- J4 腕部、重载平行夹爪、可更换锯齿夹持垫
- 检修平台、终端箱与本地急停

Files include editable source, STEP, GLB preview, multi-view verification, calculations, BOM and process plan. Dynamic performance and structural stress are design calculations until checked in the intended solver/prototype.

## 二维工程图 / 2D engineering drawings

- `drawings/总装图_Overall_Assembly.*`：A2 总装图，直接由详细 STEP 机械手生成三视图、明细栏与装配技术要求。
- `drawings/大臂侧板_Upper_Arm_Side_Plate.*`、`基础法兰_Foundation_Flange.*`、`重载夹指_Heavy_Gripper_Finger.*`：A3 关键零件图。
- `drawings/二维工程图册_2D_Engineering_Drawings.pdf`：四页合订图册。

标注采用中国大陆简体中文与 GB/T 常用机械制图术语，英文为辅助说明；每张图同时提供 DXF、PDF、PNG 和可重生成 Python 源文件。
