from __future__ import annotations

import os

from src.ml_infer import MODEL_PATH, predict_priority, train_from_csv


def test_real_train_and_predict(tmp_path):
    csv = tmp_path / "tasks.csv"
    csv.write_text(
        "task_description,priority\n"
        '"Fix login bug on website",high\n'
        '"Update documentation",low\n'
        '"Write unit tests",high\n'
        '"Clean temp files",low\n',
        encoding="utf-8",
    )

    model, acc = train_from_csv(str(csv))
    assert os.path.exists(str(MODEL_PATH))
    assert 0.0 <= acc <= 1.0

    label, prob = predict_priority("Fix login bug on website")
    assert label in {"high", "low"}
    assert 0.0 <= prob <= 1.0
