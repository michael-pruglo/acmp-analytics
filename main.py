import pandas as pd
from enum import Enum

class UrlLang(Enum):
    all = ""
    cpp = "CPP"
    python = "PY"
    pascal = "PAS"
    java = "JAVA"
    csharp = "CS"
    basic = "BAS"
    go = "GO"

def get_table(task_no, lang=UrlLang.all):
    import requests

    url = "https://acmp.ru/index.asp?main=bstatus" + "&id_t="+str(task_no) + "&lang="+lang.value
    html = requests.get(url).content

    df_list = pd.read_html(html, attrs={'class':'main'}, parse_dates=True)
    assert(len(df_list)==1)
    
    return df_list[0]

print(get_table(271, UrlLang.python))
