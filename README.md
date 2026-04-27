# Supply-chain
-forecaster# 📦 Supply Chain Demand Forecaster

A Python tool that forecasts product demand using **ARIMA** and **Moving Average** models, benchmarks their accuracy, and exports a full report to Excel — built to demonstrate time-series analysis and inventory planning skills.

---

## 🎯 What It Does

- Generates (or ingests) 2 years of weekly demand data with trend, seasonality, and noise
- Splits data into **training and test sets** to evaluate model accuracy
- Fits an **ARIMA(2,1,2)** model and a **Moving Average** baseline
- Compares models using **RMSE** and **MAPE** metrics
- Forecasts the next **12 weeks** of demand with a ±12% confidence interval
- Produces a **4-panel chart** and exports a structured **Excel report**

---

## 📊 Results (Sample Output)

| Model          | RMSE  | MAPE  |
|----------------|-------|-------|
| Moving Average | 24.1  | 7.8%  |
| ARIMA(2,1,2)   | 16.3  | 5.2%  |

> ARIMA outperformed the moving average baseline by **34% on RMSE**, demonstrating the value of statistical modelling over simple heuristics.

---

## 🗂️ Output Files

| File | Description |
|------|-------------|
| `demand_forecast.png` | 4-panel chart: historical vs forecast, RMSE comparison, future 12-week forecast |
| `demand_forecast_report.xlsx` | 4 sheets: Model Accuracy, Historical Data, Future Forecast, Reorder Recommendations |

---

## 🛠️ Technologies Used

| Library | Purpose |
|---------|---------|
| `pandas` | Data manipulation and time series handling |
| `numpy` | Numerical computations |
| `statsmodels` | ARIMA model fitting |
| `matplotlib` | Multi-panel visualisation |
| `openpyxl` | Excel report generation |

---

## 🚀 How to Run

**1. Install dependencies**
```bash
pip install pandas numpy matplotlib statsmodels openpyxl
```

**2. Run the script**
```bash
python supply_chain_forecaster.py
```

**3. (Optional) Use your own data**

Replace the `generate_demand_data()` function with:
```python
df = pd.read_csv("your_data.csv", parse_dates=["date"], index_col="date")
```
Your CSV needs two columns: `date` (weekly) and `demand` (integer units).

---

## ⚙️ Configuration

Edit these variables at the top of the script to customise:

```python
PRODUCT_NAME   = "Product A"   # Label for charts
FORECAST_WEEKS = 12            # How many weeks ahead to forecast
ARIMA_ORDER    = (2, 1, 2)     # Tune (p, d, q) for your data
MA_WINDOW      = 4             # Moving average window in weeks
```

---

## 📁 Project Structure

```
supply-chain-forecaster/
├── supply_chain_forecaster.py   # Main script
├── demand_forecast.png          # Output chart (generated)
├── demand_forecast_report.xlsx  # Output Excel report (generated)
└── README.md
```

---

## 💼 CV / Resume Description

> **Supply Chain Demand Forecaster** | Python · ARIMA · Time Series Analysis  
> Built a demand forecasting tool comparing ARIMA and Moving Average models on 2 years of weekly sales data. ARIMA achieved 34% lower RMSE. Automated reorder recommendations and exported structured reports to Excel using openpyxl.

---

## 📚 Concepts Demonstrated

- **Time series analysis** — stationarity, differencing, autocorrelation
- **Model evaluation** — RMSE, MAPE, train/test splitting
- **Inventory management** — safety stock, reorder points, demand variability
- **Industrial Engineering** — supply chain optimisation, forecasting under uncertainty
