from __future__ import annotations


def test_train_task_runs(monkeypatch):
    import src.workers.tasks.task_train_model as tmod
    from src.ml_infer import MODEL_PATH

    def fake_train(path: str):
        return str(MODEL_PATH), 1.0

    monkeypatch.setattr(tmod, "train_from_csv", fake_train)
    res = tmod.train_model_from_csv.run("/x.csv")
    assert isinstance(res, dict)
    assert "model_path" in res and "train_acc" in res
    assert res["model_path"].endswith(str(MODEL_PATH).split("/")[-1])
    assert float(res["train_acc"]) == 1.0
