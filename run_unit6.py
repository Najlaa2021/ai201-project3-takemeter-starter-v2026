#!/usr/bin/env python3
"""Headless Unit 5/6 training — same logic as takemeter.ipynb sections 3–6."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    set_seed,
)

LABELS = ["evidence", "experience", "take"]
BASE_MODEL = "distilbert-base-uncased"
EPOCHS = 3
LEARNING_RATE = 2e-5
BATCH_SIZE = 16
MAX_LENGTH = 128
SEEDS = [42, 7, 2024]
CSV = "labels.csv"


def pick_device():
    if torch.cuda.is_available():
        return "cuda", torch.cuda.get_device_name(0)
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps", "Apple Silicon GPU (MPS)"
    return "cpu", "CPU"


DEVICE, DEVICE_NAME = pick_device()


def _stratify_on(frame):
    counts = frame["label"].value_counts()
    if counts.min() < 2:
        return None
    return frame["label"]


def split_dataset(df, seed):
    rest, test = train_test_split(
        df, test_size=0.15, random_state=seed, stratify=_stratify_on(df)
    )
    train, val = train_test_split(
        rest, test_size=0.15 / 0.85, random_state=seed, stratify=_stratify_on(rest)
    )
    return (
        train.reset_index(drop=True),
        val.reset_index(drop=True),
        test.reset_index(drop=True),
    )


def to_ids(df, labels):
    lookup = {label: i for i, label in enumerate(labels)}
    out = df.copy()
    out["labels"] = out["label"].astype(str).str.strip().map(lookup)
    return out[["text", "labels"]]


def compute_metrics(eval_pred):
    logits, gold = eval_pred
    predicted = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy_score(gold, predicted),
        "f1_macro": f1_score(gold, predicted, average="macro", zero_division=0),
    }


def train_model(train_df, val_df, labels, seed, quiet=True):
    set_seed(seed)
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(
        BASE_MODEL,
        num_labels=len(labels),
        id2label={i: l for i, l in enumerate(labels)},
        label2id={l: i for i, l in enumerate(labels)},
    )

    def tokenize(batch):
        return tokenizer(
            batch["text"], truncation=True, padding="max_length", max_length=MAX_LENGTH
        )

    train_ds = Dataset.from_pandas(to_ids(train_df, labels)).map(tokenize, batched=True)
    val_ds = Dataset.from_pandas(to_ids(val_df, labels)).map(tokenize, batched=True)
    args = TrainingArguments(
        output_dir="./takemeter_out",
        num_train_epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        eval_strategy="epoch",
        save_strategy="no",
        logging_steps=10,
        seed=seed,
        report_to="none",
        disable_tqdm=quiet,
        use_cpu=(DEVICE == "cpu"),
    )
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        compute_metrics=compute_metrics,
    )
    trainer.train()
    return trainer, tokenizer


def confidence_report(confidence, gold, predicted):
    right = gold == predicted
    ranked = np.argsort(confidence)
    third = max(1, len(confidence) // 3)
    least, most = ranked[:third], ranked[-third:]
    return {
        "mean_when_right": float(confidence[right].mean()) if right.any() else None,
        "mean_when_wrong": float(confidence[~right].mean()) if (~right).any() else None,
        "accuracy_most_confident_third": float(right[most].mean()),
        "accuracy_least_confident_third": float(right[least].mean()),
        "n_per_third": int(third),
    }


def confusion_counts(gold, predicted, labels):
    matrix = {t: {p: 0 for p in labels} for t in labels}
    for g, p in zip(gold, predicted):
        matrix[labels[int(g)]][labels[int(p)]] += 1
    return matrix


def evaluate(trainer, tokenizer, test_df, labels, seed=None):
    def tokenize(batch):
        return tokenizer(
            batch["text"], truncation=True, padding="max_length", max_length=MAX_LENGTH
        )

    test_ds = Dataset.from_pandas(to_ids(test_df, labels)).map(tokenize, batched=True)
    output = trainer.predict(test_ds)
    predicted = np.argmax(output.predictions, axis=-1)
    gold = np.array(output.label_ids)
    scores = output.predictions
    exp = np.exp(scores - scores.max(axis=-1, keepdims=True))
    confidence = (exp / exp.sum(axis=-1, keepdims=True)).max(axis=-1)
    precision, recall, f1, support = precision_recall_fscore_support(
        gold, predicted, labels=list(range(len(labels))), zero_division=0
    )
    return {
        "seed": seed,
        "n_test": int(len(gold)),
        "accuracy": float(accuracy_score(gold, predicted)),
        "f1_macro": float(f1_score(gold, predicted, average="macro", zero_division=0)),
        "per_label": {
            label: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, label in enumerate(labels)
        },
        "confusion": confusion_counts(gold, predicted, labels),
        "confidence": confidence_report(confidence, gold, predicted),
    }


def stamp(result):
    result["device"] = DEVICE
    result["device_name"] = DEVICE_NAME
    result["torch_version"] = torch.__version__
    result["max_length"] = MAX_LENGTH
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", choices=["once", "before", "after"], default="once")
    parser.add_argument("--epochs", type=int, default=None)
    args = parser.parse_args()
    global EPOCHS
    if args.epochs is not None:
        EPOCHS = args.epochs
    print(f"epochs: {EPOCHS}")

    print(f"device: {DEVICE} ({DEVICE_NAME})")
    print(f"torch: {torch.__version__}")
    df = pd.read_csv(CSV)
    df["label"] = df["label"].astype(str).str.strip()
    unknown = set(df["label"]) - set(LABELS)
    if unknown:
        raise SystemExit(f"Unknown labels: {sorted(unknown)}")

    if args.label == "once":
        train_df, val_df, test_df = split_dataset(df, 42)
        print(f"train {len(train_df)}  val {len(val_df)}  test {len(test_df)}")
        print(pd.DataFrame({
            "train": train_df["label"].value_counts(),
            "val": val_df["label"].value_counts(),
            "test": test_df["label"].value_counts(),
        }).reindex(LABELS).fillna(0).astype(int).to_string())
        trainer, tokenizer = train_model(train_df, val_df, LABELS, 42, quiet=False)
        results = stamp(evaluate(trainer, tokenizer, test_df, LABELS, seed=42))
        Path("results.json").write_text(json.dumps(results, indent=2))
        test_df.to_csv("test_split.csv", index=False)
        print(f"accuracy {results['accuracy']:.3f}  macro F1 {results['f1_macro']:.3f}")
        print("Wrote results.json and test_split.csv")
        return

    all_results = []
    for i, seed in enumerate(SEEDS, 1):
        print(f"\n{'=' * 60}\nSeed {seed}  ({i} of {len(SEEDS)})\n{'=' * 60}")
        tr, va, te = split_dataset(df, seed)
        trainer, tok = train_model(tr, va, LABELS, seed, quiet=True)
        r = stamp(evaluate(trainer, tok, te, LABELS, seed=seed))
        all_results.append(r)
        print(f"  accuracy {r['accuracy']:.3f}   macro F1 {r['f1_macro']:.3f}")
    out = f"results_three_seeds_{args.label}.json"
    Path(out).write_text(json.dumps(all_results, indent=2))
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
