import pandas as pd

res_df = pd.read_csv(r"C:\python\Projects\TOURISM\AI\Data-master\restaurants_100_improved.csv")

res_df = res_df.drop(['price_range', 'cuisine'], axis=1)
res_df.to_csv()
print(res_df.head().to_string())