from globals import Lang

cache = {}

def get_table(task_info):
    if task_info in cache:
        return cache[task_info]
    else:
        table = _download_table(task_info)
        cache[task_info] = table
        return table



def _download_table(task_info):
    def form_url():
        url = "https://acmp.ru/index.asp?main=bstatus"
        url += "&id_t=" + str(task_info.id)
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
        url += "&lang=" + lang_dict[task_info.lang]
        return url

    def download():
        import requests
        import pandas as pd

        html = requests.get(form_url()).content
        df_list = pd.read_html(html, attrs={'class':'main'}, parse_dates=True)
        assert(len(df_list)==1)
        
        return df_list[0]
    
    def preprocess(table):
        column_names = ["rank", "date", "name", "lang", "runtime", "memory", "code len"]
        table.columns = column_names
        return table
    
    return preprocess(download())