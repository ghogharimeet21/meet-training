from datetime import datetime, timedelta
import os

# Configuration variables
entry_time = "12:30:00"
exit_time = "14:30:00"  # Default exit time if no target or stop-loss is hit
action = "BUY"
symbol = "NIFTY"
date_range = ["08032023", "10032023"]
strike_shift = 0
target = float(5)
stop_loss = float(5)

# Helper Functions
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

# Main Calculation Function
def calculate_pnl(all_data, entry_time, action, target, stop_loss):
    """
    Calculate P&L for a given symbol based on target and stop-loss.
    """
    # Initialize the result dictionary
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

    # Sort data by time to process in chronological order
    all_data = sorted(all_data, key=lambda x: x["Time"])

    # Find entry price
    entry_found = False
    for row in all_data:
        if row["Time"] == entry_time:
            entry_price = float(row["Open"])
            result["entry_price"] = entry_price

            if action == "BUY":
                result["target_price"] = entry_price + target
                result["stop_loss_price"] = entry_price - stop_loss
            elif action == "SELL":
                result["target_price"] = entry_price - target
                result["stop_loss_price"] = entry_price + stop_loss

            entry_found = True
            break

    # If entry price is not found, return with an error
    if not entry_found:
        print("Error: Entry time not found in data!")
        return result

    # Check for exit conditions
    for row in all_data:
        high = float(row["High"])
        low = float(row["Low"])
        time = row["Time"]

        # Check target or stop-loss conditions based on action
        if action == "BUY":
            if high >= result["target_price"]:
                result["exit_price"] = result["target_price"]
                result["exit_time"] = time
                result["exit_reason"] = "Target Hit"
                break
            if low <= result["stop_loss_price"]:
                result["exit_price"] = result["stop_loss_price"]
                result["exit_time"] = time
                result["exit_reason"] = "Stop-Loss Hit"
                break
        elif action == "SELL":
            if low <= result["target_price"]:
                result["exit_price"] = result["target_price"]
                result["exit_time"] = time
                result["exit_reason"] = "Target Hit"
                break
            if high >= result["stop_loss_price"]:
                result["exit_price"] = result["stop_loss_price"]
                result["exit_time"] = time
                result["exit_reason"] = "Stop-Loss Hit"
                break

    # Calculate P&L
    if result["exit_price"] is not None:
        if action == "BUY":
            result["P&L"] = result["exit_price"] - result["entry_price"]
        elif action == "SELL":
            result["P&L"] = result["entry_price"] - result["exit_price"]

    return result

# Backtesting Logic
def strat_backtest(available_paths, call_or_put, spot_price_symbol, action):
    for path in available_paths:
        if not os.path.exists(path):
            # print(f"File not found: {path}")
            continue

        with open(path, "r") as file:
            lines = file.readlines()
            header = lines[0].strip().split(",")

            # Parse data
            spot_price_rows = []
            call = []
            put = []

            for line in lines[1:]:
                values = line.strip().split(",")
                if values[1].strip() == spot_price_symbol:
                    spot_price_rows.append({header[i]: values[i] for i in range(len(header))})
                elif call_or_put == "CE" and values[1].endswith("CE"):
                    call.append({header[i]: values[i] for i in range(len(header))})
                elif call_or_put == "PE" and values[1].endswith("PE"):
                    put.append({header[i]: values[i] for i in range(len(header))})

            # Get the nearest expiry
            all_expiry = [row["Symbol"].replace(symbol, "").replace(call_or_put, "")[:7] for row in call + put]
            smallest_expiry = get_smallest_expiry(all_expiry)

            # Determine closest strike price
            spot_price = None
            for row in spot_price_rows:
                if row["Time"] == entry_time:
                    spot_price = float(row["Open"])
                    break

            if spot_price is None:
                print("Error: Spot price not found!")
                continue

            relevant_rows = call if call_or_put == "CE" else put
            relevant_rows = [row for row in relevant_rows if row["Symbol"].startswith(f"{symbol}{smallest_expiry}")]
            strike_prices = [float(row["Symbol"].replace(symbol, "").replace(call_or_put, "")[7:]) for row in relevant_rows]
            closest_strike = take_closest(spot_price, strike_prices)
            final_symbol = f"{symbol}{smallest_expiry}{int(closest_strike)}{call_or_put}"

            # Filter rows for the final symbol
            all_data = [row for row in relevant_rows if row["Symbol"] == final_symbol]

            # Calculate P&L
            result = calculate_pnl(all_data, entry_time, action, target, stop_loss)
            print(f"Results for {final_symbol}: {result}")

# Main Execution
available_dates = get_available_dates(date_range)
available_paths = get_all_paths(available_dates)
strat_backtest(available_paths, "PE", "NIFTY-I", action)
