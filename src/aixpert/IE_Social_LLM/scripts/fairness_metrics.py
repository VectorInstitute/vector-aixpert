#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Group fairness metrics (per-identity) + summary:
- SPD per identity: P(Ŷ=1|A=1) - P(Ŷ=1|A=0)
- EOpp per identity: TPR(A=1) - TPR(A=0)
- Per-group acc/f1/tpr/fpr/pos_rate, with min group size filter
- Worst-case (max |SPD|, max |EOpp|, worst acc/f1) across identities

uv run python scripts/fairness_metrics.py \
  --preds outputs/zs_preds.parquet \
  --labels_file data/civil.parquet \
  --label_col target \
  --id_cols male female black white muslim jewish christian \
  --out outputs/fairness_report.csv

  for jigsaw sample
  uv run python scripts/fairness_metrics.py \
  --preds outputs/zs_preds.parquet \
  --label_col target \
  --id_cols male female black white muslim jewish christian transgender homosexual_gay_or_lesbian \
  --min_group_size 1 \
  --out outputs/fairness_report.csv

  sanity checks
  uv run python -c "import pandas as pd; print(pd.read_parquet('outputs/zs_preds.parquet').head())"
uv run python -c "import pandas as pd; print(pd.read_csv('outputs/fairness_report.per_identity.csv').sort_values('SPD').head())"

uv run python -c "import pandas as pd; print(pd.read_csv('outputs/fairness_report.summary.csv'))"
uv run python -c "import pandas as pd; print(pd.read_csv('outputs/fairness_report.csv').head(20))"

"""
import argparse, importlib
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix

def load_df(path: str) -> pd.DataFrame:
    if path.endswith(".parquet"):
        if importlib.util.find_spec("pyarrow") or importlib.util.find_spec("fastparquet"):
            return pd.read_parquet(path)
        print("[warn] No parquet engine; attempting CSV fallback…")
    return pd.read_csv(path)

def binarize_labels(y, positive_label=1, thr=0.5):
    """Accept 0/1 ints or floats in [0,1]. If values are not {0,1},
    threshold at thr and then map to {0,1} where '1' means positive_label."""
    y = pd.Series(y)
    # if already integers 0/1, just map to 0/1 respecting positive_label
    if set(pd.unique(y.dropna())) <= {0,1}:
        if positive_label in (0,1):
            return (y.astype(int) == int(positive_label)).astype(int).values
    # else assume probabilities in [0,1]
    yy = (y.astype(float) >= thr).astype(int)
    if positive_label == 0:
        yy = 1 - yy
    return yy.values

def metrics_for_group(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    f1  = f1_score(y_true, y_pred, zero_division=0)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0,1]).ravel()
    tpr = tp / (tp + fn + 1e-9)
    fpr = fp / (fp + tn + 1e-9)
    pos_rate = float((y_pred == 1).mean())
    return {"acc": acc, "f1": f1, "tpr": tpr, "fpr": fpr, "pos_rate": pos_rate}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", required=True,
                    help="Parquet/CSV with at least: idx, pred (0/1), optionally label_col & id_cols.")
    ap.add_argument("--labels_file", default=None,
                    help="If labels/id_cols are in a separate file, provide it; must contain idx.")
    ap.add_argument("--label_col", required=True)
    ap.add_argument("--positive_label", type=int, default=1)
    ap.add_argument("--id_cols", nargs="+", required=True)
    ap.add_argument("--min_group_size", type=int, default=30,
                    help="Skip groups with fewer than this many rows (default=30).")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    dfp = load_df(args.preds)
    if "idx" not in dfp.columns:
        raise SystemExit("Expected 'preds' to contain an 'idx' column for alignment.")

    # Merge labels/id_cols
    if args.labels_file:
        dfl = load_df(args.labels_file)
        if "idx" not in dfl.columns:
            # common fallback: labels file is the original dataset → use its index as idx
            dfl = dfl.reset_index().rename(columns={"index": "idx"})
        df = dfp.merge(dfl, on="idx", how="left", suffixes=("", "_labels"))
    else:
        df = dfp.copy()

    if args.label_col not in df.columns:
        raise SystemExit(f"Label column '{args.label_col}' not found after merge.")

    # Prepare y_true / y_pred
    y_true = binarize_labels(df[args.label_col], positive_label=args.positive_label, thr=0.5)
    if "pred" not in df.columns:
        raise SystemExit("Missing 'pred' column in preds; compute preds first.")
    y_pred = df["pred"].astype(int).values

    rows = []
    per_identity = []  # per identity summary rows
    for a in args.id_cols:
        if a not in df.columns:
            print(f"[warn] identity column '{a}' not found; skipping")
            continue

        # membership: treat >0 as 1, NaN→0
        A = (pd.to_numeric(df[a], errors="coerce").fillna(0) > 0).astype(int).values

        # Identity=0 and Identity=1 slices
        rep_rows = []
        for val in (0, 1):
            mask = (A == val)
            n = int(mask.sum())
            if n < args.min_group_size:
                rep_rows.append({"identity": a, "group": f"{a}={val}", "n": n, "skipped": True})
                continue
            m = metrics_for_group(y_true[mask], y_pred[mask])
            rep_rows.append({"identity": a, "group": f"{a}={val}", "n": n, "skipped": False, **m})

        # compute SPD / EOpp for this identity if both groups are present and not skipped
        g0 = next((r for r in rep_rows if r["group"].endswith("=0") and not r.get("skipped")), None)
        g1 = next((r for r in rep_rows if r["group"].endswith("=1") and not r.get("skipped")), None)
        if g0 and g1:
            spd   = g1["pos_rate"] - g0["pos_rate"]   # P(Ŷ=1|A=1) - P(Ŷ=1|A=0)
            eopp  = g1["tpr"] - g0["tpr"]             # TPR diff
            per_identity.append({"identity": a, "SPD": spd, "EOpp_diff": eopp,
                                 "n_A0": g0["n"], "n_A1": g1["n"]})

        rows.extend(rep_rows)

    rep = pd.DataFrame(rows)
    rep_out = Path(args.out)
    rep_out.parent.mkdir(parents=True, exist_ok=True)
    rep.to_csv(rep_out, index=False)

    # Worst-case summaries
    summary_rows = []
    if per_identity:
        pi = pd.DataFrame(per_identity)
        # worst absolute disparities across identities
        worst_spd = pi["SPD"].abs().max()
        worst_eopp = pi["EOpp_diff"].abs().max()
        # worst performance across all non-skipped groups
        non_skipped = rep[~rep.get("skipped", False)]
        worst_acc = non_skipped["acc"].min() if "acc" in non_skipped else np.nan
        worst_f1  = non_skipped["f1"].min()  if "f1" in non_skipped else np.nan
        summary_rows.append({"WorstAbsSPD": worst_spd, "WorstAbsEOpp": worst_eopp,
                             "WorstGroupAcc": worst_acc, "WorstGroupF1": worst_f1})
        pi.to_csv(rep_out.with_suffix(".per_identity.csv"), index=False)
    else:
        summary_rows.append({"WorstAbsSPD": np.nan, "WorstAbsEOpp": np.nan,
                             "WorstGroupAcc": np.nan, "WorstGroupF1": np.nan})

    pd.DataFrame(summary_rows).to_csv(rep_out.with_suffix(".summary.csv"), index=False)
    print(f"Wrote per-group metrics -> {rep_out}")
    print(f"Wrote per-identity disparities -> {rep_out.with_suffix('.per_identity.csv')}")
    print(f"Wrote summary -> {rep_out.with_suffix('.summary.csv')}")

if __name__ == "__main__":
    main()
