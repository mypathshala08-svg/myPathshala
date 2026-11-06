"""Synthetic TiffinGo churn data: 200,000 customers."""
import numpy as np, pandas as pd
rng = np.random.default_rng(42); n = 200_000
city = rng.choice(["Mumbai", "Pune", "Delhi", "Bengaluru", "Chennai", "Hyderabad"], n, p=[.25, .15, .2, .2, .1, .1])
plan = rng.choice(["Free", "Silver", "Gold"], n, p=[.6, .3, .1])
orders_30d = rng.poisson(6, n)
avg_amount = np.round(rng.gamma(4, 80, n), 1)
days_since = rng.integers(0, 60, n)
complaints = rng.poisson(0.4, n)
late_pct = np.round(rng.beta(2, 8, n) * 100, 1)
tenure_m = rng.integers(1, 48, n)
z = (-1.2 - 0.25 * orders_30d + 0.06 * days_since + 0.7 * complaints + 0.035 * late_pct
     - 0.03 * tenure_m - 0.6 * (plan == "Gold") - 0.25 * (plan == "Silver") + 0.3 * (city == "Delhi"))
churn = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
df = pd.DataFrame(dict(customer_id=np.arange(1, n + 1), city=city, plan=plan, orders_30d=orders_30d, avg_amount=avg_amount,
                       days_since_last=days_since, complaints=complaints, late_pct=late_pct, tenure_months=tenure_m, churned=churn))
# 3% missing avg_amount, 2% missing late_pct
df.loc[rng.random(n) < .03, "avg_amount"] = np.nan
df.loc[rng.random(n) < .02, "late_pct"] = np.nan
df.to_parquet("/root/lab/spark/data/m10/customers.parquet", index=False)
print(df.head(3).to_string()); print("rows", n, "churn rate", round(churn.mean(), 3))
