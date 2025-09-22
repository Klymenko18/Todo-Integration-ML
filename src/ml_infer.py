from __future__ import annotations

import argparse
import os
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

MODEL_DIR = Path(os.getenv("MODEL_DIR", "/app/run"))
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "task_priority_model.joblib"


def build_pipeline() -> Pipeline:
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )


def train_from_csv(csv_path: str) -> tuple[Pipeline, float]:
    df = pd.read_csv(csv_path)
    if "task_description" not in df.columns or "priority" not in df.columns:
        raise ValueError("CSV must contain columns: task_description, priority")

    X = df["task_description"].astype(str).tolist()
    y = df["priority"].astype(str).tolist()

    pipe = build_pipeline()
    pipe.fit(X, y)

    acc = float(pipe.score(X, y))

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)

    return pipe, acc


_model: Pipeline | None = None


def _load_model() -> Pipeline:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}. Train it first: "
            f'python -m src.ml_infer --train "/app/data/tasks.csv"'
        )
    return joblib.load(MODEL_PATH)


def get_model() -> Pipeline:
    global _model
    if _model is None:
        _model = _load_model()
    return _model


def predict_priority(text: str) -> tuple[str, float]:
    model = get_model()
    proba = model.predict_proba([text])[0]
    classes = list(model.classes_)
    if "high" not in classes or "low" not in classes:
        label = model.predict([text])[0]
        return str(label), 0.0
    idx_high = classes.index("high")
    return ("high" if proba[idx_high] >= 0.5 else "low", float(proba[idx_high]))


def main():
    parser = argparse.ArgumentParser(description="Train or test simple task-priority model")
    parser.add_argument(
        "--train", type=str, help="Path to CSV file with columns: task_description, priority"
    )
    parser.add_argument("--predict", type=str, help="One-off prediction text")
    args = parser.parse_args()

    if args.train:
        _, acc = train_from_csv(args.train)
        print(f"Model trained and saved to {MODEL_PATH}. Train accuracy: {acc:.3f}")
    elif args.predict:
        label, prob = predict_priority(args.predict)
        print(f"Predicted: {label} (P(high)={prob:.3f})")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
