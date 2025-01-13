from datetime import datetime, timedelta
import os
import re
from dateutil import parser
from bisect import bisect_left

entry_time = "12:30:00"
exit_time = "14:30:00"
action = "BUY"
symbol = "NIFTY"
date_range = ["08032023", "10032023"]
strike_shift = 0

def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before

def nearest_price(call_put_list: list, spot_price):
    all_prices = []
    for row in call_put_list:
        price = row["Symbol"][-7:-2]
        all_prices.append(price)
    
    closest = take_closest(all_prices, spot_price)

    return closest





def get_avilable_dates(date_range: list)->list:
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
    for date in avilable_dates:
        dated = datetime.strftime(date, "%d%m%Y")
        avilable_dates_d.append(dated)
    return avilable_dates_d


avilableDates = get_avilable_dates(date_range)

def get_all_paths(avilable_dates):
    all_pathss = []
    for date in avilable_dates:
        path = f"./dataset/{symbol}_JF_FNO_{date}.csv"
        all_pathss.append(path)
    return all_pathss



def strat_backtest(avilable_dates: list, call_or_put: str, spot_price_symbol: str):

    data = []

    call = []
    put = []


    for path in get_all_paths(avilableDates):
        if not os.path.exists(path):
            continue

        with open(path, "r") as file:
            lines = file.readlines()
            header = lines[0].strip().split(",")
            # ['', 'Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest', 'TickTime']

            spot_price_rows = []

            for line in lines[1:]:
                values = line.strip().split(",")

                # Seprate Call and Put
                if values[1][-2] == "C":
                    call.append({header[i]: values[i] for i in range(len(header))})
                elif values[1][-2] == "P":
                    put.append({header[i]: values[i] for i in range(len(header))})

                if values[1].strip() == spot_price_symbol:
                    row_dict = {header[i]: values[i] for i in range(len(header))}
                    spot_price_rows.append(row_dict)

    spot_price = None
    for row in spot_price_rows:
        # print(row)
        if entry_time == row["Time"]:
            spot_price = row["Open"]
    
    # Add Expiry in a dict
    for row in call:
        Symbol = row["Symbol"]
        row["expiry"] = Symbol[-14:-7]
        # match_date = re.search(r"\d\d[A-Z]\d\d", Symbol)
        # match_date = parser.parse(Symbol, fuzzy=True)
        # row["expiry"] = match_date
    for row in put:
        Symbol = row["Symbol"]
        row["expiry"] = Symbol[-14:-7]
        # match_date = re.search(r"\d\d[A-Z]\d\d", Symbol)
        # match_date = parser.parse(Symbol, fuzzy=True)
        # row["expiry"] = match_date

    return call, put, spot_price


def nearest_number(priceList_call_or_put):
    for row in priceList_call_or_put:
        ...

    ...


call_data, put_data, spot_price = strat_backtest(avilableDates, "CALL", "NIFTY-I")


def get_nearest_to_spot_price(spot_price, call_put, ):
    spotPrice = spot_price
    # callPriceRow = None
    # if call_put == "CALL":
    #     for data in call_data:
    #         print(data)
    #         price = data["Open"]
    #         if price == spotPrice:
    #             callPriceRow = data
    #     ...
    # elif call_put == "PUT":

    #     ...

    # print(callPriceRow)


    callPriceRow = None
    if call_put == "CALL":
        for row in call_data:
            if row["Symbol"][-7:-2] == nearest_price(call_data, spot_price):
                print("--------------")
                callPriceRow = row


    return callPriceRow

    ...

print(get_nearest_to_spot_price(spot_price, "CALL"))