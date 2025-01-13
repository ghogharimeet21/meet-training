from datetime import datetime, timedelta
import os



entry_time = "11:30:00"
exit_time = "15:30:00"
action = "BUY"
symbol = "NIFTY"
date_range = ["08032023", "10032023"]
strike_shift = 0


def takeClosest(num,collection):
    return min(collection,key=lambda x:abs(float(x)-num))



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


all_paths = get_all_paths(avilableDates)

def strat_backtest(avilable_paths: list, call_or_put: str, spot_price_symbol: str):

    call = []
    put = []

    result_symbols = []

    for path in avilable_paths:
        if not os.path.exists(path):
            continue

        with open(path, "r") as file:
            lines = file.readlines()
            header = lines[0].strip().split(",")
            # ['', 'Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest', 'TickTime']

            spot_price_rows = []

            for line in lines[1:]:
                values = line.strip().split(",")

                # Get Spot price row
                if values[1].strip() == spot_price_symbol:
                    row_dict = {header[i]: values[i] for i in range(len(header))}
                    spot_price_rows.append(row_dict)

                # Seprate Call and Put
                if call_or_put == "CALL":
                    if values[1][-2] == "C":
                        call.append({header[i]: values[i] for i in range(len(header))})
                elif call_or_put == "PUT":
                    if values[1][-2] == "P":
                        put.append({header[i]: values[i] for i in range(len(header))})

            # Add expires in a dict
            if call_or_put == "CALL":
                for row in call:
                    Symbol = row["Symbol"]
                    row["expiry"] = Symbol[-14:-7]
            elif call_or_put == "PUT":
                for row in put:
                    Symbol = row["Symbol"]
                    row["expiry"] = Symbol[-14:-7]

        # Get Spot Price
        spot_price = None
        for row in spot_price_rows:
            if row["Time"] == entry_time:
                spot_price = float(row["Open"])
        
        print("Spot Price =", spot_price)
        # Get nearest strike from a given call or put
        if call_or_put == "CALL":
            nearest_call_price = None
            call_price_list = []
            for row in call:
                prices = row["Symbol"][-7:-2]
                expiry = row["expiry"]
                call_price_list.append(prices)
            nearest_call_price = takeClosest(spot_price, call_price_list)
            symbolPut = f"{symbol}{expiry}{nearest_call_price}CE"
            print(symbolPut)
            print("Nearest call strike", nearest_call_price)
        elif call_or_put == "PUT":
            nearest_put_price = None
            put_price_list = []
            for row in put:
                prices = row["Symbol"][-7:-2]
                expiry = row["expiry"]
                put_price_list.append(prices)
            nearest_put_price = takeClosest(spot_price, put_price_list)
            symbolCall = f"{symbol}{expiry}{nearest_put_price}PE"
            print(symbolCall)
            print("Nearest Put strike =", nearest_put_price, ", expity =",expiry)

            

        




strat_backtest(all_paths, "PUT", "NIFTY-I")