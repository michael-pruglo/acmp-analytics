from globals import Lang
import requests
import pandas as pd
from time import perf_counter

def get_task_leaderboard(task_info):
    def form_url():
        lang_dict = {
            Lang.all: "",
            Lang.cpp: "CPP",
            Lang.python: "PY",
            Lang.pascal: "PAS",
            Lang.java: "JAVA",
            Lang.csharp: "CS",
            Lang.basic: "BAS",
            Lang.go: "GO",
        }
        return f"https://acmp.ru/index.asp?main=bstatus&id_t={ task_info.id }&lang={ lang_dict[task_info.lang] }"

    column_names = ["rank", "date", "name", "lang", "runtime", "memory", "code_len"]
    return _download_table(form_url(), column_names)

def get_accepted_submissions(pages):
    def form_url(page_no):
        return f"https://acmp.ru/index.asp?main=tasks&str=%20&page={ page_no }&id_type=0"

    column_names = ["id", "name", "topic", "sol", "diff", "succ_percent", "acc_no"]
    return pd.concat([_download_table(form_url(page), column_names) for page in pages])



def _download_table(url, column_names):
    def download():
        html = requests.get(url).content
        df_list = pd.read_html(html, attrs={'class':'main'}, parse_dates=True)
        assert(len(df_list)==1)
        return df_list[0]
    
    def preprocess(table):
        table.columns = column_names
        return table
    
    start_time = perf_counter()
    print("network operation... ", end="", flush=True)
    ret = preprocess(download())
    print(f"download took {(perf_counter() - start_time):.3f}s")

    return ret
