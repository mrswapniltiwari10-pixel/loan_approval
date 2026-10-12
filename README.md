# Loanwise: loan approval prediction demo

A small full stack example: Flask serves the web interface and JSON API, and a scikit-learn Random Forest learns from `loan_approval_dataset.csv` when the server starts.

## Run locally

Use Python 3.10 or newer. In this directory, create an environment and install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000. The CSV must stay beside `app.py`; it is included in this project.

## API

- `GET /api/model-info` returns the model name, dataset row count, and held-out validation accuracy.
- `POST /api/predict` accepts JSON with `no_of_dependents`, `education`, `self_employed`, `income_annum`, `loan_amount`, `loan_term`, `cibil_score`, `residential_assets_value`, `commercial_assets_value`, `luxury_assets_value`, and `bank_asset_value`.

Example:

```json
{
  "no_of_dependents": 2,
  "education": "Graduate",
  "self_employed": "No",
  "income_annum": 8000000,
  "loan_amount": 25000000,
  "loan_term": 10,
  "cibil_score": 750,
  "residential_assets_value": 5000000,
  "commercial_assets_value": 2000000,
  "luxury_assets_value": 10000000,
  "bank_asset_value": 4000000
}
```

The response includes the predicted label and the model's approval probability. The model is trained on a random 80% sample and reports accuracy on a held-out 20% sample in `/api/model-info`.

## Important limitation

This is an educational prototype, not a lending system. Its predictions reflect a small historical dataset and can reproduce its biases. The probability is not a calibrated measure of an applicant's real-world chance of approval; do not use it to make or communicate actual credit decisions.
