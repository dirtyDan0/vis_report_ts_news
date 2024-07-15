import pandas as pd
import re
import requests
import json
from datetime import datetime
import random
import pickle
from tqdm import tqdm
import torch

report_data = pd.read_csv("data/reports/preprocessed_data/report_data_not_train.csv")
news_data = pd.DataFrame(report_data["SECUCODE"].unique(), columns=["SECUCODE"])


def get_news(SECUCODE):
    url = (
        "https://search-api-web.eastmoney.com/search/jsonp?cb=jQuery351019400540960126222_1709388385229&param=%7B%22uid%22%3A%22%22%2C%22keyword%22%3A%22"
        + SECUCODE
        + "%22%2C%22type%22%3A%5B%22cmsArticleWebOld%22%5D%2C%22client%22%3A%22web%22%2C%22clientType%22%3A%22web%22%2C%22clientVersion%22%3A%22curr%22%2C%22param%22%3A%7B%22cmsArticleWebOld%22%3A%7B%22searchScope%22%3A%22default%22%2C%22sort%22%3A%22default%22%2C%22pageIndex%22%3A1%2C%22pageSize%22%3A100%2C%22preTag%22%3A%22%3Cem%3E%22%2C%22postTag%22%3A%22%3C%2Fem%3E%22%7D%7D%7D&_=1709388385230"
    )
    response = requests.get(url)
    text = response.text
    result = None
    match = re.search(r"\{.*\}", text)
    result = match.group(0)
    news = json.loads(result)["result"]["cmsArticleWebOld"]
    news = [
        (
            datetime.strptime(item["date"], "%Y-%m-%d %H:%M:%S"),
            item["title"] + item["content"],
        )
        for item in news
    ]
    news = [
        (item[0].year, item[0].month, re.sub(r"<[^>]+>", "", item[1])) for item in news
    ]
    return news


news_data["news"] = news_data["SECUCODE"].apply(get_news)

with open("news_data.pkl", "wb") as f:
    pickle.dump(news_data, f)

news_wo_date = []
for news in news_data["news"]:
    if news == []:
        continue
    news_wo_date.extend([item[2] for item in news])

samples = random.sample(news_wo_date, 1000)

# 0:负面，1：中性，2：正面

labeled_data = []
for sample in samples:
    labeled_data.append([sample, input(sample)])

df = pd.DataFrame(labeled_data, columns=["news", "type"])
df.to_csv("labeled_news.csv", index=False)
