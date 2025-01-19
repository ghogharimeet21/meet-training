from datetime import datetime, timedelta
import os

sma_windows = [2, 4]
symbol = "sbin"
date_range = ["240605", "240606"]

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
    return [f"./cross over cross down/dataset/{symbol}{date}.csv" for date in available_dates]


dates = get_available_dates(date_range)
paths = get_all_paths(dates)


def load_data(paths):
    """Load data from all available paths."""
    file_data = []
    for path in paths:
        if not os.path.exists(path):
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


def add_sma_to_data(file_data, sma_windows):
    """Add SMA values to the dataset dynamically."""
    prices = [float(row["open"]) for row in file_data]
    for sma in sma_windows:
        sma_values = calculate_sma(prices, sma)
        for i, row in enumerate(file_data):
            if i >= sma - 1:
                row[f"{sma}_sma"] = sma_values[i - (sma - 1)]
            else:
                row[f"{sma}_sma"] = None
    return file_data



file_data = load_data(paths)

file_data_with_sma = add_sma_to_data(file_data, sma_windows)


for row in file_data_with_sma:
    print(row)