import pandas as pd

df = pd.read_csv("q-stock-prices-ema.csv")

df["EMA_21"] = df.groupby("Ticker")["Close_Price"].transform(
    lambda x: x.ewm(span=21, adjust=False).mean()
)
print(df.head())
last_date = df["Date"].max()

last_day = df[df["Date"] == last_date]

row = last_day.loc[last_day["EMA_21"].idxmax()]

ema_value = round(row["EMA_21"], 2)
ticker = row["Ticker"]

print(f"{ema_value}, {ticker}")

