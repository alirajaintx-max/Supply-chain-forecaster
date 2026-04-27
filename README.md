Supply Chain Demand Forecaster
A Python tool that forecasts product demand using ARIMA and Moving Average models and exports a full report to Excel.
What it does

Loads 2 years of weekly demand data with trend and seasonality
Splits data into training and test sets to evaluate model accuracy
Fits an ARIMA model and a Moving Average baseline
Compares models using RMSE and MAPE accuracy metrics
Forecasts the next 12 weeks of demand with a confidence interval
Exports a structured Excel report with reorder recommendations

Results

ARIMA RMSE: 16.3 (34% better than Moving Average)
ARIMA MAPE: 5.2%
12-week average forecast: ~287 units per week

How to run it

Install dependencies: pip install pandas numpy matplotlib statsmodels openpyxl
Run the script: python supply_chain_forecaster.py

Technologies
Python · Pandas · NumPy · Matplotlib · statsmodels · openpyxl
