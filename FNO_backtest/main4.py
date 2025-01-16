from datetime import datetime, timedelta
import os


entry_time = "11:30:00"
exit_time = "15:30:00"
action = "BUY"
symbol = "NIFTY"
date_range = ["08032023", "10032023"]
strike_shift = 0
target = float(10)
stop_loss = float(5)

def take_closest(target, num_list):
    """Return the closest number from the given list to the target."""
    return min(num_list, key=lambda x: abs(float(x) - target))

def get_smallest_expiry(all_expiry):
    """Return the smallest date in a given list of dates."""
    date_objs = [datetime.strptime(date, "%d%b%y") for date in all_expiry]
    return datetime.strftime(min(date_objs), "%d%b%y").upper()

def get_available_dates(date_range):
    """Generate a list of dates between a given range."""
    from_date = datetime.strptime(date_range[0], "%d%m%Y")
    to_date = datetime.strptime(date_range[1], "%d%m%Y")
    dates = []
    while from_date <= to_date:
        dates.append(datetime.strftime(from_date, "%d%m%Y"))
        from_date += timedelta(days=1)
    return dates

def get_all_paths(available_dates):
    """Generate file paths for all dates."""
    return [f"./dataset/{symbol}_JF_FNO_{date}.csv" for date in available_dates]

def calculate_pnl(relevant_data, entry_time, action, target, stop_loss):
    """
    Calculate P&L for a given symbol based on target and stop-loss.
    """
    result = {
        "entry_time": entry_time,
        "entry_price": None,
        "exit_time": None,
        "exit_price": None,
        "P&L": None,
        "exit_reason": None,
        "target_price": None,
        "stop_loss_price": None
    }

    for row in relevant_data:
        high = float(row["High"])
        low = float(row["Low"])
        time = row["Time"]

        if row["Time"] == entry_time:
            entry_price = float(row["Open"])
            result["entry_price"] = entry_price

            if action == "BUY":
                result["target_price"] = round(float(entry_price + target), 2)
                result["stop_loss_price"] = round(float(entry_price - stop_loss), 2)
                continue
            elif action == "SELL":
                result["target_price"] = round(float(entry_price - target), 2)
                result["stop_loss_price"] = round(float(entry_price + stop_loss), 2)
                continue
            

        if (result["target_price"] == None) and (result["stop_loss_price"] == None):
            continue


        if action == "BUY":
            if high >= result["target_price"]:
                result["exit_price"] = high
                result["exit_time"] = time
                result["exit_reason"] = "Target Hit"
                break
            elif low <= result["stop_loss_price"]:
                result["exit_price"] = low
                result["exit_time"] = time
                result["exit_reason"] = "Stop-Loss Hit"
                break
        elif action == "SELL":
            if low <= result["target_price"]:
                result["exit_price"] = low
                result["exit_time"] = time
                result["exit_reason"] = "Target Hit"
                break
            elif high >= result["stop_loss_price"]:
                result["exit_price"] = high
                result["exit_time"] = time
                result["exit_reason"] = "Stop-Loss Hit"
                break

    # Calculate P&L
    if result["exit_price"] is not None:
        if action == "BUY":
            result["P&L"] = round(result["exit_price"] - result["entry_price"], 2)
        elif action == "SELL":
            result["P&L"] = round(result["entry_price"] - result["exit_price"], 2)

    return result


def strat_backtest(available_paths, call_or_put, spot_price_symbol, action):
    for path in available_paths:
        if not os.path.exists(path):
            # print(f"File not found: {path}")
            continue

        with open(path, "r") as file:
            lines = file.readlines()
            header = lines[0].strip().split(",")
            # ['', 'Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest', 'TickTime', '', '']

            spot_price_rows = []
            call = []
            put = []
            all_expiry = []

            for line in lines[1:]:
                values = line.strip().split(",")
                if values[1].strip() == spot_price_symbol:
                    spot_price_rows.append({header[i]: values[i] for i in range(len(header))})
                elif call_or_put == "CE" and values[1].endswith("CE"):
                    call.append({header[i]: values[i] for i in range(len(header))})
                elif call_or_put == "PE" and values[1].endswith("PE"):
                    put.append({header[i]: values[i] for i in range(len(header))})

            # extract all expiries from a symbol
            if call_or_put == "CE":
                for row in call:
                    exp = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[:7]
                    row["expiry"] = exp
                    all_expiry.append(row["expiry"])
            elif call_or_put == "PE":
                for row in put:
                    exp = row["Symbol"].replace(symbol, "").replace(call_or_put, "")[:7]
                    row["expiry"] = exp
                    all_expiry.append(row["expiry"])


            smallest_expiry = get_smallest_expiry(all_expiry)
            print("Nearest expiry =", smallest_expiry)

            # get spot price
            spot_price = None
            for row in spot_price_rows:
                if row["Time"] == entry_time:
                    spot_price = float(row["Open"])
                    print("Spot_price =", spot_price)
                    break

            if spot_price is None:
                print("Error: Spot price not found!")
                continue

            relevant_rows = call if call_or_put == "CE" else put
            relevant_rows = [row for row in relevant_rows if row["Symbol"].startswith(f"{symbol}{smallest_expiry}")]
            strike_prices = [float(row["Symbol"].replace(symbol, "").replace(call_or_put, "")[7:]) for row in relevant_rows]
            closest_strike = take_closest(spot_price, strike_prices)
            final_symbol = f"{symbol}{smallest_expiry}{int(closest_strike)}{call_or_put}"

            relevant_data = [row for row in relevant_rows if row["Symbol"] == final_symbol]

            result = calculate_pnl(relevant_data, entry_time, action, target, stop_loss)
            print(f"Results for {final_symbol}: {result}")



available_dates = get_available_dates(date_range)
available_paths = get_all_paths(available_dates)

strat_backtest(available_paths, "PE", "NIFTY-I", action)