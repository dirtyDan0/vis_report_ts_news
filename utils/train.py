from tkinter import NO
import torch
from transformers.optimization import Adafactor, AdafactorSchedule
from tqdm import tqdm
from torch import nn
import numpy as np
import pandas as pd
from utils.seed import setup_seed
import json


with open("config/config.json") as f:
    config = json.load(f)
setup_seed()

if config["device"] == "gpu":
    device = torch.device("cuda" if torch.cuda.is_available else "cpu")
else:
    device = "cpu"
mm_last_epoch = config["mm_last_epoch"]
output_path = config["output_dir"]


def news_train(model, func_data, prefix, epoches=20):
    global device, output_path
    loss_acc = pd.DataFrame(
        columns=[
            "Train Loss",
            "Train Acc",
            "Valid Loss",
            "Valid Acc",
        ]
    )
    optimizer = Adafactor(
        model.parameters(),
        scale_parameter=True,
        relative_step=True,
        warmup_init=True,
        lr=None,
        weight_decay=0,
    )
    lr_scheduler = AdafactorSchedule(optimizer)
    loss_fn = nn.CrossEntropyLoss()
    train_loss, train_acc = [], []
    for i in range(epoches):
        tmp_loss_acc = []
        print("Epoch", i)
        model.train()
        Y_pred, Y_real, losses = [], [], []
        train_loader, val_loader = func_data()

        for item in tqdm(train_loader):
            y = item["label"].to(device)
            input_ids = item["input_ids"].to(device)
            attention_mask = item["attention_mask"].to(device)
            optimizer.zero_grad()
            _, y_hat = model(input_ids, attention_mask)
            loss = loss_fn(y_hat, y)
            losses.append(loss.item())
            Y_pred.extend(y_hat.argmax(dim=1).to("cpu"))
            Y_real.extend((y == 1).nonzero()[:, 1].squeeze(0).to("cpu"))
            loss.backward()
            optimizer.step()
            lr_scheduler.step()

        torch.save(
            model.state_dict(),
            f"{config['checkpoints_dir']}/news_cls/{prefix}_epoch_{i}_checkpoint.pth",
        )

        Y_pred = np.array(Y_pred)
        Y_real = np.array(Y_real)
        loss_mean = np.array(losses).mean()
        acc = (Y_real == Y_pred).sum() / Y_pred.shape[0]
        train_loss.append(loss_mean)
        train_acc.append(acc)

        print("Train loss :{:.6f}".format(loss_mean), end="\t")
        print("Train Acc  : {:.6f}".format(acc))
        tmp_loss_acc.extend([loss_mean, acc])
        tmp_loss_acc.extend(news_val(model, val_loader))

        loss_acc.loc[i] = tmp_loss_acc
    loss_acc.to_csv(f"{output_path}/{prefix}_cls_loss_and_acc.csv", index_label="Epoch")


def news_val(model, val_loader):
    global device
    model.eval()
    Y_pred, Y_real, losses = [], [], []
    loss_fn = nn.CrossEntropyLoss()
    with torch.no_grad():
        for item in val_loader:
            y = item["label"].to(device)
            input_ids = item["input_ids"].to(device)
            attention_mask = item["attention_mask"].to(device)
            _, y_hat = model(input_ids, attention_mask)
            loss = loss_fn(y_hat, y)
            losses.append(loss.item())
            Y_pred.extend(y_hat.argmax(dim=1).to("cpu"))
            Y_real.extend((y == 1).nonzero()[:, 1].squeeze(0).to("cpu"))

    Y_pred = np.array(Y_pred)
    Y_real = np.array(Y_real)

    loss_mean = np.array(losses).mean()
    acc = (Y_real == Y_pred).sum() / Y_pred.shape[0]
    print("Valid Loss : {:.6f}".format(loss_mean), end="\t")
    print("Valid Acc  : {:.6f}".format(acc))
    return [loss_mean, acc]


def ts_pretrain_train(model, func_data, epoches=50):
    global device, mm_last_epoch
    loss_df = pd.DataFrame(
        columns=[
            "Train Loss",
            "Valid Loss",
        ]
    )
    optimizer = Adafactor(
        model.parameters(),
        scale_parameter=True,
        relative_step=True,
        warmup_init=False,
        lr=None,
        weight_decay=0,
    )
    lr_scheduler = AdafactorSchedule(optimizer)
    train_loader, val_loader = func_data(mode="pretrain", ablation=None)
    for i in range(0, epoches):
        print("Epoch", i)
        model.train()
        losses = []

        for item in tqdm(train_loader):
            x = item["time_series"]["x"].to(device)
            optimizer.zero_grad()
            outputs = model(x)
            loss = outputs.loss
            losses.append(loss.item())
            loss.backward()
            optimizer.step()
            lr_scheduler.step()

        train_loss = np.array(losses).mean()
        val_loss = ts_pretrain_val(model, val_loader)
        loss_df.loc[i] = [train_loss, val_loss]
        print("Train loss :{:.6f}\tVal loss :{:.6f}".format(train_loss, val_loss))

        if val_loss < 0.2:
            torch.save(
                model.get_patchtst().state_dict(),
                f"{config['checkpoints_dir']}/mm/ts_pretrain_epoch_{i}_checkpoint.pth",
            )

        loss_df.to_csv(f"{output_path}/ts_pretrain_loss.csv", index_label="Epoch")


def ts_pretrain_val(model, val_loader):
    global device
    model.eval()
    losses = []

    with torch.no_grad():
        for item in tqdm(val_loader):
            x = item["time_series"]["x"].to(device)
            outputs = model(x)
            loss = outputs.loss
            losses.append(loss.item())
    loss_mean = np.array(losses).mean()
    return loss_mean


def mm_train(model, func_data, ablation, epoches=50):
    global device, mm_last_epoch, output_path
    loss_df = pd.DataFrame(
        columns=[
            "Train Loss",
            "Valid Loss",
        ]
    )
    optimizer = Adafactor(
        model.parameters(),
        scale_parameter=True,
        relative_step=True,
        warmup_init=False,
        lr=None,
        weight_decay=0,
    )
    lr_scheduler = AdafactorSchedule(optimizer)
    loss_fn = nn.MSELoss()
    train_loader, val_loader = func_data(mode="train", ablation=ablation)
    for i in range(mm_last_epoch + 1, mm_last_epoch + 1 + epoches):
        print("Epoch", i)
        model.train()
        losses = []

        for item in tqdm(train_loader):
            x = item["time_series"]["x"].to(device)
            y = item["time_series"]["y"].to(device)
            news = item["news"]
            news["input_ids"] = news["input_ids"].to(device)
            news["attention_mask"] = news["attention_mask"].to(device)
            optimizer.zero_grad()
            train_y_hat = model(x, news)
            loss = loss_fn(train_y_hat, y)
            losses.append(loss.item())
            loss.backward()
            optimizer.step()
            lr_scheduler.step()

        train_loss = np.array(losses).mean()
        val_loss = mm_val(model, val_loader)
        loss_df.loc[i] = [train_loss, val_loss]
        print("Train loss :{:.6f}\tVal loss :{:.6f}".format(train_loss, val_loss))

        if val_loss < 0.6:
            if ablation:
                torch.save(
                    model.state_dict(),
                    f"{config['checkpoints_dir']}/mm/mm_ablation_epoch_{i}_checkpoint.pth",
                )
            else:
                torch.save(
                    model.state_dict(),
                    f"{config['checkpoints_dir']}/mm/mm_epoch_{i}_checkpoint.pth",
                )

        if ablation:
            loss_df.to_csv(f"{output_path}/mm_ablation_loss.csv", index_label="Epoch")
        else:
            loss_df.to_csv(f"{output_path}/mm_loss.csv", index_label="Epoch")


def mm_val(model, val_loader):
    global device
    model.eval()
    loss_fn = nn.MSELoss()
    losses = []

    with torch.no_grad():

        for item in tqdm(val_loader):
            x = item["time_series"]["x"].to(device)
            y = item["time_series"]["y"].to(device)
            news = item["news"]
            news["input_ids"] = news["input_ids"].to(device)
            news["attention_mask"] = news["attention_mask"].to(device)
            train_y_hat = model(x, news)
            loss = loss_fn(train_y_hat, y)
            losses.append(loss.item())
    loss_mean = np.array(losses).mean()
    return loss_mean


def mm_test(model, func_data):
    global device, mm_last_epoch, output_path
    model.eval()

    test_loader, secucodes = func_data(mode="test", ablation=None)

    y = None

    with torch.no_grad():
        for item in tqdm(test_loader):
            x = item["time_series"]["x"].to(device)
            news = item["news"]
            news["input_ids"] = news["input_ids"].to(device)
            news["attention_mask"] = news["attention_mask"].to(device)
            y_hat = model(x, news)
            if y == None:
                y = y_hat
            else:
                y = torch.cat([y, y_hat])

    y = y.squeeze().to("cpu")
    secucodes["y_hat"] = y
    secucodes.to_csv(f"{output_path}/prediction.csv", index=False)
