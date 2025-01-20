from datetime import datetime, timedelta
import os

sma_windows = [2, 5]
symbol = "sbin"
date_range = ["240605", "240606"]
action = "BUY"

def get_available_dates(date_range: list, date_format: str):
    """Generate a list of dates between a given range."""
    if len(date_range) > 2:
        print(date_range[2:], "out of range")
        raise "please enter a date in range of 2......"
    
    from_date = datetime.strptime(date_range[0], date_format)
    to_date = datetime.strptime(date_range[1], date_format)
    dates = []
    while from_date <= to_date:
        dates.append(datetime.strftime(from_date, date_format))
        from_date += timedelta(days=1)
    return dates

def get_all_paths(available_dates):
    """Generate file paths for all dates."""
    # cwd = os.getcwd()
    # directiry_list = os.listdir(cwd)
    # workin = None
    # for directory in directiry_list:
    #     if directory == "dataset":
    #         workin = os.path.join()

    return [f"./dataset/{symbol}{date}.csv" for date in available_dates]


def load_data(paths):
    """Load data from all available paths."""
    file_data = []
    for path in paths:
        if not os.path.exists(path):
            print(f"path not exist ... {path}")
            continue
        
        with open(path, "r") as file:
            lines = file.readlines()
            header = lines[0].strip().split(",")
            for line in lines[1:]:
                values = line.strip().split(",")
                row_dict = {header[i]: values[i] for i in range(len(header))}
                file_data.append(row_dict)
    return file_data

def calculate_sma(prices, window):
    """Calculate SMA for a given list of prices and window size."""
    moving_averages = []
    for i in range(len(prices) - window + 1):
        window_avg = round(sum(prices[i:i + window]) / window, 2)
        moving_averages.append(window_avg)
    return moving_averages


def add_sma_to_data(file_data, sma_windows, action, frame: int=2):
    """Add SMA values to the dataset dynamically."""
    prices = [float(row["open"]) for row in file_data]
    for sma in sma_windows:
        sma_values = calculate_sma(prices, sma)
        for i, row in enumerate(file_data):
            if i >= sma - 1:
                row[f"{sma}_sma"] = sma_values[i - (sma - 1)]
            else:
                row[f"{sma}_sma"] = None


    for i in range(0 ,len(file_data) - 1, frame):
        previous = file_data[i]
        current = file_data[i + 1]

        # print(previous, "previous<<<<<<<<<<<<<<<<<<<<")
        # print(current, "current<<<<<<<<<<<<<<<<<<<<")

        sma_one = f"{sma_windows[0]}_sma"
        sma_two = f"{sma_windows[1]}_sma"

        previous_price = float(previous["open"])
        current_price = float(current["open"])

        previous_sma_one, previous_sma_two = previous[ sma_one ], previous[ sma_two ]
        current_sma_one, current_sma_two = current[ sma_one ], current[ sma_two ]

        if (previous_sma_one == None) or (previous_sma_two == None) or (current_sma_one == None) or (current_sma_two == None):
            continue
        else:
            if previous_sma_one < current_sma_one and previous_sma_two > current_sma_two:
                current["reason"] = "cross over"
            elif previous_sma_one > current_sma_one and previous_sma_two < current_sma_two:
                current["reason"] = "cross down"
            ...
        pnl = round(previous_price - current_price, 2) if action == "BUY" else round(current_price - previous_price, 2)
        current["P&L"] = pnl

    return file_data


dates = get_available_dates(date_range=date_range, date_format="%y%m%d")
paths = get_all_paths(dates)

file_data = load_data(paths)

file_data_with_sma = add_sma_to_data(file_data, sma_windows, "SELL", 2)


for row in file_data_with_sma:
    # key = "reason"
    # if key in row and row["reason"] == "cross down":
    #     print(row)
    
    print(row)