"""
retrain.py — Self-Healing Retail Pricing Platform
MLOps Retraining Pipeline

Usage:
    python retrain.py                                  # uses data/sales_history.csv
    python retrain.py --new_data my_data.xlsx          # uses custom Excel file
    python retrain.py --new_data data/orders.csv       # uses checkout/order CSV data
    python retrain.py --dry_run                        # runs without overwriting model
"""

import os
import sys
import logging
import argparse
import pickle
import warnings
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

warnings.filterwarnings("ignore")

# =========================
# Logging Setup
# =========================
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_filename = os.path.join(log_dir, f"retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =========================
# Config
# =========================
OLD_DATA_PATH   = "clean_demand_data.csv"
MODEL_PATH      = "pricing_model.pkl"
BACKUP_MODEL    = f"pricing_model_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"

FEATURES = ["Price", "day_of_week", "month"]
TARGET   = "demand"

RF_PARAMS = {
    "n_estimators": 100,
    "max_depth": 10,
    "min_samples_split": 5,
    "random_state": 42,
    "n_jobs": -1
}


# =========================
# Step 1: Load Old Data
# =========================
def load_old_data(path: str) -> pd.DataFrame:
    logger.info(f"Loading old cleaned data from: {path}")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Old data file not found: {path}")
    df = pd.read_csv(path)
    logger.info(f"Old data shape: {df.shape}")
    return df


# =========================
# Step 2: Load & Preprocess New Data
# =========================
def load_and_preprocess_excel(path: str) -> pd.DataFrame:
    logger.info(f"Loading new Excel data from: {path}")
    if not os.path.exists(path):
        raise FileNotFoundError(f"New data file not found: {path}")

    df = pd.read_excel(path, engine="openpyxl")
    logger.info(f"Raw new data shape: {df.shape}")

    # --- Clean ---
    df.dropna(subset=["Quantity", "Price", "InvoiceDate"], inplace=True)
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]

    # --- Parse date ---
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df.dropna(subset=["InvoiceDate"], inplace=True)

    # --- Feature engineering ---
    df["day_of_week"] = df["InvoiceDate"].dt.dayofweek
    df["month"]       = df["InvoiceDate"].dt.month
    df["date"]        = df["InvoiceDate"].dt.date

    # --- Aggregate demand (group by product + date) ---
    # Column named 'demand' to match clean_demand_data.csv schema
    df_demand = (
        df.groupby(["StockCode", "date", "day_of_week", "month"])
        .agg(demand=("Quantity", "sum"), Price=("Price", "mean"))
        .reset_index()
    )

    logger.info(f"Preprocessed new data shape: {df_demand.shape}")
    return df_demand


def load_and_preprocess_csv(path: str) -> pd.DataFrame:
    logger.info(f"Loading new CSV data from: {path}")
    if not os.path.exists(path):
        raise FileNotFoundError(f"New data file not found: {path}")

    df = pd.read_csv(path)
    logger.info(f"Raw new CSV shape: {df.shape}")
    if df.empty:
        logger.warning("New CSV is empty; no new samples will be merged.")
        return pd.DataFrame(columns=["StockCode", "date", "day_of_week", "month", "demand", "Price"])

    # Native store checkout schema: sales_history.csv
    if {"Price", "day_of_week", "month", "demand"}.issubset(df.columns):
        cleaned = df.copy()
        cleaned["Price"] = pd.to_numeric(cleaned["Price"], errors="coerce")
        cleaned["day_of_week"] = pd.to_numeric(cleaned["day_of_week"], errors="coerce")
        cleaned["month"] = pd.to_numeric(cleaned["month"], errors="coerce")
        cleaned["demand"] = pd.to_numeric(cleaned["demand"], errors="coerce")
        cleaned.dropna(subset=["Price", "day_of_week", "month", "demand"], inplace=True)
        cleaned = cleaned[(cleaned["Price"] > 0) & (cleaned["demand"] > 0)]
        return cleaned

    # Order ledger schema: orders.csv
    if {"product_id", "order_date", "quantity_sold", "price_at_sale"}.issubset(df.columns):
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df.dropna(subset=["order_date", "quantity_sold", "price_at_sale"], inplace=True)
        df["day_of_week"] = df["order_date"].dt.dayofweek
        df["month"] = df["order_date"].dt.month
        df["date"] = df["order_date"].dt.date
        df_demand = (
            df.groupby(["product_id", "date", "day_of_week", "month"])
            .agg(demand=("quantity_sold", "sum"), Price=("price_at_sale", "mean"))
            .reset_index()
            .rename(columns={"product_id": "StockCode"})
        )
        df_demand = df_demand[(df_demand["Price"] > 0) & (df_demand["demand"] > 0)]
        return df_demand

    raise ValueError(
        "CSV must use sales_history columns (Price, day_of_week, month, demand) "
        "or orders columns (product_id, order_date, quantity_sold, price_at_sale)."
    )


def load_and_preprocess_new_data(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in [".xlsx", ".xls"]:
        return load_and_preprocess_excel(path)
    if ext == ".csv":
        return load_and_preprocess_csv(path)
    raise ValueError("new_data must be a .csv, .xlsx, or .xls file")


# =========================
# Step 3: Merge Old + New Data
# =========================
def merge_datasets(old_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Merging old and new datasets...")

    # Keep only required columns
    required_cols = FEATURES + [TARGET]

    # Align columns
    for col in required_cols:
        if col not in old_df.columns:
            raise ValueError(f"Column '{col}' missing from old data.")
        if col not in new_df.columns:
            raise ValueError(f"Column '{col}' missing from new data. Available: {list(new_df.columns)}")

    old_subset = old_df[required_cols].copy()
    new_subset = new_df[required_cols].copy()

    merged = pd.concat([old_subset, new_subset], ignore_index=True)

    # Final cleaning pass
    merged.dropna(inplace=True)
    merged = merged[merged[TARGET] > 0]
    merged = merged[merged["Price"] > 0]

    logger.info(f"Merged dataset shape: {merged.shape}")
    return merged


# =========================
# Step 4: Train Model
# =========================
def train_model(df: pd.DataFrame):
    logger.info("Training Random Forest model...")

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestRegressor(**RF_PARAMS)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)

    logger.info(f"Model Evaluation — MAE: {mae:.4f} | R²: {r2:.4f}")

    return model, mae, r2, X_test, y_test


def evaluate_existing_model(X_test: pd.DataFrame, y_test: pd.Series):
    if not os.path.exists(MODEL_PATH):
        logger.info("No existing model found; new model will be saved.")
        return None, None
    with open(MODEL_PATH, "rb") as f:
        old_model = pickle.load(f)
    y_pred = old_model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    logger.info(f"Existing Model Evaluation — MAE: {mae:.4f} | R²: {r2:.4f}")
    return mae, r2


# =========================
# Step 5: Save Model
# =========================
def save_model(model, path: str, dry_run: bool = False):
    if dry_run:
        logger.info(f"[DRY RUN] Model NOT saved. Would have saved to: {path}")
        return

    # Backup old model if it exists
    if os.path.exists(path):
        import shutil
        shutil.copy(path, BACKUP_MODEL)
        logger.info(f"Old model backed up to: {BACKUP_MODEL}")

    with open(path, "wb") as f:
        pickle.dump(model, f)

    logger.info(f"New model saved to: {path}")


# =========================
# Main Pipeline
# =========================
def run_pipeline(new_data_path: str, dry_run: bool = False):
    logger.info("=" * 55)
    logger.info("  Self-Healing Retail Pricing Platform — Retraining")
    logger.info("=" * 55)
    start_time = datetime.now()

    try:
        # 1. Load old data
        old_df = load_old_data(OLD_DATA_PATH)

        # 2. Load & preprocess new data
        new_df = load_and_preprocess_new_data(new_data_path)

        # 3. Merge
        merged_df = merge_datasets(old_df, new_df)

        # 4. Train
        model, mae, r2, X_test, y_test = train_model(merged_df)

        old_mae, old_r2 = evaluate_existing_model(X_test, y_test)
        should_save = old_mae is None or mae <= old_mae or r2 >= old_r2
        if not should_save:
            logger.warning(
                "New model did not beat existing model; keeping existing model. "
                f"old_mae={old_mae:.4f}, new_mae={mae:.4f}, old_r2={old_r2:.4f}, new_r2={r2:.4f}"
            )
            dry_run = True

        # 5. Save
        save_model(model, MODEL_PATH, dry_run=dry_run)

        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Pipeline completed in {elapsed:.1f}s | MAE={mae:.4f} | R²={r2:.4f}")
        logger.info(f"Log saved to: {log_filename}")
        logger.info("=" * 55)

        return {
            "status": "success",
            "mae": mae,
            "r2": r2,
            "old_mae": old_mae,
            "old_r2": old_r2,
            "model_saved": should_save and not dry_run,
            "elapsed_seconds": elapsed
        }

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return {"status": "failed", "error": str(e)}


# =========================
# CLI Entry Point
# =========================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrain the pricing model with new data.")
    parser.add_argument(
        "--new_data",
        type=str,
        default="data/sales_history.csv",
        help="Path to new CSV/Excel data file (default: data/sales_history.csv)"
    )
    parser.add_argument(
        "--dry_run",
        action="store_true",
        help="Run pipeline without overwriting the model file"
    )

    args = parser.parse_args()
    result = run_pipeline(new_data_path=args.new_data, dry_run=args.dry_run)
    sys.exit(0 if result["status"] == "success" else 1)
