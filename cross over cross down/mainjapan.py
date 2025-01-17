import pandas as pd
import pyarrow.feather as feather
import os
    
cur_dir = os.getcwd()
files_name = os.listdir(cur_dir)

# for files in files_name:
#     if ".feather" in files:
#         name = files.split(".")[0]
#         sbin_files = feather.read_feather(files)
#         sbin_files.to_csv(f"{name}.csv")

csv_files = [file for file in files_name if (".csv" in file)]
# print(csv_files)

sbin_data = {}

for sbin_file in csv_files:
    with open(sbin_file, "r") as f:
        header = f.readline()[:-1].split(",")
        # print(header)
        indexOfDate = header.index('date')
        indexOfOpen = header.index('open')
        indexOfClose = header.index('close')
        # indexOfLabel = header.index("label")
        # print(indexOfLabel)
        
        curr_dates = sbin_file[-10:-4]
        # print(curr_dates)
        sbin_data[curr_dates] = []

        for row in f:
            data = row[:-1].split(",")
            # print(len(data))
            dict = {
                "time": data[1],
                "symbol": data[3],
                "open": data[4],
                "high": data[5],
                "low": data[6],
                "close": data[7]
                # "label": data[8],
                # "simple_moving_avg": data[9]
            }
            sbin_data[curr_dates].append(dict)

# print(sbin_data)
def sec_cal(time):
    hours,min = [int(x) for x in time.split(":")]
    return ((hours*3600) + (min*60))

def find_exit_time(start_index, exit_time, current_date, target_price, stop_loss_price, option_type):
    
    exit_index = 0
    new_exit_index = 0
    curr_index = start_index
    # print(start_index)
    # new_exit_time = exit_time
    
    for time in (sbin_data[current_date][start_index:]):
        cuu_time = int(time["time"])
        curr_index += 1
        if cuu_time == exit_time:
            exit_index = curr_index
            # print("exit_index", exit_index)
            break
    # print("exit_index", exit_index)
    
    # print(sbin_data[current_date][start_index:exit_index])
    data = sbin_data[current_date][start_index:exit_index]
    # print("len->", len(data))

    exit_index_from_target, exit_index_from_stop_loss = (-1, -1)

    exit_index_from_target = check_for_target_price(data= data, target_price = target_price, option_type = option_type)

    if (exit_index_from_target == 0):
        exit_index_from_stop_loss = check_for_stop_loss_price(data= data, stop_loss_price = stop_loss_price, option_type = option_type)
        
    if (exit_index_from_target != 0):
        new_exit_index = start_index + exit_index_from_target
    elif (exit_index_from_stop_loss != 0):
        new_exit_index = start_index + exit_index_from_stop_loss
    else:
        new_exit_index = exit_index
        
    return (new_exit_index - 1, exit_index - 1)  
        
def check_for_target_price(data, target_price, option_type):
    index, exit_index = (0, 0)
    for time in data:
        index += 1
        high_price, low_price = (float(time['high']), float(time['low']))

        if option_type == "long" and (high_price >= target_price):
            # return index
            # print("cuurr - index", index)
            exit_index = index
            break
        
        if option_type == "sorting" and (low_price <= target_price):
            # return index
            # print("cuurr - index", index)
            exit_index = index
            break
        
    return exit_index

def check_for_stop_loss_price(data, stop_loss_price, option_type):
    index, exit_index = (0, 0)
    for time in data:
        index += 1
        high_price, low_price = (float(time['high']), float(time['low']))

        if option_type == "long" and (low_price < stop_loss_price):
            # return index
            # print("cuurr - index", index)
            exit_index = index
            break
        
        if option_type == "sorting" and (high_price > stop_loss_price):
            # return index
            # print("cuurr - index", index)
            exit_index = index
            break
        
    return exit_index
        

def find_target_stopLoss_price(entry_time, current_date, target = 10, stop_loss = 5, option_type = "long"):
    target_price = 0
    stop_loss_price = 0
    start_index = -1
    for time in sbin_data[current_date]:
        cuu_time = int(time["time"])
        start_index += 1
        if entry_time == cuu_time:
            entry_open_price = float(time['open'])

            target_price = entry_open_price + (entry_open_price * (target / 100))
            stop_loss_price = entry_open_price - (entry_open_price * (stop_loss / 100))

            if option_type == "sorting":
                target_price = entry_open_price - (entry_open_price * (target / 100))
                stop_loss_price = entry_open_price + (entry_open_price * (stop_loss / 100))
            break

    return (start_index, target_price, stop_loss_price)
        

def cal_profit(buy_price, sell_price, option_type):
    (profit, profit_per) = (0, 0)
    profit = (sell_price - buy_price)
    if option_type == "sorting":
        profit_per = (profit / sell_price)*100
    else:
        profit_per = (profit / buy_price)*100
    
    return (profit, profit_per)


def find_profit(entry_time, exit_time, current_date, target = 1, stop_loss = 1, option_type = "long"):
    (entry_time_sec, exit_time_sec) = (sec_cal(entry_time), sec_cal(exit_time))
    
    (buy_open_price, sell_open_price) = (0, 0)

    # (buy_time, sell_time) = (entry_time_sec, exit_time_sec)

    (start_index, target_price, stop_loss_price) = (0, 0, 0)

    (profit, profit_per) = (0, 0)

    if option_type == "sorting":
        (buy_time, sell_time) = (exit_time_sec, entry_time_sec)

        (start_index, target_price, stop_loss_price) = find_target_stopLoss_price(sell_time, current_date, target, stop_loss, option_type)

        exit_index, old_exit_index = find_exit_time(start_index, exit_time_sec, current_date, target_price, stop_loss_price, option_type)

        entry_data = sbin_data[current_date][start_index]
        exit_data = sbin_data[current_date][exit_index]
        print("entry_data",entry_data)
        print("exit_data",exit_data)

        print("old_exit_data", sbin_data[current_date][old_exit_index])

        (sell_open_price, buy_open_price) = (float(entry_data['open']), float(exit_data['open']))
        print("sell ->", sell_open_price, "buy -> ", buy_open_price)
        # profit = (sell_open_price - buy_open_price)
        # profit_per = (profit / sell_open_price)*100
        (profit, profit_per) = cal_profit(buy_open_price, sell_open_price, option_type)
    else:
        (buy_time, sell_time) = (entry_time_sec, exit_time_sec)

        (start_index, target_price, stop_loss_price) = find_target_stopLoss_price(buy_time, current_date, target, stop_loss, option_type)

        exit_index, old_exit_index = find_exit_time(start_index, exit_time_sec, current_date, target_price, stop_loss_price, option_type)

        entry_data = sbin_data[current_date][start_index]
        exit_data = sbin_data[current_date][exit_index]
        print("entry_data", entry_data)
        print("exit_data", exit_data)

        print("old_exit_data", sbin_data[current_date][old_exit_index])

        (buy_open_price, sell_open_price) = (float(entry_data['open']), float(exit_data['open']))
        print("buy -> ", buy_open_price, "sell ->", sell_open_price)
        # profit = (sell_open_price - buy_open_price) 
        # profit_per = (profit / buy_open_price)*100
        (profit, profit_per) = cal_profit(buy_open_price, sell_open_price, option_type)

    return (profit, profit_per)

    
    

# print("short_term")
# print(find_profit(entry_time="10:00", exit_time="10:45", current_date="240606", option_type="sorting"))

# print("\nshort_term")
# print(find_profit(entry_time="10:15",exit_time="13:10",current_date="240606", option_type="sorting"))

# bullish_list = []
# bearish_list = []

def add_column_into_csv(current_date,label,data):
    for file in csv_files:
        if current_date in file:
            # print(file)
            csv_current_file = pd.read_csv(file)
            csv_current_file[label] = data
            csv_current_file.to_csv(file, index=False)
            break

def add_new_values_into_sbin_data(current_date, col_name):
    for file in csv_files:
        if current_date in file:
            # print(file)
            with open(file, "r") as f:
                header = f.readline()[:-1].split(",")
                indexOfCol = header.index(col_name)
                row_data = sbin_data[current_date]
                i = 0
                for row in f:
                    data = row[:-1].split(",")
                    row_data[i][col_name] = data[indexOfCol]
                    i += 1

add_new_values_into_sbin_data("240606", "label")
add_new_values_into_sbin_data("240606", "two_sma")
add_new_values_into_sbin_data("240606", "three_sma")
print(sbin_data)
pattern_list = ["-"]

def find_bullish_or_bearish_engulfing(entry_data, exit_data):
    print(entry_data)
    entry_open_price, entry_close_price, entry_label  = entry_data['open'], entry_data['close'], entry_data['label']
    exit_open_price, exit_close_price, exit_label = exit_data['open'], exit_data['close'], exit_data['label']
    print("entry_label", "=>", entry_label, "|", "exit_label", "=>", exit_label)
    if (entry_label == "red" and exit_label == "green") and (exit_close_price > entry_open_price) and (exit_open_price <= entry_close_price):
        # print("bullish")
        # bullish_list.append((entry_data, exit_data))
        pattern_list.append("bullish")
    elif (entry_label == "green" and exit_label == "red") and (exit_open_price >= entry_close_price) and (exit_close_price < entry_open_price):
        # print("bearish")
        # bearish_list.append((entry_data, exit_data))
        pattern_list.append("bearish")
    else:
        # print("Nothing")
        pattern_list.append("-")

def detect_bullish_bearish_engulfing_pattern(current_date):
    data, len_data = (sbin_data[current_date], len(sbin_data[current_date]))
    for row in range(1,len_data):
        # print(data[row])
        find_bullish_or_bearish_engulfing(data[row - 1], data[row])

# detect_bullish_bearish_engulfing_pattern("240606")
# print(pattern_list)
# add_column_into_csv("240606","pattern",pattern_list)

# sm_list = []
def cal_simple_moving_avg(current_date):
    sm_list = [0]
    data, len_data = (sbin_data[current_date], len(sbin_data[current_date]))
    close_values = []
    label = []
    for row in range(len_data):
        # print(data[row]['close'])
        close_values.append(float(data[row]['close']))

        # add labels
        if (data[row]['open'] > data[row]['close']):
            label.append("red")
        elif (data[row]['open'] < data[row]['close']):
            label.append("green")
        else:
            label.append("None")

        if row > 0:
            avg = pd.Series(close_values).mean()
            # avg = (sum(close_values) / len(close_values))
            sm_list.append(round(avg,3))
    return (label, sm_list)


def cal_sma(current_date, noOfRow = 2):
    sma = [0 for i in range(noOfRow-1)]
    data, len_data = (sbin_data[current_date], len(sbin_data[current_date]))
    close_values = [float(value['close']) for value in data]
    # print(close_values)
    # prv = 0
    for cur in range(noOfRow, len_data + 1):
        avg = pd.Series(close_values[(cur - noOfRow):cur]).mean()
        # print(round(avg,3))
        sma.append(round(avg,3))
    return sma

def check_for_cross_over_down(cur_data, prv_data):
    # cross down
    position = ""
    if (cur_data["two_sma"] < cur_data["three_sma"]) and (prv_data["two_sma"] > prv_data["three_sma"]):
        # print("sell")
        position = "sell"
    
    if (cur_data["two_sma"] > cur_data["three_sma"]) and (prv_data["two_sma"] < prv_data["three_sma"]):
        # print("buy")
        position = "buy"
    return position

def find_sell_or_buy_position(current_date):
    pos_list = ["-"]
    data, len_data = (sbin_data[current_date], len(sbin_data[current_date]))
    for row in range(1,len_data):
        cur = data[row]
        prv = data[row - 1]
        pos = check_for_cross_over_down(cur, prv)
        pos_list.append(pos)
    return pos_list

new_position = find_sell_or_buy_position("240606")
add_column_into_csv("240606", "buy_sell_position", new_position)



# two_sma_values = cal_sma("240606", 2)
# add_column_into_csv("240606","two_sma", two_sma_values)
# three_sma_values = cal_sma("240606", 3)
# add_column_into_csv("240606","three_sma", three_sma_values)

# detect_bullish_bearish_engulfing_pattern("240606")
# cal_simple_moving_avg("240606")
# print(pattern_list)



# detect_bullish_bearish_engulfing_pattern("240606")

# print("bullish_list\n", bullish_list)
# print("bearish_list\n", bearish_list)


# add_label_sbin_data("240606")
# add_label_sbin_data("240605")
# print(sbin_data)


    

