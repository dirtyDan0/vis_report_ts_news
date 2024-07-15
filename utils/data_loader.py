import pandas as pd
import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset, random_split
from transformers import RobertaTokenizer
from utils.seed import setup_seed
import pickle
import json

with open("config/config.json") as f:
    config = json.load(f)
setup_seed()

pd.options.mode.chained_assignment = "raise"
NO_NEWS_PAD = "There were no significant updates in the news today."


class MM_Dataset(Dataset):
    def __init__(self, mode, ablation) -> None:

        super().__init__()
        self.mode = mode

        data = pd.read_csv("data/reports/preprocessed_data/report_data.csv")
        if self.mode != "pretrain":
            self.news = pd.read_csv("data/news/news_data_tvt.csv")
            self.news.fillna(
                dict(
                    train=NO_NEWS_PAD,
                    val=NO_NEWS_PAD,
                    test=NO_NEWS_PAD,
                ),
                inplace=True,
            )
            if ablation:
                self.news.train = NO_NEWS_PAD
                self.news.val = NO_NEWS_PAD

        with open("data/reports/preprocessed_data/norm_columns.pkl", "rb") as f:
            norm_columns = pickle.load(f)

        self.tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
        with open("data/reports/preprocessed_data/mean.pkl", "rb") as f:
            self.mean = pickle.load(f)
        with open("data/reports/preprocessed_data/std.pkl", "rb") as f:
            self.std = pickle.load(f)

        data.fillna(self.mean, inplace=True)

        data[norm_columns] = (data[norm_columns] - self.mean) / self.std
        process_group = lambda group: group.sort_values(by=["DATAYEAR", "DATEMMDD"])[
            norm_columns
        ].values
        train_data = data[~((data["DATAYEAR"] == 2023) & (data["DATEMMDD"] == 4))]
        result = train_data.groupby("SECUCODE").apply(process_group)
        self.data = pd.DataFrame(result, columns=["Data"]).reset_index()

    def __len__(self):
        return self.data.shape[0]

    def __getitem__(self, index):

        sample = self.data.iloc[index]
        if self.mode == "pretrain":
            return dict(
                time_series=dict(
                    x=torch.tensor(sample["Data"][:53, :]).float(),
                ),
            )
        news_sample = self.news[self.news["SECUCODE"] == sample["SECUCODE"]].iloc[0]
        if self.mode == "train":
            news = self.tokenizer.encode_plus(
                news_sample["train"],
                max_length=64,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            return dict(
                time_series=dict(  # train
                    x=torch.tensor(sample["Data"][:53, :]).float(),
                    y=torch.tensor(sample["Data"][53, 0]).float(),
                ),
                news=dict(
                    input_ids=news["input_ids"][0],
                    attention_mask=news["attention_mask"][0],
                ),
            )
        elif self.mode == "val":
            news = self.tokenizer.encode_plus(
                news_sample["val"],
                max_length=64,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            return dict(
                time_series=dict(  # train
                    x=torch.tensor(sample["Data"][1:54, :]).float(),
                    y=torch.tensor(sample["Data"][54, 0]).float(),
                ),
                news=dict(
                    input_ids=news["input_ids"][0],
                    attention_mask=news["attention_mask"][0],
                ),
            )
        elif self.mode == "test":
            news = self.tokenizer.encode_plus(
                news_sample["test"],
                max_length=64,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )

            return dict(
                time_series=dict(x=torch.tensor(sample["Data"][2:55, :]).float()),
                news=dict(
                    input_ids=news["input_ids"][0],
                    attention_mask=news["attention_mask"][0],
                ),
            )
        else:
            print("Invalid mode!")


def mm_data(mode, ablation):
    if mode == "pretrain":
        train_data = MM_Dataset(mode="pretrain", ablation=None)
        train_size = int(0.95 * len(train_data))
        val_size = len(train_data) - train_size
        train_data, val_data = random_split(train_data, [train_size, val_size])
        train_loader = DataLoader(
            train_data, batch_size=config["batch_size"], shuffle=True
        )
        val_loader = DataLoader(val_data, batch_size=config["batch_size"], shuffle=True)
        return train_loader, val_loader

    if mode == "train":
        train_data = MM_Dataset(mode="train", ablation=ablation)
        val_data = MM_Dataset(mode="val", ablation=ablation)
        train_loader = DataLoader(
            train_data, batch_size=config["batch_size"], shuffle=True
        )
        val_loader = DataLoader(val_data, batch_size=config["batch_size"], shuffle=True)

        return train_loader, val_loader
    if mode == "test":
        test_data = MM_Dataset(mode="test", ablation=None)
        secucodes = pd.DataFrame(test_data.data["SECUCODE"])
        test_loader = DataLoader(
            test_data, batch_size=config["batch_size"], shuffle=False
        )
        return test_loader, secucodes


class FinancialPhraseBank(Dataset):

    def __init__(self) -> None:
        super().__init__()
        type2num = lambda col: (
            2
            if col == "positive"
            else (1 if col == "neutral" else (0 if col == "negative" else "error"))
        )

        fpb = pd.read_csv(
            "data/news/fpb.csv",
        )

        fpb["type"] = fpb["type"].apply(type2num)
        self.tokenizer = RobertaTokenizer.from_pretrained("roberta-base")

        news_list = fpb["news"].tolist()
        news = self.tokenizer.batch_encode_plus(
            news_list,
            max_length=64,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        self.labels = fpb.type.tolist()
        self.input_ids = news.input_ids
        self.attention_mask = news.attention_mask

    def __getitem__(self, idx):
        label = torch.zeros(3)
        label[self.labels[idx]] = 1
        input_ids = self.input_ids[idx]
        attention_mask = self.attention_mask[idx]

        return dict(label=label, input_ids=input_ids, attention_mask=attention_mask)

    def __len__(self) -> int:
        return len(self.labels)


def fpb_data():
    train_data = FinancialPhraseBank()
    train_size = int(0.95 * len(train_data))
    val_size = len(train_data) - train_size
    train_data, val_data = random_split(train_data, [train_size, val_size])

    train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=64, shuffle=True)
    return train_loader, val_loader


# only for classification pretraining
class NEWS_Finetune(Dataset):
    def __init__(self) -> None:
        super().__init__()

        self.data = pd.read_csv("data/news/labeled_news_trans.csv")
        self.tokenizer = RobertaTokenizer.from_pretrained("roberta-base")
        news_list = self.data["news"].tolist()
        news = self.tokenizer.batch_encode_plus(
            news_list,
            max_length=64,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        self.labels = self.data.type.tolist()
        self.input_ids = news.input_ids
        self.attention_mask = news.attention_mask

    def __getitem__(self, idx):
        label = torch.zeros(3)
        label[self.labels[idx]] = 1
        input_ids = self.input_ids[idx]
        attention_mask = self.attention_mask[idx]

        return dict(label=label, input_ids=input_ids, attention_mask=attention_mask)

    def __len__(self) -> int:
        return len(self.labels)


def news_finetune_data():
    train_data = NEWS_Finetune()
    train_size = int(0.9 * len(train_data))
    val_size = len(train_data) - train_size
    train_data, val_data = random_split(train_data, [train_size, val_size])

    train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_data, batch_size=64, shuffle=True)
    return train_loader, val_loader
