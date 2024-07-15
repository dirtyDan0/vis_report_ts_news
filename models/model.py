import torch
import json
from torch import nn
from transformers import (
    PatchTSTModel,
    PatchTSTConfig,
    RobertaModel,
    PatchTSTForPretraining,
)

with open("config/config.json") as f:
    config = json.load(f)

if config["device"] == "gpu":
    device = torch.device("cuda" if torch.cuda.is_available else "cpu")
else:
    device = "cpu"

configuration = PatchTSTConfig(
    **{
        "activation_function": "gelu",
        "attention_dropout": 0.0,
        "bias": True,
        "channel_attention": True,
        "channel_consistent_masking": False,
        "context_length": 53,
        "do_mask_input": True,
        "d_model": 128,
        "distribution_output": "None",
        "dropout": 0.2,
        "ff_dropout": 0.0,
        "ffn_dim": 512,
        "head_dropout": 0.2,
        "init_std": 0.02,
        "loss": "mse",
        "mask_input": True,
        "mask_type": "random",
        "random_mask_ratio": 0.4,
        "mask_value": 0,
        "model_type": "patchtst",
        "norm_eps": 1e-05,
        "norm_type": "batchnorm",
        "num_attention_heads": 16,
        "num_hidden_layers": 3,
        "num_input_channels": 64,
        "num_parallel_samples": 100,
        "patch_length": 4,
        "patch_stride": 1,
        "path_dropout": 0.0,
        "positional_dropout": 0.0,
        "positional_encoding_type": "sincos",
        "pre_norm": True,
        "prediction_length": 1,
        "random_mask_ratio": 0.5,
        "scaling": "std",
        "seed_number": 98,
        "share_embedding": True,
        "share_projection": True,
        "transformers_version": "4.38.1",
    }
)


class TS_Model_pretrain(nn.Module):
    def __init__(self):
        global configuration
        super().__init__()
        self.model = PatchTSTForPretraining(configuration)

    def forward(self, x):
        return self.model(
            past_values=x,
        )

    def get_patchtst(self) -> PatchTSTModel:
        return self.model.model


class TS_Model(nn.Module):
    def __init__(self):
        global configuration
        super().__init__()
        self.model = PatchTSTModel(configuration)

    def forward(self, x):
        return self.model(
            past_values=x,
            output_attentions=True,
        )


class News_Model(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.roberta = RobertaModel.from_pretrained("roberta-base")
        self.layer1 = nn.Linear(768, 256)
        self.activate = nn.ReLU()
        self.classifier = nn.Linear(256, 3)

    def forward(self, input_ids, attention_mask):

        output_1 = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        hidden_state = output_1[0]
        pooler = hidden_state[:, 0]
        repr = self.layer1(pooler)
        repr = self.activate(repr)
        output = self.classifier(repr)
        return repr, output


class MM_Model(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        num_channels = 64
        self.patchtst_model = TS_Model()
        if config["patchtst_pretrain_checkpoint"] != -1:

            self.patchtst_model.model.load_state_dict(
                torch.load(
                    f"{config['checkpoints_dir']}/mm/ts_pretrain_epoch_{config['patchtst_pretrain_checkpoint']}_checkpoint.pth"
                )
            )
        self.text_sentiment_model = News_Model()
        self.text_sentiment_model.load_state_dict(
            torch.load(
                f"{config['checkpoints_dir']}/news_cls/news_finetune_epoch_{config['news_checkpoint_for_mm']}_checkpoint.pth"
            )
        )
        self.dropout = nn.Dropout(0.2)
        self.point_conv = nn.Conv1d(
            in_channels=num_channels,
            out_channels=1,
            kernel_size=1,
            stride=1,
            padding=0,
            groups=1,
        )
        self.news_projection = nn.Linear(256, 7)
        self.prediction = nn.Linear(135, 1)
        self.activate = nn.ReLU()

    def forward(self, data, news):  # -> Any:
        patchtst_output = self.patchtst_model(data)
        # [bs, 64, 50, 128] [bs, 1, 64][bs, 1, 64]
        ts_hidden_state = patchtst_output.last_hidden_state

        # [bsxnum_channels(64)x1]
        loc = patchtst_output.loc.transpose(1, 2)
        scale = patchtst_output.scale.transpose(1, 2)

        # [bs x num_channels(64) x 128]
        pooled_embedding = ts_hidden_state.mean(dim=2)
        pooled_embedding = self.dropout(pooled_embedding)
        # [bs x num_channels(64)x128]
        ts_repr = pooled_embedding * scale + loc

        # [bs x 128]
        ts_repr = self.point_conv(ts_repr).squeeze(1)
        ts_repr = self.activate(ts_repr)

        # [bs x128]
        news_repr = (
            self.text_sentiment_model(
                input_ids=news["input_ids"], attention_mask=news["attention_mask"]
            )
        )[0]
        # [bs x 7]
        news_repr = self.news_projection(news_repr)
        news_repr = self.activate(news_repr)
        # [bs x 135]
        result = torch.cat((ts_repr, news_repr), dim=1)
        result = self.activate(result)

        result = self.prediction(result)
        return result.squeeze()
