import pandas as pd

df = pd.read_feather("D:/meet/FNO_backtest/dataset/NIFTY_JF_FNO_08032023.feather")

df.to_csv("D:/meet/FNO_backtest/dataset/NIFTY_JF_FNO_08032023.csv")