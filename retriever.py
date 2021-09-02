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
    def download():
        import requests

        url = "https://acmp.ru/index.asp?main=bstatus" + "&id_t="+str(task_no) + "&lang="+lang.value
        html = requests.get(url).content

        df_list = pd.read_html(html, attrs={'class':'main'}, parse_dates=True)
        assert(len(df_list)==1)
        
        return df_list[0]
    
    def preprocess(table):
        def organize_columns():
            column_names = ["rank", "date", "name", "lang", "runtime", "memory", "code len"]
            nonlocal table
            table.columns = column_names

            def insert_col(name, idx=-1, val=0):
                table[name] = val
                if idx<0:
                    column_names.append(name)
                else:
                    column_names.insert(idx, name)

            insert_col("elo", idx=3, val=0)
            insert_col("pts", val=0.0)

            table = table.reindex(columns = column_names)

        organize_columns()
        return table
    
    return preprocess(download())
