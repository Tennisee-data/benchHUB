# ml_bench.py
import time
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV

from benchHUB.utils.timing import timing_decorator

# Timing storage
timing_results = {}

@timing_decorator(n_runs=3, use_median=True, timings=timing_results)
def create_dataset(n_samples=10000, n_features=20, n_classes=2, test_size=0.2):
    """
    Create a synthetic classification dataset and split it into train/test.
    """
    X, y = make_classification(n_samples=n_samples, n_features=n_features, n_classes=n_classes)
    return train_test_split(X, y, test_size=test_size)

@timing_decorator(n_runs=3, use_median=True, timings=timing_results)
def run_grid_search(X_train, y_train):
    """
    Perform a grid search on a RandomForestClassifier with cross-validation.
    """
    param_grid = {
        'n_estimators': [10, 50, 100],
        'max_depth': [None, 10, 20]
    }
    clf = GridSearchCV(RandomForestClassifier(), param_grid, cv=3)
    clf.fit(X_train, y_train)
    return clf

def ml_benchmark():
    """
    Run the complete ML benchmark pipeline, timing the grid search step.
    Returns a dictionary with timing results and grid search details.
    """
    print("Creating dataset...")
    X_train, X_test, y_train, y_test = create_dataset()

    print("Running grid search...")
    clf = run_grid_search(X_train, y_train)

    return {
        'timings': dict(timing_results),  # ou timing_results directement
        'best_params': clf.best_params_,
        'best_score': clf.best_score_
    }


if __name__ == "__main__":
    results = ml_benchmark()
    print("\nML Benchmark Results:")
    print(results)
