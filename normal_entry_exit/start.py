from datetime import datetime, timedelta
import os

entry_time = 33300
exit_time = 34560
action = "BUY"
symbol = "sbin"
date_range = ["240604", "240608"]


def find_all_path(symbol, date_range: list=date_range):
    """
    Return Date List According to specified Date Range...[start_date, ....... , end_date]
    """
    avilable_dates = []
    from_date = datetime.strptime(date_range[0], "%y%m%d")
    to_date = datetime.strptime(date_range [1], "%y%m%d")
    while True:
        avilable_dates.append(from_date)
        from_date += timedelta(days=1)
        if from_date > to_date:
            break
    
    avilable_dates_d = []
    for date in avilable_dates:
        date = datetime.strftime(date, "%y%m%d")
        path = f"./dataset/{symbol}{date}.csv"
        avilable_dates_d.append(path)

    return avilable_dates_d

all_paths = find_all_path(symbol=symbol, date_range=date_range)
# print(all_paths)

result_dicts = []
filteredDict = {}
result_dict = {}
for path in all_paths:
    if not os.path.exists(path=path):
        continue
    
    with open(path, "r") as file:
        lines = file.readlines()
        header = lines[0].strip().split(",")
        for line in lines[1:]:
            values = line.strip().split(",")
            row_dict = {header[i]: values[i].strip() for i in range(len(header))}
            date = row_dict["date"]
            time = row_dict["time"]
            result_dicts.append(row_dict)
        ...
        entryPrice = None
        exitPrice = None
        for dict in row_dict:
            if entry_time == dict[int(time)]:                
                entryPrice = dict["open"]
            if exit_time == dict[int(time)]:
                exitPrice = dict["open"]

            if action == "BUT":
                pNl = int(exitPrice) - int(entryPrice)

            result_dict["time"] = [{"entry_price": entryPrice, "exitPrice": exitPrice, "P&L":pNl}]


print(filteredDict)

# print(all_paths[0][-10:-4])
# for date, dict in zip(all_paths, result_dicts):
#     if date[-10:-6] == dict["date"]:
#         filteredDict[date] = [dict["open"], dict["high"], dict["low"], dict["close"]]
# print(filteredDict)