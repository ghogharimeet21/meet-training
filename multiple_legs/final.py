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


def get_available_time_range(time_range: list, time_format: str):
    from_time, to_time = datetime.strptime(
        time_range[0], time_format
    ), datetime.strptime(time_range[1], time_format)
    times = []
    while from_time <= to_time:
        times.append(datetime.strftime(from_time, time_format))
        from_time += timedelta(minutes=1)
    return times


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


def get_targets(result, contracts):
    total_investment = 0
    for inst in contracts:
        total_investment += result[inst]["entry_price"]
    
    return total_investment


def check_overall_sl_tgt(
    result,
    contracts,
    total_investment,
    overall_target,
    overall_stoploss,
    time,
):
    total_currunt_value = 0
    for leg in contracts:
        if (
            result[leg]["exit_price"] is not None
        ):
            total_currunt_value += result[leg]["exit_price"]
        else:
            total_currunt_value += result[leg]["currunt_close_price"]
    chnage_in_investment = total_currunt_value - total_investment

    if (
        chnage_in_investment >= overall_target
    ):
        for leg in contracts:
            if result[leg]["exit_price"] is None:
                result[leg]["exit_price"] = result[leg]["currunt_close_price"]
                result[leg]["exit_reason"] = "Overall Target Hitt"
                result[leg]["exit_time"] = time
                result[leg]["P&L"] = result[leg]["entry_price"] - result[leg]["exit_price"]
        return True
    elif (
        chnage_in_investment <= overall_stoploss
    ):
        for leg in contracts:
            if result[leg]["exit_price"] is None:
                result[leg]["exit_price"] = result[leg]["currunt_close_price"]
                result[leg]["exit_reason"] = "Overall Stoploss Hitt"
                result[leg]["exit_time"] = time
                result[leg]["P&L"] = result[leg]["entry_price"] - result[leg]["exit_price"]
        return True
    else:
        return False

#############################################################################################################

    # total_currunt_close_value = 0
    # for inst in contracts:
    #     # print("contracts", contracts)
    #     if (
    #         result[inst]["exit_price"] is not None
    #     ):
    #         total_currunt_close_value += result[inst]["exit_price"]
    #         # print(result[inst]["exit_price"], "=", time, "contract =", inst)
    #     else:
    #         # print(result[inst]["currunt_close_price"], "=", time, "contract =", inst)
    #         total_currunt_close_value += result[inst]["currunt_close_price"]
    
    # total_overall_target = total_investment + overall_target
    # total_overall_stoploss = total_investment - overall_stoploss

    # # print("* "*50, "currun_close.txt", "a")
    # # print(f"total_currunt_close_value {total_currunt_close_value}")
    # # print(f"total_investment, {total_investment}")
    # # print(f"total_overall_target, {total_overall_target}")
    # # print(f"total_overall_stoploss, {total_overall_stoploss}")
    # # print(f"time {time}")
    # # print("* "*50, "currun_close.txt", "a")
    # # t.sleep(0.5)

    # if (
    #     result[inst]["exit_price"] is None
    # ):
    #     if (
    #         total_currunt_close_value >= total_overall_target
    #     ):
    #         for inst in contracts:
    #             result[inst]["exit_time"] = time
    #             result[inst]["exit_price"] = result[inst]["currunt_close_price"]
    #             result[inst]["exit_reason"] = "Overall Target Hitt"
    #             result[inst]["P&L"] = round(
    #                 total_investment - total_currunt_close_value, 2
    #             )
    #             print("Overall Target Hitt")
    #         return True

    #     elif (
    #         total_currunt_close_value <= total_overall_stoploss
    #     ):
    #         for inst in contracts:
    #             result[inst]["exit_time"] = time
    #             result[inst]["exit_price"] = result[inst]["currunt_close_price"]
    #             result[inst]["exit_reason"] = "Overall Stoploss Hitt"
    #             result[inst]["P&L"] = round(
    #                 total_investment - total_currunt_close_value, 2
    #             )
    #             print("Overall Stoploss Hitt")
    #         return True
    #     else:
    #         return False

def calculate_lot_size(index_derivatives_contracts: dict, result:dict, index: str, lot_size: list):
    for symbol in index_derivatives_contracts:
        lot = int(index_derivatives_contracts[symbol])
        if symbol.upper() == index.upper():
            for date in result:
                for i, contract in enumerate(result[date]):
                    total_shears = (lot * lot_size[i])
                    result[date][contract]["lot_size"] = lot_size[i]
                    result[date][contract]["entry_price"] *= total_shears
                    result[date][contract]["exit_price"] *= total_shears
                    result[date][contract]["target_price"] *= total_shears
                    result[date][contract]["stoploss_price"] *= total_shears
                    result[date][contract]["P&L"] *= total_shears
                    result[date][contract]["currunt_close_price"] *= total_shears


def get_pnl(
    time_format:str,
    dataset_mapper:dict,
    entry_times:list,
    exit_times:list,
    contracts:list,
    tread_actions:list,
    targetList:list,
    stoplossList:list,
    overall_target:int,
    overall_stoploss:int,
):
    result = {}

    min_entry_time, max_exit_time = get_startagy_overall_time_range(entry_times, exit_times, time_format)
    time_range = get_available_time_range([min_entry_time, max_exit_time], time_format)

    call_at_once_total_investment = True

    for currunt_date in dataset_mapper:
        if (
            currunt_date not in result
        ):
            result[currunt_date] = {}
        
        for time in time_range:
            for i, leg_entry_time in enumerate(entry_times):
                leg_exit_time = exit_times[i]
                leg_contract = contracts[i]
                leg_action = tread_actions[i]
                target = targetList[i]
                stoploss = stoplossList[i]
                option_type = leg_contract[-2:]

                if (
                    leg_contract not in dataset_mapper[currunt_date][option_type]
                ):
                    print(f"this contract '{leg_contract}' not avilable")
                    continue

                try:
                    open_price, high_price, low_price, close_price = map(
                        float, dataset_mapper[currunt_date][option_type][leg_contract][time]
                    )
                except KeyError:
                    print(
                        f"GOT key error >>>\n, {KeyError}, \n, at : {dataset_mapper[currunt_date][option_type][leg_contract][time]}"
                    )
                    continue

                if (
                    time == leg_entry_time
                ):
                    result[currunt_date][leg_contract] = {
                        "entry_date": currunt_date,
                        "lot_size": None,
                        "entry_time": time,
                        "exit_time": None,
                        "entry_price": open_price,
                        "exit_price": None,
                        "exit_reason": None,
                        "target_price": round(open_price + target, 2) if leg_action.upper() == "BUY" else (round(open_price - target, 2) if leg_action.upper() == "SELL" else print(f"'{leg_action}' invalid Input please enter 'BUY' or 'SELL' !"), exit()),
                        "stoploss_price": round(open_price - stoploss, 2) if leg_action.upper() == "BUY" else (round(open_price + stoploss, 2) if leg_action.upper() == "SELL" else print(f"'{leg_action}' invalid Input please enter 'BUY' or 'SELL' !"), exit()),
                        "P&L": None,
                        "currunt_close_price": close_price,
                        "action": leg_action
                    }

                elif (
                    time == leg_exit_time
                ):
                    if (
                        result[currunt_date][leg_contract]["exit_reason"] is None
                    ):
                        result[currunt_date][leg_contract]["exit_time"] = time
                        result[currunt_date][leg_contract]["exit_price"] = close_price
                        result[currunt_date][leg_contract]["exit_reason"] = "Normal Exit"
                        result[currunt_date][leg_contract]["P&L"] = (
                            round(result[currunt_date][leg_contract]["entry_price"] - close_price, 2)
                            if leg_action == "BUY"
                            else
                            round(close_price - result[currunt_date][leg_contract]["entry_price"], 2)
                        )

                elif (
                    leg_contract in result[currunt_date]
                ):
                    if (
                        (result[currunt_date][leg_contract]["entry_price"] is not None)
                        and
                        (result[currunt_date][leg_contract]["exit_reason"] is None)
                    ):
                        result[currunt_date][leg_contract]["currunt_close_price"] = close_price
                        leg_investment = result[currunt_date][leg_contract]["entry_price"]
                        target_price = result[currunt_date][leg_contract]["target_price"]
                        stoploss_price = result[currunt_date][leg_contract]["stoploss_price"]
                        if (
                            leg_action == "BUY"
                        ):
                            if (
                                high_price >= target_price
                            ):
                                print("Individual Target Hit")
                                result[currunt_date][leg_contract]["exit_time"] = time
                                result[currunt_date][leg_contract]["exit_price"] = high_price
                                result[currunt_date][leg_contract]["exit_reason"] = "Individual Target Hit"
                                result[currunt_date][leg_contract]["P&L"] = round(high_price - leg_investment, 2)
                                break
                            elif (
                                low_price <= stoploss_price
                            ):
                                result[currunt_date][leg_contract]["exit_time"] = time
                                result[currunt_date][leg_contract]["exit_price"] = low_price
                                result[currunt_date][leg_contract]["exit_reason"] = "Individual Stoploss Hit"
                                result[currunt_date][leg_contract]["P&L"] = round(low_price - leg_investment, 2)
                                break
                            
                        
                        elif leg_action == "SELL":
                            if (
                                high_price >= stoploss_price
                            ):
                                result[currunt_date][leg_contract]["exit_time"] = time
                                result[currunt_date][leg_contract]["exit_price"] = high_price
                                result[currunt_date][leg_contract]["exit_reason"] = "Individual Stoploss Hit"
                                result[currunt_date][leg_contract]["P&L"] = round(leg_investment - high_price, 2)
                                break
                            elif (
                                low_price <= target_price
                            ):
                                result[currunt_date][leg_contract]
                                result[currunt_date][leg_contract]["exit_time"] = time
                                result[currunt_date][leg_contract]["exit_price"] = low_price
                                result[currunt_date][leg_contract]["exit_reason"] = "Individual Target Hit"
                                result[currunt_date][leg_contract]["P&L"] = round(leg_investment - low_price, 2)
                                break

            try:
                if call_at_once_total_investment:
                    if result[currunt_date][leg_contract]["entry_price"]:
                        total_investment = get_targets(result[currunt_date], contracts)
                        call_at_once_total_investment = False
            except KeyError:
                continue

            
            if result[currunt_date][leg_contract]["exit_price"] is None:
                continue
            is_sq_off = check_overall_sl_tgt(
                result[currunt_date],
                contracts,
                total_investment,
                overall_target,
                overall_stoploss,
                time,
            )

            if is_sq_off:
                break
    


    return result

index_derivatives_contracts = {
    "nifty": 75,
    "banknifty": 30,
    "niftymidcapselect": 120,
    "niftyfinancialservices": 65,
    "niftynext50": 25,
    "bsesensex": 20,
    "bsebankex": 30,
    "bsesensex50": 60
}


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

    result = get_pnl(
        TIME_FORMAT,
        dataset_mapper,
        entry_time,
        exit_time,
        contracts,
        tread_actions,
        targets,
        stop_loses,
        overall_target,
        overall_stop_loss,
    )

    calculate_lot_size(index_derivatives_contracts, result, index, lot_size)

    write_file(result, "final_result.json", "output_data", "w")



if __name__ == "__main__":
    start_backtest()