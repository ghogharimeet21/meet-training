from datetime import datetime, timedelta
import os
import time

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

def extract_nearest_expiry(data, symbol, call_or_put):
    all_exps = []
    for row in data:
        exp = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[:7]
        row["expiry"] = exp
        all_exps.append(exp)
    smallest_exp = get_smallest_expiry(all_exps, "%d%b%y")
    

    return smallest_exp
    ...


#
# if call_or_put == "CE":
#     strike_prices = []
#     for row in call_data:
#         exp = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[:7]
#         strike_price = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[7:]
#         strike_prices.append(strike_price)
#         row["expiry"] = exp
#         all_expiry.append(exp)
#     # return call_data, get_smallest_expiry(all_expiry, "%d%m%Y")
#     nearest_expiry = get_smallest_expiry(all_expiry, "%d%b%y")
#     # print(nearest_expiry)

# elif call_or_put == "PE":
#     strike_prices = []
#     for row in put_data:
#         exp = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[:7]
#         strike_price = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[7:]
#         strike_prices.append(strike_price)
#         row["expiry"] = exp
#         all_expiry.append(exp)
#     # return put_data, get_smallest_expiry(all_expiry, "%d%m%Y")
#     nearest_expiry = get_smallest_expiry(all_expiry, "%d%b%y")




def main():
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
    
    # def count_dim(lst): 
    #     count = 0 
    #     while isinstance(lst, list): 
    #         count += 1 
    #         lst = lst[0] 
    #     return count
    # print(count_dim(call_and_put_data))

    strikescall = []
    strikesput = []
    smallest_exps = []  #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    for block in call_and_put_data:
        if block[0]["Symbol"][-2:] == "CE":
            for row in block:
                # print(row)
                strike_price = row["Symbol"].replace(index, "").replace("CE", "")[7:]
                strikescall.append(strike_price)
                ...
            print("Block changing........")
            # time.sleep(5)
            smallest_exp = extract_nearest_expiry(block, index, "CE")
            smallest_exps.append(smallest_exp)
        elif block[0]["Symbol"][-2:] == "PE":
            for row in block:
                strike_price = row["Symbol"].replace(index, "").replace("CE", "")[7:]
                strikesput.append(strike_price)
                # print(row)
                ...
            print("block changing........")
            # time.sleep(5)
            smallest_exp = extract_nearest_expiry(block, index, "PE")
            smallest_exps.append(smallest_exp)
    
    nearest_strike_to_spot = [] #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    for price in spot_prices:
        price = take_closest(price, strikescall)
        nearest_strike_to_spot.append(price)
    
    print("nearest expires are", smallest_exps)
    print("nearest strike prices are", nearest_strike_to_spot)

    # make treading symbols according to nearest strike to spot and nearest expires
    symbols = []    #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    for exp, strike, opt in zip(smallest_exps, nearest_strike_to_spot, option_type):
        symbols.append(f"{index}{exp}{strike}{opt}")

    print("Symbols we got", symbols)

    # get rows according to symbol
    final_data = []
    block_count = 0
    for sym in symbols:
        for block in call_and_put_data:
            block_count += 1
            for row in block:
                if row["Symbol"] == sym:
                    final_data.append(row)
    
    for block in final_data:
        print(block)
    

    print("Block count", block_count)






if __name__ == "__main__":
    main()