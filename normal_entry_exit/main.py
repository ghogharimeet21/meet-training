from datetime import datetime, timedelta
import os



entry_time = 33300
exit_time = 55500
action = "SELL"
symbol = ["bn25dec2450500ce",""]
date_range = ["240603", "240605"]
target = 15
stop_loss = 5




def find_all_path(symbol=symbol, date_range: list = date_range):
    """
    Return Date and Path List According to specified Date Range...[/start_date_path, ....... , /end_date_path]
    """
    avilable_dates = []
    from_date = datetime.strptime(date_range[0], "%y%m%d")
    to_date = datetime.strptime(date_range[1], "%y%m%d")
    while True:
        avilable_dates.append(from_date)
        from_date += timedelta(days=1)
        if from_date > to_date:
            break
    avilable_dates_d = []
    avilable_paths = []
    for date in avilable_dates:
        date = datetime.strftime(date, "%y%m%d")
        avilable_dates_d.append(date)
        path = f"./normal_entry_exit/dataset/{symbol}{date}.csv"
        avilable_paths.append(path)

    return avilable_paths, avilable_dates_d


all_paths, all_dates = find_all_path(symbol=symbol, date_range=date_range)



final_result = {}


for path, date in zip(all_paths, all_dates):
    if not os.path.exists(path=path):
        continue
    with open(file=path, mode="r") as file:
        lines = file.readlines()
        header = lines[0].strip().split(",")
        # ['', 'time', 'date', 'symbol', 'open', 'high', 'low', 'close']

        for line in lines[1:]:
            line = line.strip().split(",")
            if date == line[2]:

                if date not in final_result:
                    final_result[date] = {
                        "entry_time": entry_time,
                        "entry_price": None,
                        "exit_time": exit_time,
                        "exit_price": None,
                        "pnl": None,
                        "exit_reason":None,
                        "target_price": None,
                        "stoploss_price": None,
                    }


                if (int(line[1])==entry_time):
                    entry_price = float(line[4])
                    target_price = entry_price+target if action == "BUY" else entry_price-target
                    stoploss_price = entry_price-stop_loss if action == "BUY" else entry_price+stop_loss
                    final_result[date]["entry_price"] = entry_price
                    final_result[date]["target_price"] = target_price
                    final_result[date]["stoploss_price"] = stoploss_price

                elif (int(line[1]) == exit_time):
                    final_result[date]["exit_price"] = line[4]
                    final_result[date]["exit_reason"] = "normal exit"

                else:
                    high_price = float(line[5])
                    low_price = float(line[6])
                    entry_price = final_result[date]["entry_price"]

                    lage_exit_time = line[1]

                    if action == "BUY":

                        if (high_price >= final_result[date]["target_price"]):
                            final_result[date]["exit_time"] = lage_exit_time
                            final_result[date]["exit_price"] = high_price
                            final_result[date]["exit_reason"] = "Target hitt"
                            final_result[date]["pnl"] = round(high_price - entry_price, 2)
                            break
                        elif (low_price <= final_result[date]["stoploss_price"]):
                            final_result[date]["exit_time"] = lage_exit_time
                            final_result[date]["exit_price"] = low_price
                            final_result[date]["exit_reason"] = "Stop loass Hitt"
                            final_result[date]["pnl"] = round(low_price - entry_price, 2)                    
                            break
                    if action == "SELL":

                        if (high_price >= final_result[date]["stoploss_price"]):
                            final_result[date]["exit_time"] = lage_exit_time
                            final_result[date]["exit_price"] = high_price
                            final_result[date]["exit_reason"] = "Stop Loass hitt"
                            final_result[date]["pnl"] = round(entry_price - high_price, 2)
                            break
                        elif (low_price <= final_result[date]["target_price"]):
                            final_result[date]["exit_time"] = lage_exit_time
                            final_result[date]["exit_price"] = low_price
                            final_result[date]["exit_reason"] = "Target Hitt"
                            final_result[date]["pnl"] = round(entry_price - low_price, 2)                    
                            break


print(final_result)

for k, v in final_result.items():
    print("Date =",k, ":", v)
































# for path, date in zip(all_paths, all_dates):

#     if not os.path.exists(path=path):
#         continue

#     with open(file=path, mode="r") as file:
#         lines = file.readlines()
#         header = lines[0].strip().split(",")

#         for line in lines[1:]:
#             values = line.strip().split(",")
#             row_dict = {header[i]: values[i].strip() for i in range(len(header))}
#             resultDicts.append(row_dict)

#             if date == row_dict["date"]:
#                 filteredDicts.append({
#                     date:{row_dict["time"]:[row_dict["open"], row_dict["high"], row_dict["low"], row_dict["close"]]}
#                 })

# print(filteredDicts)
# # entryPrice = None
# # exitPrice = None
# # for row in filteredDicts:
# #     for key, val in row.items():
# #         print(key, ":", val)
# #         if str(key) in all_dates:


# print(result_dict)
