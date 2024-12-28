from datetime import datetime, timedelta
import time
import threading
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder,CommandHandler, ContextTypes, MessageHandler, filters
import asyncio
import logging
from iqoptionapi.stable_api import IQ_Option
import pandas as pd 
import numpy as np
from telegram import Bot
import random
import string
import warnings
import os
import json
from tvDatafeed import TvDatafeed, Interval
from asyncio import Lock



#Fetching the data
brokerage_lock = Lock()
lock_settf = asyncio.Lock()
today = datetime.today()
loop_task_running = False
is_running = False
last_execution = {}
day = today.strftime("%A")
TF_FILE = "tf.json"
db_file = 'database.json'
#Assiging the Dictonory
user_data = {}
pending_orders = {} #Pending orders 
timeframe = [] #TimeFrame that is set by admin
PnL = {}
crnt_pair = {
    'pair':None
}
daily_data = {'pairs': {}}
Check_Generating_signal = False

#Integrating Trading view
async def analyze_currency_pair_tradingView(pair,update: Update, context: ContextTypes.DEFAULT_TYPE,tf):
    interval = ''
    tv = TvDatafeed() 
    if tf == 60:
        interval = Interval.in_1_minute
    elif tf == 120:
        interval = Interval.in_3_minute
    elif tf == 300:
        interval = Interval.in_5_minute
    elif tf == 900:
        interval = Interval.in_15_minute
    elif tf == 1800:
        interval = Interval.in_30_minute
    elif tf == 3600:
        interval = Interval.in_1_hour
    elif tf == 7200:
        interval = Interval.in_2_hour
    elif tf == 10800:
        interval = Interval.in_3_hour
    elif tf == 14400:
        interval = Interval.in_4_hour
    elif tf == 86400:
        interval = Interval.in_daily

    df = tv.get_hist(symbol=pair, exchange='Fx', interval=interval, n_bars=200)
    if  df is None:
        df = tv.get_hist(symbol=pair, exchange='Fx', interval=interval, n_bars=200)
    # Reverse the dataframe to ensure indexing works correctly
    df = df.iloc[::-1]
    json_data = df.to_json(orient='records')
    # Ignore the current (most recent) candle
    df = df.iloc[1:]

    if df is not None and not df.empty:
        if len(df) >= 11:  # Ensure we have at least 11 candles (ignoring the most recent one)
            for i in range(1, 12):  # Iterating for 11 candles
                row = df.iloc[i - 1]
                open_price = row['open']
                high_price = row['high']
                low_price = row['low']
                close_price = row['close']
                candle_time = row.name
                candle_time_ist = candle_time.strftime('%Y-%m-%d %H:%M:%S')  # Converting timestamp to string

                if i == 1:
                    global candle1_open, candle1_high, candle1_low, candle1_close, candle1_time
                    candle1_open = open_price
                    candle1_high = high_price
                    candle1_low = low_price
                    candle1_close = close_price
                    candle1_time = candle_time_ist
                elif i == 2:
                    global candle2_open, candle2_high, candle2_low, candle2_close, candle2_time
                    candle2_open = open_price
                    candle2_high = high_price
                    candle2_low = low_price
                    candle2_close = close_price
                    candle2_time = candle_time_ist
                elif i == 3:
                    global candle3_open, candle3_high, candle3_low, candle3_close, candle3_time
                    candle3_open = open_price
                    candle3_high = high_price
                    candle3_low = low_price
                    candle3_close = close_price
                    candle3_time = candle_time_ist
                elif i == 4:
                    global candle4_open, candle4_high, candle4_low, candle4_close, candle4_time
                    candle4_open = open_price
                    candle4_high = high_price
                    candle4_low = low_price
                    candle4_close = close_price
                    candle4_time = candle_time_ist
                elif i == 5:
                    global candle5_open, candle5_high, candle5_low, candle5_close, candle5_time
                    candle5_open = open_price
                    candle5_high = high_price
                    candle5_low = low_price
                    candle5_close = close_price
                    candle5_time = candle_time_ist
                elif i == 6:
                    global candle6_open, candle6_high, candle6_low, candle6_close, candle6_time
                    candle6_open = open_price
                    candle6_high = high_price
                    candle6_low = low_price
                    candle6_close = close_price
                    candle6_time = candle_time_ist
                elif i == 7:
                    global candle7_open, candle7_high, candle7_low, candle7_close, candle7_time
                    candle7_open = open_price
                    candle7_high = high_price
                    candle7_low = low_price
                    candle7_close = close_price
                    candle7_time = candle_time_ist
                elif i == 8:
                    global candle8_open, candle8_high, candle8_low, candle8_close, candle8_time
                    candle8_open = open_price
                    candle8_high = high_price
                    candle8_low = low_price
                    candle8_close = close_price
                    candle8_time = candle_time_ist
                elif i == 9:
                    global candle9_open, candle9_high, candle9_low, candle9_close, candle9_time
                    candle9_open = open_price
                    candle9_high = high_price
                    candle9_low = low_price
                    candle9_close = close_price
                    candle9_time = candle_time_ist
                elif i == 10:
                    global candle10_open, candle10_high, candle10_low, candle10_close, candle10_time
                    candle10_open = open_price
                    candle10_high = high_price
                    candle10_low = low_price
                    candle10_close = close_price
                    candle10_time = candle_time_ist
                elif i == 11:
                    global candle11_open, candle11_high, candle11_low, candle11_close, candle11_time
                    candle11_open = open_price
                    candle11_high = high_price
                    candle11_low = low_price
                    candle11_close = close_price
                    candle11_time = candle_time_ist
        
    if len(json_data) >= 100:
        trend = identify_trend_trview(json_data)
        rsi = get_rsi_trview(json_data)

    await Generating_signals(update, candle1_open, candle1_close, candle2_open, candle2_close, pair, trend, candle1_low, candle1_high,candle3_open,candle3_close,candle4_open,candle4_close,candle5_open,candle5_close,update.effective_user.id,context,pair, candle6_open, candle6_high, candle6_low, candle6_close, candle6_time,candle7_open, candle7_high, candle7_low, candle7_close, candle7_time,candle8_open, candle8_high, candle8_low, candle8_close, candle8_time,candle9_open, candle9_high, candle9_low, candle9_close, candle9_time,candle10_open, candle10_high, candle10_low, candle10_close, candle10_time,rsi,tf)



def get_rsi_trview(candle_data, period=14):
    # Parse JSON string into Python list if not already parsed
    if isinstance(candle_data, str):
        candle_data = json.loads(candle_data)
    
    # Get the closing prices from the candle data
    close_prices = np.array([float(candle['close']) for candle in candle_data])
    
    if len(close_prices) < period + 1:
        raise ValueError(f"Not enough data to calculate RSI. Need at least {period + 1} data points.")
    
    # Calculate the differences in the closing prices
    deltas = np.diff(close_prices)
    
    # Calculate the gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate the initial average gain and loss for the given period
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    # RSI calculation using the smoothing method
    if avg_loss == 0:
        rsi = 100  # All gains, no losses
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    
    # Smooth RSI over the rest of the series
    for i in range(period, len(close_prices) - 1):
        gain = gains[i]
        loss = losses[i]
        
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
    
    # Return the most recent RSI value and its interpretation
    if rsi > 70:
        return "Overbought"
    elif 50 < rsi <= 70:
        return "Up"
    elif 30 < rsi <= 50:
        return "Down"
    elif rsi <= 30:
        return "Oversold"
    


def identify_trend_trview(candle_data, sma_short_window=3, sma_long_window=5):
        # Parse the JSON string into a Python object (list of dictionaries)
        candle_list = json.loads(candle_data)
        
        # Extract close prices as floats
        closes = [float(candle['close']) for candle in candle_list]
        
        # Check if sufficient data is available
        if len(closes) < max(sma_short_window, sma_long_window):
            raise ValueError("Not enough data to calculate SMAs.")

        # Calculate short-term and long-term SMAs
        sma_short = sum(closes[-sma_short_window:]) / sma_short_window
        sma_long = sum(closes[-sma_long_window:]) / sma_long_window
        
        # Determine trend based on SMA comparison
        if sma_short < closes[0]:
            return "Uptrend"
        elif sma_short > closes[0]:
            return "Downtrend"
        else:
            return "Sideways"

def update_exchange_rate_trdview(symbol):
    tv = TvDatafeed()
    df = tv.get_hist(symbol=symbol, exchange='Fx', interval=Interval.in_1_minute, n_bars=2)
    if df is None:
        df = tv.get_hist(symbol=symbol, exchange='Fx', interval=Interval.in_1_minute, n_bars=2)
        json_data = df.to_json(orient='records')
    json_data = json.loads(json_data)
    price = json_data[0]['close']
    return price



def calculate_accuracy(total_signal, total_win):
    if total_signal != 0:
        return f"{round((total_win / total_signal) * 100, 2)}%"
    else:
        return "0%"







def update_json_data(file_path, time_frame, date, pair, day, tsk,strategy_no):
    try:
        # Step 1: Load JSON data from the file
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Step 2: Find the matching record and update it
        updated = False  # Flag to check if an update occurred
        for record in data:
            # Check if the record contains the target date
            if date in record:
                # Get the details of the date
                details = record[date][day]
                # Check if Pair and Time Frame match
                if details["Pair"] == pair and details["Time Frame"] == time_frame and details["Strategy"] == strategy_no:
                    if tsk == "ts":
                        # Update Total Signal (+1)
                        details["Total Signal"] += 1
                    elif tsk == "tw":
                        # Update Total Signal, Total Win, and Accuracy
                        details["Total Win"] += 1
                        details["Accuracy"] = round((details["Total Win"] / details["Total Signal"]) * 100, 2)
                    elif tsk == "rf":
                        # Reduce Total Signal (-1)
                        details["Total Signal"] -= 1
                    elif tsk == 'um':
                        details["Total MTG"] += 1
                    elif tsk == 'uml':
                        details["MTG Loss"] += 1 
                    updated = True
                    break

       
        # Step 3: Save the updated data back to the file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        print("JSON data updated successfully.")

    except FileNotFoundError:
        print("Error: JSON file not found.")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format.")
    except Exception as e:
        print(f"An error occurred: {e}")


def update_to_json_with_preprocessing(tf, symbol, date,day,tsk,strategy_no):
    update_json_data("database.json", tf, date, symbol,day,tsk,strategy_no)
    




#Telegram Token
TOKEN = '8077880108:AAHNk-tA4oGiVpsPgkKTdiPS-vJ3C9GBKiY'

#Setup the api key
Api = IQ_Option("anubhavtomer263@gmail.com", "7592301521Arpit")
Api.connect()

#Debug the output
print("Bot is working properly....")

def initialize_pending_orders(serial_number):
    if serial_number not in pending_orders:
        pending_orders[serial_number] = {
            'pair': None,
            'direction': None,
            'st': 0,
            'et': 0,
            'mn': 0,
            'serial_number': None,
            'entery_position': 0,
            'Strategy': 0
        }

def initialize_p_L(user_id):
    pairs = load_pairs()
    if user_id not in PnL:
        PnL[user_id] = {
            'take_risk':{pair: 0 for pair in pairs},
            'commision': {pair: 0 for pair in pairs},
            'amount': 0
        }


def find_result(pair,position,dir,dta):
    if dir == 'up':
        if dta == 2 or dta == '2':
            current_price = update_exchange_rate(pair)
        elif dta == 1 or dta == '1':
            current_price = update_exchange_rate_trdview(pair)
        if current_price > position:
            return 'Win'
        elif current_price < position:
            return 'Loss'
        elif current_price == position:
            return 'Refund'
    elif dir == 'down':
        if dta == 2 or dta == '2':
            current_price = update_exchange_rate(pair)
        elif dta == 1 or dta == '1':
            current_price = update_exchange_rate_trdview(pair)
        if current_price < position:
            return 'Win'
        elif current_price > position:
            return 'Loss'
        elif current_price == position:
            return 'Refund'

def calc_amount(pair,rs):
    for user_id in PnL:
        brokerage = PnL[user_id]['commision'][pair]
        Risk_amount = PnL[user_id]['take_risk'][pair]
        if rs == 'win':
            reward = (Risk_amount/100) * int(brokerage)
            PnL[user_id]['amount'] += reward
        elif rs == 'loss':
            PnL[user_id]['amount'] -= Risk_amount


def get_results(user_id,dta):
    def execute_position(symbol):
        try:
            if dta == 2 or dta == '2':
                position = update_exchange_rate(symbol)
            elif dta == 1 or dta == '1':
                position = update_exchange_rate_trdview(symbol)
            return position
        except Exception as e:
            print(f"Error in execute_position for symbol {symbol}: {e}")
            return None
    results = []  # Store results for all pairs
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    date = now.strftime("%d/%m/%Y")
    day = now.strftime("%A")

    if not pending_orders:
        return []

    for key, order in list(pending_orders.items()):  # Use list to avoid mutation during iteration
        try:
            # Safely extract data from each order
            start_time = order.get('st', None)
            end_time = order.get('et', None)
            real_pair = order.get('pair', None)
            direction = order.get('direction', None)
            minute = order.get('mn', 0)
            serial_number = order.get('serial_number', None)
            entry_position = order.get('entery_position', 0)
            strategy = order.get('Strategy', 0)
            
            # Ensure necessary fields are populated
            if real_pair is None or direction is None or start_time == 0 or end_time == 0:
                print(f"Invalid data for order {key}: Missing pair or times")
                continue

            # Check if we are at the start time
            if current_time == start_time:
                position = execute_position(real_pair)
                if position is not None:
                    pending_orders[key]['entery_position'] = position
                else:
                    print(f"Failed to execute position for {real_pair}")

            # Check if we are at the end time
            elif current_time == end_time and entry_position != 0: 
                result = find_result(real_pair, entry_position, direction,dta)
                msg_template = (
                    f"Result:\n\nSignal ID: #{serial_number}\n\n{real_pair} : {minute} min {direction}\n"
                    f"Time: {start_time} to {end_time}\n"
                )

                if result == 'Win':
                    calc_amount(real_pair,'win')
                    user_data[user_id]['total_win'] += 1
                    tf = convert_m_to_tf(minute)
                    update_to_json_with_preprocessing(tf, real_pair, date, day, "tw", strategy)
                    del pending_orders[key]
                    results.append(msg_template + "🎯 Win 🎯")

                elif result == 'Loss':
                    calc_amount(real_pair,'loss')
                    user_data[user_id]['Loss'] += 1
                    del pending_orders[key]
                    results.append(msg_template + "😟 Loss 😟")

                elif result == 'Refund':
                    user_data[user_id]['Total_signal'] -= 1
                    tf = convert_m_to_tf(minute)
                    update_to_json_with_preprocessing(tf, real_pair, date, day, "rf", strategy)
                    del pending_orders[key]
                    results.append(msg_template + "😐 Refund 😐")

        except Exception as e:
            print(f"Error processing order {key}: {e}")

    return results  # Return all results collected




def convert_m_to_tf(m):
    tf = 0 
    if m == 1:
        tf = 60
    elif m == 2:
        tf = 120
    elif m == 5:
        tf = 300
    elif m == 15:
        tf = 900
    elif m == 30:
        tf = 1800
    elif m == 60:
        tf = 3600
    elif m == 120:
        tf = 7200
    elif m == 180:
        tf = 10800
    elif m == 240:
        tf = 14400
    elif m == 1440:
        tf = 86400          
    return tf

def generate_serial_code():
    digits = ''.join(random.choices(string.digits, k=3))
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    code = ''.join(random.sample(digits + letters, k=6))
    return code

#Before Making the anylsings function we will make setup user first
def initialize_user(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'Total_signal': 0,
            'total_win': 0,
            'Refund': 0,
            'Result': 0,
            'MTG': 0,
            'Loss':0,
            'is_running': True,
            'Total_mtg':0,
            'waiting_for_report':None
        }



#MaKing the fucntion to fetch the data
async def analyze_currency_pair(pair,update: Update, context: ContextTypes.DEFAULT_TYPE,tf):
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    
    try:
        # Fetch 1-minute candlestick data
        interval_1min = tf # In seconds
        outputsize_1min = 200
        candle_data_1min = Api.get_candles(pair, interval_1min, outputsize_1min, time.time())
        
        if len(candle_data_1min) >= 12:
            # Convert timestamps to IST
            ist = pytz.timezone('Asia/Kolkata')
            # Reverse the candle data list to have the most recent candle as candle1
            candle_data_1min.reverse()

            # Process each candle's data
            for i in range(12):
                candle = candle_data_1min[i]
                
                # Assign values for each 1-minute candle
                open_price = float(candle.get('open', 0))
                high_price = float(candle.get('max', 0))
                low_price = float(candle.get('min', 0))
                close_price = float(candle.get('close', 0))
                
                # Convert timestamp to IST
                candle_time_utc = datetime.utcfromtimestamp(candle.get('from', 0))
                candle_time_ist = candle_time_utc.replace(tzinfo=pytz.utc).astimezone(ist).strftime('%Y-%m-%d %H:%M:%S')
                
                # Store in separate variables
                if i == 1:
                    global candle1_open, candle1_high, candle1_low, candle1_close, candle1_time
                    candle1_open = open_price
                    candle1_high = high_price
                    candle1_low = low_price
                    candle1_close = close_price
                    candle1_time = candle_time_ist
                elif i == 2:
                    global candle2_open, candle2_high, candle2_low, candle2_close, candle2_time
                    candle2_open = open_price
                    candle2_high = high_price
                    candle2_low = low_price
                    candle2_close = close_price
                    candle2_time = candle_time_ist
                elif i == 3:
                    global candle3_open, candle3_high, candle3_low, candle3_close, candle3_time
                    candle3_open = open_price
                    candle3_high = high_price
                    candle3_low = low_price
                    candle3_close = close_price
                    candle3_time = candle_time_ist
                elif i == 4:
                    global candle4_open, candle4_high, candle4_low, candle4_close, candle4_time
                    candle4_open = open_price
                    candle4_high = high_price
                    candle4_low = low_price
                    candle4_close = close_price
                    candle4_time = candle_time_ist
                elif i == 5:
                    global candle5_open, candle5_high, candle5_low, candle5_close, candle5_time
                    candle5_open = open_price
                    candle5_high = high_price
                    candle5_low = low_price
                    candle5_close = close_price
                    candle5_time = candle_time_ist
                elif i == 6:
                    global candle6_open, candle6_high, candle6_low, candle6_close, candle6_time
                    candle6_open = open_price
                    candle6_high = high_price
                    candle6_low = low_price
                    candle6_close = close_price
                    candle6_time = candle_time_ist
                elif i == 7:
                    global candle7_open, candle7_high, candle7_low, candle7_close, candle7_time
                    candle7_open = open_price
                    candle7_high = high_price
                    candle7_low = low_price
                    candle7_close = close_price
                    candle7_time = candle_time_ist
                elif i == 8:
                    global candle8_open, candle8_high, candle8_low, candle8_close, candle8_time
                    candle8_open = open_price
                    candle8_high = high_price
                    candle8_low = low_price
                    candle8_close = close_price
                    candle8_time = candle_time_ist
                elif i == 9:
                    global candle9_open, candle9_high, candle9_low, candle9_close, candle9_time
                    candle9_open = open_price
                    candle9_high = high_price
                    candle9_low = low_price
                    candle9_close = close_price
                    candle9_time = candle_time_ist
                elif i == 10:
                    global candle10_open, candle10_high, candle10_low, candle10_close, candle10_time
                    candle10_open = open_price
                    candle10_high = high_price
                    candle10_low = low_price
                    candle10_close = close_price
                    candle10_time = candle_time_ist
                elif i == 11:
                    global candle11_open, candle11_high, candle11_low, candle11_close, candle11_time
                    candle11_open = open_price
                    candle11_high = high_price
                    candle11_low = low_price
                    candle11_close = close_price
                    candle11_time = candle_time_ist


        # Determine the trend based on the candle data
        candle_data_1min.reverse()
        if len(candle_data_1min) >= 100:
            trend = identify_trend(candle_data_1min)
            rsi = get_rsi(candle_data_1min)
        else:
            trend = "Insufficient data"
            print("Insufficient data")
      
          
    
        await Generating_signals(update, candle1_open, candle1_close, candle2_open, candle2_close, pair, trend, candle1_low, candle1_high,candle3_open,candle3_close,candle4_open,candle4_close,candle5_open,candle5_close,update.effective_user.id,context,pair, candle6_open, candle6_high, candle6_low, candle6_close, candle6_time,candle7_open, candle7_high, candle7_low, candle7_close, candle7_time,candle8_open, candle8_high, candle8_low, candle8_close, candle8_time,candle9_open, candle9_high, candle9_low, candle9_close, candle9_time,candle10_open, candle10_high, candle10_low, candle10_close, candle10_time,rsi,tf)

    except Exception as e:
        print(f"An error occurred in anylsing function: {e}")




#Using the rsi
def get_rsi(candle_data, period=14):
    # Get the closing prices from the candle data
    close_prices = np.array([candle['close'] for candle in candle_data])
    
    # Calculate the differences in the closing prices
    deltas = np.diff(close_prices)
    
    # Calculate the gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate the average gain and average loss over the period
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    # RSI calculation using the smoothing method
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    
    # Process further RSI values for all candles
    for i in range(period, len(close_prices)):
        gain = gains[i - 1]
        loss = losses[i - 1]
        
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs))
    
    # Check the most recent RSI value and return the corresponding signal as a string
    if rsi > 70:
        return f"Overbought"
    elif 50 < rsi <= 70:
        return f"Up"
    elif 30 < rsi <= 50:
        return f"Down"
    elif rsi <= 30:
        return f"Oversold"
    
#Support and ressitance
def calculate_support_resistance(candle_data):
    highs = [float(candle['max']) for candle in candle_data]
    lows = [float(candle['min']) for candle in candle_data]

    if len(highs) < 100 or len(lows) < 100:
        raise ValueError("Insufficient data")

    # Calculate resistance and support levels based on different lookback perisnrods
    R1 = max(highs[-100:])  # Resistance based on last 100 candles
    S1 = min(lows[-100:])   # Support based on last 100 candles

    R2 = max(highs[-25:])   # Resistance based on last 25 candles
    S2 = min(lows[-25:])    # Support based on last 25 candles

    R3 = max(highs[-10:])   # Resistance based on last 10 candles
    S3 = min(lows[-10:])    # Support based on last 10 candles

    return R1, R2, R3, S1, S2, S3


#Trend
def identify_trend(candle_data, sma_short_window=100, sma_long_window=100):
    closes = [float(candle['close']) for candle in candle_data]
    
    # Calculate the short-term and long-term SMAs
    sma_short = sum(closes[-sma_short_window:]) / sma_short_window
    sma_long = sum(closes[-sma_long_window:]) / sma_long_window
    
    # Determine trend based on SMA comparison
    if sma_short < closes[-1]:
        return "Uptrend"
    elif sma_short > closes[-1]:
        return "Downtrend"
    else:
        return "Sideways"
    

def create_database_for_pairs_and_timeframes(pairs_to_check, time_frames_to_check):
    filename = 'database.json'
    now = datetime.now()
    date = now.strftime("%d/%m/%Y")
    day = now.strftime("%A")
    strategies = [1, 2, 3]

    # Load existing data or initialize an empty list
    try:
        with open(filename, "r") as file:
            data = json.load(file)
            if not isinstance(data, list):
                raise ValueError("Invalid data format in the JSON file. Expected a list.")
    except (FileNotFoundError, json.JSONDecodeError):
        print("Initializing a new database.")
        data = []

    # Helper function to check if a pair and timeframe exist for a given date
    def is_pair_and_timeframe_in_database(pair, time_frame):
        for entry in data:
            if (
                date in entry and 
                entry[date][day]["Pair"] == pair and 
                entry[date][day]["Time Frame"] == time_frame
            ):
                return True
        return False

    # Helper function to create a new database entry
    def create_entry(pair, time_frame, strategy):
        return {
            date: {
                day: {
                    "Date": date,
                    "Day": day,
                    "Pair": pair,
                    "Strategy": strategy,
                    "Time Frame": time_frame,
                    "Total Signal": 0,
                    "Total Win": 0,
                    "Accuracy": "0%"
                }
            }
        }

    # Check pairs and timeframes and add missing ones
    new_entries = []
    for pair in pairs_to_check:
        for time_frame in time_frames_to_check:
            if not is_pair_and_timeframe_in_database(pair, time_frame):  # Check if pair and timeframe exist
                for strategy in strategies:
                    new_entries.append(create_entry(pair, time_frame, strategy))

    # Update the database if new entries were added
    if new_entries:
        data.extend(new_entries)
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Added {len(new_entries)} new entries to the database.")
    else:
        print("All provided pairs and timeframes are already in the database.")

##Now Making the function that will anylsis the currency pairs(Price action)

async def Generating_signals(update, candle1_open, candle1_close, candle2_open, candle2_close, pair, trend, candle1_low, candle1_high,candle3_open,candle3_close,candle4_open,candle4_close,candle5_open,candle5_close,user_id,context,symbol, candle6_open, candle6_high, candle6_low, candle6_close, candle6_time,candle7_open, candle7_high, candle7_low, candle7_close, candle7_time,candle8_open, candle8_high, candle8_low, candle8_close, candle8_time,candle9_open, candle9_high, candle9_low, candle9_close, candle9_time,candle10_open, candle10_high, candle10_low, candle10_close, candle10_time,rsi,tf):
        global Check_Generating_signal
        now = datetime.now()
        date = now.strftime("%d/%m/%Y")
        day = now.strftime("%A")
        #Making the gloabal flag to identify that the function is running or not
        Check_Generating_signal = True
        st = None
        mtg_status = get_mtg_status()
        #Making some Variables to use in code 
        cndlevol2 = 0
        t = int(load_gap())
        rslt = ''
        chances = ""
        #SetUp the user
        initialize_user(user_id)
        strategy = load_strategy()

        if not strategy:
            strategy = [1,2,3]

        #Return the code if use Is_running is set to False
        if not user_data[user_id]['is_running']:
            return
        
        if not user_id in user_data:
            initialize_user(user_id)
        


        try:
           
            waiting = 'Waiting for result....'
            Result = ''

            

            ##Calculating the Candles volume 

            #Candle1
            if candle1_open < candle1_close:
                color2 = 'green'
                solution1 = candle1_close - candle1_open
            elif candle1_open > candle1_close:
                color2 = 'red'
                solution1 = candle1_open - candle1_close
            else:
                solution1 = 0  

            #Candle2
            if candle2_open < candle2_close:
                solution2 = candle2_close - candle2_open
            elif candle2_open > candle2_close:
                solution2 = candle2_open - candle2_close
            else:
                solution2 = 0  
            if 'timelist' not in user_data[user_id]:
                user_data[user_id]['timelist'] = {
                    'tmst': None,
                    'endtm': None,
                    'dir': None,
                    'sym': None
                }

            
            #Candle3
            if candle3_open < candle3_close:
                color2 = 'green'
               
            elif candle3_open > candle3_close:
                color2 = 'red'


           






 
       
       
            # Helper function to detect Dragonfly Doji
            def is_dragonfly_doji():
                return candle1_close == candle1_high and abs(candle1_open - candle1_low) > abs(candle1_high - candle1_close) * 2

            # Helper function to detect Evening Star Doji
            def is_evening_star_doji():
                return candle1_open < candle1_close < (candle1_high + candle1_low) / 2

            # Helper function to detect Inverted Hammer
            def is_inverted_hammer():
                return (candle1_close > candle1_open) and (candle1_high - candle1_close) >= 2 * abs(candle1_close - candle1_open)

            # Helper function to detect Gravestone Doji
            def is_gravestone_doji():
                return candle1_close == candle1_low and abs(candle1_open - candle1_high) > abs(candle1_low - candle1_open) * 2

            # Helper function to detect Shooting Star Doji
            def is_shooting_star_doji():
                return candle1_open > candle1_close > (candle1_high + candle1_low) / 2

            # Helper function to detect Hammer
            def is_hammer():
                return (candle1_open > candle1_close) and (candle1_high - candle1_open) >= 2 * abs(candle1_open - candle1_close)
            

            # Function to detect if Candle 1 is an "up" type (Dragonfly Doji, Evening Star Doji, or Inverted Hammer)
            def Detect_up_candle():
                if is_dragonfly_doji() or is_evening_star_doji() or is_inverted_hammer():
                    return True
                return False

            # Function to detect if Candle 1 is a "down" type (Gravestone Doji, Shooting Star Doji, or Hammer)
            def Detect_down_candle():
                if is_gravestone_doji() or is_shooting_star_doji() or is_hammer():
                    return True
                return False

            def strategy1(dir):
                wg = 0
                wick = 0
                if dir == 'up':
                    if trend == "Uptrend":
                        wg += 1
                    elif rsi == "Up":
                        wg += 1
                    elif candle1_open > candle1_close and candle2_open > candle2_close and solution2 >= (1.75 * solution1):
                        wg += 1
                    if color2 == "red":
                        wick = candle1_close - candle1_low

                    if wick != 0:
                        if solution1 < wick:
                            wg += 1 
                    return wg
                elif dir == 'down':
                    if trend == "Downtrend":
                        wg += 1
                    elif rsi == "Down":
                        wg += 1
                    elif candle1_open < candle1_close and candle2_open < candle2_close and solution2 >= (1.75 * solution1):
                        wg += 1
                    
                    if color2 == "green":
                        wick = candle1_close - candle1_high

                    if wick != 0:
                        if solution1 < wick:
                            wg += 1
                    return wg

            def strategy2(dir):
                if dir == 'up':
                    if (candle1_open > candle2_close) and (candle1_close > candle2_high):
                        return True
                    return False
                if dir == 'down':
                    if (candle1_open < candle2_close) and (candle1_close < candle2_low):
                        return True
                    return False      

            def strategy3(dir):
                if dir == 'up':
                    a = Detect_up_candle()
                    if candle2_open < candle2_close and candle3_open < candle3_close and candle4_open < candle4_close and a == True: 
                        return a 
                elif dir == 'down':
                    a = Detect_down_candle()
                    if candle2_open > candle2_close and candle3_open > candle3_close and candle4_open > candle4_close and a == True: 
                        return a 

            #Now adding the most Important function Trading signals Up and down
            async def trade_up_strategy():
                global time_start      
                dir = None
                m1 = ''
                if tf == 60:
                    m1 = '1 min'
                elif tf == 120:
                    m1 = '2 min' 
                elif tf == 300:
                    m1 = '5 min'
                elif tf == 900:
                    m1 = '15 min'
                elif tf == 1800:
                    m1 = '30 min'
                elif tf == 3600:
                    m1 = '1 Hour'
                elif tf == 7200:
                    m1 = '2 Hour'
                elif tf == 10800:
                    m1 = '3 Hour'
                elif tf == 14400:
                    m1 = '4 Hour'
                elif tf == 86400:
                    m1 = '1 Day'
                m = 0
                if tf == 60:
                    m = 1
                elif tf == 120:
                    m = 2 
                elif tf == 300:
                    m = 5
                elif tf == 900:
                    m = 15
                elif tf == 1800:
                    m = 30
                elif tf == 3600:
                    m = 60
                elif tf == 7200:
                    m = 120
                elif tf == 10800:
                    m = 180
                elif tf == 14400:
                    m = 240
                elif tf == 86400:
                    m = 1440
            # Implement the main strategy
                try:    

                    async def to_do_up(sgnl_type,str):
                        serial_number = generate_serial_code()
                        initialize_pending_orders(serial_number)
                        ist_zone = pytz.timezone('Asia/Kolkata')
                        now_utc = datetime.now(pytz.utc)
                        now = now_utc.astimezone(ist_zone)
                        rounded_time = (now + timedelta(minutes=t)).replace(second=0, microsecond=0)
                        end_time = rounded_time + timedelta(minutes=m)
                        Signal = f"{symbol} : {m1} Up"
                        st_time = rounded_time.strftime('%H:%M')
                        en_time = end_time.strftime('%H:%M')
                        Time_range = f"Time : {st_time} to {en_time}"
                        user_data[user_id]['Total_signal'] += 1         
                        update_to_json_with_preprocessing( tf, symbol, date,day,"ts",str)  
                
                        await send_signal(update,context,Signal, Time_range,sgnl_type,str,serial_number)
                        pending_orders[serial_number]['pair'] = symbol
                        pending_orders[serial_number]['direction'] = 'up'
                        pending_orders[serial_number]['mn'] = m
                        pending_orders[serial_number]['st'] = st_time
                        pending_orders[serial_number]['et'] = en_time
                        pending_orders[serial_number]['serial_number'] = serial_number
                        pending_orders[serial_number]['Strategy']  = str
                        
                        




                    if '1' in strategy:
                        wg = strategy1('up')
                        if wg >= 2:
                            sgnl_type = ''
                            if wg == 2:
                                sgnl_type = 'Signal'
                            elif wg == 3:
                                sgnl_type = 'Strong Singal'
                            elif wg == 4:
                                sgnl_type = 'Super Strong Singal'
                            await to_do_up(sgnl_type,1)
                    if '2' in strategy:
                        a =  strategy2('up')
                        if a:
                            sgnl_type = 'Strong Singal'
                            await to_do_up(sgnl_type,2)

                    if '3' in strategy:
                        a = strategy3('up')
                        if a:
                            sgnl_type = 'Strong Singal'
                            await to_do_up(sgnl_type,3)

                    
                    
                   
                        
                except Exception as e:
                    print("error in St function",e) 

            async def trade_down_strategy() :
                global time_start
                dir = None
                m1 = ''
                if tf == 60:
                    m1 = '1 min'
                elif tf == 120:
                    m1 = '2 min' 
                elif tf == 300:
                    m1 = '5 min'
                elif tf == 900:
                    m1 = '15 min'
                elif tf == 1800:
                    m1 = '30 min'
                elif tf == 3600:
                    m1 = '1 Hour'
                elif tf == 7200:
                    m1 = '2 Hour'
                elif tf == 10800:
                    m1 = '3 Hour'
                elif tf == 14400:
                    m1 = '4 Hour'
                elif tf == 86400:
                    m1 = '1 Day'
                m = 0
                
                if tf == 60:
                    m = 1
                elif tf == 120:
                    m = 2 
                elif tf == 300:
                    m = 5
                elif tf == 900:
                    m = 15
                elif tf == 1800:
                    m = 30
                elif tf == 3600:
                    m = 60
                elif tf == 7200:
                    m = 120
                elif tf == 10800:
                    m = 180
                elif tf == 14400:
                    m = 240
                elif tf == 86400:
                    m = 1440
                
                try: 
                    
                    async def to_do_down(sgnl_type,str):
                        serial_number = generate_serial_code()
                        initialize_pending_orders(serial_number)
                        if wg == 2:
                            sgnl_type = 'Signal'
                        elif wg == 3:
                            sgnl_type = 'Strong Singal'
                        elif wg == 4:
                            sgnl_type = 'Super Strong Singal'
                        ist_zone = pytz.timezone('Asia/Kolkata')
                        now_utc = datetime.now(pytz.utc)
                        now = now_utc.astimezone(ist_zone)
                        rounded_time = (now + timedelta(minutes=t)).replace(second=0, microsecond=0)
                        end_time = rounded_time + timedelta(minutes=m)
                        st_time = rounded_time.strftime('%H:%M')
                        en_time = end_time.strftime('%H:%M')
                        serial_no =  serial_number
                        Signal = f"{symbol} : {m1}  Down"
                        Time_range = f"Time : {st_time} to {en_time}"
                        user_data[user_id]['Total_signal'] += 1     
                        update_to_json_with_preprocessing(tf, symbol, date,day,"ts",str)   
                
                        await send_signal(update,context,Signal, Time_range,sgnl_type,str,serial_no)
                        pending_orders[serial_number]['pair'] = symbol
                        pending_orders[serial_number]['direction'] = 'down'
                        pending_orders[serial_number]['mn'] = m
                        pending_orders[serial_number]['st'] = st_time
                        pending_orders[serial_number]['et'] = en_time
                        pending_orders[serial_number]['serial_number'] = serial_number
                        pending_orders[serial_number]['Strategy']  = str
                        
                        
                    if '1' in strategy:
                        wg = strategy1('down')
                        if wg >= 2:
                            sgnl_type = ''
                            if wg == 2:
                                sgnl_type = 'Signal'
                            elif wg == 3:
                                sgnl_type = 'Strong Singal'
                            elif wg == 4:
                                sgnl_type = 'Super Strong Singal'
                            await to_do_down(sgnl_type,1)

                    if '2' in strategy:    
                        a =  strategy2('down')
                        if a == True:
                            sgnl_type = 'Strong Singal'
                            await to_do_down(sgnl_type,2)
                    if '3' in strategy:
                        a = strategy3('down')
                        if a:
                            sgnl_type = 'Strong Singal'
                            await to_do_down(sgnl_type,3)
                except Exception as e:
                    print("error in St function",e)
            await  trade_down_strategy()
            await trade_up_strategy()
            
            
    
            
            print(f"No signals Generate in {symbol}")
        except Exception as e:
            print(f"Error in Generating_signals: {e}")


#Fetching the exchange rates
def update_exchange_rate(symbol):
    rate = Api.get_candles(symbol, 60, 2, time.time())
    rate.reverse()
    if len(rate) > 0:
           ps_rate = float(rate[1].get('close', 0))
    return ps_rate


#Making group flag to false
group = False


def load_timeframes():
    if os.path.exists(TF_FILE):
        with open(TF_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_timeframes(timeframes):
    with open(TF_FILE, 'w') as file:
        json.dump(timeframes, file, indent=4)

async def send_signal(update: Update,context: ContextTypes.DEFAULT_TYPE, Signal, Time_range,sgnl_type,str,srl_no) -> None:
        ld = load_mtg()
        ld = ld['status']
        if ld == "ON" or ld == 2:
            # message = f"Strong Signal: Strategy{str}\n\nSignal ID:"
            message = f"{sgnl_type}: Strategy {str}\n\nSignal ID: #{srl_no}\n\n{Signal}\n\n{Time_range}\n\n"
        else:
            message = f"{sgnl_type}:\n\n{Signal}\n\n{Time_range}"
        if  update.message.chat.type in ['group', 'supergroup'] or group == True:
            await update.message.reply_text(message)
        # Send the message to all users with is_running set to True
        else:
            for user_id in user_data:
                if user_data[user_id].get('is_running', False):
                    try:
                        await context.bot.send_message(user_id, message)
                    except Exception as e:
                        # Handle potential errors
                        print(f"Error sending message to user ID {user_id}: {e}")

async def send_result(update: Update, context: ContextTypes.DEFAULT_TYPE, results) -> None:
    # Check if results is a single string or a list
    if isinstance(results, str):
        results = [results]  # Ensure results is a list for consistent handling

    # Process and format each result
    for result in results:
        try:
            # Strip unnecessary characters like brackets or escaped characters
            if result.startswith("[") and result.endswith("]"):
                result = eval(result)[0]  # Convert string representation of list back to string
            
            # Send the formatted result
            if update.message.chat.type in ['group', 'supergroup'] or group:
                await update.message.reply_text(result)
            else:
                for user_id in user_data:
                    if user_data[user_id].get('is_running', False):
                        await context.bot.send_message(user_id, result)
        except Exception as e:
            print(f"Error formatting or sending message: {e}")




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global is_running
    global stop_requested
    global group
    user_id = update.effective_user.id
    if update.message.chat.type in ['group', 'supergroup']:
        bot_username = context.bot.username
        group = True
        
        initialize_user(user_id)
        if bot_username not in update.message.text:
            return  # Ignore messages not mentioning the bot
        context.user_data.get('waiting_for_pairs') == True
        await update.message.reply_text("Send the currency pairs list in this format: Eg: USDJPY,EURUSD.")
    first_name = update.effective_user.first_name

    username = update.effective_user.username
    
    print(f"{first_name} started the bot with this username {username}.")

    stop_requested = False
    await update.message.reply_text('Hi')
    await update.message.reply_text("Please send the key.")
    context.user_data['waiting_for_key'] = True
    context.user_data['timeout_task'] = context.application.create_task(wait_for_key(update, context))


# Function to wait for the key entry
async def wait_for_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    timeout = datetime.now() + timedelta(seconds=20)  # Set a 20-second timeout

    while datetime.now() < timeout:
        if 'user_key' in context.user_data:
            # Key was entered, exit the loop
            return
        await asyncio.sleep(1)  # Check every second

    if context.user_data.get('waiting_for_key'):
        context.user_data.clear()

# Function to handle the user's key


VALID_PAIRS = [
    # Major Pairs
    'EURUSD', 'EURGBP', 'GBPJPY', 'EURJPY', 'GBPUSD', 'USDJPY', 'AUDCAD', 'NZDUSD', 'USDRUB', 'AMAZON', 
    'APPLE', 'BAIDU', 'CISCO', 'FACEBOOK', 'GOOGLE', 'INTEL', 'MSFT', 'YAHOO', 'AIG', 'CITI', 'COKE', 
    'GE', 'GM', 'GS', 'JPM', 'MCDON', 'MORSTAN', 'NIKE', 'USDCHF', 'XAUUSD', 'XAGUSD', 'EURUSD-OTC', 
    'EURGBP-OTC', 'USDCHF-OTC', 'EURJPY-OTC', 'NZDUSD-OTC', 'GBPUSD-OTC', 'GBPJPY-OTC', 'USDJPY-OTC', 
    'AUDCAD-OTC', 'ALIBABA', 'YANDEX', 'AUDUSD', 'USDCAD', 'AUDJPY', 'GBPCAD', 'GBPCHF', 'GBPAUD', 'EURCAD', 
    'CHFJPY', 'CADCHF', 'EURAUD', 'TWITTER', 'FERRARI', 'TESLA', 'USDNOK', 'EURNZD', 'USDSEK', 'USDTRY', 
    'MMM:US', 'ABT:US', 'ABBV:US', 'ACN:US', 'ATVI:US', 'ADBE:US', 'AAP:US', 'AA:US', 'AGN:US', 'MO:US', 
    'AMGN:US', 'T:US', 'ADSK:US', 'BAC:US', 'BBY:US', 'BA:US', 'BMY:US', 'CAT:US', 'CTL:US', 'CVX:US', 
    'CTAS:US', 'CTXS:US', 'CL:US', 'CMCSA:US', 'CXO:US', 'COP:US', 'ED:US', 'COST:US', 'CVS:US', 'DHI:US', 
    'DHR:US', 'DRI:US', 'DVA:US', 'DAL:US', 'DVN:US', 'DO:US', 'DLR:US', 'DFS:US', 'DISCA:US', 'DOV:US', 
    'DTE:US', 'DNB:US', 'ETFC:US', 'EMN:US', 'EBAY:US', 'ECL:US', 'EIX:US', 'EMR:US', 'ETR:US', 'EQT:US', 
    'EFX:US', 'EQR:US', 'ESS:US', 'EXPD:US', 'EXR:US', 'XOM:US', 'FFIV:US', 'FAST:US', 'FRT:US', 'FDX:US', 
    'FIS:US', 'FITB:US', 'FSLR:US', 'FE:US', 'FISV:US', 'FLS:US', 'FMC:US', 'FBHS:US', 'FCX:US', 'FTR:US', 
    'GILD:US', 'HAS:US', 'HON:US', 'IBM:US', 'KHC:US', 'LMT:US', 'MA:US', 'MDT:US', 'MU:US', 'NFLX:US', 
    'NEE:US', 'NVDA:US', 'PYPL:US', 'PFE:US', 'PM:US', 'PG:US', 'QCOM:US', 'DGX:US', 'RTN:US', 'CRM:US', 
    'SLB:US', 'SBUX:US', 'SYK:US', 'DIS:US', 'TWX:US', 'VZ:US', 'V:US', 'WMT:US', 'WBA:US', 'WFC:US', 'SNAP', 
    'DUBAI', 'TA25', 'AMD', 'ALGN', 'ANSS', 'DRE', 'IDXX', 'RMD', 'SU', 'TFX', 'TMUS', 'QQQ', 'SPY', 'BTCUSD', 
    'XRPUSD', 'ETHUSD', 'LTCUSD', 'DSHUSD', 'BCHUSD', 'OMGUSD', 'ZECUSD', 'ETCUSD', 'BTCUSD-L', 'ETHUSD-L', 
    'LTCUSD-L', 'BCHUSD-L', 'BTGUSD', 'QTMUSD', 'XLMUSD', 'TRXUSD', 'EOSUSD', 'USDINR', 'USDPLN', 'USDBRL', 
    'USDZAR', 'DBX', 'SPOT', 'USDSGD', 'USDHKD', 'LLOYL-CHIX', 'VODL-CHIX', 'BARCL-CHIX', 'TSCOL-CHIX', 
    'BPL-CHIX', 'HSBAL-CHIX', 'RBSL-CHIX', 'BLTL-CHIX', 'MRWL-CHIX', 'STANL-CHIX', 'RRL-CHIX', 'MKSL-CHIX', 
    'BATSL-CHIX', 'ULVRL-CHIX', 'EZJL-CHIX', 'ADSD-CHIX', 'ALVD-CHIX', 'BAYND-CHIX', 'BMWD-CHIX', 'CBKD-CHIX', 
    'COND-CHIX', 'DAID-CHIX', 'DBKD-CHIX', 'DPWD-CHIX', 'DTED-CHIX', 'EOAND-CHIX', 'MRKD-CHIX', 'SIED-CHIX', 
    'TKAD-CHIX', 'VOW3D-CHIX', 'PIRCM-CHIX', 'PSTM-CHIX', 'TITM-CHIX', 'CSGNZ-CHIX', 'NESNZ-CHIX', 'ROGZ-CHIX', 
    'UBSGZ-CHIX', 'SANE-CHIX', 'BBVAE-CHIX', 'TEFE-CHIX', 'AIRP-CHIX', 'HEIOA-CHIX', 'ORP-CHIX', 'AUDCHF', 
    'AUDNZD', 'CADJPY', 'EURCHF', 'GBPNZD', 'NZDCAD', 'NZDJPY', 'EURNOK', 'CHFSGD', 'EURSGD', 'USDMXN', 'JUVEM', 
    'ASRM', 'MANU', 'UKOUSD', 'XPTUSD', 'USOUSD', 'W1', 'AUDDKK', 'AUDMXN', 'AUDNOK', 'AUDSEK', 'AUDSGD', 'AUDTRY', 
    'CADMXN', 'CADNOK', 'CADPLN', 'CADTRY', 'CHFDKK', 'CHFNOK', 'CHFSEK', 'CHFTRY', 'DKKPLN', 'DKKSGD', 'EURDKK', 
    'EURMXN', 'EURTRY', 'EURZAR', 'GBPILS', 'GBPMXN', 'GBPNOK', 'GBPPLN', 'GBPSEK', 'GBPSGD', 'GBPTRY', 'NOKDKK', 
    'NOKJPY', 'NOKSEK', 'NZDDKK', 'NZDMXN', 'NZDNOK', 'NZDSEK', 'NZDSGD', 'NZDTRY', 'NZDZAR', 'PLNSEK', 'SEKDKK', 
    'SEKJPY', 'SGDJPY', 'USDDKK', 'NZDCHF', 'GBPHUF', 'USDCZK', 'USDHUF', 'CADSGD', 'EURCZK', 'EURHUF', 'USDTHB', 
    'IOTUSD-L'
]



# Function to validate currency pairs format
def is_valid_pair(pair):
    return pair in VALID_PAIRS

# Handle the messages and store the pairs
# Global variable to control the loop task
loop_task_running = False
signal_task = None


async def check_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['step'] = None
    context.user_data['waiting_for_timeframe'] = False
    context.user_data['gap'] = False
    context.user_data['waiting_for_Strategy'] = False
    context.user_data['waiting_for_MTG'] = False
    context.user_data['waiting_for_pair'] = False
    context.user_data['Datasource'] = False
    await update.message.reply_text("Please provide the Risk Per Trade Amount along with the Brokerage Amount in the following format: Risk Amount,Brokerage Amount.  e.g., 1000,20")
    context.user_data['brokerage'] = True
    context.user_data['why'] = None

    



async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global user_key
    global message
    global loop_task_running
    global signal_task
    global brokerage_lock
    timeframe = []
    user_id = update.effective_user.id
    message = update.message.text.split(',')
    # Ensure user is initialized
   

    if context.user_data.get('waiting_for_key'):
        user_key = update.message.text
        admin_key = "Pranav125"
        Cm_key = "user125"
       
        if user_key in [admin_key]:
            initialize_user(user_id)
            context.user_data.pop('waiting_for_key', None)
            print(f'Welcome Pranav sir to Smart AI Bot admin panel')
            await update.message.reply_text(f"Welcome Pranav sir to Smart AI Bot admin panel")
            msg = """
1) /check_reports--> Check Reports
2) /set_tf-->  Set Timeframe
3) /set_pairs--> Set Currency Pairs
4) /set_strategy--> Set Strategy
5) /dis_str --> Display strategy
6) /chng_datasrc --> Change Datasource
    """

            await update.message.reply_text(msg)
            

            
            # await update.message.reply_text("Send the currency pairs list in this format: Eg: USDJPY,EURUSD.")
            # context.user_data['waiting_for_pair'] = True
        elif user_key == Cm_key:
            # Remove waiting state and initialize the user
            context.user_data.pop('waiting_for_key', None)
            initialize_user(user_id)
            initialize_p_L(user_id)
            
            # Load the pairs
            pairs = load_pairs()  # This will return the list of pairs
            
            await update.message.reply_text("Welcome User to the Smart AI Bot")
            await start_processing(update, context)           
            user_data[user_id]['is_running'] = True
            

        else:
            await update.message.reply_text("You are not verified by admin. Please message this ID: @Arpit_tomer263")
        
        # Handle timeout tasks
        if 'timeout_task' in context.user_data:
            context.user_data['timeout_task'].cancel()

        
        
   
    
    elif context.user_data.get('brokerage'):
       



        try:
            msg = update.message.text.strip()
            user_id = update.effective_user.id
            current_position = ''
            
            if context.user_data.get('why') is None:
                try:
                    amount = float(msg.split(',')[0].strip())
                    brokerage = float(msg.split(',')[1].strip())
                    brokerage = 100 - brokerage
                    if amount <= 0 or brokerage < 0:
                        await update.message.reply_text("Both amount and brokerage should be positive values. Try again.")
                        return

                    # Update context variables
                    context.user_data['amt'] = amount
                    context.user_data['brk'] = brokerage
                    context.user_data['why'] = True  # Mark as processed
                    context.user_data['pair_recive'] = None
                    await update.message.reply_text("Risk Per Trade & Brokerage Amount Set")
                    await update.message.reply_text("Enter the currency pairs to generate the report. Use the format: USDJPY, EURUSD.")
                except ValueError:
                    await update.message.reply_text("Please ensure the input is in the format 'Amount,Brokerage'.")
            else:
                msg = update.message.text.strip()

                # Reverse one step logic (for each stage)
                if msg == '0':
                    if current_position == 'to_get_pair':
                        context.user_data['why'] = None
                        context.user_data['pair_recive'] = True

                        await update.message.reply_text("Reversed one step. Please provide the amount and brokerage in the format 'Amount,Brokerage'.")
                        return
                    elif current_position == 'to_get_timeframe':
                        context.user_data['pair_recive'] = None
                        context.user_data['timeframe_recive'] = False

                    elif current_position == 'to_get_strategy':
                        context.user_data['strategy_recive'] = False
                        context.user_data['pair_recive'] = True
                        context.user_data['timeframe_recive'] = False
                    elif current_position == 'to_get_date':
                        context.user_data['strategy_recive'] = False
                        context.user_data['timeframe_recive'] = True

                # Handle pair receipt
                if context.user_data.get('pair_recive') is None:
                    current_position = 'to_get_pair'
                    if msg == '0':
                        await update.message.reply_text("Reverse One step.")
                        context.user_data['pair_recive'] = None
                        context.user_data['why'] = None
                        context.user_data['timeframe_recive'] = None
                        context.user_data['strategy_recive'] = None
                        return

                    report = [pair.strip().upper() for pair in msg.split(',')]
                    if all(pair in VALID_PAIRS for pair in report):
                        context.user_data['pair_recive'] = True
                        context.user_data['timeframe_recive'] = False
                        context.user_data['pairs'] = report
                        await update.message.reply_text(f"Received the following pairs: {', '.join(report)}. Proceeding to generate the report.")
                        await update.message.reply_text("Specify the timeframe(s) for the report in seconds. Example: 60, 120, 300.")
                    else:
                        await update.message.reply_text("Invalid pairs. Please provide valid pairs separated by commas.")
                    return

                # Handle timeframe receipt
                if context.user_data.get('pair_recive') and not context.user_data.get('timeframe_recive'):
                    current_position = 'to_get_timeframe'
                    if msg == '0':
                        await update.message.reply_text("Reverse One step.")
                        context.user_data['timeframe_recive'] = None
                        context.user_data['pair_recive'] = None
                        return
                    try:
                        timeframes = [int(t.strip()) for t in msg.split(',')]
                        if all(t > 0 for t in timeframes):  # Ensure all are positive integers
                            context.user_data['timeframe_recive'] = True
                            context.user_data['pair_recive'] = False
                            context.user_data['strategy_recive'] = False

                            context.user_data['timeframe'] = timeframes
                            await update.message.reply_text(f"Received the timeframe: {', '.join(map(str, timeframes))}  seconds. Proceeding with the report generation.")
                            await update.message.reply_text("Enter the strategy number(s) to be used. Example: 1, 2, 3.")
                        else:
                            await update.message.reply_text("All timeframes must be positive integers. Please try again.")
                    except ValueError:
                        await update.message.reply_text("Please provide timeframes as numbers separated by commas.")
                    return

                # Handle strategy receipt
                if context.user_data.get('timeframe_recive') and not context.user_data.get('strategy_recive'):
                    current_position = 'to_get_strategy'
                    if msg == '0':
                        await update.message.reply_text("Reverse One step.")
                        context.user_data['strategy_recive'] = None
                        context.user_data['timeframe_recive'] = None
                        return
                    if msg != '0':
                        try:
                            strategies = [int(s.strip()) for s in msg.split(',')]
                            VALID_STRATEGIES = [1, 2, 3]
                            if all(s in VALID_STRATEGIES for s in strategies):
                                context.user_data['timeframe_recive'] = False
                                context.user_data['strategy_recive'] = True
                                context.user_data['strategy'] = strategies
                                await update.message.reply_text(f"Strategies Confirmed: {', '.join(map(str, strategies))}.")
                                await update.message.reply_text("Specify the date range using one of the following formats:")
                                await update.message.reply_text("Enter a date range (e.g., 24/12/2024 to 26/12/2024).")
                                await update.message.reply_text("2. The word 'ALL'")
                                await update.message.reply_text("3. A range of dates (e.g., 24/12/2024 to 26/12/2024)")
                            else:
                                await update.message.reply_text("Invalid strategy number(s). Please provide valid strategy numbers (1, 2, 3).")
                        except ValueError:
                            await update.message.reply_text("Please provide strategies as numbers separated by commas.")
                        return

                # Handle date receipt
                if context.user_data.get('strategy_recive'):
                    current_position = 'to_get_date'
                    if msg == '0':
                        await update.message.reply_text("Reversed One step.")
                        context.user_data['strategy_recive'] = False
                        context.user_data['timeframe_recive'] = True
                    
                    if msg != '0':
                        date_input = update.message.text
                        if date_input.upper() == "ALL":
                            context.user_data['date'] = "ALL"
                        elif "to" in date_input.lower():
                            try:
                                start_date, end_date = map(str.strip, date_input.split('to'))
                                context.user_data['date'] = f"{start_date} to {end_date}"
                            except ValueError:
                                await update.message.reply_text("Invalid date range format. Please use: '24/12/2024 to 26/12/2024'.")
                                return
                        else:
                            context.user_data['date'] = date_input

                        # Once the date is set, generate the report
                        pairs = context.user_data.get('pairs')
                        timeframes = context.user_data.get('timeframe')
                        strategies = context.user_data.get('strategy')
                        date = context.user_data.get('date')
                        amount = context.user_data.get('amt')
                        brokerage = context.user_data.get('brk')

                        # Fetch the report
                        result = await get_report(pairs, timeframes, date, strategies, amount, brokerage)
                        if isinstance(result, list):  # Convert list items to strings before joining
                            result = ', '.join(map(str, result))
                        await update.message.reply_text(f"{result}")

                        # Clear all temporary states
                        context.user_data['brokerage'] = False
                        context.user_data['why'] = True  # Mark as processed
                        context.user_data['pair_recive'] = False
        except Exception as e:
            print("Error occur in report Generation:",e)
                    




    



    elif context.user_data.get('step') == 'risk':
        
        try:
            # Get user input (risk)
            risk_input = update.message.text.strip()
            pair = context.user_data.get('current_pair')
            PnL[user_id]['take_risk'][pair] = float(risk_input)  # Store risk per pair

            # Now move to the brokerage question
            context.user_data['step'] = 'brokerage'
            await update.message.reply_text(f"Brokerage on {pair}. Enter only number:")
        except Exception as e:
            print("Error occur in Risk:",e)

    elif context.user_data.get('step') == 'brokerage':
        try:
            # Get user input (brokerage)
            brokerage_input = update.message.text.strip()
            pair = context.user_data.get('current_pair')
            if brokerage_input:
                try:
                    brokerage_input = int(brokerage_input)
                    brokerage_input = 100 - brokerage_input
                    print(brokerage_input)
                except Exception as e:
                    await update.message.reply_text("Enter only number.")
            PnL[user_id]['commision'][pair] = float(brokerage_input)  # Store brokerage per pair

            # Ask for next pair
            context.user_data['step'] = 'wait'  # Reset step
            await update.message.reply_text(f"{pair} processed.")

            # Move on to the next pair
            await process_next_pair(update, context)
        except Exception as e:
            print("Error in Brokerage",e)
    
       
    
                




    elif context.user_data.get('waiting_for_timeframe'):
        
        try:
            message = update.message.text.strip()
            # Process the input timeframes (e.g., "H1,H2,H3")
            intervals = {
                "M1": 60,    
                "M2": 120,   
                "M5": 300,   
                "M15": 900,  
                "M30": 1800, 
                "H1": 3600,  
                "H2": 7200,  
                "H3": 10800, 
                "H4": 14400 ,
                'D':86400,
            }
            
            
            user_inputs = message.split(",")

            for item in user_inputs:
                item = item.strip().upper()  # Clean input and ensure uppercase
                if item in intervals:
                    timeframe.append(intervals[item])  # Add corresponding second
                else:
                    await update.message.reply_text(f"Invalid input: {item}. Please use: M1, M2, M5, etc.")
                    return
            save_timeframes(timeframe)
            
            if timeframe:
                timeframes_str = ",".join([key for key, value in intervals.items() if value in timeframe])

                await update.message.reply_text(f"The time frame has been successfully set to: {timeframes_str}")
                context.user_data['waiting_for_timeframe'] = False  # Reset waiting flag after receiving valid input
                await update.message.reply_text("Please specify the time gap for your trades:\n1. 1 minute gap\n2. 2 minute gap")
                context.user_data['gap'] = True
                # Now you can proceed with the next actions (e.g., asking for pairs or other tasks)
            else:
                await update.message.reply_text("No valid timeframes entered. Please try again.")
        except Exception as e:
            print("Error in Entering TimeFrame:",e)

    elif context.user_data.get('gap'):
        
        try:
            gap = update.message.text
            if gap == '1' or gap == '2':
                await update.message.reply_text(f'The time gap has been set to: {gap}')
                save_gap(gap)
                context.user_data['gap'] = False
            else:
                await update.message.reply_text("Gap is not set yet.")
                save_gap('1')
                context.user_data['gap'] = False
        except Exception as e:
            print("Error in Gap entering",e)

    elif context.user_data.get('waiting_for_Strategy'):
        
        try:
            strategy = update.message.text.split(',')
            if all(s in ['1', '2', '3'] for s in strategy):  # Ensure all strategies are valid
                save_strategy(strategy)  # Save the strategy list
                await update.message.reply_text(f"Strategy is {', '.join(strategy)}")  # Inform the user
                context.user_data['waiting_for_Strategy'] = False

            else:
                await update.message.reply_text(f"Strategy is not set please enter vaild value i.e 1,2")
        except Exception as e:
            print("ERROR in giving strategy:",e)
    elif context.user_data.get('waiting_for_MTG'):
        
        try:
            mtgs = int(update.message.text.strip().upper())
            
            if (mtgs in [1,2]):
                if mtgs == 1 or mtgs == '2':
                    Upload_mtg('OFF')
                    await update.message.reply_text(f"Strategy Display is Set to OFF")
                elif mtgs == '2' or mtgs == 2:
                    Upload_mtg('ON')
                    await update.message.reply_text(f"Strategy Display is Set to ON")
                context.user_data.pop('waiting_for_MTG', False)
            else:
                await update.message.reply_text("Invalid input. Please provide either 'ON' or 'OFF'.")
        except Exception as e:
            print("Error in MTG type",e)

    elif (context.user_data.get('waiting_for_pair')) or (update.message.chat.type in ['group','supergroup']):        
        
        try:
            # Process new pairs
            pairs = update.message.text.split(',')
            pairs = [pair.strip().upper() for pair in pairs]
            invalid_pairs = [pair for pair in pairs if not is_valid_pair(pair)]
            if invalid_pairs:
                await update.message.reply_text(
                    f"Invalid currency pair(s) detected: {', '.join(invalid_pairs)}. "
                    "Please separate pairs by a comma (,) and provide them in this format: Eg: USDJPY, EURUSD."
                )
                return
            save_paris(pairs)
            await update.message.reply_text(f"The pair has been updated to: {pairs}")
            context.user_data['waiting_for_pair'] = False
        except Exception as e:
            print("Error in the Wating for pair",e)

    elif context.user_data.get('Datasource'):
        
        try:
            optn = update.message.text
            if optn == '1' or optn == '2':
                optn = int(update.message.text)
                upload_dataset(optn)
                await update.message.reply_text("Datasource is changed.")
                context.user_data['Datasource'] = False

            else:
                await update.message.reply_text("Please choose 1 or 2")
        except Exception as e:
            print("Error in Changing datasource:",e)





async def change_data_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['brokerage'] = False
    context.user_data['why'] = True
    context.user_data['pair_recive'] = False
    context.user_data['timeframe_recive'] = None
    context.user_data['strategy_recive'] = None
    context.user_data['waiting_for_timeframe'] = False
    context.user_data['gap'] = False
    context.user_data['waiting_for_Strategy'] = False
    context.user_data['waiting_for_MTG'] = False
    context.user_data['waiting_for_pair'] = False
    datasrc = load_dataset()
    if datasrc == 1 or datasrc == '1':
        await update.message.reply_text("The current data source is: Trading View")
        await update.message.reply_text("To change the data source, please select one of the following options:")
        await update.message.reply_text("1) TradingView\n\n2) Iqoption")
        context.user_data['Datasource'] = True
    elif datasrc == 2 or datasrc == '2':
        await update.message.reply_text("The current data source is: Iqoption")
        await update.message.reply_text("To change the data source, please select one of the following options:")
        await update.message.reply_text("1) TradingView\n\n2) Iqoption")
        context.user_data['Datasource'] = True
 
    else:
        await update.message.reply_text("Currently Data source is Not set.")
        await update.message.reply_text("1) TradingView\n\n2) Iqoption")
        context.user_data['Datasource'] = True



async def dis_str(update: Update, context: ContextTypes.DEFAULT_TYPE):
    load = load_mtg()
    if load == 'ON':
        await update.message.reply_text("The strategy is displayed alongside the signals.To adjust the display, please select:")
        await update.message.reply_text(f'1) OFF\n2) ON')
        context.user_data['waiting_for_MTG'] = True
    else:
        await update.message.reply_text(f"The strategy is showcased alongside the signals!")
        await update.message.reply_text(f'If you want to show it please provide me\n1) OFF\n2) ON')
        context.user_data['waiting_for_MTG'] = True



async def start_processing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    initialize_p_L(user_id)  # Initialize PnL data for the user

    # Start with the pairs list
    context.user_data['pairs'] = load_pairs()
    context.user_data['step'] = 'risk'

    await process_next_pair(update, context)  # Start the process with the first pair

def save_strategy(strs):
    File = 'strategy.json'

    with open(File,'w') as file:
        json.dump(strs,file,indent=4)

def load_strategy():
    # Check if the file exists
    if os.path.exists('strategy.json'):
        try:
            # Try to open and load the JSON data
            with open('strategy.json', 'r') as file:
                data = json.load(file)
                if not data:  # If the file is empty, return an empty dictionary
                    return {}
                return data
        except json.JSONDecodeError:
            return {}
    return {}  # Return empty dictionary if file doesn't exist

async def wait_for_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Helper to wait for the user input"""
    response = await update.message.reply_text("Please enter the value:")
    user_input =  update.message.text
    return user_input


def save_paris(pairs):
    File = 'pairs.json'

    with open(File,'w') as file:
        json.dump(pairs, file, indent=4)

def save_gap(gap):
    File = 'gap.json'
    if not isinstance(gap, list):
        gap = [gap]  # Ensure it's a list
    with open(File, 'w') as file:
        json.dump(gap, file, indent=4)


def load_gap():
    file_name = 'gap.json'

    try:
        if os.path.getsize(file_name) == 0:
            print(f"{file_name} is empty. Returning None.")
            return None  # Return None for empty file

        with open(file_name, 'r') as file:
            data = json.load(file)
            
            # If the data is a string or numeric value, return it directly
            if isinstance(data, (int, float, str)):
                return data
            elif isinstance(data, list) and len(data) == 1:
                # If it's a single value stored in a list, return the value
                return data[0]
            else:
                print(f"Invalid data format in {file_name}. Returning None.")
                return None
    except FileNotFoundError:
        print(f"{file_name} not found. Returning None.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON data in {file_name}. Returning None.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    

async def ask_risk_brokerage(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: str, pair: str):
    # Ask for risk
    await update.message.reply_text(f"Risk per trade on {pair}. Enter only the amount:")
    context.user_data['current_pair'] = pair  # Store the current pair
    context.user_data['step'] = 'risk'  # Set the current step to 'risk'

# Helper function to start processing pairs one by one
async def process_next_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    pairs = context.user_data.get('pairs', [])

    if pairs:
        pair = pairs.pop(0)  # Get the next pair in the list
        context.user_data['pairs'] = pairs  # Update the remaining pairs list
        await ask_risk_brokerage(update, context, user_id, pair)
    else:
        await update.message.reply_text("All pairs processed. Starting signal generation...")
        # Trigger signal generation logic
        
        await start_signal_generation(update, context)

def load_pairs():
    file_name = 'pairs.json'

    try:
        # Check if the file is empty
        if os.path.getsize(file_name) == 0:
            print(f"{file_name} is empty. Returning an empty list.")
            return []

        # Read the file and load JSON content
        with open(file_name, 'r') as file:
            data = json.load(file)
            if isinstance(data, list):
                return data
            else:
                print(f"Invalid data format in {file_name}. Returning an empty list.")
                return []

    except FileNotFoundError:
        print(f"{file_name} not found. Returning an empty list.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON data in {file_name}. Returning an empty list.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    
async def set_pair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['brokerage'] = False
    context.user_data['why'] = True
    context.user_data['pair_recive'] = False
    context.user_data['timeframe_recive'] = None
    context.user_data['strategy_recive'] = None
    context.user_data['waiting_for_timeframe'] = False
    context.user_data['gap'] = False
    context.user_data['waiting_for_Strategy'] = False
    context.user_data['waiting_for_MTG'] = False
    context.user_data['waiting_for_pair'] = False
    context.user_data['Datasource'] = False
    crt_pair = load_pairs()

    if crt_pair:
        await update.message.reply_text(f"Currently selected pairs:{crt_pair}.To change the pairs, please provide the desired pairs.")
        await update.message.reply_text("Use the format: USDJPY, EURUSD.")
    
    else:
        await update.message.reply_text("Currently Time frame is not set.Please Give me the pairs.")
    context.user_data['waiting_for_pair'] = True


async def get_report(pair, timeframe, date, strategy, amt, brk):
    file = 'database.json'

    try:
        # Load data from the JSON file
        with open(file, "r") as f:
            data = json.load(f)

        # Initialize accumulators for aggregate data
        total_signals = 0
        total_wins = 0
        start_date = None
        end_date = None
        found_data = False  # Flag to check if data was found

        # Process the pair input to always be a list
        if isinstance(pair, str):
            pair = [pair]

        # Process the timeframe input to always be a list
        if isinstance(timeframe, int):
            timeframe = [timeframe]

        # Process the strategy input to always be a list
        if isinstance(strategy, str):
            strategy = [strategy]

        # Check if the date is a range
        if "to" in date:
            start_date_str, end_date_str = map(str.strip, date.split("to"))
            start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
            end_date = datetime.strptime(end_date_str, "%d/%m/%Y")

        if date.upper() == "ALL":
            # Aggregate data across all dates
            for entry in data:
                for entry_date, date_content in entry.items():
                    for day_data_key, day_data in date_content.items():
                        if (
                            day_data["Pair"] in pair
                            and day_data["Time Frame"] in timeframe
                            and day_data["Strategy"] in strategy
                        ):
                            total_signals += day_data["Total Signal"]
                            total_wins += day_data["Total Win"]
                            found_data = True

            # Calculate accuracy
            accuracy = f"{(total_wins / total_signals) * 100:.2f}%" if total_signals > 0 else "0%"
            Prf = (int(amt) / 100) * int(brk)
            Tlmny = (total_wins * Prf)
            lsmny = (total_signals - total_wins) * amt
            PL = Tlmny - lsmny
            return (
                f"     Report Summary:\n\n"
                f"     Date: All\n"
                f"     Pair: {', '.join(pair)}\n"
                f"     Strategy: {', '.join(map(str, strategy))}\n"
                f"     Time Frame: {', '.join(map(str, timeframe))}\n\n"
                f"     Statistics:\n\n"
                f"     Total Signal: {total_signals}\n"
                f"     Total Win: {total_wins}\n"
                f"     Accuracy: {accuracy}\n"
                f"     P&L:{PL} "
            )

        elif "to" in date:
            # Aggregate data for the date range
            for entry in data:
                for entry_date, date_content in entry.items():
                    entry_datetime = datetime.strptime(entry_date, "%d/%m/%Y")
                    if start_date <= entry_datetime <= end_date:
                        for day_data_key, day_data in date_content.items():
                            if (
                                day_data["Pair"] in pair
                                and day_data["Time Frame"] in timeframe
                                and day_data["Strategy"] in strategy
                            ):
                                total_signals += day_data["Total Signal"]
                                total_wins += day_data["Total Win"]
                                found_data = True

            accuracy = f"{(total_wins / total_signals) * 100:.2f}%" if total_signals > 0 else "0%"
            Prf = (int(amt) / 100) * int(brk)
            Tlmny = (total_wins * Prf)
            lsmny = (total_signals - total_wins) * amt
            PL = Tlmny - lsmny
            return (
                f"     Report Summary:\n\n"
                f"     Date: {start_date_str} to {end_date_str}\n"
                f"     Pair: {', '.join(pair)}\n"
                f"     Strategy: {', '.join(map(str, strategy))}\n"
                f"     Time Frame: {', '.join(map(str, timeframe))}\n\n"
                f"     Statistics:\n\n"
                f"     Total Signal: {total_signals}\n"
                f"     Total Win: {total_wins}\n"
                f"     Accuracy: {accuracy}\n"
                f"     P&L:{PL} "
            )

        else:
            # Aggregate data for a specific date across multiple pairs
            for entry in data:
                if date in entry:
                    day_content = entry[date]
                    for day_data_key, day_data in day_content.items():
                        if (
                            day_data["Pair"] in pair
                            and day_data["Time Frame"] in timeframe
                            and day_data["Strategy"] in strategy
                        ):
                            total_signals += day_data["Total Signal"]
                            total_wins += day_data["Total Win"]
                            found_data = True

            # If no data was found, provide a default report
            if not found_data:
                print("Data not found.")
                return (
                    f"     Report Summary:\n\n"
                    f"     Date: {date}\n"
                    f"     Pair: {', '.join(pair)}\n"
                    f"     Strategy: {', '.join(map(str, strategy))}\n"
                    f"     Time Frame: {', '.join(map(str, timeframe))} seconds\n\n"
                    f"     Statistics:\n\n"
                    f"     Total Signal: 0\n"
                    f"     Total Win: 0\n"
                    f"     Accuracy: 0%\n"
                    f"     P&L:0 "
                )

            # Calculate accuracy
            accuracy = f"{(total_wins / total_signals) * 100:.2f}%" if total_signals > 0 else "0%"
            Prf = (int(amt) / 100) * int(brk)
            Tlmny = (total_wins * Prf)
            lsmny = (total_signals - total_wins) * amt
            PL = Tlmny - lsmny
            return (
                f"     Report Summary:\n\n"
                f"     Date: {date}\n"
                f"     Pair: {', '.join(pair)}\n"
                f"     Strategy: {', '.join(map(str, strategy))}\n"
                f"     Time Frame: {', '.join(map(str, timeframe))} seconds\n\n"
                f"     Statistics:\n\n"
                f"     Total Signal: {total_signals}\n"
                f"     Total Win: {total_wins}\n"
                f"     Accuracy: {accuracy}\n"
                f"     P&L:{PL} "
            )

    except FileNotFoundError:
        return "Report:\n     Error: Database file not found."
    except json.JSONDecodeError:
        return "Report:\n     Error: Database file is empty or improperly formatted."
    except ValueError as e:
        return f"Report:\n     Error: Invalid date format provided. {str(e)}"



def load_mtg(file="mtg.json"):
    if not os.path.exists(file) or os.path.getsize(file) == 0:
        # File doesn't exist or is empty, return a default value
        return {"status": "OFF"}

    with open(file, 'r') as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError:
            # Handle cases where the JSON file is improperly formatted
            return {"status": "OFF"}
        
def load_dataset():
    File = 'data.json'

    with open(File,'r') as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError:
            return []
        
def upload_dataset(st):
    file = 'data.json'
    if st in [1,2]:
        with open(file, 'w') as f:
            json.dump(st, f, indent=4)
            return True
    else:
        return False

def get_mtg_status(file="mtg.json"):
    """
    Extracts the MTG status from the JSON file and returns 'ON' or 'OFF'.
    If the file is missing, empty, or invalid, it defaults to 'OFF'.
    """
    try:
        data = load_mtg(file)
        status = data.get("status", "OFF")
        return status if status in ["ON", "OFF"] else "OFF"
    except Exception as e:
        # Log the error if necessary
        print(f"Error reading MTG status: {e}")
        return "OFF"


def Upload_mtg(status):
    file = "mtg.json"
    if status not in ["ON", "OFF"]:
        raise ValueError("Invalid MTG status. Must be 'ON' or 'OFF'.")

    with open(file, 'w') as f:
        json.dump({"status": status}, f, indent=4)


async def ocmtg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['brokerage'] = False
    context.user_data['why'] = True
    context.user_data['pair_recive'] = False
    context.user_data['timeframe_recive'] = None
    context.user_data['strategy_recive'] = None
    context.user_data['waiting_for_timeframe'] = False
    context.user_data['gap'] = False
    context.user_data['waiting_for_Strategy'] = False
    context.user_data['waiting_for_pair'] = False
    context.user_data['Datasource'] = False
    mtg = load_mtg()
    status = mtg.get("status", "OFF")  # Default to OFF if not set
    await update.message.reply_text(f"Currently, MTG is set to {status}.")
    await update.message.reply_text("If you want to change it, please reply with either 'ON' or 'OFF'.")
    context.user_data['waiting_for_MTG'] = True





async def start_signal_generation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global loop_task_running
    global is_running
    global last_execution

    user_pairs = load_pairs()
    user_id = update.effective_user.id
    
    if loop_task_running:
        print("Signal generation task is already running.")
        return  # Avoid starting a duplicate task

    await update.message.reply_text(f"Analyzing the following currency pairs: {user_pairs}")

    async def loop_task():
        global is_running
        global last_execution
        is_running = True
        
        def load_timeframes():
            with open("tf.json", "r") as file:
                return json.load(file)

        # Load timeframes from tf.json
        timeframe = load_timeframes()
        if not timeframe:
            await update.message.reply_text("Time frame is not set by admin. Defaulting to M1.")
            timeframe = [60]

        # Initialize last_execution for all pair-timeframe combinations
        if not last_execution:
            last_execution.update({
                (pair, tf): datetime.now() - timedelta(seconds=tf) 
                for pair in user_pairs for tf in timeframe
            })

        while is_running:
            try:
                # Reload timeframes and pairs dynamically
                timeframe = load_timeframes()  
                pairs = load_pairs()  
                create_database_for_pairs_and_timeframes(pairs, timeframe)
                dtasource=  load_dataset()
                current_time = datetime.now()
                for pair in pairs:
                    for tf in timeframe:
                        try:
                            # Use .get() to avoid KeyError
                            last_exec_time = last_execution.get((pair, tf), None)
                            if last_exec_time is None:
                                # If the key does not exist, initialize it
                                last_execution[(pair, tf)] = current_time
                                print(f"Initializing execution time for {pair} with timeframe {tf} seconds.")
                                continue

                            # Calculate elapsed time and run analysis
                            elapsed = (current_time - last_exec_time).total_seconds()

                            if elapsed >= tf:  # Run analysis if the interval has elapsed
                                last_execution[(pair, tf)] = current_time  # Update the last execution time
                                if dtasource == 2:
                                    print("Running on Iqoption Datasource.")
                                    await analyze_currency_pair(pair, update, context, tf)
                                elif dtasource == 1:
                                    print("Running on TradingView Datasource.")
                                    await analyze_currency_pair_tradingView(pair,update,context,tf)
                        except Exception as e:
                            print(f"An error occurred while analyzing {pair} with timeframe {tf}: {e}")

                result = get_results(user_id,dtasource)
                if result:
                    await send_result(update, context, result)

                # Align the loop to start close to the next minute
                ist_zone = pytz.timezone('Asia/Kolkata')
                now_utc = datetime.now(pytz.utc)
                now = now_utc.astimezone(ist_zone)
                rounded_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
                time_to_wait = (rounded_time - now).total_seconds()
                
                await asyncio.sleep(time_to_wait)
                await asyncio.sleep(5)

            except Exception as e:
                print(f"An error occurred in the main loop: {e}")
                await asyncio.sleep(60)

    # Start the loop task in the background
    if not loop_task_running:
        loop_task_running = True
        asyncio.create_task(loop_task())




async def set_strategy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['brokerage'] = False
    context.user_data['why'] = True
    context.user_data['pair_recive'] = False
    context.user_data['timeframe_recive'] = None
    context.user_data['strategy_recive'] = None
    context.user_data['waiting_for_timeframe'] = False
    context.user_data['gap'] = False
    context.user_data['waiting_for_MTG'] = False
    context.user_data['waiting_for_pair'] = False
    context.user_data['Datasource'] = False
    strg = load_strategy()
    if strg:
        await update.message.reply_text(f"Currently strategy is {strg}")
        await update.message.reply_text("To update the strategy, please provide the strategy number") 
        await update.message.reply_text(f"Send Strategies to Generate Signals From below list:\n\n1--> Strategy 1\n2--> Strategy 2\n3 --> Strategy 3")
    else:
        await update.message.reply_text(f"Send Strategies to Generate Signals From below list:\n\n1--> Strategy 1\n2--> Strategy 2\n3 --> Strategy 3")
    context.user_data['waiting_for_Strategy'] = True

async def settf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['brokerage'] = False
    context.user_data['why'] = True
    context.user_data['pair_recive'] = False
    context.user_data['timeframe_recive'] = None
    context.user_data['strategy_recive'] = None
    context.user_data['gap'] = False
    context.user_data['waiting_for_Strategy'] = False
    context.user_data['waiting_for_MTG'] = False
    context.user_data['waiting_for_pair'] = False
    context.user_data['Datasource'] = False
    # Time frame intervals
    intervals = {
        "M1": 60,    
        "M2": 120,   
        "M5": 300,   
        "M15": 900,  
        "M30": 1800, 
        "H1": 3600,  
        "H2": 7200,  
        "H3": 10800, 
        "H4": 14400,
        'D': 86400,
    }
    
    async with lock_settf:
        # Load timeframes (in seconds)
        timeframe = load_timeframes() 
        
        # If no timeframe is set
        if not timeframe:
            await update.message.reply_text("Currently Time frame is not set. Please set it:")
            await update.message.reply_text(""" 
                M1 --> One minute\nM2 --> Two minutes\nM5 --> Five minutes\nM15 --> fifteen minutes\nM30 --> Thirty minutes\nH1 --> One hour\nH2 --> Two hours\nH3 --> Three hours\nH4 --> Four hours\nD --> One Day     
                """) 
            await update.message.reply_text("To proceed: Select the time frames for receiving signals by typing your choices separated by commas (e.g., H1, H2, H3).")
            context.user_data['waiting_for_timeframe'] = True
        else:
            # Convert seconds to corresponding time labels
            selected_timeframes = [key for key, value in intervals.items() if value in timeframe]
            
            # Format and send the message with selected time frames
            timeframes_str = ",".join(selected_timeframes)
            await update.message.reply_text(f"This Time Frame is already set: {timeframes_str}")
            
            await update.message.reply_text("Modify the time frame by entering the desired values.")
            await update.message.reply_text(""" 
                M1 --> One minute\nM2 --> Two minutes\nM5 --> Five minutes\nM15 --> fifteen minutes\nM30 --> Thirty minutes\nH1 --> One hour\nH2 --> Two hours\nH3 --> Three hours\nH4 --> Four hours\nD --> One Day     
                """) 
            await update.message.reply_text("How to Proceed:\nTo select the time frames for receiving signals, type your choices separated by commas.  Example: H1,H2,H3  ")
            context.user_data['waiting_for_timeframe'] = True



async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id  # Get the user ID
    first_name = update.effective_user.first_name  # Get the user's first name

    # Initialize user data if not already done
    initialize_user(user_id)

    # Calculate accuracy and other statistics for the user
    if user_data[user_id]['Total_signal'] != 0:
        Accuracy = (user_data[user_id]['total_win'] / user_data[user_id]['Total_signal']) * 100
    else:
        Accuracy = 0

    
    # **If the bot is in a group or supergroup, check if it was mentioned or if the command is /stop**
    if update.message.chat.type in ['group', 'supergroup']:  # Check if message is in a group/supergroup
        bot_username = context.bot.username
        # **Check if the bot is mentioned or if the command is /stop**
        if f"@{bot_username}" not in update.message.text and not update.message.text.startswith('/stop'):
            return  # **Ignore messages not mentioning the bot or not starting with /stop**

    # **Stop the bot for this user**
    user_data[user_id]['is_running'] = False  # **This flag stops the bot's operations for this user in all contexts**
    print(f"{first_name} stopped the bot.")

    

    # Construct the last message with user statistics
    last_msg = f"""Total Signals: {user_data[user_id]['Total_signal']}\n\n
Total Wins: {user_data[user_id]['total_win']}\n\n
Total Losses: {user_data[user_id]['Loss']}\n\n
P&L: {PnL[user_id]['amount']}
"""

    await update.message.reply_text(last_msg)

    # Optionally reset user data if you want to clear it after stopping
    user_data[user_id]['Total_signal'] = 0
    user_data[user_id]['total_win'] = 0
    user_data[user_id]['Loss'] = 0
    user_data[user_id]['Refund'] = 0
    user_data[user_id]['MTG'] = 0
    del PnL[user_id]

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = """
1) /check_reports--> Check Reports
2) /set_tf-->  Set Timeframe
3) /set_pairs--> Set Currency Pairs
4) /set_strategy--> Set Strategy
5) /dis_str --> Display strategy
6) /chng_datasrc --> Change Datasource
    """
    await update.message.reply_text(msg)
                
# Add this check in the message handler for when waiting for currency pairs
def main() -> None:

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("check_reports", check_report))
    application.add_handler(CommandHandler("mtg_option", ocmtg))
    application.add_handler(CommandHandler("set_tf", settf))
    application.add_handler(CommandHandler("Set_Pairs",set_pair))
    application.add_handler(CommandHandler("set_strategy",set_strategy))
    application.add_handler(CommandHandler("dis_str",dis_str))
    application.add_handler(CommandHandler("chng_datasrc",change_data_source))
    application.add_handler(CommandHandler("menu759",menu))

    # MessageHandler for key and currency pairs
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    application.run_polling()

if __name__ == '__main__':
    main()
