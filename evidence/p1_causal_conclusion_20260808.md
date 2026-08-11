# P1 因果控制组：T=20 快速检验结论（2026-08-08，负结果）

## 数据
- 陷阱题（含干扰项/单位陷阱/负步）+ deepseek-v4-flash executor（seed agent 高置信注入）。
- T=20，3 reps × 3 agents × 20 轮。

## 结果（final ECE 逐 rep）
| 条件 | rep0 | rep1 | rep2 | 说明 |
|---|---|---|---|---|
| C2 (sync) | 0.37 | 0.35 | 0.17 | 标准传染条件 |
| G1 (no-peer) | 0.52 | 0.37 | 0.33 | 隔离 |
| G2 (no-update) | 0.21 | 0.42 | 0.17 | 抑制传染 |
| G3 (placebo) | 0.05 | 0.27 | 0.09 | 随机反馈 |
| G4 (matched-hist) | 0.30 | - | - | 自己历史 |

## 结论（T=20 快速检验）
1. **无 T 疲劳效应**：C2 在 T=20（0.17–0.37）与 T=10（0.10–0.42）重叠；P3 的 T=20 ECE 升高（+0.207）无法用 deepseek-v4-flash 复现。
2. **控制组差异方向不稳定**：G1 (no-peer) 不低于 C2（0.33–0.52 vs 0.17–0.37），G3 (placebo) 反而最低（0.05–0.27）——与"sync 传染升高 ECE"的机制假设不一致。
3. 陷阱题确认了 miscalibration 基线（全部条件 ECE>0.05），但那是**任务固有**的，与记忆/传染机制无关。

## 判定
- **P1 因果控制组路径在可用模型（deepseek-v4-flash）上正式受阻**：该模型在长对话下校准不退化（无 T 疲劳），P3 的 +0.207/90.8% 分解是 GPT-4o 特有现象。
- P1-A（第二 backbone）与因果控制组均依赖具有 T 疲劳特性的模型（GPT-4o 类）或 GSM8K 数据——当前资源不可得。
- **P1 停在 3.45**（Monitor 案例 C→5 已完成；N→4/Si→4 受阻）。替代：获得 GPT-4o 访问或 GSM8K 数据后重启。

## 交付
- scripts: probe_calibration_pressure.py（陷阱题探针，ECE 0.10–0.55）、p1_causal_quick.py（控制组，T=10/T=20）
- results: analyses/p1_calibration_pressure_probe_20260808.json、p1_causal_quick_20260808.json
