# ml_bench.py
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from benchHUB.utils.timing import timing_decorator

# Timing storage
timing_results = {}

@timing_decorator(n_runs=1, use_median=True, timings=timing_results)
def create_dataset(n_samples=10000, n_features=20, n_classes=2, test_size=0.2):
    """
    Create a synthetic classification dataset and split it into train/test.
    """
    X, y = make_classification(n_samples=n_samples, n_features=n_features, n_classes=n_classes, random_state=42)
    return train_test_split(X, y, test_size=test_size, random_state=42)

@timing_decorator(n_runs=1, use_median=True, timings=timing_results)
def train_random_forest(X_train, y_train):
    """
    Train a RandomForestClassifier with fixed parameters.
    """
    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf.fit(X_train, y_train)
    return clf

def ml_benchmark(config: dict):
    """
    Run the complete ML benchmark pipeline using parameters from a configuration dictionary.
    Returns a dictionary with timing results and model accuracy.
    """
    n_samples = config.get("ML_N_SAMPLES", 10000)
    n_features = config.get("ML_N_FEATURES", 20)
    n_runs = config.get("N_RUNS", 1)

    # Update decorator runs
    create_dataset.n_runs = n_runs
    train_random_forest.n_runs = n_runs

    print("Creating dataset...")
    X_train, X_test, y_train, y_test = create_dataset(n_samples=n_samples, n_features=n_features)

    print("Training RandomForest model...")
    model = train_random_forest(X_train, y_train)

    # Evaluate model accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    return {
        'timings': dict(timing_results),
        'model_accuracy': accuracy
    }

if __name__ == "__main__":
    results = ml_benchmark()
    print("\nML Benchmark Results:")
    print(results)
