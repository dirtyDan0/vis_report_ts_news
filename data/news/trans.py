from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd
import torch
from tqdm import tqdm
from itertools import chain
import pickle
import numpy as np


device = torch.device("cuda" if torch.cuda.is_available else "cpu")

trans_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en")
trans_model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-zh-en").to(
    device
)
data = pd.read_pickle("news_data.pkl")
data["nums"] = data["news"].apply(len)
news_list = list(chain.from_iterable(data["news"].tolist()))
news_list = [item[2] for item in news_list]

news_encode = trans_tokenizer.batch_encode_plus(
    news_list,
    max_length=64,
    padding="max_length",
    truncation=True,
    return_tensors="pt",
)
news_encode.input_ids = news_encode.input_ids
news_encode.attention_mask = news_encode.attention_mask
res = []
batch_size = 32
count = 12

for i in tqdm(range(count * 100, int(np.ceil(len(news_list) / batch_size)))):
    input_ids = (
        news_encode.input_ids[
            batch_size * i : min(len(news_list), (i + 1) * batch_size)
        ]
        .clone()
        .to(device)
    )
    attention_mask = (
        news_encode.attention_mask[
            batch_size * i : min(len(news_list), (i + 1) * batch_size)
        ]
        .clone()
        .to(device)
    )

    translated = trans_model.generate(
        input_ids=input_ids,
        attention_mask=attention_mask,
    )
    del input_ids, attention_mask
    torch.cuda.empty_cache()
    res.extend(
        [trans_tokenizer.decode(t, skip_special_tokens=True) for t in translated]
    )


count = 0
for index in range(data.shape[0]):
    row = data.iloc[index]
    row["news"] = [
        (row["news"][i][0], row["news"][i][1], res[count : count + row["nums"]])
        for i in range(row["nums"])
    ]
    data.iloc[index] = row
    count += row["nums"]

with open("news_data_trans.pkl", "wb") as f:
    pickle.dump(data, f)
