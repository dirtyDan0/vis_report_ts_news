import pandas as pd
from itertools import chain

news = pd.read_pickle("data/news/news_data_trans.pkl")

yearmonth2num = lambda year, month: (year - 2010) * 4 + int((month - 1) / 3)


def news_time(row):
    news = row["news"]
    news = [(yearmonth2num(item[0], item[1]), item[2]) for item in news]
    row["train"] = "".join(
        list(
            chain(
                [
                    item[1]
                    for item in news
                    if item[0] in [yearmonth2num(2023, 1), yearmonth2num(2023, 4)]
                ]
            )
        )
    )
    row["val"] = "".join(
        list(
            chain(
                [
                    item[1]
                    for item in news
                    if item[0] in [yearmonth2num(2023, 4), yearmonth2num(2023, 7)]
                ]
            )
        )
    )
    row["test"] = "".join(
        list(
            chain(
                [
                    item[1]
                    for item in news
                    if item[0] in [yearmonth2num(2023, 7), yearmonth2num(2023, 10)]
                ]
            )
        )
    )
    return row


news = news.apply(news_time, axis=1)

news[["SECUCODE", "train", "val", "test"]].to_csv(
    "data/news/news_data_tvt.csv", index=False
)
