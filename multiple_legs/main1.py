from datetime import datetime, timedelta
import os
import time


def make_dict(header, values):
    return {header[i]: values[i] for i in range(len(header))}

def get_strike_expiry(symbol: str, index, option_type):
    strike = symbol.replace(index, "").replace(option_type, "")[7:]
    expiry = symbol.replace(index, "").replace(option_type, "")[:7]

    return strike, expiry


def write_in_jsonFile(result, outputpath, fileName):
    import json

    jsondata = json.dumps(result, indent=4)
    with open(f"./{outputpath}/{fileName}.json", "w") as file:
        file.write(jsondata)


def take_closest(target, num_list):
    """Return the closest number from the given list to the target."""
    return min(num_list, key=lambda x: abs(float(x) - target))


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
            if (date in file) and (file.endswith(".csv")):
                paths.append(f"{os.path.join(dataset_path, file)}")
        ...

    return paths


def load_data(paths, spot_price_symbol) -> dict:

    spot_price_rows = []
    dataset_mapper = {}
    for path in paths:
        if not os.path.exists(path):
            continue

        with open(path, "r") as file:
            lines = file.readlines()
            header = lines[0].strip().split(",")
            # ['', 'Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest', 'TickTime', '', '']

            
            for line in lines[1:]:

                values = line.strip().split(",")

                symbol = values[1]
                date = values[2]
                time = values[3]
                open_price = values[4]
                high_price = values[5]
                low_price = values[6]
                close_price = values[7]

                if values[1][-2:] == "CE":
                    
                    # initialized the if not available in the mapper
                    if date not in dataset_mapper:
                        dataset_mapper[date] = {
                            "CALL": {},
                            "CALL_DETAILS": {
                                "avilable_strikes": [],
                                "avilable_expires": []
                                },
                            "PUT": {},
                            "PUT_DETAILS": {
                                "avilable_strikes": [],
                                "avilable_expires": []
                            },
                            "NIFTY-I": {},
                        }
                    # Intialize symbol.
                    if symbol not in dataset_mapper[date]["CALL"]:
                        dataset_mapper[date]["CALL"][symbol] = {}

                    
                    # initialize time
                    if time not in dataset_mapper[date]["CALL"][symbol]:
                        dataset_mapper[date]["CALL"][symbol][time] = []
                    
                    dataset_mapper[date]["CALL"][symbol][time] = [open_price, high_price, low_price, close_price]

                elif values[1][-2:] == "PE":
                    # initialized the if not available in the mapper
                    if date not in dataset_mapper:
                        dataset_mapper[date] = {
                            "CALL": {},
                            "CALL_DETAILS": {
                                "avilable_strikes": [],
                                "avilable_expires": []
                                },
                            "PUT": {},
                            "PUT_DETAILS": {
                                "avilable_strikes": [],
                                "avilable_expires": []
                            },
                            "NIFTY-I": {},
                        }
                    # Intialize symbol.
                    if symbol not in dataset_mapper[date]["PUT"]:
                        dataset_mapper[date]["PUT"][symbol] = {}
                    
                    # initialize time
                    if time not in dataset_mapper[date]["PUT"][symbol]:
                        dataset_mapper[date]["PUT"][symbol][time] = []
                    
                    dataset_mapper[date]["PUT"][symbol][time] = [open_price,high_price, low_price, close_price]

                elif values[1] == spot_price_symbol:
                    # initialized the if not available in the mapper
                    if date not in dataset_mapper:
                        dataset_mapper[date] = {
                            "CALL": {},
                            "CALL_DETAILS": {
                                "avilable_strikes": [],
                                "avilable_expires": []
                                },
                            "PUT": {},
                            "PUT_DETAILS": {
                                "avilable_strikes": [],
                                "avilable_expires": []
                            },
                            "NIFTY-I": {},
                        }
                    # Intialize symbol.
                    if symbol not in dataset_mapper[date][spot_price_symbol]:
                        dataset_mapper[date][spot_price_symbol][symbol] = {}
                    
                    # initialize time
                    if time not in dataset_mapper[date][spot_price_symbol][symbol]:
                        dataset_mapper[date][spot_price_symbol][symbol][time] = []
                    
                    dataset_mapper[date][spot_price_symbol][symbol][time] = [open_price,high_price, low_price, close_price]

    return dataset_mapper


def get_spot_price(entry_time, spot_price_rows):
    spot_price = None
    for row in spot_price_rows:
        if row["Time"] == entry_time:
            spot_price = float(row["Open"])
    return spot_price
    ...


def extract_expiry(data, symbol, option_type):
    all_exps_objs = []
    for row in data:
        exp = row["Symbol"].replace(symbol, "").replace(option_type, "")[:7]
        row["expiry"] = exp
        all_exps_objs.append(datetime.strptime(exp, "%d%b%y"))
    weekly = sorted(list(set(all_exps_objs)))[0]
    weekly_exp = datetime.strftime(weekly, "%d%b%y").upper()

    currunt_month = weekly.month
    currunt_month_list = list(
        set([date for date in all_exps_objs if date.month == currunt_month])
    )
    sortedList = sorted(currunt_month_list)
    monthly_expiry = sortedList[-1]
    monthly_exp = datetime.strftime(monthly_expiry.date(), "%d%b%y").upper()

    return weekly_exp, monthly_exp


def start_backtest():
    spot_price_symbol = "NIFTY-I"
    index = "NIFTY"
    date_range = ["08032023", "10032023"]
    entry_time = ["10:30:00", "9:45:00"]
    exit_time = ["14:30:00", "15:15:00"]
    tread_action = ["BUY", "SELL"]
    option_type = ["PE", "CE"]
    strike = ["ATM", "ATM + 1"]
    expiry = ["WEEKLY", "MONTHLY"]

    dates = get_available_dates(date_range=date_range, date_format="%d%m%Y")

    paths = get_all_dataset_paths("dataset", dates)

    # got data according to input option_type in a list
    dataset_mapper = load_data(paths, spot_price_symbol)

    # write_in_jsonFile(dataset_mapper, "outputdata", "data")

    


if __name__ == "__main__":
    start_backtest()
