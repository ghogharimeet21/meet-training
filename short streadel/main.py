from datetime import datetime, timedelta
import os
import json
import time as t


def make_dict(header, values):
    return {header[i]: values[i] for i in range(len(header))}


def get_strike_expiry(symbol: str, index, option_type):
    strike = symbol.replace(index, "").replace(option_type, "")[7:]
    expiry = symbol.replace(index, "").replace(option_type, "")[:7]
    return strike, expiry


def convert_dateformat(date, format, to_format):
    return datetime.strftime(datetime.strptime(date, format).date(), to_format)


def write_file(data_obj, file_name:str, output_directory_name:str="output_data", mode:str="w"):
    if file_name.endswith(".json"):
        jsondata = json.dumps(data_obj, indent=4)
        os.makedirs(f"./{output_directory_name}", exist_ok=True)
        with open(f"./{output_directory_name}/{file_name}", mode) as file:
            file.write(jsondata)


def get_atm(spot_price, strike_list):
    # print(strike_list, "^"*50)
    return min(strike_list, key=lambda x: abs(float(x) - spot_price))


def get_available_dates_in_range(date_range: list, date_format: str):
    if (
        len(date_range) > 2
    ):
        raise ValueError("Please enter a date range of 2.")
    from_date = datetime.strptime(date_range[0], date_format)
    to_date = datetime.strptime(date_range[1], date_format)
    dates = []
    while from_date <= to_date:
        dates.append(datetime.strftime(from_date, date_format))
        from_date += timedelta(days=1)
    return dates


def get_all_dataset_paths(dataset_folder_path, date_range):
    dataset_path = os.path.join(os.getcwd(), dataset_folder_path)
    files = os.listdir(dataset_folder_path)
    paths = [
        os.path.join(dataset_path, file)
        for file in files
        if any(date in file for date in date_range) and file.endswith(".csv")
    ]
    return paths

def get_monthly_expiry(date_list, date_format):
    date_objs = [datetime.strptime(date, date_format) for date in date_list]
    first_date = date_objs[0]
    current_month = first_date.month
    current_month_dates = [date for date in date_objs if date.month == current_month]
    return datetime.strftime(current_month_dates[-1], date_format).upper()

def sort_dates(date_format: str, date_list: list):
    return [
        datetime.strftime(obj, date_format).upper()
        for obj in sorted([datetime.strptime(date, date_format) for date in date_list])
    ]

def load_data(paths, spot_price_symbol, index, exp_date_format) -> dict:

    
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
                option = symbol[-2:]
                date = values[2]
                time = values[3]
                open_price = values[4]
                high_price = values[5]
                low_price = values[6]
                close_price = values[7]

                if option == "CE":
                    # initialized the if not available in the mapper
                    if date not in dataset_mapper:
                        dataset_mapper[date] = {
                            "PE":{},
                            "PE_DETAILS":{
                                "available_strikes":[],
                                "available_expiries":[]
                            },
                            "CE":{},
                            "CE_DETAILS":{
                                "available_strikes":[],
                                "available_expiries":[]
                            },
                            f"{spot_price_symbol}":{}
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

                elif option == "PE":
                    # initialized the if not available in the mapper
                    if date not in dataset_mapper:
                        dataset_mapper[date] = {
                            "PE":{},
                            "PE_DETAILS":{
                                "available_strikes":[],
                                "available_expiries":[]
                            },
                            "CE":{},
                            "CE_DETAILS":{
                                "available_strikes":[],
                                "available_expiries":[]
                            },
                            f"{spot_price_symbol}":{}
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

                elif symbol == spot_price_symbol:
                    # initialized the if not available in the mapper
                    if date not in dataset_mapper:
                        dataset_mapper[date] = {
                            "PE":{},
                            "PE_DETAILS":{
                                "available_strikes":[],
                                "available_expiries":[]
                            },
                            "CE":{},
                            "CE_DETAILS":{
                                "available_strikes":[],
                                "available_expiries":[]
                            },
                            f"{spot_price_symbol}":{}
                        }
                    # Intialize symbol.
                    if spot_price_symbol not in dataset_mapper[date]:
                        dataset_mapper[date][spot_price_symbol] = {}
                    

                    # initialize time
                    if time not in dataset_mapper[date][symbol]:
                        dataset_mapper[date][symbol][time] = []
                    
                    dataset_mapper[date][symbol][time] = [open_price,high_price, low_price, close_price]
            
                    if time not in dataset_mapper[date]:
                        dataset_mapper[date][symbol][time] = []

                    dataset_mapper[date][symbol][time] = [
                        open_price,
                        high_price,
                        low_price,
                        close_price,
                    ]

    symbols = []
    for date in dataset_mapper:
        for segment in dataset_mapper[date]:
            for symbol in dataset_mapper[date][segment]:
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

        elif sym[-2:] == "PE":
            strike, expiry = get_strike_expiry(sym, index, "PE")
            if expiry not in PE_exps:
                PE_exps.append(expiry)
            if strike not in PE_strikes:
                PE_strikes.append(strike)


    sorted_PE_exps = sort_dates(date_format=exp_date_format, date_list=PE_exps)
    sorted_PE_strikes = sorted(PE_strikes)

    sorted_CE_exps = sort_dates(date_format=exp_date_format, date_list=CE_exps)
    sorted_CE_strikes = sorted(CE_strikes)

    for date in dataset_mapper:
        for row in dataset_mapper[date]:
            if row == "PE_DETAILS":
                for elm in dataset_mapper[date][row]:
                    if elm == "available_strikes":
                        dataset_mapper[date][row][elm] = sorted_PE_strikes
                    elif elm == "available_expiries":
                        dataset_mapper[date][row][elm] = sorted_PE_exps
            elif row == "CE_DETAILS":
                for elm in dataset_mapper[date][row]:
                    if elm == "available_strikes":
                        dataset_mapper[date][row][elm] = sorted_CE_strikes
                    elif elm == "available_expiries":
                        dataset_mapper[date][row][elm] = sorted_CE_exps

    write_file(dataset_mapper, "dataset_mapper.json", "output_data", "w")

    return dataset_mapper


def get_startagy_overall_time_range(entry_time: str, exit_time: str, time_format: str):
    entry_objs, exit_objs = [
        datetime.strptime(time, time_format) for time in entry_time
    ], [datetime.strptime(time, time_format) for time in exit_time]
    return [datetime.strftime(min(entry_objs), time_format), datetime.strftime(max(exit_objs), time_format)]


def find_symbol(
    time_format:str,
    index: str,
    spot_price: float,
    available_expiries: list,
    available_strikes: list,
    opt_type: str,
    shift: int,
    expiry_type: str,
):
    strike = None
    expiry = None
    atm = get_atm(float(spot_price), available_strikes)
    atm_index = available_strikes.index(atm)
    strike = available_strikes[atm_index + shift]
    expiry = (
        available_expiries[0]
        if expiry_type.upper() == "WEEKLY"
        else (
            available_expiries[1]
            if expiry_type.upper() == "NEXT_WEEKLY"
            else get_monthly_expiry(available_expiries, time_format)
        )
    )
    return f"{index}{expiry}{strike}{opt_type}"



spot_price_symbol = "NIFTY-I"
index = "NIFTY"
date_range = ["08032023", "10032023"]
lot_size = [10, 15]
entry_time = ["10:00:00", "10:00:00"]
exit_time = ["13:30:00", "13:30:00"]
overall_target = 50
overall_stop_loss = 25
targets = [10, 10]
stop_loses = [4, 4]
tread_actions = ["BUY", "BUY"]
option_type = ["CE", "PE"]
strike = ["ATM", "ATM+1"]
expiries = ["weekly", "monthly"]

FILE_DATE_FORMAT = "%d%m%Y"
ROW_EXPIRY_TIME_FORMAT = "%d%b%y"
TIME_FORMAT = "%H:%M:%S"

def start_backtest():
    dates = get_available_dates_in_range(date_range, FILE_DATE_FORMAT)
    paths = get_all_dataset_paths("dataset", dates)
    dataset_mapper = load_data(paths, spot_price_symbol, index, ROW_EXPIRY_TIME_FORMAT)


    contracts = []
    for currunt_date in dataset_mapper:
        for i, ent_time in enumerate(entry_time):
            for time, index_prices in dataset_mapper[currunt_date][spot_price_symbol].items():
                if time == ent_time:
                    spot_price = index_prices[0]
                    shift_num = strike[i].replace("ATM", "")
                    if shift_num == "":
                        shift = 0
                    else:
                        shift = int(shift_num)
                    
                    segment_type = "CE_DETAILS" if option_type[i] == "CE" else "PE_DETAILS"
                    segment_details = dataset_mapper[currunt_date][segment_type]

                    contract = find_symbol(
                        ROW_EXPIRY_TIME_FORMAT,
                        index,
                        spot_price,
                        segment_details["available_expiries"],
                        segment_details["available_strikes"],
                        option_type[i],
                        shift,
                        expiries[i]
                    )
                    if contract:
                        contracts.append(contract)

    print(contracts)




if __name__ == "__main__":
    start_backtest()