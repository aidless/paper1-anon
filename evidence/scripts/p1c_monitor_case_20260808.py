# -*- coding: utf-8 -*-
"""P1-C: Calibration Monitor deployment-decision case on the 11-condition archive.
Applies the Monitor rules (ECE>0.20 red; gamma>0.50 amber; CV>0.30 red; CNR<2 skip)
to choose/advise an evaluator for deployment. Inputs: P2 eleven-condition values.
Output: analyses/p1c_monitor_case_20260808.json"""
import os, json, io
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "analyses", "p1c_monitor_case_20260808.json")
# eleven-condition archive values (P2 tab:recon / p2_cv_sensitivity): gamma, CV (full-archive)
CONDS = {
    "DS Self-Eval":            {"gamma": 0.0332, "CV": 5.477, "ECE": 0.20},
    "DS x Qwen (qwen eval)":   {"gamma": 0.1865, "CV": 2.306, "ECE": 0.20},
    "Qwen x DS (official A)":  {"gamma": 0.9866, "CV": 0.241, "ECE": 0.20},
    "Ablation max":            {"gamma": 1.0384, "CV": 0.366, "ECE": 0.20},
    "Qwen37":                  {"gamma": 1.0591, "CV": 0.260, "ECE": 0.20},
    "DS self-eval r30":        {"gamma": 0.9360, "CV": 0.196, "ECE": 0.20},
}
def decide(gamma, cv, ece, cnr):
    flags = []
    if ece > 0.20:
        flags.append("R1-red: reduce T")
    if gamma > 0.50 and cv < 0.30:
        flags.append("R2-amber: apply confidence-gating")
    if cv > 0.30:
        flags.append("R3-red: increase evaluator diversity")
    if cnr < 2.0:
        flags.append("R4-skip: do not apply calibration")
    if not flags:
        return ["green: proceed"]
    return flags
rows = []
for name, v in CONDS.items():
    cnr = v["gamma"] / v["CV"] if v["CV"] else None
    rows.append({"condition": name, "gamma": v["gamma"], "CV": v["CV"], "CNR": round(cnr, 3) if cnr else None,
                 "ECE": v["ECE"], "decisions": decide(v["gamma"], v["CV"], v["ECE"], cnr)})
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({"case": "Deployment selection of an evaluator using the Calibration Monitor rules (P1-C)",
           "rows": rows}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for r in rows:
    print(f"{r['condition']:24s} gamma={r['gamma']:.3f} CV={r['CV']:.3f} CNR={r['CNR']} -> {r['decisions']}")
print("saved", OUT)
