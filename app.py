from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import pymysql
import json
from gevent import pywsgi


app = Flask(__name__)
CORS(app)
avg_attrs = [
    "BASIC_EPS",
    "TOTAL_OPERATE_INCOME",
    "PARENT_NETPROFIT",
    "BPS",
    "MGJYXJJE",
    "ACCOUNTS_RECE",
    "TOTAL_ASSETS",
    "ACCOUNTS_PAYABLE",
    "TOTAL_LIABILITIES",
    "TOTAL_EQUITY",
    "TOTAL_OPERATE_COST",
    "OPERATE_PROFIT",
    "TOTAL_PROFIT",
    "CCE_ADD",
    "NETCASH_OPERATE",
    "NETCASH_INVEST",
    "NETCASH_FINANCE",
    "DATAYEAR",
    "DATEMMDD",
]

nece_attrs_won = [
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
    "DATAYEAR",
    "DATEMMDD",
    "SECUCODE",
]
nece_attrs_wn = nece_attrs_won + ["SECURITY_NAME_ABBR", "TRADE_MARKET"]
mean_industry_sql = (
    lambda year, season: f"select INDUSTRY_NAME, avg(BASIC_EPS) as BASIC_EPS, avg(TOTAL_OPERATE_INCOME) as TOTAL_OPERATE_INCOME, avg(PARENT_NETPROFIT) as PARENT_NETPROFIT, avg(BPS) as BPS, avg(MGJYXJJE) as MGJYXJJE, avg(ACCOUNTS_RECE) as ACCOUNTS_RECE, avg(TOTAL_ASSETS) as TOTAL_ASSETS, avg(ACCOUNTS_PAYABLE) as ACCOUNTS_PAYABLE, avg(TOTAL_LIABILITIES) as TOTAL_LIABILITIES, avg(TOTAL_EQUITY) as TOTAL_EQUITY, avg(TOTAL_OPERATE_COST) as TOTAL_OPERATE_COST, avg(OPERATE_PROFIT) as OPERATE_PROFIT, avg(TOTAL_PROFIT) as TOTAL_PROFIT, avg(CCE_ADD) as CCE_ADD, avg(NETCASH_OPERATE) as NETCASH_OPERATE, avg(NETCASH_INVEST) as NETCASH_INVEST, avg(NETCASH_FINANCE) as NETCASH_FINANCE from reports where DATAYEAR={year} and DATEMMDD={season} group by INDUSTRY_NAME;"
)

mean_sql = (
    lambda year, season, market: f"select avg(BASIC_EPS) as BASIC_EPS, avg(TOTAL_OPERATE_INCOME) as TOTAL_OPERATE_INCOME, avg(PARENT_NETPROFIT) as PARENT_NETPROFIT, avg(BPS) as BPS, avg(MGJYXJJE) as MGJYXJJE, avg(ACCOUNTS_RECE) as ACCOUNTS_RECE, avg(TOTAL_ASSETS) as TOTAL_ASSETS, avg(ACCOUNTS_PAYABLE) as ACCOUNTS_PAYABLE, avg(TOTAL_LIABILITIES) as TOTAL_LIABILITIES, avg(TOTAL_EQUITY) as TOTAL_EQUITY, avg(TOTAL_OPERATE_COST) as TOTAL_OPERATE_COST, avg(OPERATE_PROFIT) as OPERATE_PROFIT, avg(TOTAL_PROFIT) as TOTAL_PROFIT, avg(CCE_ADD) as CCE_ADD, avg(NETCASH_OPERATE) as NETCASH_OPERATE, avg(NETCASH_INVEST) as NETCASH_INVEST, avg(NETCASH_FINANCE) as NETCASH_FINANCE from reports where DATAYEAR={year} and DATEMMDD={season} and TRADE_MARKET='{market}';"
)

all_data_sql = (
    lambda year, season, market: f"select BASIC_EPS,TOTAL_OPERATE_INCOME,YSTZ,YSHZ,PARENT_NETPROFIT,SJLTZ,SJLHZ,BPS,WEIGHTAVG_ROE,MGJYXJJE,XSMLL,INDUSTRY_NAME,MONETARYFUNDS,ACCOUNTS_RECE,INVENTORY,TOTAL_ASSETS,TOTAL_ASSETS_RATIO,ACCOUNTS_PAYABLE,ADVANCE_RECEIVABLES,TOTAL_LIABILITIES,TOTAL_LIAB_RATIO,DEBT_ASSET_RATIO,TOTAL_EQUITY,PARENT_NETPROFIT_RATIO,TOI_RATIO,OPERATE_COST,SALE_EXPENSE,MANAGE_EXPENSE,FINANCE_EXPENSE,TOTAL_OPERATE_COST,OPERATE_PROFIT,TOTAL_PROFIT,CCE_ADD,CCE_ADD_RATIO,NETCASH_OPERATE,NETCASH_OPERATE_RATIO,NETCASH_INVEST,NETCASH_INVEST_RATIO,NETCASH_FINANCE,NETCASH_FINANCE_RATIO,SECUCODE,DATAYEAR,DATEMMDD,SECURITY_NAME_ABBR,TRADE_MARKET from reports where DATAYEAR={year} and DATEMMDD={season} and TRADE_MARKET='{market}'"
)

news_sql = lambda secucode: f"select news,cls from news where SECUCODE='{secucode}';"
detail_sql = (
    lambda secucode: f"select BASIC_EPS,TOTAL_OPERATE_INCOME,YSTZ,YSHZ,PARENT_NETPROFIT,SJLTZ,SJLHZ,BPS,WEIGHTAVG_ROE,MGJYXJJE,XSMLL,INDUSTRY_NAME,MONETARYFUNDS,ACCOUNTS_RECE,INVENTORY,TOTAL_ASSETS,TOTAL_ASSETS_RATIO,ACCOUNTS_PAYABLE,ADVANCE_RECEIVABLES,TOTAL_LIABILITIES,TOTAL_LIAB_RATIO,DEBT_ASSET_RATIO,TOTAL_EQUITY,PARENT_NETPROFIT_RATIO,TOI_RATIO,OPERATE_COST,SALE_EXPENSE,MANAGE_EXPENSE,FINANCE_EXPENSE,TOTAL_OPERATE_COST,OPERATE_PROFIT,TOTAL_PROFIT,CCE_ADD,CCE_ADD_RATIO,NETCASH_OPERATE,NETCASH_OPERATE_RATIO,NETCASH_INVEST,NETCASH_INVEST_RATIO,NETCASH_FINANCE,NETCASH_FINANCE_RATIO,SECUCODE,DATAYEAR,DATEMMDD from reports where SECUCODE='{secucode}' order by DATAYEAR asc, DATEMMDD asc;"
)


@app.route("/reportdata")
def get_report():
    conn = pymysql.connect(
        host="localhost",
        user="user1",
        password="123456",
        database="financial_dashboard",
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    market = request.args.get("market")
    year = request.args.get("year")
    season = request.args.get("season")
    cursor.execute(mean_industry_sql(year, season))
    means_industry = list(cursor.fetchall())
    means_industry = {
        item["INDUSTRY_NAME"]: {k: v for k, v in item.items() if k != "INDUSTRY_NAME"}
        for item in means_industry
    }
    cursor.execute(mean_sql(year, season, market))
    avg = list(cursor.fetchall())
    cursor.execute(all_data_sql(year, season, market))
    json_data = list(cursor.fetchall())
    cursor.close()
    conn.close()
    return jsonify(
        means_industry=json.dumps(means_industry),
        mean=json.dumps(avg),
        json_data=json.dumps(json_data),
    )


@app.route("/news")
def get_news():
    secucode = request.args.get("secucode")
    conn = pymysql.connect(
        host="localhost",
        user="user1",
        password="123456",
        database="financial_dashboard",
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(news_sql(secucode))
    data = list(cursor.fetchall())

    if len(data) == 0:
        return jsonify(json_data="empty")
    else:
        return jsonify(json_data=json.dumps(data))


@app.route("/detail")
def get_data() -> Response:
    secucode = request.args.get("secucode")
    conn = pymysql.connect(
        host="localhost",
        user="user1",
        password="123456",
        database="financial_dashboard",
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(detail_sql(secucode))
    data = list(cursor.fetchall())
    result_dict = {key: [item[key] for item in data] for key in nece_attrs_won}

    return json.dumps(result_dict)


@app.route("/prediction")
def get_prediction() -> Response:
    secucode = request.args.get("secucode")
    conn = pymysql.connect(
        host="localhost",
        user="user1",
        password="123456",
        database="financial_dashboard",
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute(
        f"select y_hat as prediction from prediction where SECUCODE='{secucode}';"
    )
    y_hat = list(cursor.fetchall())[0]
    return json.dumps(y_hat)


if __name__ == "__main__":
    server = pywsgi.WSGIServer(("0.0.0.0", 5000), app)
    server.serve_forever()
