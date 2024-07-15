import pandas as pd
import pickle

data = pd.read_csv("data/reports/preprocessed_data/report_data.csv")
news = pd.read_csv("data/news/news_data_tvt.csv")

norm_columns = [
    col for col in data.columns if col not in ["SECUCODE", "DATAYEAR", "DATEMMDD"]
]

mean = data[norm_columns].mean()
std = data[norm_columns].std() + 1e-5
norm_columns = [
    col for col in data.columns if col not in ["SECUCODE", "DATAYEAR", "DATEMMDD"]
]

with open("data/reports/preprocessed_data/mean.pkl", "wb") as f:
    pickle.dump(mean, f)
with open("data/reports/preprocessed_data/std.pkl", "wb") as f:
    pickle.dump(std, f)
with open("data/reports/preprocessed_data/norm_columns.pkl", "wb") as f:
    pickle.dump(norm_columns, f)
