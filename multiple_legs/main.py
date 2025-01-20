from datetime import datetime, timedelta
import os

def make_dict(header, values):
    return {header[i]: values[i] for i in range(len(header))}


def take_closest(target, num_list):
    """Return the closest number from the given list to the target."""
    return min(num_list, key=lambda x: abs(float(x) - target))


def get_smallest_expiry(all_expiry, date_format):
    """Return the smallest date in a given list of dates."""
    date_objs = [datetime.strptime(date, date_format) for date in all_expiry]
    return datetime.strftime(min(date_objs), date_format).upper()


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


def get_all_dataset_paths(dataset_folder_path, date_range):
    """Generate file paths for all dates."""
    cwd = os.getcwd()
    dataset_path = os.path.join(cwd, dataset_folder_path)
    files = os.listdir(dataset_folder_path)
    paths = []
    for file in files:
        for date in date_range:
            if date in file:
                paths.append(f"{os.path.join(dataset_path, file)}")
        ...

    return paths


def load_data(symbol, paths, spot_price_symbol, call_or_put, action):


    spot_price_rows = []
    call_data = []
    put_data = []
    all_expiry = []


    for path in paths:
        if not os.path.exists(path):
            continue
        
        with open(path, "r") as file:
            lines = file.readlines()
            header = lines[0].strip().split(",")
            # ['', 'Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest', 'TickTime', '', '']
            for line in lines:
                values = line.strip().split(",")
                if values[1] == spot_price_symbol:
                    spot_price_rows.append(make_dict(header, values))
                    ...
                
                if call_or_put == "CE":
                    if values[1][-2:] == "CE":
                        call_data.append(make_dict(header, values))
                elif call_or_put == "PE":
                    if values[1][-2:] == "PE":
                        put_data.append(make_dict(header, values))
            
            spot_price = None
            for row in spot_price_rows:
                if row["Time"] == entry_time:
                    spot_price = float(row["Open"])
            

            if call_or_put == "CE":
                strike_prices = []
                for row in call_data:
                    exp = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[:7]
                    strike_price = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[7:]
                    strike_prices.append(strike_price)
                    row["expiry"] = exp
                    all_expiry.append(exp)
                # return call_data, get_smallest_expiry(all_expiry, "%d%m%Y")
                nearest_expiry = get_smallest_expiry(all_expiry, "%d%b%y")
                closest_strike = take_closest(spot_price, strike_prices)
            
            elif call_or_put == "PE":
                strike_prices = []
                for row in put_data:
                    exp = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[:7]
                    strike_price = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[7:]
                    strike_prices.append(strike_price)
                    row["expiry"] = exp
                    all_expiry.append(exp)
                # return put_data, get_smallest_expiry(all_expiry, "%d%m%Y")
                nearest_expiry = get_smallest_expiry(all_expiry, "%d%b%y")
                closest_strike = take_closest(spot_price, strike_prices)
                



spot_price_symbol = "NIFTY-I"
index = "NIFTY"
date_range = ["08032023", "10032023"]
entry_time = ["10:30:00", "11:00:00"]
exit_time = ["14:30:00", "15:15:00"]
tread_action = ["BUY", "SELL"]
option_type = ["PE", "CE"]
strike = ["ATM", "ATM + 1"]
expiry = ["WEEKLY", "MONTHLY"]

dates = get_available_dates(date_range=date_range, date_format="%d%m%Y")

paths = get_all_dataset_paths("dataset", dates)

load_data(index, paths, spot_price_symbol, "CE", "BUY")