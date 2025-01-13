from datetime import datetime, timedelta
import os


entry_time = "11:30:00"
exit_time = "14:30:00"
action = "BUY"
symbol = "NIFTY"
date_range = ["08032023", "10032023"]
strike_shift = 0


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



def strat_backtest(avilable_dates: list):

    data = []

    call = []
    put = []


    for date in avilable_dates:
        path = f"./dataset/{symbol}_JF_FNO_{date}.csv"

        if not os.path.exists(path):
            continue

        with open(path, "r") as file:
            lines = file.readlines()
            header = lines[0].strip().split(",")
            # ['', 'Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest', 'TickTime']

            for line in lines[1:]:
                value = line.strip().split(",")
                if value[1].strip() == "NIFTY-I":
                    data.append(value)

                # Seprate call put
                if value[1][-2] == "C":
                    call.append(value)
                elif value[1][-2] == "P":
                    put.append(value)

            # Get Spot Price
            spot_price_row = None
            for row in data:
                if entry_time == row[3]:
                    spot_price_row = row


    return spot_price_row, call, put


avilable_dates = get_avilable_dates(date_range)

spot_price_row, call, put = strat_backtest(avilable_dates)

spot_price = spot_price_row[4]


for row in call:
    print(row[1][-14:-7])




def get_nearest_price(call_or_put: str):

    prices = []

    if call_or_put == "CALL":
        for row in call:
            expiry = row[1][-14:-7]

            price = row[1][-7:-2]
            prices.append(price)
        nearest_price = prices[min(range(len(prices)), key = lambda i: abs(float(prices[i]) - float(spot_price) ))]
    
    elif call_or_put == "PUT":
            for row in put:
                expiry = row[1][-14:-7]

                price = row[1][-7:-2]
                prices.append(price)
            nearest_price = prices[min(range(len(prices)), key = lambda i: abs(float(prices[i]) - float(spot_price)))]
            ...
    ...
    return nearest_price



# print(f"nearest Put price near {spot_price} is", get_nearest_price("CALL"))