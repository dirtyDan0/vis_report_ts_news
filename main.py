from utils.train import news_train, mm_train, mm_test, ts_pretrain_train
import argparse
import torch
from models.model import News_Model, MM_Model, TS_Model_pretrain
from utils.data_loader import fpb_data, news_finetune_data, mm_data
from utils.seed import setup_seed
import json

with open("config/config.json") as f:
    config = json.load(f)

mm_last_epoch = config["mm_last_epoch"]
mm_checkponit = config["mm_checkpoint"]


setup_seed()


if config["device"] == "gpu":
    device = torch.device("cuda" if torch.cuda.is_available else "cpu")
else:
    device = "cpu"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    """
    mode:
    [1] news_train : use FinancialPhraseBank dataset to train News_Model
    [2] news_finetune : use labeled news from eastmoney.com to finetune News_Model. Pretained checkpoint needed
    [3] train : train MM_Model
    [4] ablation: ablation study for MM_Model
    [5] test: inference
    """
    parser.add_argument("--mode", type=str)
    """
    cls_checkpt : pick which checkpoint to load for fintuning
    """
    parser.add_argument("--cls_checkpt", type=str)

    args = parser.parse_args()

    if args.mode == "news_train":
        model = News_Model().to(device)
        news_train(model, fpb_data, prefix="news_fpb", epoches=40)

    elif args.mode == "news_finetune":
        model = News_Model().to(device)
        model.load_state_dict(
            torch.load(
                f"{config['checkpoints_dir']}/news_cls/news_fpb_epoch_{args.cls_checkpt}_checkpoint.pth"
            )
        )
        news_train(model, news_finetune_data, prefix="news_finetune", epoches=40)

    elif args.mode == "ts_pretrain":
        model = TS_Model_pretrain().to(device)
        ts_pretrain_train(model, mm_data, epoches=50)

    elif args.mode == "train":
        model = MM_Model().to(device)
        if mm_last_epoch != -1:
            model.load_state_dict(
                torch.load(
                    f"{config['checkpoints_dir']}/mm/mm_epoch_{mm_last_epoch}_checkpoint.pth"
                )
            )
        mm_train(model, mm_data, ablation=False, epoches=400)
    elif args.mode == "ablation":
        model = MM_Model().to(device)
        mm_train(model, mm_data, ablation=True, epoches=400)
    elif args.mode == "test":
        model = MM_Model().to(device)
        model.load_state_dict(
            torch.load(
                f"{config['checkpoints_dir']}/mm/mm_epoch_{mm_checkponit}_checkpoint.pth"
            ),
        )
        mm_test(model, mm_data)
