# Self-Healing Retail Pricing Platform

> AI-powered demand prediction and revenue-maximising price optimisation using Random Forest.

---

## Overview

This system predicts product demand and recommends the optimal selling price to maximise revenue.
It uses a machine learning model trained on historical retail transaction data (UCI Online Retail II dataset).

**System Flow:**
```
User → Streamlit UI → Flask REST API → ML Model → Price Recommendation
                                                 ↓
                               GitHub Push → Jenkins → retrain.py → Updated Model
```

---

## Tech Stack

| Layer       | Technology                        |
|-------------|-----------------------------------|
| ML Model    | Scikit-learn (Random Forest)      |
| Backend     | Flask (REST API)                  |
| Frontend    | Streamlit                         |
| Data        | Pandas, NumPy                     |
| MLOps       | retrain.py pipeline + Jenkins CI  |

---

## Project Structure

```
SPE_MP/
├── app.py                  # Flask REST API
├── streamlit_app.py        # Streamlit frontend
├── retrain.py              # MLOps retraining pipeline
├── test_api.py             # API smoke-test script
├── requirements.txt        # Python dependencies
├── pricing_model.pkl       # Trained Random Forest model (not in git)
├── clean_demand_data.csv   # Preprocessed training data (not in git)
├── online_retail_II.xlsx   # Raw dataset (not in git)
├── logs/                   # Auto-created by retrain.py
└── SPE_Major_1_4.ipynb     # EDA + model training notebook (Colab)
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate the model
Run all cells in `SPE_Major_1_4.ipynb` (Google Colab) to produce:
- `pricing_model.pkl`
- `clean_demand_data.csv`

### 3. Start the Flask API
```bash
python app.py
```
API runs on `http://localhost:5000`

### 4. Start the Streamlit UI (new terminal)
```bash
streamlit run streamlit_app.py
```
UI opens at `http://localhost:8501`

### 5. Run API smoke tests (optional)
```bash
python test_api.py
```
Runs 6 test groups covering all endpoints and edge cases.

---

## API Endpoints

### `GET /health`
Health check — returns model status.

```json
{ "status": "ok", "model_loaded": true, "model_path": "pricing_model.pkl" }
```

---

### `POST /optimize`
Optimise price for maximum revenue.

**Request:**
```json
{
  "price": 100.0,
  "day": 2,
  "month": 5,
  "stock": 50,
  "competitor_price": 95.0
}
```
> `stock` and `competitor_price` are optional.

**Response:**
```json
{
  "current_price": 100.0,
  "current_demand": 42.0,
  "current_revenue": 4200.0,
  "best_price": 112.5,
  "best_demand": 40.0,
  "best_revenue": 4500.0,
  "improvement_%": 7.14,
  "decision": "Apply Optimized Price",
  "competitor_price": 95.0
}
```

**Decision Logic (A/B):**
| Condition | Decision |
|-----------|----------|
| Revenue improves > 5% | Apply Optimized Price |
| Best price > competitor × 1.1 | Consider Competitive Pricing |
| Otherwise | Keep Current Price |

---

### `POST /trigger_retrain`
Trigger model retraining in the background (used by Jenkins after a GitHub push).
Flask runs `retrain.py` as a subprocess, then hot-reloads the updated model automatically.

```bash
curl -X POST http://localhost:5000/trigger_retrain \
     -H "Content-Type: application/json" \
     -d '{"new_data": "online_retail_II.xlsx"}'
```

**Response (202 Accepted):**
```json
{ "status": "accepted", "message": "Retraining started in background.", "new_data": "online_retail_II.xlsx" }
```

| HTTP Code | Meaning |
|-----------|---------|
| 202 | Retraining started |
| 409 | Already running |
| 401 | Bad token |

---

### `GET /retrain_status`
Check if retraining is in progress and what the last run result was.

```json
{ "running": false, "last_status": "success", "last_log": "..." }
```

---

### `POST /reload_model`
Hot-reload the model from disk after retraining (no restart needed).

```bash
curl -X POST http://localhost:5000/reload_model \
     -H "X-Reload-Token: your_secret_token"
```

Set `RELOAD_TOKEN` environment variable to enable token protection.

---

## MLOps — Retraining

The `retrain.py` pipeline:
1. Loads old cleaned data (`clean_demand_data.csv`)
2. Loads a new Excel file, applies the same preprocessing
3. Merges both datasets
4. Retrains the Random Forest model
5. Backs up old `pricing_model.pkl` and overwrites it
6. Logs all metrics to `logs/retrain_<timestamp>.log`

```bash
# Retrain using default file
python retrain.py

# Use a custom new-data file
python retrain.py --new_data new_sales_data.xlsx

# Dry run (no model overwrite)
python retrain.py --dry_run
```

---

## Notes

- The `.pkl`, `.xlsx`, and `.csv` files are excluded from git due to size (see `.gitignore`).
- Jenkins CI/CD triggers `retrain.py` automatically on GitHub push (Ubuntu server setup).
- Drift detection is a planned future improvement.
