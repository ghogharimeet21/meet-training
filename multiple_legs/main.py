from datetime import datetime, timedelta
import os
import time

def make_dict(header, values):
    return {header[i]: values[i] for i in range(len(header))}

def write_in_jsonFile(result, outputpath, fileName):
    import json
    jsondata = json.dumps(result, indent=4)
    with open(f"./{outputpath}/{fileName}.json", "w") as file:
        file.write(jsondata)

def take_closest(target, num_list):
    """Return the closest number from the given list to the target."""
    return min(num_list, key=lambda x: abs(float(x) - target))


def get_smallest_expiry(all_expiry, date_format):
    """Return the smallest date in a given list of dates."""
    date_objs = [datetime.strptime(date, date_format) for date in all_expiry]
    return datetime.strftime(min(date_objs), date_format).upper()

def get_weekly_expiry(data):
    all_dates_obj = []
    for row in data:
        exp_date = row["expiry"]
        date_obj = datetime.strptime(exp_date, "%d%b%y")
        all_dates_obj.append(date_obj)

    return datetime.strftime(sorted(list(set(all_dates_obj)))[0].date(), "%d%b%y").upper()

def get_monthly_expiry(data):
    all_dates_obj = []
    for row in data:
        exp_date = row["expiry"]
        date_obj = datetime.strptime(exp_date, "%d%b%y")
        all_dates_obj.append(date_obj)
    
    weekly = get_weekly_expiry(data)

    all_sorted_dates = sorted(all_dates_obj)

    for date in all_sorted_dates:
        weekly += timedelta(days=1)



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

def get_spot_price(spot_price_rows, entry_time):
    spot_price = None
    for row in spot_price_rows:
        if row["Time"] == entry_time:
            spot_price = float(row["Open"])
            # print("Spot_price =", spot_price)
            break
    return spot_price


def load_data(paths, spot_price_symbol, call_or_put) -> list:

    spot_price_rows = []
    data = []
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
                        data.append(make_dict(header, values))
                elif call_or_put == "PE":
                    if values[1][-2:] == "PE":
                        data.append(make_dict(header, values))
    
    return data, spot_price_rows

def get_spot_price(entry_time, spot_price_rows):
    spot_price = None
    for row in spot_price_rows:
        if row["Time"] == entry_time:
            spot_price = float(row["Open"])
    return spot_price
    ...


def extract_expiry(data, symbol, call_or_put):
    all_exps_objs = []
    for row in data:
        exp = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[:7]
        row["expiry"] = exp
        all_exps_objs.append(datetime.strptime(exp, "%d%b%y"))
    weekly = sorted(list(set(all_exps_objs)))[0]
    weekly_exp = datetime.strftime(weekly, "%d%b%y").upper()

    currunt_month = weekly.month
    currunt_month_list = list(set([date for date in all_exps_objs if date.month == currunt_month]))
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
    call_and_put_data = []
    for opt in option_type:
        data, spot_price_rows = load_data(paths, spot_price_symbol, opt)
        call_and_put_data.append(data)

    # for d in call_or_put_data:
    #     for i in d:
    #         print(i)

    # spot prices according to entry time in spot_price_symbol data
    spot_prices = []
    for entry in entry_time:
        price = get_spot_price(entry, spot_price_rows)
        spot_prices.append(price)

    print("Spot prices i got", spot_prices)
    
    def count_dim(lst): 
        count = 0 
        while isinstance(lst, list): 
            count += 1 
            lst = lst[0] 
        return count
    # print(count_dim(call_and_put_data), "D", len(call_and_put_data))

    strikescall = []
    strikesput = []
    weekly_exps = []  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    monthly_exps = [] #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    for block in call_and_put_data:
        if block[0]["Symbol"][-2:] == "CE":
            for row in block:
                # print(row)
                strike_price = row["Symbol"].replace(index, "").replace("CE", "")[7:]
                strikescall.append(strike_price)
                ...
            # print("Block changing........")
            # time.sleep(5)
            weekly_exp, monthly_exp = extract_expiry(block, index, "CE")
            weekly_exps.append(weekly_exp)
            monthly_exps.append(monthly_exp)
        elif block[0]["Symbol"][-2:] == "PE":
            for row in block:
                strike_price = row["Symbol"].replace(index, "").replace("CE", "")[7:]
                strikesput.append(strike_price)
                # print(row)
                ...
            # print("block changing........")
            # time.sleep(5)
            weekly_exp, monthly_exp = extract_expiry(block, index, "PE")
            weekly_exps.append(weekly_exp)
            monthly_exps.append(monthly_exp)
    
    nearest_strike_to_spot = [] #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    for price in spot_prices:
        price = take_closest(price, strikescall)
        nearest_strike_to_spot.append(price)
    
    print("weekly expires are", weekly_exps)
    print("monthly expires are", monthly_exps)
    print("nearest strike prices are", nearest_strike_to_spot)

    # make treading symbols according to nearest strike to spot and nearest expires
    symbols = []    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    for expe in expiry:
        for expweek, expmonth, strike, opt in zip(weekly_exps, monthly_exps, nearest_strike_to_spot, option_type):
            if expe == "WEEKLY":
                symbols.append(f"{index}{expweek}{strike}{opt}")
            elif expe == "MONTHLY":
                symbols.append(f"{index}{expmonth}{strike}{opt}")

    print("Treading Symbols we got", symbols)

    result = []
    for sym in symbols:
        for block in call_and_put_data:
            for row in block:
                if sym == row["Symbol"]:
                    result.append(row)

    write_in_jsonFile(result=result, outputpath="outputdata", fileName="result_data")

    final_result = {}

    for sym in symbols:
        for row in result:
            if row["Symbol"] == sym:
                for entime, extime in zip(entry_time, exit_time):
                    if entime == row["Time"]:
                        if sym not in final_result:
                            final_result[sym] = {}
                        final_result[sym]["entry_time"] = entime
                        final_result[sym]["entry_price"] = row["Open"]
                    elif extime == row["Time"]:
                        if sym not in final_result:
                            final_result[sym] = {}
                        final_result[sym]["exit_time"] = extime
                        final_result[sym]["exit_price"] = row["Open"]

    write_in_jsonFile(result=final_result, outputpath="outputdata", fileName="final_result")

    print(final_result)







if __name__ == "__main__":
    start_backtest()