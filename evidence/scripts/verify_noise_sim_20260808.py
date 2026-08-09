# -*- coding: utf-8 -*-
"""Regenerate Table (3a noise) values from canonical_results_v5.json (60 non-none conditions).
Per method m: relative DeltaCV = (mean CV_N5(m) - mean CV_N5(none)) / mean CV_N5(none) over the
4 alpha x 3 tau grid; DeltaGamma = (mean gamma(m) - mean gamma(none)) / mean gamma(none).
Output: analyses/noise_sim_verification_20260808.json + printed rows."""
import json, os, statistics as st, io

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
SRC = os.path.join(BASE, "canonical_results_v5.json")
OUT = os.path.join(BASE, "analyses", "noise_sim_verification_20260808.json")

rows = json.load(open(SRC, encoding="utf-8"))
methods = ["platt", "temperature", "isotonic", "histogram", "conf_gating"]
agg = {}
for m in methods + ["none"]:
    rs = [r for r in rows if r["method"] == m]
    agg[m] = {"n": len(rs), "cv5": st.mean([r["CV_N5"] for r in rs]),
              "cv8": st.mean([r["CV_N8"] for r in rs]),
              "gamma": st.mean([r["gamma_mean"] for r in rs])}
base = agg["none"]
out_rows = []
print("method          n   gamma      dgamma%   CV5     dCV5%    CV8     dCV8%")
for m in methods:
    a = agg[m]
    dg = (a["gamma"] - base["gamma"]) / base["gamma"] * 100
    d5 = (a["cv5"] - base["cv5"]) / base["cv5"] * 100
    d8 = (a["cv8"] - base["cv8"]) / base["cv8"] * 100
    out_rows.append({"method": m, "n": a["n"], "gamma": round(a["gamma"], 4),
                     "dgamma_pct": round(dg, 1), "cv5": round(a["cv5"], 4),
                     "dcv5_pct": round(d5, 1), "cv8": round(a["cv8"], 4), "dcv8_pct": round(d8, 1),
                     "cv5_se_of_mean": round(st.stdev([r["CV_N5"] for r in rs]) / (len(rs) ** 0.5), 4)})
    print(f"{m:14s} {a['n']:3d} {a['gamma']:8.4f} {dg:+7.1f} {a['cv5']:7.4f} {d5:+7.1f} {a['cv8']:7.4f} {d8:+7.1f}")
json.dump({"method": "aggregate over 4 alpha x 3 tau per method (relative to none)",
           "rows": out_rows, "input": SRC}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", OUT)
