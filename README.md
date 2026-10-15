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

## Deploy a live version

This app includes both the frontend and Flask API, so deploy it as a web service rather than GitHub Pages. To publish with automatic deploys from GitHub:

1. Push this project to a GitHub repository. Include `app.py`, `requirements.txt`, `render.yaml`, the `static/` and `templates/` folders, and `loan_approval_dataset.csv`.
2. In Render, create a new **Web Service**, connect the GitHub repository, and deploy the `main` branch. Render reads `render.yaml` to install the dependencies and run the app with Gunicorn.
3. When the first deploy succeeds, Render provides a public `onrender.com` URL. Later pushes to the connected branch deploy automatically.

The free web service can sleep after inactivity, so the first request after a quiet period may take longer while it starts. The model is trained during startup, which also adds to startup time.

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
