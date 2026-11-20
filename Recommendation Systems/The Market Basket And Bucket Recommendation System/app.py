"""
app.py
======
Flask application entry point.

Route overview:
  GET  /            → Render the main dashboard
  POST /            → Handle item search or user lookup (same page)
  POST /upload      → Replace the active CSV dataset
  GET  /download_report → Generate and download a plain-text report
"""

import io
import os
import uuid
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, Response
from werkzeug.utils import secure_filename

from model.apriori_model           import AprioriModel
from model.collaborative_filtering import CollaborativeFiltering

# ── App setup ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(32)

UPLOAD_FOLDER = "data"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit

DATA_PATH = os.path.join(UPLOAD_FOLDER, "default.csv")

apriori_model = AprioriModel(DATA_PATH)
cf_model      = CollaborativeFiltering(DATA_PATH)


# ── Utility functions ──────────────────────────────────────────────────────────

def get_item_frequency(path: str, top_n: int = 15) -> tuple:
    try:
        df  = pd.read_csv(path)
        col = {c.lower(): c for c in df.columns}.get("items", df.columns[0])
        flat = [
            i.strip()
            for sublist in df[col].apply(lambda x: str(x).split(","))
            for i in sublist
            if i.strip() and i.strip().lower() != "nan"
        ]
        counts = pd.Series(flat).value_counts().head(top_n)
        return counts.index.tolist(), [int(v) for v in counts.values]
    except Exception:
        return [], []


def get_low_performers(path: str, limit: int = 5) -> list:
    try:
        df  = pd.read_csv(path)
        col = {c.lower(): c for c in df.columns}.get("items", df.columns[0])
        flat = [
            i.strip()
            for sublist in df[col].apply(lambda x: str(x).split(","))
            for i in sublist
            if i.strip() and i.strip().lower() != "nan"
        ]
        return pd.Series(flat).value_counts(ascending=True).head(limit).index.tolist()
    except Exception:
        return []


def get_summary_stats(path: str) -> dict:
    try:
        df      = pd.read_csv(path)
        col_map = {c.lower(): c for c in df.columns}
        items_col = col_map.get("items", df.columns[0])
        user_col  = col_map.get("userid") or col_map.get("user_id") or col_map.get("user")

        total_tx  = len(df)
        total_usr = df[user_col].nunique() if user_col and user_col in df.columns else df.iloc[:, 0].nunique()
        baskets   = df[items_col].apply(
            lambda value: [item.strip() for item in str(value).split(",")
                           if item.strip() and item.strip().lower() != "nan"]
        )
        avg_size  = round(baskets.apply(len).mean(), 1)

        return {
            "db_name":      os.path.basename(path),
            "total_tx":     total_tx,
            "total_users":  total_usr,
            "avg_basket":   avg_size,
        }
    except Exception:
        return {"db_name": "Error", "total_tx": 0, "total_users": 0, "avg_basket": 0}


def get_user_purchase_history(user_id: str, path: str) -> list:
    """Return the ordered list of all items bought by a user (flat, deduplicated)."""
    try:
        df      = pd.read_csv(path)
        col_map = {c.lower(): c for c in df.columns}
        items_col = col_map.get("items", df.columns[0])
        user_col  = col_map.get("userid") or col_map.get("user_id") or col_map.get("user")
        tx_col    = col_map.get("transactionid") or col_map.get("transaction_id") or col_map.get("txid")

        if not user_col:
            return []

        # Try int and str matching
        uid = user_id
        try:
            uid_int = int(user_id)
            if uid_int in df[user_col].values:
                uid = uid_int
        except (ValueError, TypeError):
            pass

        user_df = df[df[user_col] == uid]
        if user_df.empty:
            return []

        if tx_col:
            user_df = user_df.sort_values(tx_col)

        flat = []
        seen = set()
        for items_str in user_df[items_col]:
            for item in str(items_str).split(","):
                item = item.strip()
                if item and item.lower() != "nan" and item not in seen:
                    seen.add(item)
                    flat.append(item)
        return flat
    except Exception as e:
        print(f"[history] {e}")
        return []


def get_user_purchase_stats(user_id: str, cf) -> dict:
    empty = {"items_bought": 0, "total_items": 0, "coverage_pct": 0,
             "avg_items": 0, "percentile": 0}

    if cf.user_item_matrix is None:
        return empty

    matrix = cf.user_item_matrix
    uid = None
    if user_id in matrix.index:
        uid = user_id
    else:
        try:
            if int(user_id) in matrix.index:
                uid = int(user_id)
        except (ValueError, TypeError):
            pass

    total_items = len(matrix.columns)

    if uid is None:
        return {**empty, "total_items": total_items}

    per_user_counts = matrix.sum(axis=1)
    items_bought    = int(per_user_counts[uid])
    avg_items       = round(per_user_counts.mean(), 1)
    coverage_pct    = round((items_bought / total_items) * 100, 1) if total_items > 0 else 0
    percentile      = round((per_user_counts < items_bought).sum() / len(per_user_counts) * 100)

    return {
        "items_bought": items_bought,
        "total_items":  total_items,
        "coverage_pct": coverage_pct,
        "avg_items":    avg_items,
        "percentile":   percentile,
    }


def build_user_profile(user_id: str, cf) -> dict:
    recs   = cf.recommend_for_user(user_id)
    is_new = not recs

    if is_new:
        recs = cf.get_popular_items()

    stats        = get_user_purchase_stats(user_id, cf)
    items_bought = stats["items_bought"]
    avg_items    = stats["avg_items"]
    percentile   = stats["percentile"]
    loyalty      = stats["coverage_pct"]

    if is_new or items_bought == 0:
        status = "New / Inactive"
    elif percentile >= 75:
        status = "Elite Buyer"
    elif percentile >= 40:
        status = "Regular Buyer"
    else:
        status = "Occasional Buyer"

    if is_new or items_bought == 0:
        churn_risk = "High"
    elif items_bought >= avg_items * 0.8:
        churn_risk = "Low"
    elif items_bought >= avg_items * 0.4:
        churn_risk = "Medium"
    else:
        churn_risk = "High"

    return {
        "recommendations": recs,
        "is_new_user":     is_new,
        "status":          status,
        "churn_risk":      churn_risk,
        "loyalty_score":   loyalty,
        "items_bought":    items_bought,
        "total_items":     stats["total_items"],
        "avg_items":       avg_items,
        "percentile":      percentile,
    }


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/upload", methods=["POST"])
def upload():
    global apriori_model, cf_model, DATA_PATH

    file = request.files.get("csv_file")
    if not file or not file.filename:
        return Response("Please choose a CSV file.", status=400, mimetype="text/plain")

    filename = secure_filename(file.filename)
    if not filename or not filename.lower().endswith(".csv"):
        return Response("Only CSV files are allowed.", status=400, mimetype="text/plain")

    try:
        file_bytes = file.read()
        if not file_bytes:
            return Response("The uploaded CSV is empty.", status=400, mimetype="text/plain")

        preview = pd.read_csv(io.BytesIO(file_bytes))
        # Normalize header whitespace so the model classes see the same schema
        # that the upload validator checks.
        preview.columns = [str(column).strip() for column in preview.columns]
        column_map = {column.lower(): column for column in preview.columns}
        items_column = column_map.get("items")
        user_column = column_map.get("userid") or column_map.get("user_id") or column_map.get("user")
        if not items_column or not user_column:
            return Response(
                "CSV must contain Items and UserID columns.",
                status=400,
                mimetype="text/plain",
            )

        preview[items_column] = preview[items_column].fillna("").astype(str).str.strip()
        preview[user_column] = preview[user_column].fillna("").astype(str).str.strip()
        usable_rows = preview[items_column].ne("") & preview[user_column].ne("")
        preview = preview.loc[usable_rows].copy()
        if preview.empty:
            return Response(
                "CSV must contain at least one row with both a UserID and Items value.",
                status=400,
                mimetype="text/plain",
            )

        unique_name = f"upload_{uuid.uuid4().hex}_{filename}"
        new_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
        # Save the normalized dataframe, not the original bytes, so header
        # cleanup and row validation are reflected in the active dataset.
        preview.to_csv(new_path, index=False)

        try:
            # Build both models before switching the active dataset.
            new_apriori_model = AprioriModel(new_path)
            new_cf_model = CollaborativeFiltering(new_path)
            if (
                new_cf_model.user_item_matrix is None
                or not new_cf_model.all_items
                or not new_apriori_model.all_items
            ):
                os.remove(new_path)
                return Response(
                    "Could not build recommendations from this dataset. Check Items and UserID values.",
                    status=400,
                    mimetype="text/plain",
                )
        except Exception:
            if os.path.exists(new_path):
                os.remove(new_path)
            raise

        DATA_PATH = new_path
        apriori_model = new_apriori_model
        cf_model = new_cf_model
        return redirect(url_for("index"))

    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError, ValueError, OSError) as error:
        return Response(
            f"Could not process uploaded CSV: {error}",
            status=400,
            mimetype="text/plain",
        )


@app.route("/", methods=["GET", "POST"])
def index():
    user_id = request.form.get("user_id", "Guest").strip() or "Guest"
    item    = request.form.get("item", "").strip()

    item_recs = apriori_model.recommend(item) if item else []
    profile   = build_user_profile(user_id, cf_model)

    stats          = get_summary_stats(DATA_PATH)
    low_performers = get_low_performers(DATA_PATH)
    items, counts  = get_item_frequency(DATA_PATH)
    chart          = apriori_model.get_top_rules_chart_data()

    # ── Next-purchase prediction ───────────────────────────────────────────────
    purchase_history  = get_user_purchase_history(user_id, DATA_PATH)
    next_predictions  = apriori_model.predict_next(purchase_history, top_n=5)

    return render_template(
        "index.html",
        # User
        user_id               = user_id,
        user_recommendations  = profile["recommendations"],
        user_behavior         = profile,
        # Next-buy prediction
        purchase_history      = purchase_history,
        next_predictions      = next_predictions,
        # Product search
        item                  = item,
        item_recommendations  = item_recs,
        # Bundles & chart
        bundles               = apriori_model.get_bundles(),
        chart_labels          = chart["labels"],
        chart_confidence      = chart["confidence"],
        chart_lift            = chart["lift"],
        # Item frequency chart
        items  = items,
        counts = counts,
        # KPIs
        active_db_name        = stats["db_name"],
        total_transactions    = stats["total_tx"],
        total_users           = stats["total_users"],
        avg_basket_size       = stats["avg_basket"],
        low_performers        = low_performers,
        total_active_rules    = len(apriori_model.rules),
        total_tracked_items   = len(cf_model.all_items),
    )


@app.route("/download_report")
def download_report():
    user_id = request.args.get("user_id", "Guest")
    stats   = get_summary_stats(DATA_PATH)
    profile = build_user_profile(user_id, cf_model)
    bundles = apriori_model.get_bundles(5)

    # Next predictions for report
    history      = get_user_purchase_history(user_id, DATA_PATH)
    predictions  = apriori_model.predict_next(history, top_n=5)
    pred_lines   = "\n".join(
        f"  {p['item']:<20} {p['pct']}%  [{p['source']}]"
        for p in predictions
    ) or "  Not enough purchase history to predict."

    bundle_lines = "\n".join(
        f"  Bundle {i}: {' + '.join(b)}"
        for i, b in enumerate(bundles, 1)
    ) or "  No bundles detected."

    report = f"""
==============================================================
      MARKET BASKET & BUNDLING ENGINE — EXECUTIVE REPORT
==============================================================
Generated : {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
Dataset   : {stats['db_name']}
User      : #{user_id}

[PART 1 — MARKET OVERVIEW]
--------------------------------------------------------------
Total Transactions  : {stats['total_tx']}
Unique Users        : {stats['total_users']}
Avg. Basket Size    : {stats['avg_basket']}
Unique Products     : {len(cf_model.all_items)}

[PART 2 — INVENTORY ALERTS]
--------------------------------------------------------------
Low-Performing Items:
  {', '.join(get_low_performers(DATA_PATH)) or 'None detected.'}

[PART 3 — ASSOCIATION & BUNDLING]
--------------------------------------------------------------
Association Rules Found : {len(apriori_model.rules)}
Top Product Bundles:
{bundle_lines}

[PART 4 — USER BEHAVIOUR]
--------------------------------------------------------------
User ID              : {user_id}
Engagement Rank      : {profile['status']}
Churn Risk           : {profile['churn_risk']}
Items Purchased      : {profile['items_bought']} of {profile['total_items']} catalogue items
Catalogue Coverage   : {profile['loyalty_score']}%
Buyer Percentile     : Top {100 - profile['percentile']}% (buys more than {profile['percentile']}% of users)
Avg. User Buys       : {profile['avg_items']} items
Recommended Items    : {', '.join(profile['recommendations']) or 'No history found.'}

[PART 5 — NEXT PURCHASE PREDICTIONS]
--------------------------------------------------------------
{'Item':<20} {'Probability':<12} Source
{'─'*50}
{pred_lines}

==============================================================
                       END OF REPORT
==============================================================
"""

    safe_user_id = secure_filename(str(user_id)) or "user"
    return Response(
        report,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename=Report_{safe_user_id}.txt"},
    )


if __name__ == "__main__":
    app.run(debug=False)
