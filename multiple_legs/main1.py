from datetime import datetime, timedelta
import os
import json


def make_dict(header, values):
    return {header[i]: values[i] for i in range(len(header))}


def get_strike_expiry(symbol: str, index, option_type):
    strike = symbol.replace(index, "").replace(option_type, "")[7:]
    expiry = symbol.replace(index, "").replace(option_type, "")[:7]

    return strike, expiry


def convert_dateformat(date, format, to_format):
    return datetime.strftime(datetime.strptime(date, format), to_format)


def write_in_jsonFile(result, fileName):
    jsondata = json.dumps(result, indent=4)
    with open(f"./outputdata/{fileName}", "w") as file:
        file.write(jsondata)


def get_atm(spot_perice, strike_list):
    return min(strike_list, key=lambda x: abs(float(x) - spot_perice))


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


def load_data(paths, spot_price_symbol, index) -> dict:

    dataset_mapper = {}
    for path in paths:
        if not os.path.exists(path):
            continue

        with open(path, "r") as file:
            lines = file.readlines()
            header = lines[0].strip().split(",")
            # ['', 'Symbol', 'Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Open Interest', 'TickTime', '', '']

            for line in lines[1:]:

                values = line.strip().split(",")

                symbol = values[1]
                date = values[2]
                time = values[3]
                open_price = values[4]
                high_price = values[5]
                low_price = values[6]
                close_price = values[7]

                if values[1][-2:] == "CE":

                    # initialized the if not available in the mapper
                    if date not in dataset_mapper:
                        dataset_mapper[date] = {
                            "CE": {},
                            "CE_DETAILS": {
                                "available_strikes": [],
                                "": [],
                            },
                            "PE": {},
                            "PE_DETAILS": {
                                "available_strikes": [],
                                "available_expiries": [],
                            },
                            f"{spot_price_symbol}": {},
                        }
                    # Intialize symbol.
                    if symbol not in dataset_mapper[date]["CE"]:
                        dataset_mapper[date]["CE"][symbol] = {}

                    # initialize time
                    if time not in dataset_mapper[date]["CE"][symbol]:
                        dataset_mapper[date]["CE"][symbol][time] = []

                    dataset_mapper[date]["CE"][symbol][time] = [
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                    ]

                elif values[1][-2:] == "PE":
                    # initialized the if not available in the mapper
                    if date not in dataset_mapper:
                        dataset_mapper[date] = {
                            "CE": {},
                            "CE_DETAILS": {
                                "available_strikes": [],
                                "available_expiries": [],
                            },
                            "PE": {},
                            "PE_DETAILS": {
                                "available_strikes": [],
                                "available_expiries": [],
                            },
                            f"{spot_price_symbol}": {},
                        }
                    # Intialize symbol.
                    if symbol not in dataset_mapper[date]["PE"]:
                        dataset_mapper[date]["PE"][symbol] = {}

                    # initialize time
                    if time not in dataset_mapper[date]["PE"][symbol]:
                        dataset_mapper[date]["PE"][symbol][time] = []

                    dataset_mapper[date]["PE"][symbol][time] = [
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                    ]

                elif values[1] == spot_price_symbol:
                    # initialized the if not available in the mapper
                    if date not in dataset_mapper:
                        dataset_mapper[date] = {
                            "CE": {},
                            "CE_DETAILS": {
                                "available_strikes": [],
                                "available_expiries": [],
                            },
                            "PE": {},
                            "PE_DETAILS": {
                                "available_strikes": [],
                                "available_expiries": [],
                            },
                            f"{spot_price_symbol}": {},
                        }

                    # initialize time
                    if time not in dataset_mapper[date][spot_price_symbol]:
                        dataset_mapper[date][spot_price_symbol][time] = []

                    dataset_mapper[date][spot_price_symbol][time] = [
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                    ]

    symbols = []
    for date in dataset_mapper:
        for type in dataset_mapper[date]:
            for symbol in dataset_mapper[date][type]:
                symbols.append(symbol)

    CE_exps = []
    PE_exps = []
    CE_strikes = []
    PE_strikes = []
    for sym in symbols:
        if sym[-2:] == "CE":
            strike, expiry = get_strike_expiry(sym, index, "CE")
            if expiry not in CE_exps:
                CE_exps.append(expiry)
            if strike not in CE_strikes:
                CE_strikes.append(strike)
        if sym[-2:] == "PE":
            strike, expiry = get_strike_expiry(sym, index, "PE")
            if expiry not in PE_exps:
                PE_exps.append(expiry)
            if strike not in PE_strikes:
                PE_strikes.append(strike)

    sorted_PE_exps = sort_dates(date_format="%d%b%y", date_list=PE_exps)
    sorted_PE_strikes = sorted(PE_strikes)

    sorted_CE_exps = sort_dates(date_format="%d%b%y", date_list=CE_exps)
    sorted_CE_strikes = sorted(CE_strikes)

    for date in dataset_mapper:
        for row in dataset_mapper[date]:
            if row == "PE_DETAILS":
                for elm in dataset_mapper[date][row]:
                    if elm == "available_strikes":
                        dataset_mapper[date][row][elm] = sorted_PE_strikes
                    elif elm == "available_expiries":
                        dataset_mapper[date][row][elm] = sorted_PE_exps
    for date in dataset_mapper:
        for row in dataset_mapper[date]:
            if row == "CE_DETAILS":
                for elm in dataset_mapper[date][row]:
                    if elm == "available_strikes":
                        dataset_mapper[date][row][elm] = sorted_CE_strikes
                    elif elm == "available_expiries":
                        dataset_mapper[date][row][elm] = sorted_CE_exps

    return dataset_mapper


def extract_expiry(data, symbol, option_type, date_format="%d%b%y"):
    all_exps_objs = []
    for row in data:
        exp = row["Symbol"].replace(symbol, "").replace(option_type, "")[:7]
        row["expiry"] = exp
        all_exps_objs.append(datetime.strptime(exp, date_format))
    weekly = sorted(list(set(all_exps_objs)))[0]
    weekly_exp = datetime.strftime(weekly, date_format).upper()

    currunt_month = weekly.month
    currunt_month_list = list(
        set([date for date in all_exps_objs if date.month == currunt_month])
    )
    sortedList = sorted(currunt_month_list)
    monthly_expiry = sortedList[-1]
    monthly_exp = datetime.strftime(monthly_expiry.date(), date_format).upper()

    return weekly_exp, monthly_exp


def get_monthly_expiry(date_list: list, date_fomat="%d%b%y"):
    date_objs = [datetime.strptime(date, date_fomat) for date in date_list]
    weekly = date_objs[0]
    currunt_month = weekly.month
    currunt_month_list = [date for date in date_objs if date.month == currunt_month]
    return datetime.strftime(currunt_month_list[-1], date_fomat).upper()


def sort_dates(date_format: str, date_list: list):
    return [
        datetime.strftime(obj, date_format).upper()
        for obj in sorted([datetime.strptime(date, date_format) for date in date_list])
    ]


def find_symbol(
    index,
    spot_price,
    available_expiries,
    available_strikes,
    opt_type,
    shift,
    expiry_type,
):
    strike = None
    expiry = None

    atm = get_atm(float(spot_price), available_strikes)

    atm_index = available_strikes.index(atm)
    strike = available_strikes[atm_index + shift]

    if expiry_type == "WEEKLY":
        expiry = available_expiries[0]

    elif expiry_type == "NEXT_WEEKLY":
        expiry = available_expiries[1]

    elif expiry_type == "MONTHLY":
        expiry = get_monthly_expiry(available_expiries)

    if (not strike) or (not expiry):
        return

    return index + expiry + strike + opt_type


def get_startagy_entry_exit_time(entry_time: list, exit_time: list):
    entry_objs = [datetime.strptime(time, "%H:%M:%S") for time in entry_time]
    exit_objs = [datetime.strptime(time, "%H:%M:%S") for time in exit_time]

    return min(entry_objs), max(exit_objs)


def get_available_time_range(date_range: list, date_format: str):
    """Generate a list of dates between a given range."""
    if len(date_range) > 2:
        print(date_range[2:], "out of range")
        raise "please enter a date in range of 2......"

    from_date = datetime.strptime(date_range[0], date_format)
    to_date = datetime.strptime(date_range[1], date_format)
    dates = []
    while from_date <= to_date:
        dates.append(datetime.strftime(from_date, date_format))
        from_date += timedelta(minutes=1)
    return dates


def get_percent(action, inverstmest, currunt_price):
    if action == "BUY":
        return round(((currunt_price - inverstmest) * 100) / inverstmest, 2)
    elif action == "SELL":
        return round(((inverstmest - currunt_price) * 100) / inverstmest, 2)


def get_targets(result, contracts):
    total_investment = 0
    for contract in contracts:
        total_investment += result[contract]["entry_price"]
    return round(total_investment, 2)


def get_overall_sl_tgt(
    result, contracts, total_investment, overall_target, overall_stoploss
):
    total_currunt_value = 0
    for inst in contracts:
        if result[inst]["exit_price"]:
            total_currunt_value += result[inst]["exit_price"]
        else:
            total_currunt_value += result[inst]["currunt_close_price"]
    chnage_in_investment = total_currunt_value - total_investment

    if chnage_in_investment >= overall_target:
        for inst in contracts:
            if result[inst]["exit_price"] == None:
                result[inst]["exit_price"] = result[inst]["currunt_close_price"]
                result[inst]["exit_reason"] = "Overall Target Hitt"
        return True, result
    elif chnage_in_investment <= overall_stoploss:
        for inst in contracts:
            if result[inst]["exit_price"] == None:
                result[inst]["exit_price"] = result[inst]["currunt_close_price"]
                result[inst]["exit_reason"] = "Overall Stoploss Hitt"
        return True, result
    else:
        return False, result


def get_pNl(
    datset_mapper,
    entry_time,
    exit_time,
    contracts,
    tread_actions,
    targetList,
    stop_lossList,
    overall_target,
    overall_stoploss,
):
    result = {}

    min_entry_time, max_exit_time = get_startagy_entry_exit_time(entry_time, exit_time)
    time_range = get_available_time_range(
        [
            datetime.strftime(min_entry_time, "%H:%M:%S"),
            datetime.strftime(max_exit_time, "%H:%M:%S"),
        ],
        "%H:%M:%S",
    )

    call_at_ones = True

    for currunt_date in datset_mapper:
        if currunt_date not in result:
            result[currunt_date] = {}
        # Loop over time_span.
        for time in time_range:
            # Loop over legs.
            for i, leg_entry_time in enumerate(entry_time):
                leg_exit_time = exit_time[i]
                contract = contracts[i]
                option_type = contract[-2:]
                open_price = float(
                    datset_mapper[currunt_date][option_type][contract][time][0]
                )
                high_price = float(
                    datset_mapper[currunt_date][option_type][contract][time][1]
                )
                low_price = float(
                    datset_mapper[currunt_date][option_type][contract][time][2]
                )
                close_price = float(
                    datset_mapper[currunt_date][option_type][contract][time][3]
                )
                if time == leg_entry_time:
                    if contract not in result[currunt_date]:
                        result[currunt_date]["overall"] = {}
                        result[currunt_date][contract] = {
                            "entry_time": None,
                            "exit_time": None,
                            "entry_price": None,
                            "exit_price": None,
                            "exit_reason": None,
                            "target_price": None,
                            "target_stoploss": None,
                            "pnl": None,
                        }
                    result[currunt_date][contract]["entry_time"] = time
                    result[currunt_date][contract]["entry_price"] = open_price
                    result[currunt_date][contract]["currunt_close_price"] = close_price
                elif time == leg_exit_time:
                    if result[contract]["exit_reason"] is not None:
                        break
                    result[currunt_date][contract]["exit_time"] = time
                    result[currunt_date][contract]["exit_price"] = open_price
                    result[currunt_date][contract]["currunt_close_price"] = close_price
                else:
                    if result[currunt_date][contract]["entry_price"] != None:
                        leg_investment = result[currunt_date][contract]["entry_price"]
                        target_price = (
                            leg_investment + targetList[i]
                            if tread_actions[i] == "BUY"
                            else leg_investment - stop_lossList[i]
                        )

                        stop_loss_price = (
                            leg_investment - stop_lossList[i]
                            if tread_actions[i] == "BUY"
                            else leg_investment + stop_lossList[i]
                        )
                        result[currunt_date][contract]["target_price"] = target_price
                        result[currunt_date][contract][
                            "target_stoploss"
                        ] = stop_loss_price

                        result[currunt_date][contract]["action"] = tread_actions[i]

                        if tread_actions[i] == "BUY":
                            if high_price >= target_price:
                                result[currunt_date][contract]["exit_time"] = time
                                result[currunt_date][contract][
                                    "exit_price"
                                ] = high_price
                                result[currunt_date][contract][
                                    "exit_reason"
                                ] = "Individual Target Hitt"
                                result[currunt_date][contract]["pnl"] = round(
                                    high_price - leg_investment, 2
                                )
                                result[currunt_date][contract][
                                    "currunt_close_price"
                                ] = close_price
                                break
                            elif low_price <= stop_loss_price:
                                result[currunt_date][contract]["exit_time"] = time
                                result[currunt_date][contract]["exit_price"] = low_price
                                result[currunt_date][contract][
                                    "exit_reason"
                                ] = "Individual Stop Loss Hitt"
                                result[currunt_date][contract]["pnl"] = round(
                                    low_price - leg_investment, 2
                                )
                                result[currunt_date][contract][
                                    "currunt_close_price"
                                ] = close_price
                                break
                        elif tread_actions[i] == "SELL":
                            if high_price >= stop_loss_price:
                                result[currunt_date][contract]["exit_time"] = time
                                result[currunt_date][contract][
                                    "exit_price"
                                ] = high_price
                                result[currunt_date][contract][
                                    "exit_reason"
                                ] = "Individual Stoploss Hitt"
                                result[currunt_date][contract]["pnl"] = round(
                                    leg_investment - high_price, 2
                                )
                                result[currunt_date][contract][
                                    "currunt_close_price"
                                ] = close_price
                                break
                            elif low_price <= target_price:
                                result[currunt_date][contract]["exit_time"] = time
                                result[currunt_date][contract]["exit_price"] = low_price
                                result[currunt_date][contract][
                                    "exit_reason"
                                ] = "Individual Target Hitt"
                                result[currunt_date][contract]["pnl"] = round(
                                    leg_investment - low_price, 2
                                )
                                result[currunt_date][contract][
                                    "currunt_close_price"
                                ] = close_price
                                break
            if call_at_ones:
                total_investment = get_targets(result[currunt_date], contracts)
                result[currunt_date]["overall"]["overall_investment"] = total_investment
                call_at_ones = False
            is_sq_off, result = get_overall_sl_tgt(
                result[currunt_date],
                contracts,
                total_investment,
                overall_target,
                overall_stoploss,
            )

            if is_sq_off:
                break

    return result


def start_backtest():
    spot_price_symbol = "NIFTY-I"
    index = "NIFTY"
    date_range = ["08032023", "10032023"]
    entry_time = ["11:00:00", "11:00:00"]
    exit_time = ["13:30:00", "13:30:00"]
    overall_target = 100
    overall_stop_loss = 50
    target = [2, 2]
    stop_loss = [1, 1]
    tread_actions = ["BUY", "BUY"]
    option_type = ["CE", "PE"]
    strike = ["ATM", "ATM+1"]
    expiries = ["WEEKLY", "MONTHLY"]

    if (
        (len(entry_time) != len(exit_time))
        or (len(tread_actions) != len(option_type))
        or (len(strike) != len(expiries))
    ):
        raise "Please check all inputs"

    dates = get_available_dates(date_range=date_range, date_format="%d%m%Y")

    paths = get_all_dataset_paths("dataset", dates)

    # got data according to inPE option_type in a list
    dataset_mapper = load_data(paths, spot_price_symbol, index)

    write_in_jsonFile(dataset_mapper, "dataset_mapper")

    spot_prices = []
    contracts = []
    for current_date in dataset_mapper:
        for i, ent_time in enumerate(entry_time):
            opt_type = option_type[i]

            for time, index_prices in dataset_mapper[current_date][
                spot_price_symbol
            ].items():
                if time == ent_time:
                    spot_prices.append(index_prices[0])

        for i, spot_price in enumerate(spot_prices):
            opt_type = option_type[i]
            expiry_type = expiries[i]
            shift = strike[i].replace("ATM", "")
            if len(shift) == 0:
                shift = 0
            else:
                shift = int(shift)

            segment_type = "CE_DETAILS" if option_type == "CE" else "PE_DETAILS"
            segment_details = dataset_mapper[current_date][segment_type]
            contract = find_symbol(
                index,
                spot_price,
                segment_details["available_expiries"],
                segment_details["available_strikes"],
                opt_type,
                shift,
                expiry_type,
            )
            contracts.append(contract)

    result = get_pNl(
        dataset_mapper,
        entry_time,
        exit_time,
        contracts,
        tread_actions,
        target,
        stop_loss,
        overall_target,
        overall_stop_loss,
    )

    print(result)

    write_in_jsonFile(result, "final_output.json")


if __name__ == "__main__":
    start_backtest()
