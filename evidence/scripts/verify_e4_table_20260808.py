# -*- coding: utf-8 -*-
"""Verify all E4 30-seed numbers in the merged manuscript (self-eval + coupling tables).
Input: e4_n15_results.json (seeds 0-29). Bootstrap: percentile, B=2000, random.seed(42).
Outputs: analyses/e4_table_verification_20260808.json + printed LaTeX rows."""
import json, os, random, statistics as st, io

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
RES = os.path.join(BASE, "e4_n15_results.json")
OUT = os.path.join(BASE, "analyses", "e4_table_verification_20260808.json")

res = json.load(open(RES, encoding="utf-8"))
assert res["n_seeds"] == 30
unc = res["results"]["uncalibrated"]
cal = res["results"]["calibrated"]

def boot_ci(vals, B=2000, seed=42):
    rng = random.Random(seed)
    means = sorted(st.mean(rng.choices(vals, k=len(vals))) for _ in range(B))
    return means[int(0.025*B)], means[int(0.975*B)]

def summarize(rs):
    out = {}
    for key in ["gTV", "gVT", "jsd_TV", "jsd_VT"]:
        vals = [r[key] for r in rs]
        mn = st.mean(vals)
        lo, hi = boot_ci(vals)
        out[key] = {"mean": round(mn, 4), "sd": round(st.stdev(vals), 4), "ci": [round(lo, 4), round(hi, 4)]}
    return out

unc_s = summarize(unc)
cal_s = summarize(cal)
# reductions (full precision, computed from unrounded means)
red = {}
for key in ["gTV", "gVT", "jsd_TV", "jsd_VT"]:
    base = st.mean([r[key] for r in unc]); red_val = st.mean([r[key] for r in cal])
    red[key] = round(100 * (1 - red_val / base), 1)

rows = {
  "standard": {k: {"mean": v["mean"], "ci": v["ci"]} for k, v in unc_s.items()},
  "calibrated": {k: {"mean": v["mean"], "ci": v["ci"]} for k, v in cal_s.items()},
  "reduction_pct": red,
  "method": "percentile bootstrap B=2000, random.seed(42); reduction computed on full-precision means",
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
json.dump({"rows": rows, "input": "e4_n15_results.json"}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("=== self-eval / coupling table (30-seed) ===")
print(f"Standard  : gTV {unc_s['gTV']['mean']:.3f} [{unc_s['gTV']['ci'][0]:.3f},{unc_s['gTV']['ci'][1]:.3f}]  gVT {unc_s['gVT']['mean']:.3f} [{unc_s['gVT']['ci'][0]:.3f},{unc_s['gVT']['ci'][1]:.3f}]  JSD {unc_s['jsd_TV']['mean']:.3f}/{unc_s['jsd_VT']['mean']:.3f}")
print(f"Calibrated: gTV {cal_s['gTV']['mean']:.3f} [{cal_s['gTV']['ci'][0]:.3f},{cal_s['gTV']['ci'][1]:.3f}]  gVT {cal_s['gVT']['mean']:.3f} [{cal_s['gVT']['ci'][0]:.3f},{cal_s['gVT']['ci'][1]:.3f}]  JSD {cal_s['jsd_TV']['mean']:.3f}/{cal_s['jsd_VT']['mean']:.3f}")
print(f"Reduction : gTV -{red['gTV']}%  gVT -{red['gVT']}%  JSD_TV -{red['jsd_TV']}%  JSD_VT -{red['jsd_VT']}%")
print("saved", OUT)
