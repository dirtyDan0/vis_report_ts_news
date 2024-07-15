from typing import final
import pandas as pd
import numpy as np

cpd = (
    pd.read_csv("data/reports/crawl_data/RPT_LICO_FN_CPD.csv")
    .drop(columns=["NOTICE_DATE"])
    .drop_duplicates()
)
income = (
    pd.read_csv("data/reports/crawl_data/RPT_DMSK_FN_INCOME.csv")
    .drop(columns=["NOTICE_DATE"])
    .drop_duplicates()
)
balance = (
    pd.read_csv("data/reports/crawl_data/RPT_DMSK_FN_BALANCE.csv")
    .drop(columns=["NOTICE_DATE"])
    .drop_duplicates()
)
cashflow = (
    pd.read_csv("data/reports/crawl_data/RPT_DMSK_FN_CASHFLOW.csv")
    .drop(columns=["NOTICE_DATE"])
    .drop_duplicates()
    .rename(columns={"REPORTDATE": "REPORT_DATE"})
)

df = pd.DataFrame(
    {
        "col": list(
            set(
                cpd.columns.append(income.columns)
                .append(balance.columns)
                .append(cashflow.columns)
            )
        )
    }
)
df["cpd"] = df["col"].isin(cpd.columns)
df["income"] = df["col"].isin(income.columns)
df["balance"] = df["col"].isin(balance.columns)
df["cashflow"] = df["col"].isin(cashflow.columns)
df["sum"] = df[["cpd", "income", "balance", "cashflow"]].apply(sum, axis=1)
df1 = pd.merge(
    cpd,
    income,
    on=(df[(df["cpd"] == True) & (df["income"] == True)]["col"]).to_list(),
    how="inner",
)
df2 = pd.merge(
    balance,
    cashflow,
    on=(df[(df["balance"] == True) & (df["cashflow"] == True)]["col"]).to_list(),
    how="inner",
)
cols_exclude = [
    "INDUSTRY_CODE",
    "ORG_CODE",
    "SECURITY_TYPE_CODE",
    "TRADE_MARKET_CODE",
    "DATE_TYPE_CODE",
    "REPORT_TYPE_CODE",
    "DATA_STATE",
    "REPORT_DATE",
    "SECURITY_TYPE",
    "UPDATE_DATE",
    "ISNEW",
    "TRADE_MARKET_ZJG",
    "DATATYPE",
    "EITIME",
    "FCN_RATIO",
    "ASSIGNDSCRPT",
    "PAYYEAR",
]
final_df = pd.merge(
    df1,
    df2,
    on=(df[(df["cpd"] == True) & (df["income"] == True)]["col"]).to_list(),
    how="inner",
).drop(columns=cols_exclude)

final_df = final_df[final_df["DATAYEAR"] >= 2010]
final_df.dropna(subset=["BASIC_EPS"], inplace=True)

QDATE_NECE = [
    str(i) + "Q" + str(j)
    for i in range(2010, 2024, 1)
    for j in range(1, 5)
    if not (i == 2023 and j == 4)
]


def is_sublist(mainlist) -> bool:
    global QDATE_NECE
    return all(elem in mainlist for elem in QDATE_NECE)


def is_complete(df):
    QDATE_NECE_TRUE = pd.DataFrame(
        df.groupby("SECUCODE")["QDATE"].apply(list).reset_index()
    )
    QDATE_NECE_TRUE["complete"] = QDATE_NECE_TRUE["QDATE"].apply(is_sublist)
    return df[
        df["SECUCODE"].isin(
            QDATE_NECE_TRUE[(QDATE_NECE_TRUE["complete"] == True)]["SECUCODE"].tolist()
        )
    ]


final_df = is_complete(final_df)

final_df.drop(
    columns=final_df.columns[
        (final_df.isna().sum() > 0.75 * final_df.shape[0]) == True
    ],
    inplace=True,
)

datemmdd2num = {"一季报": 1, "半年报": 2, "三季报": 3, "年报": 4}

final_df["DATEMMDD"] = final_df["DATEMMDD"].map(datemmdd2num)

column_to_move = "BASIC_EPS"
new_index = 1

columns = final_df.columns.tolist()
columns.remove(column_to_move)
columns.insert(new_index, column_to_move)

final_df = final_df[columns]
final_df[
    [
        "SECUCODE",
        "SECURITY_NAME_ABBR",
        "BASIC_EPS",
        "TOTAL_OPERATE_INCOME",
        "YSTZ",
        "YSHZ",
        "PARENT_NETPROFIT",
        "SJLTZ",
        "SJLHZ",
        "BPS",
        "WEIGHTAVG_ROE",
        "MGJYXJJE",
        "XSMLL",
        "INDUSTRY_NAME",
        "TRADE_MARKET",
        "DATEMMDD",
        "DATAYEAR",
        "MONETARYFUNDS",
        "ACCOUNTS_RECE",
        "INVENTORY",
        "TOTAL_ASSETS",
        "TOTAL_ASSETS_RATIO",
        "ACCOUNTS_PAYABLE",
        "ADVANCE_RECEIVABLES",
        "TOTAL_LIABILITIES",
        "TOTAL_LIAB_RATIO",
        "DEBT_ASSET_RATIO",
        "TOTAL_EQUITY",
        "PARENT_NETPROFIT_RATIO",
        "TOI_RATIO",
        "OPERATE_COST",
        "SALE_EXPENSE",
        "MANAGE_EXPENSE",
        "FINANCE_EXPENSE",
        "TOTAL_OPERATE_COST",
        "OPERATE_PROFIT",
        "TOTAL_PROFIT",
        "CCE_ADD",
        "CCE_ADD_RATIO",
        "NETCASH_OPERATE",
        "NETCASH_OPERATE_RATIO",
        "NETCASH_INVEST",
        "NETCASH_INVEST_RATIO",
        "NETCASH_FINANCE",
        "NETCASH_FINANCE_RATIO",
    ]
].to_csv("data/reports/preprocessed_data/report_data_all.csv", index=False)

data_not_train = final_df[
    final_df.columns[(final_df.dtypes == "object").values]
].drop_duplicates()
final_df.drop(
    columns=["SECURITY_NAME_ABBR", "INDUSTRY_NAME", "MARKET", "TRADE_MARKET", "QDATE"],
    inplace=True,
)
final_df.to_csv("data/reports/preprocessed_data/report_data.csv", index=False)
data_not_train.to_csv(
    "data/reports/preprocessed_data/report_data_not_train.csv", index=False
)
