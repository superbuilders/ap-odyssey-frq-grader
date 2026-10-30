"""Composition rules under test. Each maps one averaged gate vector -> (level, signal).

`g` is {noul_key: value}; `m` is {n_seg, frq_type, cited}. Identical inputs to
run.compose_b, just without the record object.
"""
T = 0.5


def _parts(g, m):
    K = m["n_seg"]
    syn = m["frq_type"] == "synthesis"
    rhet = m["frq_type"] == "rhetorical_analysis"
    sev = [g["seg%d_ev" % i] for i in range(1, K + 1)]
    sex = [g["seg%d_expl" % i] for i in range(1, K + 1)]
    srh = [g["seg%d_rhet" % i] for i in range(1, K + 1)] if rhet else []
    return K, syn, rhet, sev, sex, srh


# ---------- R0: byte-faithful port of run.compose_b ----------
def r0_exact(g, m):
    K, syn, rhet, sev, sex, srh = _parts(g, m)
    restates = g["b_restates"]; specific = g["b_specific"]
    multiclaims = g["b_multiclaims"]; lor = g["b_lor"]; mech = g["b_mech"]
    idx_ev = [i for i in range(K) if sev[i] > T]
    n_ev = len(idx_ev); n_expl = sum(1 for i in idx_ev if sex[i] > T)
    n_rhet = sum(1 for v in srh if v > T)
    cited = m["cited"]
    ev_ge2 = (cited >= 2) if syn else (n_ev >= 1)
    ev_ge3 = (cited >= 3) if syn else (n_ev >= 1)
    if restates > T or not ev_ge2:               lvl = 0
    elif n_expl == 0:                            lvl = 1
    elif not (lor > T):                          lvl = 2
    elif not ev_ge3:                             lvl = 2
    elif not (specific > T and multiclaims > T): lvl = 2
    else:
        consistently = n_ev >= 2 and n_expl == n_ev
        lvl = 4 if (consistently and not (mech > T)) else 3
    if rhet:
        if n_rhet == 0:   lvl = min(lvl, 2)
        elif n_rhet < 2:  lvl = min(lvl, 3)
    p1 = (1 - restates) * (1.0 if ev_ge2 else 0.0)
    p2 = p1 * (max(sex) if sex else 0.0)
    p3 = p2 * lor * (1.0 if ev_ge3 else 0.0) * specific * multiclaims
    if rhet: p3 *= (max(srh) if srh else 0.0)
    cons = min([sex[i] for i in idx_ev]) if n_ev >= 2 else 0.0
    p4 = p3 * cons * (1 - mech)
    if rhet: p4 *= (sorted(srh, reverse=True)[1] if len(srh) > 1 else 0.0)
    return lvl, p1 + p2 + p3 + p4


def _common(g, m):
    K, syn, rhet, sev, sex, srh = _parts(g, m)
    idx = [i for i in range(K) if sev[i] > T]
    d = dict(K=K, syn=syn, rhet=rhet, sev=sev, sex=sex, srh=srh, idx=idx,
             n_ev=len(idx), n_expl=sum(1 for i in idx if sex[i] > T),
             n_rhet=sum(1 for v in srh if v > T),
             restates=g["b_restates"], specific=g["b_specific"],
             multi=g["b_multiclaims"], lor=g["b_lor"], mech=g["b_mech"])
    d["ev_ge2"] = (m["cited"] >= 2) if syn else (d["n_ev"] >= 1)
    d["ev_ge3"] = (m["cited"] >= 3) if syn else (d["n_ev"] >= 1)
    sx = sorted([sex[i] for i in idx], reverse=True)
    d["p_any_expl"] = sx[0] if sx else 0.0          # soft  n_expl >= 1
    d["p_two_expl"] = sx[1] if len(sx) > 1 else 0.0  # soft  n_expl >= 2
    d["p_all_expl"] = min(sx) if len(sx) > 1 else 0.0  # soft  n_expl == n_ev
    rs = sorted(srh, reverse=True)
    d["p_rh1"] = rs[0] if rs else 0.0
    d["p_rh2"] = rs[1] if len(rs) > 1 else 0.0
    return d


def _cap_rhet(d, lvl):
    if d["rhet"]:
        if d["n_rhet"] == 0:   lvl = min(lvl, 2)
        elif d["n_rhet"] < 2:  lvl = min(lvl, 3)
    return lvl


def _raw(p1, p2, p3, p4):
    return p1 + p2 + p3 + p4


# ---------- R1: universal "all segments explain" -> count "at least two" ----------
# A universal over K binary gates fails if ANY one flips, so it multiplies the
# per-gate instability by K. A count threshold moves only when one named gate
# crosses 0.5.
def r1_count4(g, m):
    d = _common(g, m)
    if d["restates"] > T or not d["ev_ge2"]:            lvl = 0
    elif d["n_expl"] == 0:                              lvl = 1
    elif not (d["lor"] > T):                            lvl = 2
    elif not d["ev_ge3"]:                               lvl = 2
    elif not (d["specific"] > T and d["multi"] > T):    lvl = 2
    else:
        lvl = 4 if (d["n_expl"] >= 2 and not (d["mech"] > T)) else 3
    lvl = _cap_rhet(d, lvl)
    p1 = (1 - d["restates"]) * (1.0 if d["ev_ge2"] else 0.0)
    p2 = p1 * d["p_any_expl"]
    p3 = p2 * d["lor"] * (1.0 if d["ev_ge3"] else 0.0) * d["specific"] * d["multi"]
    if d["rhet"]: p3 *= d["p_rh1"]
    p4 = p3 * d["p_two_expl"] * (1 - d["mech"])
    if d["rhet"]: p4 *= d["p_rh2"]
    return lvl, _raw(p1, p2, p3, p4)


# ---------- R2: put "specific" where the rubric puts it ----------
# CB 1-point text is "mostly general evidence"; the 2-point text is "a mix of
# specific evidence and broad generalities". So specific-vs-general separates 1
# from 2, not 2 from 3. compose_b uses it at 2|3, which leaves level 1 reachable
# only when NO segment explains anything.
def r2_specific_low(g, m):
    d = _common(g, m)
    if d["restates"] > T or not d["ev_ge2"]:  lvl = 0
    elif d["n_expl"] == 0:                    lvl = 1
    elif not (d["specific"] > T):             lvl = 1
    elif not (d["lor"] > T):                  lvl = 2
    elif not d["ev_ge3"]:                     lvl = 2
    elif not (d["multi"] > T):                lvl = 2
    else:
        consistently = d["n_ev"] >= 2 and d["n_expl"] == d["n_ev"]
        lvl = 4 if (consistently and not (d["mech"] > T)) else 3
    lvl = _cap_rhet(d, lvl)
    p1 = (1 - d["restates"]) * (1.0 if d["ev_ge2"] else 0.0)
    p2 = p1 * d["p_any_expl"] * d["specific"]
    p3 = p2 * d["lor"] * (1.0 if d["ev_ge3"] else 0.0) * d["multi"]
    if d["rhet"]: p3 *= d["p_rh1"]
    p4 = p3 * d["p_all_expl"] * (1 - d["mech"])
    if d["rhet"]: p4 *= d["p_rh2"]
    return lvl, _raw(p1, p2, p3, p4)


# ---------- R3: both ----------
def r3_both(g, m):
    d = _common(g, m)
    if d["restates"] > T or not d["ev_ge2"]:  lvl = 0
    elif d["n_expl"] == 0:                    lvl = 1
    elif not (d["specific"] > T):             lvl = 1
    elif not (d["lor"] > T):                  lvl = 2
    elif not d["ev_ge3"]:                     lvl = 2
    elif not (d["multi"] > T):                lvl = 2
    else:
        lvl = 4 if (d["n_expl"] >= 2 and not (d["mech"] > T)) else 3
    lvl = _cap_rhet(d, lvl)
    p1 = (1 - d["restates"]) * (1.0 if d["ev_ge2"] else 0.0)
    p2 = p1 * d["p_any_expl"] * d["specific"]
    p3 = p2 * d["lor"] * (1.0 if d["ev_ge3"] else 0.0) * d["multi"]
    if d["rhet"]: p3 *= d["p_rh1"]
    p4 = p3 * d["p_two_expl"] * (1 - d["mech"])
    if d["rhet"]: p4 *= d["p_rh2"]
    return lvl, _raw(p1, p2, p3, p4)


# ---------- R4: R3 minus the mech gate ----------
# b_mech is the least decisive noul in the set: mean 0.386, 10/36 essays within
# 0.10 of the cut, and the only gate that flips its boolean on 4 essays. It
# gates 3|4 alone, so every one of those flips is a level flip.
def r4_nomech(g, m):
    d = _common(g, m)
    if d["restates"] > T or not d["ev_ge2"]:  lvl = 0
    elif d["n_expl"] == 0:                    lvl = 1
    elif not (d["specific"] > T):             lvl = 1
    elif not (d["lor"] > T):                  lvl = 2
    elif not d["ev_ge3"]:                     lvl = 2
    elif not (d["multi"] > T):                lvl = 2
    else:
        lvl = 4 if d["n_expl"] >= 2 else 3
    lvl = _cap_rhet(d, lvl)
    p1 = (1 - d["restates"]) * (1.0 if d["ev_ge2"] else 0.0)
    p2 = p1 * d["p_any_expl"] * d["specific"]
    p3 = p2 * d["lor"] * (1.0 if d["ev_ge3"] else 0.0) * d["multi"]
    if d["rhet"]: p3 *= d["p_rh1"]
    p4 = p3 * d["p_two_expl"]
    if d["rhet"]: p4 *= d["p_rh2"]
    return lvl, _raw(p1, p2, p3, p4)
