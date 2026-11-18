from src.training import run_experiment


def test_run_experiment_smoke() -> None:
    run_experiment({"project": {"name": "test"}})
