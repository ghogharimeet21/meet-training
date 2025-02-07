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
    os.makedirs("./outputdata", exist_ok=True)
    with open(f"./outputdata/{fileName}", "w") as file:
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


def sort_dates(date_format: str, date_list: list):
    return [
        datetime.strftime(obj, date_format).upper()
        for obj in sorted([datetime.strptime(date, date_format) for date in date_list])
    ]




def get_monthly_expiry(date_list, date_format="%d%b%y"):
    date_objs = [datetime.strptime(date, date_format) for date in date_list]
    first_date = date_objs[0]
    current_month = first_date.month
    current_month_dates = [date for date in date_objs if date.month == current_month]
    return datetime.strftime(current_month_dates[-1], date_format).upper()


def find_symbol(
    index,
    spot_price,
    available_expiries,
    available_strikes,
    opt_type,
    shift,
    expiry_type,
):
    atm = get_atm(float(spot_price), available_strikes)
    atm_index = available_strikes.index(atm)
    strike = available_strikes[min(atm_index + shift, len(available_strikes) - 1)]
    expiry = (
        available_expiries[0]
        if expiry_type.upper() == "WEEKLY"
        else (
            available_expiries[1]
            if expiry_type.upper() == "NEXT_WEEKLY"
            else get_monthly_expiry(available_expiries)
        )
    )
    return f"{index}{expiry}{strike}{opt_type}" if strike and expiry else None


def get_startagy_overall_time_range(entry_time, exit_time, time_format):
    entry_objs, exit_objs = [
        datetime.strptime(time, time_format) for time in entry_time
    ], [datetime.strptime(time, time_format) for time in exit_time]
    return min(entry_objs), max(exit_objs)


def get_available_time_range(time_range, time_format):
    from_time, to_time = datetime.strptime(
        time_range[0], time_format
    ), datetime.strptime(time_range[1], time_format)
    times = []
    while from_time <= to_time:
        times.append(datetime.strftime(from_time, time_format))
        from_time += timedelta(minutes=1)
    return times


def get_targets(result, contracts):
    # print("C"*50, contracts)
    total_investment = 0
    for contract in contracts:
        result[contract]["entry_price"] += total_investment
    return total_investment


def get_overall_sl_tgt(
    result,
    contracts,
    total_investment,
    overall_target,
    overall_stoploss,
    time,
    tread_action,
):
    
    total_current_value = sum(
        (
            result[inst]["exit_price"]
            if result[inst]["exit_price"] is not None
            else result[inst]["currunt_close_price"]
        )
        for inst in contracts
    )
    change_in_investment = total_current_value - total_investment

    print(
        f"Time: {time} | Total Investment: {total_investment} | Total Current Value: {total_current_value} | Change: {change_in_investment}"
    )

    if tread_action == "BUY":
        if change_in_investment >= overall_target:
            for inst in contracts:
                if result[inst]["exit_price"] is None:
                    result[inst].update(
                        {
                            "exit_price": result[inst]["currunt_close_price"],
                            "exit_reason": "Overall Target Hit",
                            "exit_time": time,
                        }
                    )
                    result[inst]["pnl"] = (
                        result[inst]["exit_price"] - result[inst]["entry_price"]
                    )
            return True, result
        elif change_in_investment <= -overall_stoploss:
            for inst in contracts:
                if result[inst]["exit_price"] is None:
                    result[inst].update(
                        {
                            "exit_price": result[inst]["currunt_close_price"],
                            "exit_reason": "Overall Stoploss Hit",
                            "exit_time": time,
                        }
                    )
                    result[inst]["pnl"] = (
                        result[inst]["exit_price"] - result[inst]["entry_price"]
                    )
            return True, result
        return False, result
    if tread_action == "SELL":
        if change_in_investment <= overall_target:
            for inst in contracts:
                if result[inst]["exit_price"] is None:
                    result[inst].update(
                        {
                            "exit_price": result[inst]["currunt_close_price"],
                            "exit_reason": "Overall Target Hit",
                            "exit_time": time,
                        }
                    )
                    result[inst]["pnl"] = (
                        result[inst]["entry_price"] - result[inst]["exit_price"]
                    )
            return True, result
        elif change_in_investment >= -overall_stoploss:
            for inst in contracts:
                if result[inst]["exit_price"] is None:
                    result[inst].update(
                        {
                            "exit_price": result[inst]["currunt_close_price"],
                            "exit_reason": "Overall Stoploss Hit",
                            "exit_time": time,
                        }
                    )
                    result[inst]["pnl"] = (
                        result[inst]["entry_price"] - result[inst]["exit_price"]
                    )
            return True, result
        return False, result


def get_pNl(
    dataset_mapper,
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
    min_entry_time, max_exit_time = get_startagy_overall_time_range(
        entry_time, exit_time, "%H:%M:%S"
    )
    time_range = get_available_time_range(
        [
            datetime.strftime(min_entry_time, "%H:%M:%S"),
            datetime.strftime(max_exit_time, "%H:%M:%S"),
        ],
        "%H:%M:%S",
    )
    call_at_once = True

    for currunt_date in dataset_mapper:
        result[currunt_date] = {}
        for time in time_range:
            for i, leg_entry_time in enumerate(entry_time):
                contract = contracts[i] 
                option_type = contract[-2:]

                if contract not in dataset_mapper[currunt_date][option_type]:
                    continue

                try:
                    open_price, high_price, low_price, close_price = map(
                        float, dataset_mapper[currunt_date][option_type][contract][time]
                    )
                except KeyError:
                    continue

                if time == leg_entry_time:
                    result[currunt_date]["overall"] = {}
                    result[currunt_date][contract] = {
                        "entry_date": currunt_date,
                        "entry_time": time,
                        "exit_time": None,
                        "entry_price": open_price,
                        "exit_price": None,
                        "exit_reason": None,
                        "target_price": None,
                        "target_stoploss": None,
                        "pnl": None,
                        "currunt_close_price": close_price,
                        "action": tread_actions[i],
                    }

                elif contract in result[currunt_date]:
                    if (
                        result[currunt_date][contract]["entry_price"] is not None
                        and result[currunt_date][contract]["exit_reason"] is None
                    ):
                        leg_investment = result[currunt_date][contract]["entry_price"]
                        target_price = (
                            leg_investment + targetList[i]
                            if tread_actions[i] == "BUY"
                            else leg_investment - targetList[i]
                        )
                        stop_loss_price = (
                            leg_investment - stop_lossList[i]
                            if tread_actions[i] == "BUY"
                            else leg_investment + stop_lossList[i]
                        )

                        result[currunt_date][contract].update(
                            {
                                "target_price": target_price,
                                "target_stoploss": stop_loss_price,
                            }
                        )

                        if tread_actions[i] == "BUY":
                            if high_price >= target_price:
                                result[currunt_date][contract].update(
                                    {
                                        "exit_time": time,
                                        "exit_price": high_price,
                                        "exit_reason": "Individual Target Hit",
                                        "pnl": round(high_price - leg_investment, 2),
                                    }
                                )
                                break
                            elif low_price <= stop_loss_price:
                                result[currunt_date][contract].update(
                                    {
                                        "exit_time": time,
                                        "exit_price": low_price,
                                        "exit_reason": "Individual Stoploss Hit",
                                        "pnl": round(low_price - leg_investment, 2),
                                    }
                                )
                                break
                        elif tread_actions[i] == "SELL":
                            if high_price >= stop_loss_price:
                                result[currunt_date][contract].update(
                                    {
                                        "exit_time": time,
                                        "exit_price": high_price,
                                        "exit_reason": "Individual Stoploss Hit",
                                        "pnl": round(leg_investment - high_price, 2),
                                    }
                                )
                                break
                            elif low_price <= target_price:
                                result[currunt_date][contract].update(
                                    {
                                        "exit_time": time,
                                        "exit_price": low_price,
                                        "exit_reason": "Individual Target Hit",
                                        "pnl": round(leg_investment - low_price, 2),
                                    }
                                )
                                break

            if call_at_once:
                total_investment = get_targets(result[currunt_date], contracts)
                result[currunt_date]["overall"] = {
                    "overall_investment": total_investment
                }
                call_at_once = False

            is_sq_off, result[currunt_date] = get_overall_sl_tgt(
                result[currunt_date],
                contracts,
                total_investment,
                overall_target,
                overall_stoploss,
                time,
                tread_actions[i],
            )
            if is_sq_off:
                print(f"Overall exit triggered at {time}")
                break

    return result


def start_backtest():
    spot_price_symbol = "NIFTY-I"
    index = "NIFTY"
    date_range = ["08032023", "10032023"]
    entry_time = ["11:00:00", "11:00:00"]
    exit_time = ["13:30:00", "13:30:00"]
    overall_target = 50
    overall_stop_loss = 25
    target = [20, 20]
    stop_loss = [10, 10]
    tread_actions = ["BUY", "BUY"]
    option_type = ["CE", "PE"]
    strike = ["ATM", "ATM+1"]
    expiries = ["weekly", "weekly"]

    dates = get_available_dates(date_range, "%d%m%Y")
    paths = get_all_dataset_paths("dataset", dates)
    dataset_mapper = load_data(paths, spot_price_symbol, index)

    contracts = []
    for current_date in dataset_mapper:
        for i, ent_time in enumerate(entry_time):
            for time, index_prices in dataset_mapper[current_date][
                spot_price_symbol
            ].items():
                if time == ent_time:
                    spot_price = index_prices[0]
                    shift = int(strike[i].replace("ATM", "") or 0)
                    segment_type = (
                        "CE_DETAILS" if option_type[i] == "CE" else "PE_DETAILS"
                    )
                    segment_details = dataset_mapper[current_date][segment_type]
                    contract = find_symbol(
                        index,
                        spot_price,
                        segment_details["available_expiries"],
                        segment_details["available_strikes"],
                        option_type[i],
                        shift,
                        expiries[i],
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
    write_in_jsonFile(result, "final.json")


if __name__ == "__main__":
    start_backtest()
