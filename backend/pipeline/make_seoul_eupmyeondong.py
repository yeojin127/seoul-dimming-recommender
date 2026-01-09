import pandas as pd

src = r"C:\Users\jyj20\Desktop\KW\2_winter\sw경진대회\data\국토교통부_전국 법정동_20250807.csv"
out = r"C:\Users\jyj20\Desktop\KW\2_winter\sw경진대회\data\seoul_eupmyeondong_codes.csv"

df = pd.read_csv(src, encoding="utf-8")
seoul = df[(df["시도명"]=="서울특별시") & (df["삭제일자"].isna())].copy()

seoul["code_str"] = seoul["법정동코드"].astype(str).str.zfill(10)

eup = seoul[seoul["읍면동명"].notna()].copy()
eup["sigunguCd"] = eup["code_str"].str[:5]
eup["bjdongCd_5"] = eup["code_str"].str[5:10]

eup[["시군구명","읍면동명","법정동코드","sigunguCd","bjdongCd_5"]].to_csv(out, index=False, encoding="utf-8-sig")
print("saved:", out, "rows:", len(eup))
