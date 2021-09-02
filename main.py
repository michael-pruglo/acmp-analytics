from retriever import *

t = get_table(271, UrlLang.cpp)

t["pts"] = 100.00 - t["rank"]
print(t)
print("Decsribe:\n", t["code len"].describe())
