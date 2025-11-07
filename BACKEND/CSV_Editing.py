import pandas as pd
import numpy as np

_RES50 = pd.read_csv(r"Projects\TOURISM\DATA\restaurants_50.csv")
_MENU50 = pd.read_csv(r"Projects\TOURISM\DATA\menus_50.csv")

_MENU50["restaurant_id"] = [f"R{i:03d}" for i in range(1, len(_MENU50) + 1)]
print(_MENU50["restaurant_id"])

_MENU50.to_csv(r"Projects\TOURISM\DATA\menus_50.csv", index=False)
# _RES50.to_csv(r"Projects\TOURISM\DATA\restaurants_50.csv", index=False)