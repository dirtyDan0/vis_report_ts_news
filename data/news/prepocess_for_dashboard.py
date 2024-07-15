import pandas as pd
from itertools import chain
from transformers import RobertaTokenizer
from models.model import News_Model
from torch.utils.data import DataLoader, Dataset, random_split
from tqdm import tqdm

import torch
from torch import nn

device = torch.device("cuda" if torch.cuda.is_available else "cpu")


data = pd.read_pickle("data/news/news_data.pkl")
data_transed = pd.read_pickle("data/news/news_data_trans.pkl")
yearmonth2num = lambda year, month: (year - 2010) * 4 + int((month - 1) / 3)


def addcode2news(row):
    row["news"] = [(row["SECUCODE"], item[0], item[1], item[2]) for item in row["news"]]
    return row


data = data.apply(addcode2news, axis=1)
data_transed = data_transed.apply(addcode2news, axis=1)
data_new = pd.DataFrame(
    list(chain(*data["news"].tolist())), columns=["SECUCODE", "year", "month", "news"]
)
data_new_transed = pd.DataFrame(
    list(chain(*data_transed["news"].tolist())),
    columns=["SECUCODE", "year", "month", "news"],
)
data_new["trans"] = data_new_transed["news"]
data_new = data_new[(data_new["year"] == 2023) & (data_new["month"] == 12)]
data_new.drop(columns=["year", "month"], inplace=True)
sentences = data_new["trans"].tolist()

tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
sentences_token = tokenizer.batch_encode_plus(
    sentences,
    max_length=64,
    padding="max_length",
    truncation=True,
    return_tensors="pt",
)

model = News_Model().to(device)
model.load_state_dict(
    torch.load(
        f"checkpoints/news_cls/news_finetune_epoch_27_checkpoint.pth",
        map_location=torch.device("cpu"),
    )
)

res = []
m = nn.Softmax(dim=1)


class Sentence(Dataset):
    def __init__(self) -> None:
        super().__init__()

        self.data = sentences_token

    def __getitem__(self, idx):

        return dict(
            input_ids=self.data.input_ids[idx],
            attention_mask=self.data.attention_mask[idx],
        )

    def __len__(self) -> int:
        return len(self.data.input_ids)


dataloader = DataLoader(Sentence(), batch_size=32, shuffle=False)

for item in tqdm(dataloader):
    input_ids = item["input_ids"].to(device)
    attention_mask = item["attention_mask"].to(device)
    _, output = model(input_ids=input_ids, attention_mask=attention_mask)
    outputs = m(output)
    cls = list(outputs.argmax(dim=1))
    res.extend(cls)

res = [int(item.to("cpu")) for item in res]
data_new["cls"] = res
data_new.drop(columns=["trans"], inplace=True)
data_new.to_csv("data/news/news_cls.csv", index=False)
