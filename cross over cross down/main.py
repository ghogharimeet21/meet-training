from datetime import datetime, timedelta
import os


sma = 2

symbol = "sbin"
date_range = ["240604", "240606"]

def get_available_dates(date_range):
    """Generate a list of dates between a given range."""
    from_date = datetime.strptime(date_range[0], "%y%m%d")
    to_date = datetime.strptime(date_range[1], "%y%m%d")
    dates = []
    while from_date <= to_date:
        dates.append(datetime.strftime(from_date, "%y%m%d"))
        from_date += timedelta(days=1)
    return dates

def get_all_paths(available_dates):
    """Generate file paths for all dates."""
    return [f"./dataset/{symbol}{date}.csv" for date in available_dates]


dates = get_available_dates(date_range)
paths = get_all_paths(dates)


file_data = []
for path in paths:
    if not os.path.exists(path):
        continue

    with open(path, "r") as file:
        lines = file.readlines()
        header = lines[0].strip().split(",")
        # ['', 'time', 'date', 'symbol', 'open', 'high', 'low', 'close']

        for line in lines[1:]:
            values = line.strip().split(",")
            row_dict = {header[i]: values[i] for i in range(len(header))}
            # print(row_dict)
            date = row_dict["date"]
            # file_data[date] = row_dict
            file_data.append(row_dict)
        print(file_data)

def sma_finder(prices, sma, datafile: list):
    moving_averages = []

    i = 0
    while i < len(prices) - sma + 1:
        
        window = prices[i : i + sma]
        window_average = round(sum(window) / sma, 2)
        moving_averages.append(window_average)

        i += 1

    x= 0
    for data in file_data:
        if datafile.index(data) in list(range(sma)):
            continue
            ...
        data[str(sma)+"sma"] = moving_averages[x]
        x += 1

    return moving_averages


# calculate moving avrage
def add_sma(smaone: float, smatwo: float, file_datas: list):
    prices = []
    for row in file_datas:
        open_price = row["open"]
        prices.append(float(open_price))



        ...
