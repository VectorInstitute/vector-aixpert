#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM zero-shot scoring on social-problem data + Integrated Gradients (IG).

Key fixes in this version:
- IG score depends on the SAME forward that uses `inputs_embeds` (proper gradients).
- Dtype consistency (avoid Float vs Half LayerNorm crash). Use `--force_float32` if needed.
- Uses `dtype=` (not deprecated `torch_dtype`).
- Parquet read guard (falls back to CSV if no engine is present).

uv run python scripts/llm_zero_shot_explain.py \
  --in data/jigsaw_sample.parquet \
  --text_col comment_text \
  --task toxicity \
  --out outputs/zs_preds.parquet \
  --model distilgpt2 \
  --max_rows 1000 \
  --ig_rows 25 --ig_steps 32 --save_heatmaps \
  --force_float32 \
  --label_col target \
  --id_cols male female black white muslim jewish christian transgender homosexual_gay_or_lesbian

"""
import argparse, os
from pathlib import Path
import pandas as pd
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM
import matplotlib.pyplot as plt
from rich.progress import track
import importlib

LABELS = {
    # Binary label pairs; first entry treated as "positive" for score sign
    "toxicity": ["toxic", "non-toxic"],
    "hate": ["hateful", "not hateful"],
    "offense": ["offensive", "not offensive"],
}

def get_device():
    # Prefer CUDA, then Apple MPS, else CPU
    if torch.cuda.is_available(): return torch.device("cuda")
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available(): return torch.device("mps")
    return torch.device("cpu")

def load_llm(model_name, device, force_float32=False):
    # Load tokenizer + model; float32 optional for stable grads (LayerNorm FP16 issues)
    tok = AutoTokenizer.from_pretrained(model_name, use_fast=True)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token  # Ensure padding token exists
    load_dtype = torch.float32 if (force_float32 or device.type != "cuda") else torch.float16
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        dtype=load_dtype,             # <- use dtype (not deprecated torch_dtype)
        low_cpu_mem_usage=True
    ).to(device).eval()
    # Some models crash returning big intermediates with cache on; harmless to disable
    if hasattr(model.config, "use_cache"):
        model.config.use_cache = False  # Disable KV cache (not needed for scoring / IG)
    return model, tok

def format_prompt(text, task):
    # Simple instruction + user text -> ensures final token is "Label:" to predict after
    instruction = {
        "toxicity": "Decide if the following text is toxic or non-toxic. Answer with a single word.\nText: ",
        "hate": "Decide if the text is hateful or not hateful. Answer with a single word.\nText: ",
        "offense": "Decide if the text is offensive or not offensive. Answer with a single word.\nText: "
    }[task]
    return f"{instruction}{text}\nLabel:"

@torch.no_grad()
def label_logprob(model, tok, prompt_ids, label_str, max_label_tokens=3):
    # Compute log p(label | prompt) by teacher-forcing each label token sequentially
    label_ids = tok.encode(label_str, add_special_tokens=False)
    if len(label_ids) > max_label_tokens:
        label_ids = label_ids[:max_label_tokens]  # Truncate very long textual labels
    cur_ids = prompt_ids.clone()
    logp = 0.0
    for lid in label_ids:
        out = model(input_ids=cur_ids)              # Forward over current context
        next_logits = out.logits[:, -1, :]          # Next-token distribution
        logp += F.log_softmax(next_logits, dim=-1)[0, lid]
        # Append the ground-truth label token (teacher forcing)
        cur_ids = torch.cat([cur_ids, torch.tensor([[lid]], device=cur_ids.device)], dim=1)
    return float(logp.item())

def score_and_predict(model, tok, text, task):
    # Score = log p(pos_label) - log p(neg_label); sign => prediction
    prompt = format_prompt(text, task)
    batch = tok(prompt, return_tensors="pt").to(next(model.parameters()).device)
    prompt_ids = batch["input_ids"]
    y_pos, y_neg = LABELS[task]
    lp_pos = label_logprob(model, tok, prompt_ids, y_pos)
    lp_neg = label_logprob(model, tok, prompt_ids, y_neg)
    score = lp_pos - lp_neg
    pred = 1 if score > 0 else 0  # Positive if pos_label more likely
    return {"prompt": prompt, "score": score, "pred": pred, "labels": (y_pos, y_neg), "lp_pos": lp_pos, "lp_neg": lp_neg}

def integrated_gradients(model, tok, text, task, steps=32):
    """
    Integrated Gradients on scalar: log p(pos_first_token) - log p(neg_first_token)
    w.r.t. prompt embeddings. Uses path baseline = zeros.
    """
    device = next(model.parameters()).device
    model_dtype = next(model.parameters()).dtype

    prompt = format_prompt(text, task)
    enc = tok(prompt, return_tensors="pt", add_special_tokens=True)
    input_ids = enc["input_ids"].to(device)
    attn = enc["attention_mask"].to(device)

    emb_layer = model.get_input_embeddings()
    x = emb_layer(input_ids).detach().to(model_dtype)  # Current embeddings (no grad yet)
    x0 = torch.zeros_like(x)                           # Zero baseline (can swap for mean/embed of pad)

    pos_label, neg_label = LABELS[task]
    # Use only first token of each label for stable logits (fast; avoids multi-token loops)
    pos_id = tok.encode(pos_label, add_special_tokens=False)[0]
    neg_id = tok.encode(neg_label, add_special_tokens=False)[0]

    def score_fn(emb):
        # Single forward with inputs_embeds ensures gradient path
        out = model(inputs_embeds=emb, attention_mask=attn, use_cache=False)
        last_logits = out.logits[:, -1, :]            # Logits predicting label position
        last_logprobs = F.log_softmax(last_logits, dim=-1)
        return last_logprobs[0, pos_id] - last_logprobs[0, neg_id]

    alphas = torch.linspace(0, 1, steps=steps, device=device, dtype=model_dtype).view(-1, 1, 1, 1)
    grads = torch.zeros_like(x)
    for a in alphas:
        emb = (x0 + a * (x - x0)).requires_grad_(True)  # Interpolated embeddings
        s = score_fn(emb)
        s.backward()
        grads += emb.grad.detach()

    avg_grads = grads / steps                          # Path integral approximation
    atts = (avg_grads * (x - x0)).sum(dim=-1).squeeze(0)  # Dot product across hidden dim
    atts = atts / (atts.abs().sum() + 1e-8)            # Normalize to sum(|atts|)=1

    tokens = tok.convert_ids_to_tokens(input_ids[0].tolist())
    return tokens, atts.cpu().numpy(), prompt

def save_heatmap(tokens, atts, out_path):
    # Simple bar plot; token strings lightly cleaned for readability
    plt.figure(figsize=(max(6, len(tokens) * 0.2), 2.8))
    plt.bar(range(len(tokens)), atts)
    plt.xticks(range(len(tokens)), [t.replace("Ġ", "▯") for t in tokens], rotation=70, ha="right")
    plt.ylabel("IG attribution")
    plt.tight_layout()
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=200)
    plt.close()

def load_df_safely(path):
    # Attempt Parquet; fallback to CSV if engine missing or read fails
    try:
        if path.endswith(".parquet"):
            if not (importlib.util.find_spec("pyarrow") or importlib.util.find_spec("fastparquet")):
                raise ImportError("No parquet engine (pyarrow/fastparquet) found.")
            return pd.read_parquet(path)
        return pd.read_csv(path)
    except Exception as e:
        print(f"[warn] Failed to read '{path}' as Parquet ({e}); trying CSV…")
        return pd.read_csv(path)

def main():
    # Parse CLI, load data/model, loop over rows, optional IG subset
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Parquet/CSV file with a text column")
    ap.add_argument("--text_col", required=True)
    ap.add_argument("--task", required=True, choices=list(LABELS.keys()))
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="distilgpt2")
    ap.add_argument("--max_rows", type=int, default=2000)
    ap.add_argument("--ig_rows", type=int, default=25, help="How many rows to run IG on")
    ap.add_argument("--ig_steps", type=int, default=32)
    ap.add_argument("--save_heatmaps", action="store_true")
    ap.add_argument("--label_col", default=None, help="Copy label column from input into preds")
    ap.add_argument("--id_cols", nargs="*", default=None, help="Copy identity columns from input into preds")
    ap.add_argument("--force_float32", action="store_true", help="Load model in float32 (safer for IG / LayerNorm).")
    args = ap.parse_args()

    df = load_df_safely(args.inp)
    if len(df) > args.max_rows:
        df = df.iloc[:args.max_rows].copy()  # Hard cap for quick experimentation

    device = get_device()
    model, tok = load_llm(args.model, device, force_float32=args.force_float32)

    preds, ig_records = [], []
    extra_cols = []
    if args.label_col and args.label_col in df.columns:
        extra_cols.append(args.label_col)
    if args.id_cols:
        for c in args.id_cols:
            if c in df.columns:
                extra_cols.append(c)

    for i in track(range(len(df)), description="Scoring"):
        # Truncate overly long texts (context length safety)
        text = str(df.iloc[i][args.text_col])[:4096]
        res = score_and_predict(model, tok, text, args.task)
        row = {"idx": i, "pred": res["pred"], "score": res["score"], "lp_pos": res["lp_pos"], "lp_neg": res["lp_neg"]}
        for c in extra_cols:
            row[c] = df.iloc[i][c]
        preds.append(row)

        if args.save_heatmaps and len(ig_records) < args.ig_rows:
            # Only compute IG for first N rows (expensive)
            toks, atts, prompt = integrated_gradients(model, tok, text, args.task, steps=args.ig_steps)
            img_path = Path("outputs/ig_heatmaps") / f"row{i}.png"
            save_heatmap(toks, atts, img_path)
            ig_records.append({"idx": i, "heatmap": str(img_path), "prompt": prompt})

    outdir = Path(args.out).parent
    outdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(preds).to_parquet(args.out, index=False)
    if ig_records:
        pd.DataFrame(ig_records).to_parquet(Path(args.out).with_suffix(".ig.parquet"), index=False)
    print(f"Saved predictions -> {args.out}")

if __name__ == "__main__":
    main()



# GitHub Copilot
# Summary:

# Purpose: Zero-shot binary classification (toxicity, hate, offense) with a causal LM plus token-level Integrated Gradients (IG) explanations.
# Labels: Uses predefined positive/negative label pairs; score = log p(pos) - log p(neg) via teacher forcing.
# Prompt: Instruction + text + “Label:” so model predicts a one-word label.
# Prediction: Computes separate label log-prob sums (first few tokens) and assigns pred based on score sign.
# IG Explanation: Computes attributions over prompt embeddings using path integration (zero baseline) on a simplified scalar (difference of first-token log probs of pos vs neg labels) in a single forward with inputs_embeds.
# Stability: Optional --force_float32 to avoid FP16 LayerNorm issues; disables use_cache for consistent gradients.
# Data Loading: Safe Parquet/CSV loader with fallback if no Parquet engine.
# Outputs: Main parquet (pred, score, lp_pos, lp_neg, optional extra cols) plus optional IG parquet and heatmap PNGs.
# Performance controls: --max_rows limits data; --ig_rows and --ig_steps bound explanation cost.
# Device selection: Prefers CUDA, then MPS, else CPU.