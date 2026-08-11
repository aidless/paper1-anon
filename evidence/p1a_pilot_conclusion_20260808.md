# P1-A 第二 backbone 验证 — pilot 结论（2026-08-08）

## 已执行
- v1 pilot（2 seeds × 8 条件，合成两位算术）：全部 ECE≈0.05、acc=conf=1.0，无疲劳信号。
- v2 pilot（多步文字题 + seed 高置信注入，C1/C2）：acc 0.98–1.0、conf 0.985–0.993，仍无 T=20 疲劳。
- 大数多步题探针：deepseek-v4-flash 12/12 全对 conf 0.996；gpt-5.6-luna 12/12 全对 conf 0.99。

## 结论（诚实负结果）
1. **可用 backbone 模型（deepseek-v4-flash / gpt-5.6-luna）在可控算术任务上近乎完美校准**（acc≈1.0、conf≈0.99+），无法产生 miscalibration / 校准疲劳信号。
2. P3 的 +0.207 / 90.8% 分解依赖 GSM8K 级难度 + 具有真实过度自信的模型（原 GPT-4o 设置）；GSM8K 本地不可得（HF 不可达）、可用模型校准天花板过高。
3. **P1-A 在当前资源下无法建立协议可比性**；强行用合成题 + 完美校准模型跑全量会得到"无信号"的空结果，不支撑 Si→4。

## 建议
- P1-A 标记为"受数据/模型可得性阻塞"（阻塞条件：GSM8K 数据或具有校准缺陷的 backbone 模型）。
- 替代路径（零成本）：
  - **P1-C**：Calibration Monitor 规则在真实评估决策上的演示（用现有 CNR/γ/CV 数据做一次部署选择案例）——C 4→5，间接提升。
  - 或接受 P1 维持 3.45（Accept 阈值线），后续获得 GSM8K 数据后再补 P1-A。

## 交付物
- scripts: p1a_backbone_pilot.py / p1a_backbone_pilot_v2.py / probe_hard.py / probe_luna.py
- results: analyses/p1a_pilot_*.json（16 条件）、p1a_pilot_summary_20260808.json
