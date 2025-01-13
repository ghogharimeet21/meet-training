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


            # find P%L for all this

            # totalRows = 0
            # for row in rows_i_want:
            #     totalRows += 1

            # totalrows = 0
            # entry_price = None
            # for row in rows_i_want:
            #     if entry_time == row["Time"]:
            #         totalrows += 1
            #         entry_price = row["Open"]
            # print(entry_price)
            # print("Total Number of rows match in nearest strike", totalRows)
            # print("Tatal rows match", totalrows)


            all_pnl_data = []
            if call_or_put == "CE":
                for row in call:
                    if row["Symbol"] == finalSymbol:
                        all_pnl_data.append(row)
            
            elif call_or_put == "PE":
                for row in put:
                    if row["Symbol"] == finalSymbol:
                        all_pnl_data.append(row)

            for data in all_pnl_data:
                if data["Time"] == entry_time:
                    entry_price = data["Open"]
                if data["Time"] == exit_time:
                    exit_price = data["Open"]
            print("Entry Price", entry_price, ",", "Exit Price", exit_price)

            PNL = None
            if action == "BUY":
                PNL = round(float(exit_price) - float(entry_price), 2)
            elif action == "SELL":
                PNL = round(float(entry_price) - float(exit_price), 2)

            print(f"For {action} P&L is {PNL}")

            



strat_backtest(all_paths, "CE", "NIFTY-I", "SELL")