from util import file

df = file.get_source("ignore/XAUT-USDT_15m.csv")

print(df.iloc[0]["volume"])
