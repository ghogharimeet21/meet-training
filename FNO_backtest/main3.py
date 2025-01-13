from datetime import datetime, timedelta
import os



entry_time = "12:30:00"
exit_time = "14:30:00"
action = "BUY"
symbol = "NIFTY"
date_range = ["08032023", "10032023"]
strike_shift = 0
target = float(5)
stop_loss = float(5)

def takeClosest(num,collection):
    return min(collection,key=lambda x:abs(float(x)-num))

def get_smallest_expiry(all_expiry):
    dateobjs = []
    for date in all_expiry:
        # print("---------", date, type(date), "---------------")
        dateobj = datetime.strptime(date, "%d%b%y")
        dateobjs.append(dateobj)
    nearestDate = datetime.strftime(min(dateobjs), "%d%b%y").upper()

    return nearestDate
    ...

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

def strat_backtest(avilable_paths: list, call_or_put: str, spot_price_symbol: str, action):

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
                if call_or_put == "CE":
                    if values[1][-2] == "C":
                        call.append({header[i]: values[i] for i in range(len(header))})
                elif call_or_put == "PE":
                    if values[1][-2] == "P":
                        put.append({header[i]: values[i] for i in range(len(header))})

            # Add expires in a dict
            all_expiry = []
            if call_or_put == "CE":
                for row in call:
                    Symbol = row["Symbol"].replace(symbol, "").replace("CE", "")
                    row["expiry"] = Symbol[0:7]
                    expiry = row["expiry"]
                    row["strike"] = float(Symbol[7:])
                    strike = row["strike"]
                    all_expiry.append(expiry)

            elif call_or_put == "PE":
                for row in put:
                    Symbol = row["Symbol"].replace(symbol, "").replace("PE", "")
                    row["expiry"] = Symbol[0:7]
                    expiry = row["expiry"]
                    row["strike"] = float(Symbol[7:])
                    strike = row["strike"]
                    all_expiry.append(expiry)

            smallestExpiry = get_smallest_expiry(all_expiry)

            # Get Spot Price
            spot_price = None
            for row in spot_price_rows:
                if row["Time"] == entry_time:
                    spot_price = float(row["Open"])
            

            rows_i_want = []
            strike_prices = []
            if call_or_put == "CE":
                for row in call:
                    if row["expiry"] == smallestExpiry:
                        strike_prices.append(row["strike"])
                        rows_i_want.append(row)
            elif call_or_put == "PE":
                for row in put:
                    if row["expiry"] == smallestExpiry:
                        strike_prices.append(row["strike"])
                        rows_i_want.append(row)



            closest_strike = round(takeClosest(spot_price, strike_prices))

            finalSymbol = f"{symbol}{smallestExpiry}{closest_strike}{call_or_put}"


            print(f"Nearest expiry in {call_or_put} is {smallestExpiry}")
            print("Spot Price =", spot_price)
            print("Closest strike price", closest_strike)
            print("Symbol =", finalSymbol)



            all_data = []
            if call_or_put == "CE":
                for row in call:
                    if row["Symbol"] == finalSymbol:
                        all_data.append(row)
            
            elif call_or_put == "PE":
                for row in put:
                    if row["Symbol"] == finalSymbol:
                        all_data.append(row)

            result = {
                "entry_time": entry_time,
                "entry_price":None,
                "exit_time": exit_time,
                "exit_price": None,
                "P&L": None,
                "exit_reason": None,
                "target_price": None,
                "target_stop_loss": None
            }

            for data in all_data:
                
                if entry_time == data["Time"]:
                    result["entry_price"] = float(data["Open"])

                    target_price =  float(result["entry_price"] + target if action == "BUY" else result["entry_price"] - target)
                    target_stop_loss = float(result["entry_price"] - stop_loss if action == "BUY" else result["entry_price"] + stop_loss)
                    result["target_price"] = target_price
                    result["target_stop_loss"] = target_stop_loss

                    if exit_time == data["Time"]:
                        result["exit_price"] = float(data["Open"])
                        result["exit_reason"] = "Normal Exit"
                        result["P&L"] = result["exit_price"] - result["entry_price"] if action == "BUY" else result["entry_price"] - result["exit_price"]

                    else:

                        high = float(data["High"])
                        low = float(data["Low"])

                        if (result["target_price"] != None) and (result["target_stop_loss"] != None):

                            if action == "BUY":

                                if high >= result["target_price"]:
                                    result["exit_price"] = high
                                elif low <= result["target_stop_loss"]:
                                    result["exit_price"] = low
                            
            
            print(result)






strat_backtest(all_paths, "PE", "NIFTY-I", "BUY")