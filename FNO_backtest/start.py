from datetime import datetime, timedelta
import os


entry_time = "10:30:00"
exit_time = "14:30:00"
action = "BUY"
symbols = ["NIFTY", "BANKNIFTY"]
date_range = ["08032023", "10032023"]
strike_shift = 0





def find_all_path(symbols=symbols, date_range: list = date_range):
    """
    Return Date and Path List According to specified Date Range...[/start_date_path, ....... , /end_date_path]
    """
    avilable_dates = []
    from_date = datetime.strptime(date_range[0], "%d%m%Y")
    to_date = datetime.strptime(date_range[1], "%d%m%Y")
    while True:
        avilable_dates.append(from_date)
        from_date += timedelta(days=1)
        if from_date > to_date:
            break
    avilable_dates_d = []
    avilable_paths = []
    for date in avilable_dates:
        dated = datetime.strftime(date, "%d%m%Y")
        avilable_dates_d.append(dated)

    for sym in symbols:
        for datef in avilable_dates:
            datex = datetime.strftime(datef, "%d%m%Y")
            path = f"./dataset/{sym}_JF_FNO_{datex}.csv"
            avilable_paths.append(path)

    return avilable_paths, avilable_dates_d

all_paths, all_dates = find_all_path()






def get_data_by_symbol(file_paths: list=all_paths, symbols: list=symbols, date_range: list=all_dates):

    data = []

    treading_symbols_ce = []
    treading_symbols_pe = []

    for path in file_paths:
        if not os.path.exists(path=path):
            continue

        with open(file=path, mode="r") as file:
            lines = file.readlines()
            header = lines[0].strip().split(",")
            # ['', 'Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest', 'TickTime']
            for line in lines:
                line = line.strip().split(",")

                for sym in symbols:
                    if line[1].find(sym) != -1:
                        if line[1][-2] == "P":
                            treading_symbols_pe.append({header[i]: line[i].strip() for i in range(len(header))})
                        elif line[1][-2] == "C":
                            treading_symbols_ce.append({header[i]: line[i].strip() for i in range(len(header))})

    for ce in treading_symbols_ce:
        strike_price = ce["Symbol"][-7:-2]
        ce["strike_price"] = int(strike_price)
    for pe in treading_symbols_pe:
        strike_price = pe["Symbol"][-7:-2]
        pe["strike_price"] = int(strike_price)

    return treading_symbols_ce, treading_symbols_pe
    ...



call_symbol, put_symbol = get_data_by_symbol()


# def convert_datetime_object(data: list):
#     datetimeObjs = []
#     datetimeStrings = []
#     for row in data:
#         time = row["Time"]
#         timeobj = datetime.strptime(time, "%H:%M:%S")
#         datetimeObjs.append(timeobj)

#         timeString = timeobj
#         timeS = datetime.strftime(timeString, "%H:%M:%S")
#         datetimeStrings.append(timeS)
#     return datetimeObjs, datetimeStrings

# call_dates_objs, call_dates_strings = convert_datetime_object(call_symbol)
# put_dates_objs, put_dates_strings = convert_datetime_object(put_symbol)

def get_spot_price(Data: list):
    for row in Data:
        strike_price = row["strike_price"]
        if row["Time"] == entry_time:
            entry_time_price = strike_price
        if row["Time"] == exit_time:
            exit_time_price = strike_price
    
    return entry_time_price, exit_time_price



def get_nearest_price(data: list, entryPrice, keyname="strike_price"):
    all_prices = []
    for row in data:
        price = row[keyname]
        all_prices.append(price)
    
    return all_prices[min(range(len(all_prices)), key = lambda i: abs(all_prices[i]-entryPrice))], all_prices


