# ml_bench.py
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from benchHUB.utils.timing import timing_decorator

def ml_benchmark(config: dict):
    """
    Run the complete ML benchmark pipeline using parameters from a configuration dictionary.
    Returns a dictionary with timing results and model accuracy.
    """
    timing_results = {}

    @timing_decorator(timings=timing_results)
    def create_dataset(n_samples, n_features):
        X, y = make_classification(n_samples=n_samples, n_features=n_features, n_classes=2, random_state=42)
        return train_test_split(X, y, test_size=0.2, random_state=42)

    @timing_decorator(timings=timing_results)
    def train_random_forest(X_train, y_train):
        clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        clf.fit(X_train, y_train)
        return clf

    n_samples = config.get("ML_N_SAMPLES", 10000)
    n_features = config.get("ML_N_FEATURES", 20)
    n_runs = config.get("N_RUNS", 1)

    create_dataset.n_runs = n_runs
    train_random_forest.n_runs = n_runs

    print("Creating dataset...")
    X_train, X_test, y_train, y_test = create_dataset(n_samples=n_samples, n_features=n_features)

    print("Training RandomForest model...")
    model = train_random_forest(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Add accuracy to the results, but keep timings separate
    results = timing_results.copy()
    results['model_accuracy'] = accuracy
    
    return results