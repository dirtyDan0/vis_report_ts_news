from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pandas as pd
import torch
from tqdm import tqdm

device = torch.device("cuda" if torch.cuda.is_available else "cpu")

trans_tokenizer = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-zh-en")
trans_model = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-zh-en").to(
    device
)


data = pd.read_csv("data/news/labeled_news.csv")
news_list = data["news"].tolist()
news_encode = trans_tokenizer.batch_encode_plus(
    news_list,
    max_length=64,
    padding="max_length",
    truncation=True,
    return_tensors="pt",
)
news_encode.input_ids = news_encode.input_ids.to(device)
news_encode.attention_mask = news_encode.attention_mask.to(device)

nnums = data.shape[0]
res = []
for i in tqdm(range(100)):

    translated = trans_model.generate(
        input_ids=news_encode.input_ids[10 * i : 10 * (i + 1)],
        attention_mask=news_encode.attention_mask[10 * i : 10 * (i + 1)],
    )
    res.extend(
        [trans_tokenizer.decode(t, skip_special_tokens=True) for t in translated]
    )

data["news"] = res

data.to_csv("data/news/labeled_news_trans.csv", index=False)
