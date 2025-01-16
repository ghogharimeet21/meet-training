from datetime import datetime, timedelta
import os


entry_time = "12:30:00"
exit_time = "14:30:00"
action = "BUY"
symbol = "NIFTY"
date_range = ["08032023", "10032023"]
strike_shift = 0
target = float(2)
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

def calculate_pnl(all_data, entry_time, action, target, stop_loss):
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

    # Sort data by time
    # all_data = sorted(all_data, key=lambda x: x["Time"])

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
    # for data in all_data:
    #     print("ROW", data)
    
    for row in all_data:
        high = float(row["High"])
        low = float(row["Low"])
        time = row["Time"]


        if action == "BUY":
            if high >= result["target_price"]:
                result["exit_price"] = high
                result["exit_time"] = time
                result["exit_reason"] = "Target Hit"
                break
            if low <= result["stop_loss_price"]:
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
            if high >= result["stop_loss_price"]:
                result["exit_price"] = high
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


