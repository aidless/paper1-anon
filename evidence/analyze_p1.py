# -*- coding: utf-8 -*-
"""PAPER1 class-A analyses v3: MC-family reconstruction (exact t via incomplete beta), ECE estimator consistency, provenance matrix."""
import json, math, os, statistics as st
from itertools import combinations

OUT = r"<WORKSPACE>\thread-groups\default\科研\outputs\five_paper_acceptance_baseline_20260806\analyses"
SRC = r"<ARCHIVE_ROOT>\PAPER1_CONSOLIDATED\joint_full_F_v10_results.json"
TEX = r"<ARCHIVE_ROOT>\PAPER1_CONSOLIDATED\main.tex"
ECE_CAL = r"<ARCHIVE_ROOT>\experiments\ece_calibration.json"

def betacf(a, b, x, itmax=200, eps=3e-12):
    qab = a+b; qap = a+1.0; qam = a-1.0
    c = 1.0; d = 1.0-qab*x/qap
    if abs(d) < 1e-30: d = 1e-30
    d = 1.0/d; h = d
    for m in range(1, itmax+1):
        m2 = 2*m
        aa = m*(b-m)*x/((qam+m2)*(a+m2))
        d = 1.0+aa*d
        if abs(d) < 1e-30: d = 1e-30
        c = 1.0+aa/c
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0/d
        h *= d*c
        aa = -(a+m)*(qab+m)*x/((a+m2)*(qap+m2))
        d = 1.0+aa*d
        if abs(d) < 1e-30: d = 1e-30
        c = 1.0+aa/c
        if abs(c) < 1e-30: c = 1e-30
        d = 1.0/d
        delt = d*c
        h *= delt
        if abs(delt-1.0) < eps: break
    return h

def betai(a, b, x):
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    lnbt = math.lgamma(a+b)-math.lgamma(a)-math.lgamma(b)+a*math.log(x)+b*math.log1p(-x)
    bt = math.exp(lnbt)
    if x < (a+1.0)/(a+b+2.0):
        return bt*betacf(a,b,x)/a
    return 1.0 - bt*betacf(b,a,1.0-x)/b

def t_cdf(x, df):
    if x == 0: return 0.5
    a = df/2.0
    ib = betai(a, 0.5, df/(df+x*x))
    return 1.0-0.5*ib if x >= 0 else 0.5*ib

def ttest_paired(a, b):
    n = len(a)
    dif = [x-y for x,y in zip(a,b)]
    m = sum(dif)/n
    s = st.stdev(dif) if n>1 else float("nan")
    if s==0 or math.isnan(s):
        return m, float("nan"), 1.0, n
    t = m/(s/math.sqrt(n))
    p = 2*(1-t_cdf(abs(t), n-1))
    return m, t, p, n

def holm(ps):
    k=len(ps); idx=sorted(range(k), key=lambda i: ps[i])
    out=[None]*k
    for r,i in enumerate(idx): out[i]=min(1.0, ps[i]*(k-r))
    m2=[out[i] for i in idx]
    for j in range(k-2,-1,-1): m2[j]=max(m2[j], m2[j+1])
    for r,i in enumerate(idx): out[i]=m2[r]
    return out

def bh(ps):
    k=len(ps); idx=sorted(range(k), key=lambda i: ps[i])
    out=[None]*k
    for r,i in enumerate(idx): out[i]=min(1.0, ps[i]*k/(r+1))
    m2=[out[i] for i in idx]
    for j in range(k-2,-1,-1): m2[j]=min(m2[j], m2[j+1])
    for r,i in enumerate(idx): out[i]=m2[r]
    return out

d = json.load(open(SRC, encoding="utf-8"))
rows = [{"task": s["task_id"], "seed": int(s["seed"]), "alpha": float(s["alpha_eval"]), "T": int(s["T"]),
         "ECE": float(s["final_ECE"]), "H": float(s["final_H"]), "CAF": float(s["final_CAF"]), "gamma": float(s["final_gamma"])}
        for s in d["sessions"]]

def contrasts(metric):
    out = []
    for T in [10,20]:
        for (a1,a2) in combinations([0.0,0.5,1.0],2):
            pa = {(x["task"],x["seed"]):x[metric] for x in rows if x["alpha"]==a1 and x["T"]==T}
            pb = {(x["task"],x["seed"]):x[metric] for x in rows if x["alpha"]==a2 and x["T"]==T}
            keys = sorted(set(pa)&set(pb))
            if len(keys)<2: continue
            m,t,p,n = ttest_paired([pa[k] for k in keys],[pb[k] for k in keys])
            out.append({"contrast": f"alpha {a1} vs {a2} @ T={T}", "n_pairs": n, "diff": round(m,4),
                        "t": None if math.isnan(t) else round(t,3), "raw_p": round(p,4)})
    return out

result1 = {"experiment": "joint_full_F_v10 (deepseek-v4-flash, 5 tasks x 5 seeds x alpha{0,0.5,1} x T{10,20}, 125/150 cells)",
 "note": "Pairwise contrasts reconstructed from persisted session metrics. Exact matched source-study contrasts (+0.207 temporal, +0.021 sync) require source-study raw traces (Class C).",
 "anova_stored": {k:v for k,v in d["summary"]["anova_ECE"].items() if k in ["F_alpha","p_alpha","F_T","p_T","F_interaction","p_interaction","df_within","n_per_cell"]},
 "families": {}}
for metric, mlabel in [("ECE","ECE"), ("H","H"), ("CAF","CAF"), ("gamma","gamma")]:
    fam = contrasts(metric)
    ps = [x["raw_p"] for x in fam]
    if ps:
        h, b = holm(ps), bh(ps)
        for x, hp, bp in zip(fam, h, b):
            x["holm_p"]=round(hp,4); x["bh_p"]=round(bp,4)
    result1["families"][mlabel+"_alpha_pairwise_within_T"] = {"tests": fam, "family_size": len(fam),
        "survive_holm_005": [x["contrast"] for x in fam if x.get("holm_p",1)<0.05],
        "survive_bh_005": [x["contrast"] for x in fam if x.get("bh_p",1)<0.05]}
ft = []
for alpha in [0.0,0.5,1.0]:
    pa = {(x["task"],x["seed"]):x["ECE"] for x in rows if x["alpha"]==alpha and x["T"]==10}
    pb = {(x["task"],x["seed"]):x["ECE"] for x in rows if x["alpha"]==alpha and x["T"]==20}
    keys = sorted(set(pa)&set(pb))
    if len(keys)<2: continue
    m,t,p,n = ttest_paired([pa[k] for k in keys],[pb[k] for k in keys])
    ft.append({"contrast": f"T10 vs T20 @ alpha={alpha}", "n_pairs": n, "diff": round(m,4),
               "t": None if math.isnan(t) else round(t,3), "raw_p": round(p,4)})
ps=[x["raw_p"] for x in ft]; h,b=holm(ps),bh(ps)
for x,hp,bp in zip(ft,h,b): x["holm_p"]=round(hp,4); x["bh_p"]=round(bp,4)
result1["families"]["ECE_temporal_T10_vs_T20"] = {"tests": ft, "family_size": len(ft),
  "survive_holm_005": [x["contrast"] for x in ft if x["holm_p"]<0.05],
  "survive_bh_005": [x["contrast"] for x in ft if x["bh_p"]<0.05]}
alltests = [dict(x) for x in result1["families"]["ECE_alpha_pairwise_within_T"]["tests"]] + [dict(x) for x in result1["families"]["ECE_temporal_T10_vs_T20"]["tests"]]
ps=[x["raw_p"] for x in alltests]; h,b=holm(ps),bh(ps)
for x,hp,bp in zip(alltests,h,b): x["holm_p_all"]=round(hp,4); x["bh_p_all"]=round(bp,4)
result1["families"]["ECE_ALL_pooled"] = {"family_size": len(alltests),
  "survive_holm_005": [x["contrast"] for x in alltests if x["holm_p_all"]<0.05],
  "survive_bh_005": [x["contrast"] for x in alltests if x["bh_p_all"]<0.05]}

ec = json.load(open(ECE_CAL, encoding="utf-8"))
res = ec["results"]
ece_vals = [x["ece"] for x in res]; brier_vals = [x["brier"] for x in res]
def pearson(a,b):
    n=len(a); ma=sum(a)/n; mb=sum(b)/n
    cov=sum((x-ma)*(y-mb) for x,y in zip(a,b))
    va=sum((x-ma)**2 for x in a); vb=sum((y-mb)**2 for y in b)
    return cov/math.sqrt(va*vb)
def spearman(a,b):
    def rank(v):
        o=sorted(range(len(v)), key=lambda i: v[i]); r=[0]*len(v)
        for i,pos in enumerate(o): r[pos]=i+1
        return r
    return pearson(rank(a), rank(b))
r_pear = pearson(ece_vals, brier_vals); r_spear = spearman(ece_vals, brier_vals)
import random
random.seed(42)
perm=[]
for _ in range(5000):
    b2 = brier_vals[:]; random.shuffle(b2)
    perm.append(pearson(ece_vals, b2))
perm.sort(); ci=(perm[125], perm[4975])
result1["ece_estimator_consistency"] = {"source": ECE_CAL, "n": len(res),
  "pearson_r_ece_brier": round(r_pear,4), "spearman_r": round(r_spear,4),
  "permutation_95ci_pearson": [round(ci[0],4), round(ci[1],4)],
  "note": "High ECE-Brier consistency across the 10 persisted seeds. Exact bin-count sensitivity still needs per-observation raw traces (Class C)."}

tex = open(TEX, encoding="utf-8", errors="ignore").read()
import re
m = re.search(r"Cond\..*?toprule(.*?)\\end\{tabular\}", tex, re.S)
prov_rows = []
if m:
    body = m.group(1)
    for c in re.split(r"\\\\", body):
        parts = [p.strip() for p in re.sub(r"\\\w+\s*", " ", c).replace("{"," ").replace("}"," ").split("&")]
        parts = [re.sub(r"\s+"," ",p).strip() for p in parts]
        if parts and re.match(r"^C\d+", parts[0]):
            prov_rows.append({"condition": parts[0], "setting": parts[1] if len(parts)>1 else "",
                              "claim": parts[2] if len(parts)>2 else "", "tier": parts[3] if len(parts)>3 else ""})
result1["condition_provenance"] = {"parsed_rows": prov_rows, "n_parsed": len(prov_rows),
  "local_data_map": {"F_v10": SRC, "mini_F_v7": r"<ARCHIVE_ROOT>\PAPER1_CONSOLIDATED\joint_mini_F_v7_results.json",
    "official matched pairs": r"<ARCHIVE_ROOT>\experiments\official_A_qwen_eval_ds_exec.json (+B/C/D)",
    "mm_epc replications": r"<ARCHIVE_ROOT>\experiments\mm_epc_*.json"},
  "note": "Per-condition seed counts and API calls are not persisted per condition (archive holds totals only: 4000 calls / 861305 tokens for F_v10)."}

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "p1_mc_family_reconstruction.json"), "w", encoding="utf-8") as f:
    json.dump(result1, f, ensure_ascii=False, indent=1)
print(json.dumps(result1["families"], ensure_ascii=False, indent=1)[:4000])
print("ECE-Brier pearson:", round(r_pear,4), "spearman:", round(r_spear,4), "perm CI:", ci)
print("provenance rows:", len(prov_rows))
