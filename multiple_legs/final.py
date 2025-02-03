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
    return datetime.strftime(datetime.strptime(date, format).date(), to_format)


def write_file(result, fileName, mode):
    jsondata = json.dumps(result, indent=4)
    os.makedirs("./outputdata", exist_ok=True)
    with open(f"./outputdata/{fileName}", mode) as file:
        file.write(jsondata)


def get_atm(spot_price, strike_list):
    return min(strike_list, key=lambda x: abs(float(x) - spot_price))


def get_available_dates(date_range: list, date_format: str):
    if len(date_range) > 2:
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


def load_data(paths, spot_price_symbol, index, time_format):
    dataset_mapper = {}
    for path in paths:
        if not os.path.exists(path):
            continue
        with open(path, "r") as file:
            lines = file.readlines()
            for line in lines[1:]:
                values = line.strip().split(",")
                symbol, date, time = values[1], values[2], values[3]
                prices = values[4:8]

                if date not in dataset_mapper:
                    dataset_mapper[date] = {
                        "CE": {},
                        "PE": {},
                        spot_price_symbol: {},
                        "CE_DETAILS": {
                            "available_strikes": [],
                            "available_expiries": [],
                        },
                        "PE_DETAILS": {
                            "available_strikes": [],
                            "available_expiries": [],
                        },
                    }

                option_type = (
                    "CE"
                    if symbol.endswith("CE")
                    else "PE" if symbol.endswith("PE") else spot_price_symbol
                )
                if option_type != spot_price_symbol:
                    if symbol not in dataset_mapper[date][option_type]:
                        dataset_mapper[date][option_type][symbol] = {}
                    dataset_mapper[date][option_type][symbol][time] = prices
                else:
                    dataset_mapper[date][spot_price_symbol][time] = prices

    symbols = [
        symbol
        for date in dataset_mapper
        for typ in ["CE", "PE"]
        for symbol in dataset_mapper[date][typ]
    ]
    for sym in symbols:
        if sym.endswith("CE"):
            strike, expiry = get_strike_expiry(sym, index, "CE")
            dataset_mapper[date]["CE_DETAILS"]["available_strikes"].append(strike)
            dataset_mapper[date]["CE_DETAILS"]["available_expiries"].append(expiry)
        elif sym.endswith("PE"):
            strike, expiry = get_strike_expiry(sym, index, "PE")
            dataset_mapper[date]["PE_DETAILS"]["available_strikes"].append(strike)
            dataset_mapper[date]["PE_DETAILS"]["available_expiries"].append(expiry)

    for date in dataset_mapper:
        dataset_mapper[date]["CE_DETAILS"]["available_strikes"] = sorted(
            set(dataset_mapper[date]["CE_DETAILS"]["available_strikes"])
        )
        dataset_mapper[date]["CE_DETAILS"]["available_expiries"] = sort_dates(
            time_format, set(dataset_mapper[date]["CE_DETAILS"]["available_expiries"])
        )
        dataset_mapper[date]["PE_DETAILS"]["available_strikes"] = sorted(
            set(dataset_mapper[date]["PE_DETAILS"]["available_strikes"])
        )
        dataset_mapper[date]["PE_DETAILS"]["available_expiries"] = sort_dates(
            time_format, set(dataset_mapper[date]["PE_DETAILS"]["available_expiries"])
        )

    write_file(dataset_mapper, "dataset_mapper.json", "w")

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


def get_overall_sl_tgt(
    result,
    contracts,
    total_investment,
    overall_target,
    overall_stoploss,
    time,
):
    total_currunt_value = 0
    for inst in contracts:
        if result[inst]["exit_price"] is not None:
            total_currunt_value += result[inst]["exit_price"]
            # print("total_currunt_value", total_currunt_value, "exit")
        else:
            total_currunt_value += result[inst]["currunt_close_price"]
            # print("total_currunt_value", total_currunt_value, "close")
    
    chnage_in_investment = total_currunt_value - total_investment

    if chnage_in_investment >= overall_target:
        for inst in contracts:
            if result[inst]["exit_price"] is None:
                result[inst]["exit_time"] = time
                result[inst]["exit_price"] = result[inst]["currunt_close_price"]
                result[inst]["exit_reason"] = "Overall Target Hitt"
        return True, result
    
    elif chnage_in_investment <= overall_stoploss:
        for inst in contracts:
            if result[inst]["exit_price"] is None:
                result[inst]["exit_time"] = time
                result[inst]["exit_price"] = result[inst]["currunt_close_price"]
                result[inst]["exit_reason"] = "Overall Stoploss Hitt"
        
        return True, result
    else:
        return False, result


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
    overall_stoploss:int
):
    result = {}

    min_entry_time, max_exit_time = get_startagy_overall_time_range(entry_times, exit_times, time_format)
    time_range = get_available_time_range([min_entry_time, max_exit_time], time_format)

    call_at_once_total_investment = True

    for currunt_date in dataset_mapper:
        if currunt_date not in result:
            result[currunt_date] = {}
        
        for time in time_range:
            for i, leg_entry_time in enumerate(entry_times):
                leg_exit_time = exit_times[i]
                leg_contract = contracts[i]
                action = tread_actions[i]
                target = targetList[i]
                stoploss = stoplossList[i]
                option_type = leg_contract[-2:]

                if leg_contract not in dataset_mapper[currunt_date][option_type]:
                    continue

                try:
                    open_price, high_price, low_price, close_price = map(float, dataset_mapper[currunt_date][option_type][leg_contract][time])
                except KeyError:
                    print("GOT key error >>>", KeyError)
                    continue

                if time == leg_entry_time:
                    result[currunt_date][leg_contract] = {
                        "entry_date": currunt_date,
                        "entry_time": time,
                        "exit_time": None,
                        "entry_price": open_price,
                        "exit_price": None,
                        "exit_reason": None,
                        "target_price": round(open_price + target, 2) if action == "BUY" else round(open_price - target, 2),
                        "stoploss_price": round(open_price - stoploss, 2) if action == "BUY" else round(open_price + stoploss, 2),
                        "P&L": None,
                        "currunt_close_price": close_price,
                        "action": action
                    }

                elif time == leg_exit_time:
                    if result[currunt_date][leg_contract]["exit_reason"] is None:
                        result[currunt_date][leg_contract]["exit_time"] = time
                        result[currunt_date][leg_contract]["exit_price"] = close_price
                        result[currunt_date][leg_contract]["exit_reason"] = "Normal Exit"
                        result[currunt_date][leg_contract]["P&L"] = (
                            round(result[currunt_date][leg_contract]["entry_price"] - close_price, 2)
                            if action == "BUY"
                            else
                            round(close_price - result[currunt_date][leg_contract]["entry_price"], 2)
                        )

                elif leg_contract in result[currunt_date]:
                    if (
                        (result[currunt_date][leg_contract]["entry_price"] is not None)
                        and
                        (result[currunt_date][leg_contract]["exit_reason"] is None)
                    ):
                        leg_investment = result[currunt_date][leg_contract]["entry_price"]
                        target_price = result[currunt_date][leg_contract]["target_price"]
                        stoploss_price = result[currunt_date][leg_contract]["stoploss_price"]
                        if action == "BUY":
                            if high_price >= target_price:
                                result[currunt_date][leg_contract]["exit_time"] = time
                                result[currunt_date][leg_contract]["exit_price"] = high_price
                                result[currunt_date][leg_contract]["exit_reason"] = "Individual Target Hit"
                                result[currunt_date][leg_contract]["P&L"] = round(high_price - leg_investment, 2)
                                result[currunt_date][leg_contract]["currunt_close_price"] = close_price
                                break
                            elif low_price <= stoploss_price:
                                result[currunt_date][leg_contract]["exit_time"] = time
                                result[currunt_date][leg_contract]["exit_price"] = low_price
                                result[currunt_date][leg_contract]["exit_reason"] = "Individual Stoploss Hit"
                                result[currunt_date][leg_contract]["P&L"] = round(low_price - leg_investment, 2)
                                result[currunt_date][leg_contract]["currunt_close_price"] = close_price
                                break
                        
                        elif action == "SELL":
                            if high_price >= stoploss_price:
                                result[currunt_date][leg_contract]["exit_time"] = time
                                result[currunt_date][leg_contract]["exit_price"] = high_price
                                result[currunt_date][leg_contract]["exit_reason"] = "Individual Stoploss Hit"
                                result[currunt_date][leg_contract]["P&L"] = round(leg_investment - high_price, 2)
                                result[currunt_date][leg_contract]["currunt_close_price"] = close_price
                                break
                            elif low_price <= target_price:
                                result[currunt_date][leg_contract]
                                result[currunt_date][leg_contract]["exit_time"] = time
                                result[currunt_date][leg_contract]["exit_price"] = low_price
                                result[currunt_date][leg_contract]["exit_reason"] = "Individual Target Hit"
                                result[currunt_date][leg_contract]["P&L"] = round(leg_investment - low_price, 2)
                                result[currunt_date][leg_contract]["currunt_close_price"] = close_price
                                break

            # overall
            if call_at_once_total_investment:
                total_investment = get_targets(result[currunt_date], contracts)
                call_at_once_total_investment = False
                result[currunt_date]["total_investment"] = total_investment

            is_sq_off,  result_x = get_overall_sl_tgt(
                result[currunt_date],
                contracts,
                total_investment,
                overall_target,
                overall_stoploss,
                time,
            )


    write_file(result, "final_result.json", mode="w")

    return result




def start_backtest():
    spot_price_symbol = "NIFTY-I"
    index = "NIFTY"
    date_range = ["08032023", "10032023"]
    entry_time = ["10:00:00", "10:00:00"]
    exit_time = ["13:30:00", "13:30:00"]
    overall_target = 50
    overall_stop_loss = 25
    targets = [100, 100]
    stop_loses = [100, 100]
    tread_actions = ["BUY", "BUY"]
    option_type = ["CE", "PE"]
    strike = ["ATM", "ATM+1"]
    expiries = ["weekly", "weekly"]

    FILE_DATE_FORMAT = "%d%m%Y"
    ROW_EXPIRY_TIME_FORMAT = "%d%b%y"
    TIME_FORMAT = "%H:%M:%S"

    dates = get_available_dates(date_range, FILE_DATE_FORMAT)
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
        overall_stop_loss
    )

    write_file(result, "final_result.json", "w")

    # print(result)



if __name__ == "__main__":
    start_backtest()