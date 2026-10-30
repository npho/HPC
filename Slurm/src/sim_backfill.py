"""
sim_backfill.py - MY toy model of FIFO vs backfill scheduling (NOT Slurm code).

What it models
  * a homogeneous machine of N nodes, whole-node jobs, single queue, strict priority = arrival order
  * 'fifo'      : if the head job doesn't fit, nothing behind it starts  (like sched/builtin)
  * 'backfill'  : every pass rebuilds a plan from scratch. Running jobs are assumed to end at
                  start + ESTIMATE. Waiting jobs are walked in priority order; each gets the earliest
                  slot that fits the plan, and that slot is *reserved*. A job whose slot is "now" starts.
                  This mirrors the behaviour the Slurm docs describe (reserve for expected run time,
                  start only if no higher-priority job's expected start is delayed), with unlimited depth,
                  whole nodes only, and no preemption/limits/topology.
  * user estimate = min(f * true_runtime, 48 h)   ("f-model", as in Mu'alem & Feitelson 2001)
  * jobs are never killed at their limit (estimate >= runtime always holds here)

Outputs data/backfill_sweep.json, consumed by the video scene and the notes file.
"""
import json
import math
import sys
import time

import numpy as np
from numba import njit

SLOT_MIN = 5            # one time slot = 5 minutes
N_NODES = 128
HORIZON = 1152          # planning horizon: 96 h of slots
MAX_RUN = 288           # 24 h
MAX_EST = 576           # 48 h cap on user estimates
SIZES = np.array([1, 2, 4, 8, 16, 32, 64])
PROBS = np.array([0.30, 0.22, 0.18, 0.13, 0.09, 0.05, 0.03])


@njit(cache=True)
def simulate(arr, size, run, est, N, mode, depth, H):
    n = arr.shape[0]
    start = np.full(n, -1, np.int64)
    end_act = np.zeros(n, np.int64)
    end_est = np.zeros(n, np.int64)
    backfilled = np.zeros(n, np.bool_)
    first_plan = np.full(n, -1, np.int64)   # start time promised by the first plan that included the job
    qlist = np.empty(n, np.int64)
    qn = 0
    run_idx = np.empty(n, np.int64)
    rn = 0
    F = np.empty(H, np.int64)
    free = N
    nxt = 0
    nfin = 0
    t = 0
    while nfin < n:
        tn = 1 << 60
        if nxt < n:
            tn = arr[nxt]
        for k in range(rn):
            e = end_act[run_idx[k]]
            if e < tn:
                tn = e
        t = tn
        k = 0
        while k < rn:
            j = run_idx[k]
            if end_act[j] <= t:
                free += size[j]
                nfin += 1
                run_idx[k] = run_idx[rn - 1]
                rn -= 1
            else:
                k += 1
        while nxt < n and arr[nxt] <= t:
            qlist[qn] = nxt
            qn += 1
            nxt += 1

        if mode == 0:  # strict FIFO
            h = 0
            while h < qn and size[qlist[h]] <= free:
                j = qlist[h]
                start[j] = t
                end_act[j] = t + run[j]
                end_est[j] = t + est[j]
                free -= size[j]
                run_idx[rn] = j
                rn += 1
                h += 1
            if h > 0:
                for q in range(h, qn):
                    qlist[q - h] = qlist[q]
                qn -= h
        else:  # conservative-style backfill, plan rebuilt every pass
            for k in range(H):
                F[k] = N
            for k in range(rn):
                j = run_idx[k]
                d = end_est[j] - t
                if d > H:
                    d = H
                if d > 0:
                    for q in range(d):
                        F[q] -= size[j]
            started_flag = np.zeros(qn, np.bool_)
            first_waiting = -1
            lim = qn if qn < depth else depth
            for qi in range(lim):
                j = qlist[qi]
                s = size[j]
                d = est[j]
                if d > H:
                    d = H
                run_len = 0
                ist = -1
                for k in range(H):
                    if F[k] >= s:
                        run_len += 1
                    else:
                        run_len = 0
                    if run_len >= d:
                        ist = k - d + 1
                        break
                if ist < 0:
                    if first_waiting < 0:
                        first_waiting = qi
                    continue
                if first_plan[j] < 0:
                    first_plan[j] = t + ist
                for q in range(ist, ist + d):
                    F[q] -= s
                if ist == 0:
                    start[j] = t
                    end_act[j] = t + run[j]
                    end_est[j] = t + est[j]
                    free -= s
                    run_idx[rn] = j
                    rn += 1
                    started_flag[qi] = True
                    if first_waiting >= 0:
                        backfilled[j] = True
                else:
                    if first_waiting < 0:
                        first_waiting = qi
            m = 0
            for qi in range(qn):
                if qi < lim and started_flag[qi]:
                    continue
                qlist[m] = qlist[qi]
                m += 1
            qn = m
    return start, end_act, backfilled, first_plan


def make_workload(seed, n_jobs, rho):
    rng = np.random.default_rng(seed)
    size = rng.choice(SIZES, size=n_jobs, p=PROBS).astype(np.int64)
    run = np.exp(rng.normal(math.log(12), 1.2, size=n_jobs))
    run = np.clip(np.rint(run), 1, MAX_RUN).astype(np.int64)
    es, er = float((SIZES * PROBS).sum()), float(run.mean())
    lam = rho * N_NODES / (es * er)           # arrivals per slot
    gaps = rng.exponential(1.0 / lam, size=n_jobs)
    arr = np.floor(np.cumsum(gaps)).astype(np.int64)
    return arr, size, run


def metrics(arr, size, run, start, bf, lo, hi, plan=None):
    sl = slice(lo, hi)
    wait = (start[sl] - arr[sl]).astype(float)
    r = run[sl].astype(float)
    bsld = np.maximum(1.0, (wait + r) / np.maximum(r, 2.0))
    h = SLOT_MIN / 60.0
    out = dict(
        mean_wait_h=float(wait.mean() * h),
        p95_wait_h=float(np.percentile(wait, 95) * h),
        mean_bsld=float(bsld.mean()),
        pct_backfilled=float(bf[sl].mean() * 100),
    )
    if plan is not None:
        pl = plan[sl]
        st = start[sl]
        w = wait > 0                       # only jobs that actually had to wait
        over = (pl - st)[w].astype(float) * h   # >0: promised later than reality (pessimistic)
        out["pred_error_mean_h"] = float(over.mean())          # signed: planned - actual
        out["pred_abs_error_mean_h"] = float(np.abs(over).mean())
        out["pct_started_later_than_first_plan"] = float((st > pl).mean() * 100)
    return out


def main():
    n_jobs, rho, seeds = 3000, 0.85, 30
    factors = [1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
    lo, hi = 300, 2700
    out = dict(params=dict(nodes=N_NODES, slot_min=SLOT_MIN, n_jobs=n_jobs, offered_load=rho, seeds=seeds,
                           sizes=SIZES.tolist(), probs=PROBS.tolist(), runtime_median_h=1.0, runtime_sigma=1.2,
                           max_run_h=24, max_estimate_h=48, metric_window=[lo, hi], depth="unlimited (500)"),
               fifo=[], backfill={str(f): [] for f in factors})
    t0 = time.time()
    for sd in range(seeds):
        arr, size, run = make_workload(sd, n_jobs, rho)
        est1 = run.copy()
        s, e, bf, pl = simulate(arr, size, run, est1, N_NODES, 0, 500, HORIZON)
        out["fifo"].append(metrics(arr, size, run, s, bf, lo, hi))
        for f in factors:
            est = np.minimum(np.ceil(run * f), MAX_EST).astype(np.int64)
            s, e, bf, pl = simulate(arr, size, run, est, N_NODES, 1, 500, HORIZON)
            out["backfill"][str(f)].append(metrics(arr, size, run, s, bf, lo, hi, pl))
        print("seed", sd, "done %.1fs" % (time.time() - t0), flush=True)

    def agg(rows, key):
        v = np.array([r[key] for r in rows])
        return float(v.mean()), float(1.96 * v.std(ddof=1) / math.sqrt(len(v)))

    summary = {"fifo": {k: agg(out["fifo"], k) for k in out["fifo"][0]}}
    for f in factors:
        rows = out["backfill"][str(f)]
        summary["f=%g" % f] = {k: agg(rows, k) for k in rows[0]}
        # paired difference vs f=1 on mean wait
        base = np.array([r["mean_wait_h"] for r in out["backfill"]["1.0"]])
        cur = np.array([r["mean_wait_h"] for r in rows])
        d = cur - base
        summary["f=%g" % f]["paired_dwait_vs_f1"] = (float(d.mean()), float(1.96 * d.std(ddof=1) / math.sqrt(len(d))) if f != 1.0 else 0.0)
    out["summary"] = summary
    from paths import DATA
    with open(DATA / "backfill_sweep.json", "w") as fh:
        json.dump(out, fh, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
