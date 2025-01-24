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


def write_in_jsonFile(result, outPEpath, fileName):
    jsondata = json.dumps(result, indent=4)
    with open(f"./{outPEpath}/{fileName}.json", "w") as file:
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
                            "NIFTY-I": {},
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
                            "NIFTY-I": {},
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
                            "NIFTY-I": {},
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
            # print(type)
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
    currunt_month_list = list(
        set([date for date in date_objs if date.month == currunt_month])
    )
    return datetime.strftime(currunt_month[-1], date_fomat).upper()


def sort_dates(date_format: str, date_list: list):
    return [
        datetime.strftime(obj, date_format).upper()
        for obj in sorted([datetime.strptime(date, date_format) for date in date_list])
    ]


def get_spot_price(spot_price_symbol, datset_mapper, entry_time):
    spot_price = None
    for date in datset_mapper:
        for segment in datset_mapper[date]:
            if segment == spot_price_symbol:
                for symbol in datset_mapper[segment]:
                    for time in datset_mapper[segment][symbol]:
                        if time == entry_time:
                            spot_price = float(datset_mapper[segment][symbol][time][0])
    return spot_price


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
        # expiry = get_monthly_expiry(available_expiries)
        pass

    if (not strike) or (not expiry):
        return

    return index + strike + expiry + opt_type


def start_backtest():
    spot_price_symbol = "NIFTY-I"
    index = "NIFTY"
    date_range = ["08032023", "10032023"]
    entry_time = ["10:30:00", "9:45:00"]
    exit_time = ["14:30:00", "15:15:00"]
    trade_option = ["BUY", "SELL"]
    option_type = ["PE", "CE"]
    strike = ["ATM", "ATM+1"]
    expiries = ["WEEKLY", "NEXT_WEEKLY"]

    if (
        (len(entry_time) != len(exit_time))
        or (len(trade_option) != len(option_type))
        or (len(strike) != len(expiries))
    ):
        raise "Please check all inPEs"

    dates = get_available_dates(date_range=date_range, date_format="%d%m%Y")

    paths = get_all_dataset_paths("dataset", dates)

    # got data according to inPE option_type in a list
    dataset_mapper = load_data(paths, spot_price_symbol, index)

    write_in_jsonFile(dataset_mapper, "outputdata", "dataset_mapper")
    # ---------------------------------------------------------------------
    for current_date in dataset_mapper:
        spot_prices = []
        for i, ent_time in enumerate(entry_time):
            opt_type = option_type[i]

            for time, index_prices in dataset_mapper[current_date][spot_price_symbol].items():
                if time == ent_time:
                    spot_prices.append(index_prices[0])

        contracts = []
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

        print(contracts)

    # ---------------------------------------------------------------------
    # spot_prices = []
    # nearest_strike_to_spot = []
    # for ent_time, ext_time, action, option, strike_type, expiry_type in zip(entry_time, exit_time, trade_option, option_type, strike, expiry):

    #     for date in dataset_mapper:
    #         spot_prices.append(get_spot_price(spot_price_symbol, dataset_mapper[date], ent_time))

    # # get nearest to spot_price
    # for date in dataset_mapper:
    #     for segment in dataset_mapper[date]:
    #         if segment == "PE_DETAILS":
    #             for options in dataset_mapper[date][segment]:
    #                 # print(options)

    #                 if options == "available_strikes":
    #                     strikes = dataset_mapper[date][segment][options]

    #                     symbol = find_symbol(dataset_mapper[date], index, strike_type, )
    #                     ...
    #                 ...
    #             ...

    # print("Spot Prices", spot_prices)
    # print("nearest strikes to spot", nearest_strike_to_spot)


if __name__ == "__main__":
    start_backtest()
