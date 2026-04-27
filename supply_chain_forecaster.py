# ============================================================
#  SUPPLY CHAIN DEMAND FORECASTER
#  Author: [Your Name]
#  Description: Forecasts product demand using ARIMA and a
#               simple moving average. Compares accuracy and
#               exports a full report to Excel.
# ============================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.stattools import adfuller
    STATSMODELS_OK = True
except ImportError:
    STATSMODELS_OK = False
    print("Install statsmodels: pip install statsmodels")

try:
    import openpyxl
    EXCEL_OK = True
except ImportError:
    EXCEL_OK = False
    print("Install openpyxl: pip install openpyxl")


# ============================================================
# CONFIGURATION
# ============================================================

PRODUCT_NAME   = "Product A"
FORECAST_WEEKS = 12          # how many weeks ahead to forecast
ARIMA_ORDER    = (2, 1, 2)   # (p, d, q) — tune if needed
MA_WINDOW      = 4           # moving average window (weeks)
RANDOM_SEED    = 42


# ============================================================
# STEP 1: Generate realistic demand data
# (Replace this with your own CSV if you have real data)
# ============================================================

def generate_demand_data(n_weeks=104):
    """
    Simulates 2 years of weekly demand with:
      - An upward trend
      - Seasonal peaks (e.g. holiday season)
      - Random noise
    """
    np.random.seed(RANDOM_SEED)
    dates = pd.date_range(start="2022-01-03", periods=n_weeks, freq="W")

    trend    = np.linspace(200, 320, n_weeks)
    season   = 40 * np.sin(2 * np.pi * np.arange(n_weeks) / 52)
    noise    = np.random.normal(0, 18, n_weeks)
    demand   = trend + season + noise
    demand   = np.clip(demand, 50, None).round().astype(int)

    df = pd.DataFrame({"date": dates, "demand": demand})
    df.set_index("date", inplace=True)
    print(f"✅ Generated {n_weeks} weeks of demand data for '{PRODUCT_NAME}'")
    return df


# ============================================================
# STEP 2: Train / test split
# ============================================================

def split_data(df, test_weeks=12):
    train = df.iloc[:-test_weeks]
    test  = df.iloc[-test_weeks:]
    print(f"   Train: {len(train)} weeks  |  Test: {len(test)} weeks")
    return train, test


# ============================================================
# STEP 3: Moving Average forecast (simple baseline)
# ============================================================

def moving_average_forecast(train, n_periods):
    last_values = train["demand"].values[-MA_WINDOW:]
    ma_value    = last_values.mean()
    forecast    = np.full(n_periods, ma_value)
    return forecast


# ============================================================
# STEP 4: ARIMA forecast
# ============================================================

def arima_forecast(train, n_periods):
    if not STATSMODELS_OK:
        print("⚠️  statsmodels not available, using MA instead.")
        return moving_average_forecast(train, n_periods)

    model  = ARIMA(train["demand"], order=ARIMA_ORDER)
    fitted = model.fit()
    fc     = fitted.forecast(steps=n_periods)
    return fc.values


# ============================================================
# STEP 5: Evaluate accuracy
# ============================================================

def rmse(actual, predicted):
    return np.sqrt(np.mean((actual - predicted) ** 2))

def mape(actual, predicted):
    return np.mean(np.abs((actual - predicted) / actual)) * 100

def evaluate(test, ma_fc, arima_fc):
    actual = test["demand"].values
    results = {
        "Moving Average": {"RMSE": rmse(actual, ma_fc),   "MAPE": mape(actual, ma_fc)},
        "ARIMA":          {"RMSE": rmse(actual, arima_fc), "MAPE": mape(actual, arima_fc)},
    }
    print("\n📊 Model Accuracy (lower is better):")
    for model, m in results.items():
        print(f"   {model:20s}  RMSE: {m['RMSE']:.1f}   MAPE: {m['MAPE']:.1f}%")
    return results


# ============================================================
# STEP 6: Future forecast (beyond the dataset)
# ============================================================

def future_forecast(df, n_periods):
    if STATSMODELS_OK:
        model  = ARIMA(df["demand"], order=ARIMA_ORDER)
        fitted = model.fit()
        fc     = fitted.forecast(steps=n_periods).values
    else:
        fc = moving_average_forecast(df, n_periods)

    future_dates = pd.date_range(
        start=df.index[-1] + timedelta(weeks=1),
        periods=n_periods, freq="W"
    )
    return pd.Series(fc, index=future_dates)


# ============================================================
# STEP 7: Plot everything
# ============================================================

def plot_results(train, test, ma_fc, arima_fc, future_fc):
    fig = plt.figure(figsize=(14, 9))
    fig.patch.set_facecolor("#0d1117")
    gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, :])   # top row: full forecast
    ax2 = fig.add_subplot(gs[1, 0])   # bottom left: accuracy bar
    ax3 = fig.add_subplot(gs[1, 1])   # bottom right: future demand

    for ax in [ax1, ax2, ax3]:
        ax.set_facecolor("#0d1117")
        ax.tick_params(colors="white")
        ax.grid(color="#1e1e2e", linestyle="--", linewidth=0.5)
        for spine in ax.spines.values():
            spine.set_edgecolor("#333")

    # --- Chart 1: Historical + test forecasts ---
    ax1.plot(train.index, train["demand"], color="#4A90D9", linewidth=1.5, label="Historical demand")
    ax1.plot(test.index,  test["demand"],  color="#AAAAAA", linewidth=1.5, linestyle="--", label="Actual (test)")
    ax1.plot(test.index,  ma_fc,    color="#F5A623", linewidth=2, label=f"Moving Avg (MA{MA_WINDOW})")
    ax1.plot(test.index,  arima_fc, color="#7ED321", linewidth=2, label="ARIMA forecast")
    ax1.axvline(test.index[0], color="#555", linewidth=1, linestyle=":")
    ax1.text(test.index[0], ax1.get_ylim()[1] * 0.95, "  Test period", color="#888", fontsize=9)
    ax1.set_title("Demand Forecast — Model Comparison", color="white", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Units", color="white")
    ax1.legend(fontsize=9, facecolor="#1a1a2e", labelcolor="white", edgecolor="#333")

    # --- Chart 2: RMSE comparison ---
    models = ["Moving Average", "ARIMA"]
    actual = test["demand"].values
    rmses  = [rmse(actual, ma_fc), rmse(actual, arima_fc)]
    colors = ["#F5A623", "#7ED321"]
    bars   = ax2.bar(models, rmses, color=colors, width=0.4, edgecolor="#0d1117")
    for bar, val in zip(bars, rmses):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                 f"{val:.1f}", ha="center", va="bottom", color="white", fontsize=11)
    ax2.set_title("RMSE Comparison", color="white", fontsize=11)
    ax2.set_ylabel("RMSE (lower = better)", color="white")

    # --- Chart 3: Future forecast ---
    last_hist = train["demand"].iloc[-8:]
    ax3.plot(last_hist.index, last_hist.values, color="#4A90D9", linewidth=1.5, label="Historical")
    ax3.plot(future_fc.index, future_fc.values, color="#BD10E0", linewidth=2,
             linestyle="--", marker="o", markersize=4, label=f"{FORECAST_WEEKS}wk Forecast")
    ax3.fill_between(future_fc.index,
                     future_fc.values * 0.88, future_fc.values * 1.12,
                     alpha=0.2, color="#BD10E0", label="±12% CI")
    ax3.set_title(f"Next {FORECAST_WEEKS}-Week Forecast", color="white", fontsize=11)
    ax3.set_ylabel("Units", color="white")
    ax3.legend(fontsize=9, facecolor="#1a1a2e", labelcolor="white", edgecolor="#333")

    plt.suptitle(f"Supply Chain Demand Forecaster — {PRODUCT_NAME}",
                 color="white", fontsize=15, fontweight="bold", y=1.01)

    plt.savefig("demand_forecast.png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.show()
    print("\n💾 Chart saved as demand_forecast.png")


# ============================================================
# STEP 8: Export to Excel
# ============================================================

def export_excel(df, test, ma_fc, arima_fc, future_fc, metrics):
    if not EXCEL_OK:
        print("⚠️  Skipping Excel export.")
        return

    fname = "demand_forecast_report.xlsx"
    with pd.ExcelWriter(fname, engine="openpyxl") as writer:

        # Sheet 1: Model accuracy
        acc = pd.DataFrame({
            "Model":   ["Moving Average", "ARIMA"],
            "RMSE":    [round(metrics["Moving Average"]["RMSE"], 2),
                        round(metrics["ARIMA"]["RMSE"], 2)],
            "MAPE (%)": [round(metrics["Moving Average"]["MAPE"], 2),
                         round(metrics["ARIMA"]["MAPE"], 2)],
        })
        acc.to_excel(writer, sheet_name="Model Accuracy", index=False)

        # Sheet 2: Historical demand
        df.reset_index().rename(columns={"date":"Date","demand":"Units"}).to_excel(
            writer, sheet_name="Historical Data", index=False)

        # Sheet 3: Future forecast
        future_df = pd.DataFrame({
            "Week":        future_fc.index.strftime("%Y-%m-%d"),
            "Forecast":    future_fc.values.round().astype(int),
            "Lower Bound": (future_fc.values * 0.88).round().astype(int),
            "Upper Bound": (future_fc.values * 1.12).round().astype(int),
        })
        future_df.to_excel(writer, sheet_name="Future Forecast", index=False)

        # Sheet 4: Reorder recommendations
        avg_future    = future_fc.values.mean()
        safety_stock  = avg_future * 0.20
        reorder_point = avg_future + safety_stock
        rec = pd.DataFrame({
            "Metric":  ["Avg Weekly Forecast", "Safety Stock (20%)", "Reorder Point", "12-Week Total"],
            "Units":   [round(avg_future), round(safety_stock),
                        round(reorder_point), round(future_fc.values.sum())]
        })
        rec.to_excel(writer, sheet_name="Reorder Recommendations", index=False)

    print(f"📁 Excel report saved as {fname}")


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 55)
    print("   SUPPLY CHAIN DEMAND FORECASTER")
    print("   ARIMA vs Moving Average · Excel Report")
    print("=" * 55)

    df           = generate_demand_data()
    train, test  = split_data(df)

    print("\n🔮 Fitting models...")
    ma_fc    = moving_average_forecast(train, len(test))
    arima_fc = arima_forecast(train, len(test))
    metrics  = evaluate(test, ma_fc, arima_fc)

    print("\n📅 Generating future forecast...")
    future_fc = future_forecast(df, FORECAST_WEEKS)
    print(f"   Next {FORECAST_WEEKS} weeks avg demand: {future_fc.mean():.0f} units/week")

    plot_results(train, test, ma_fc, arima_fc, future_fc)
    export_excel(df, test, ma_fc, arima_fc, future_fc, metrics)

    print("\n✅ All done!")
    print("=" * 55)


if __name__ == "__main__":
    main()
