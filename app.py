"""Loan approval prediction demo: Flask API and a scikit-learn pipeline."""

from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, render_template, request
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "loan_approval_dataset.csv"
NUMERIC_FEATURES = [
    "no_of_dependents",
    "income_annum",
    "loan_amount",
    "loan_term",
    "cibil_score",
    "residential_assets_value",
    "commercial_assets_value",
    "luxury_assets_value",
    "bank_asset_value",
]
CATEGORICAL_FEATURES = ["education", "self_employed"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

app = Flask(__name__)


def train_model():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found at {DATA_PATH}. Place loan_approval_dataset.csv next to app.py."
        )
    data = pd.read_csv(DATA_PATH)
    data.columns = data.columns.str.strip()
    missing = set(FEATURES + ["loan_status"]) - set(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(sorted(missing))}")

    X = data[FEATURES].copy()
    X["education"] = X["education"].astype(str).str.strip()
    X["self_employed"] = X["self_employed"].astype(str).str.strip()
    y = data["loan_status"].astype(str).str.strip().str.title()

    preprocessor = ColumnTransformer(
        [
            ("numbers", "passthrough", NUMERIC_FEATURES),
            ("categories", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )
    pipeline = Pipeline(
        [
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=300,
                    min_samples_leaf=2,
                    class_weight="balanced_subsample",
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    pipeline.fit(X_train, y_train)
    return pipeline, len(data), round(pipeline.score(X_test, y_test) * 100, 1)


model, dataset_rows, validation_accuracy = train_model()


@app.get("/")
def home():
    return render_template("index.html", dataset_rows=dataset_rows)


@app.get("/api/model-info")
def model_info():
    return jsonify(
        {
            "model": "Random Forest classifier",
            "dataset_rows": dataset_rows,
            "validation_accuracy_percent": validation_accuracy,
            "features": FEATURES,
        }
    )


@app.post("/api/predict")
def predict():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Send the borrower details as JSON."}), 400
    try:
        values = {}
        for name in NUMERIC_FEATURES:
            value = float(payload[name])
            if value < 0:
                raise ValueError(f"{name} cannot be negative.")
            values[name] = value
        if values["loan_term"] <= 0:
            raise ValueError("Loan term must be greater than zero.")
        if values["cibil_score"] > 900:
            raise ValueError("CIBIL score must be 900 or less.")
        values["education"] = str(payload["education"]).strip()
        values["self_employed"] = str(payload["self_employed"]).strip()
        if values["education"] not in {"Graduate", "Not Graduate"}:
            raise ValueError("Choose Graduate or Not Graduate.")
        if values["self_employed"] not in {"Yes", "No"}:
            raise ValueError("Choose Yes or No for self-employment.")
    except (KeyError, TypeError, ValueError) as error:
        return jsonify({"error": str(error) or "Check the submitted values."}), 400

    sample = pd.DataFrame([values], columns=FEATURES)
    probabilities = model.predict_proba(sample)[0]
    classes = list(model.classes_)
    approved_probability = float(probabilities[classes.index("Approved")])
    decision = "Approved" if approved_probability >= 0.5 else "Rejected"
    return jsonify(
        {
            "decision": decision,
            "approval_probability": round(approved_probability * 100, 1),
            "model": "Random Forest classifier",
            "disclaimer": "This estimate is based on historical data and is not a lending decision.",
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
