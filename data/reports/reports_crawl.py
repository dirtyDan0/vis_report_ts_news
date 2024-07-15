from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from copy import deepcopy
import threading
import re
import requests
import json
import csv

url_base = r"https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery1123029909101759936596_1708332019846&sortColumns=REPORT_DATE%2CSECURITY_CODE&sortTypes=-1%2C-1&pageSize=500&pageNumber=1&columns=ALL&filter=(REPORT_DATE%3C%3D%20%272023-12-31%27)(REPORT_DATE%3E%3D%20%272000-01-01%27)"
parsed_url = urlparse(url_base)
query_params = parse_qs(parsed_url.query)
report_names = [
    "RPT_LICO_FN_CPD",
    "RPT_DMSK_FN_BALANCE",
    "RPT_DMSK_FN_INCOME",
    "RPT_DMSK_FN_CASHFLOW",
]
params = []
dics = []

for idx, name in enumerate(report_names):
    param = deepcopy(query_params)
    param["reportName"] = name
    if idx == 0:
        param["sortColumns"][0] = "REPORTDATE,SECURITY_CODE"
        param["filter"][0] = "(REPORTDATE<= '2023-12-31')(REPORTDATE>= '2000-01-01')"
    params.append(param)

params2url = lambda param: urlunparse(
    (
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        urlencode(param, doseq=True),
        parsed_url.fragment,
    )
)


def get_response(param):
    url = params2url(param=param)
    response = requests.get(url)
    text = response.text
    result = None
    match = re.search(r"jQuery\d+_\d+\s*\((.*?)\);", text)
    if not match:
        return False
    result = match.group(1)
    dic = json.loads(result)["result"]
    return dic


def crawling(param):
    global dics
    data = []
    dic = get_response(param)
    pages = dic["pages"]
    data.extend(dic["data"])
    for pgnum in range(pages - 1):
        param["pageNumber"] = str(pgnum + 2)
        dic = get_response(param)
        data.extend(dic["data"])
    dics.append(data)


threads = []
for i in range(4):
    threads.append(threading.Thread(target=crawling, args=(params[i],)))
threads[0].start()
threads[1].start()
threads[2].start()
threads[3].start()
threads[0].join()
threads[1].join()
threads[2].join()
threads[3].join()

for idx, name in enumerate(report_names):
    with open(f"data/reports/crawl_data/{name}.csv", "w", newline="") as csv_file:
        fieldnames = dics[idx][0].keys()
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dics[idx])
