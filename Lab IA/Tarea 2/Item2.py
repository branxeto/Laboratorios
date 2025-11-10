import numpy as np
import pandas as pd
import yaml
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from joblib import Parallel, delayed

# ==========================
# Cargar el dataset
# ==========================
def load_dataset():
    # Cargar el dataset California Housing
    data = fetch_california_housing()
    return data

# ==========================
# Preprocesamiento
# ==========================
def make_preprocessor(df, target, cfg):
    y = df[target]
    X = df.drop(columns=[target])

    num_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in X.columns if c not in num_cols]

    transformers = []

    if num_cols:
        steps_num = [("imputer", SimpleImputer(strategy=cfg["impute_strategy_num"]))]
        if cfg["scale_numeric"]:
            steps_num.append(("scaler", StandardScaler()))
        transformers.append(("num", Pipeline(steps=steps_num), num_cols))

    if cat_cols and cfg["one_hot_encode"]:
        transformers.append(("cat", Pipeline(steps=[
                                 ("imputer", SimpleImputer(strategy=cfg["impute_strategy_cat"])),
                                 ("ohe", OneHotEncoder(handle_unknown="ignore", sparse=False))
                             ]), cat_cols))
    pre = ColumnTransformer(transformers=transformers)
    return X, y, pre

# ==========================
# Construcción del modelo
# ==========================
def build_sgd_classifier(cfg, classes_):
    clf = SGDClassifier(
        loss=cfg["loss"],
        learning_rate=cfg["learning_rate"],
        eta0=cfg["eta0"],
        alpha=cfg.get("alpha", 0.0001),
        penalty=cfg.get("penalty", "l2"),
        random_state=cfg.get("seed", 42),
        early_stopping=False,      
        warm_start=True,
        max_iter=1,                
        tol=None
    )
    clf.partial_fit(np.zeros((1, classes_.shape[0])), classes=classes_)
    return clf

# ==========================
# Función para entrenar por épocas
# ==========================
def train_one_epoch(clf, X_train, y_train, batch_size=256, shuffle=True, classes_=None):
    n = X_train.shape[0]
    idx = np.arange(n)
    if shuffle:
        np.random.shuffle(idx)
    for start in range(0, n, batch_size):
        end = min(start + batch_size, n)
        batch_idx = idx[start:end]
        clf.partial_fit(X_train[batch_idx], y_train[batch_idx], classes=classes_)
    return clf

# ==========================
# Función de evaluación
# ==========================
def score_for_culling(model_type, clf, X, y, scoring="neg_mean_squared_error"):
    if scoring == "neg_mean_squared_error":
        y_pred = clf.predict(X)
        return -mean_squared_error(y, y_pred)
    elif scoring == "r2":
        y_pred = clf.predict(X)
        return r2_score(y, y_pred)
    else:
        return r2_score(y, clf.predict(X))

# ==========================
# Culling y entrenamiento en paralelo
# ==========================
def _train_epoch_job(model_pack, X_train, y_train, batch_size, shuffle, classes_):
    name, clf = model_pack["name"], model_pack["model"]
    clf = train_one_epoch(clf, X_train, y_train, batch_size=batch_size, shuffle=shuffle, classes_=classes_)
    return {"name": name, "model": clf}

def train_with_culling(
    model_type, configs, X_train, y_train, classes_,
    batch_size=256, shuffle=True, max_epochs=50, eval_every=5, scoring="neg_mean_squared_error", n_jobs=-1):
    active = []
    for cfg in configs:
        clf = build_sgd_classifier(cfg, classes_)
        active.append({"name": cfg["name"], "cfg": cfg, "model": clf, "history": []})

    epoch = 0
    while epoch < max_epochs and len(active) > 1:
        results = Parallel(n_jobs=n_jobs)(delayed(_train_epoch_job)(m, X_train, y_train, batch_size, shuffle, classes_) for m in active)
        for i, res in enumerate(results):
            active[i]["model"] = res["model"]
        epoch += 1
        if epoch % eval_every == 0:
            scores = []
            for m in active:
                s = score_for_culling(model_type, m["model"], X_train, y_train, scoring=scoring)
                m["history"].append({"epoch": epoch, "score": s})
                scores.append((m["name"], s))
            worst = min(scores, key=lambda x: x[1])
            active = [m for m in active if m["name"] != worst[0]]
    
    active.sort(key=lambda m: m["history"][-1]["score"], reverse=True)
    return active

# ==========================
# Evaluación final en el conjunto de test
# ==========================
def test_metrics(clf, X_test, y_test):
    y_pred = clf.predict(X_test)
    return {
        "MSE": mean_squared_error(y_test, y_pred),
        "R2": r2_score(y_test, y_pred)
    }

# ==========================
# Orquestador principal
# ==========================
def main():
    # Cargar configuración desde YAML
    with open("configs/experiment.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    # Cargar datos
    data = load_dataset()
    X = data.data
    y = data.target

    # Preprocesar datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    classes_ = np.unique(y_train)

    # Entrenamiento en paralelo y culling para Logística
    best_log = train_with_culling("logistic", cfg["logistic_configs"], X_train, y_train, classes_)

    # Entrenamiento en paralelo y culling para SVM
    best_svm = train_with_culling("svm", cfg["svm_configs"], X_train, y_train, classes_)

    # Evaluación final de los mejores modelos
    top_log = best_log[:2]
    top_svm = best_svm[:2]

    print("\nTop-2 Logistic in Test:")
    for i, m in enumerate(top_log):
        metrics = test_metrics(m["model"], X_test, y_test)
        print(f"{i+1}: {m['name']} - {metrics}")

    print("\nTop-2 SVM in Test:")
    for i, m in enumerate(top_svm):
        metrics = test_metrics(m["model"], X_test, y_test)
        print(f"{i+1}: {m['name']} - {metrics}")

# Ejecutar el experimento
if __name__ == "__main__":
    main()
