from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)

# Pluggable data source
def get_data_yfinance(symbol, interval="5m", limit=500):
    try:
        period_map = {"1m": "7d", "5m": "60d", "15m": "60d", "30m": "60d", "1h": "730d", "1d": "730d"}
        period = period_map.get(interval, "60d")
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return []
            
        df = df.tail(limit)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df.reset_index(inplace=True)
        
        data = []
        for _, row in df.iterrows():
            ts = int(row['Date'].timestamp() * 1000) if hasattr(row['Date'], 'timestamp') else int(datetime.now().timestamp() * 1000)
            data.append({
                "time": ts // 1000,
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close'])
            })
        return data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return []

# Change this to swap data source (future: zerodha, binance, etc.)
data_source = get_data_yfinance

@app.route('/api/ohlc')
def ohlc():
    symbol = request.args.get('symbol', 'RELIANCE.NS')
    tf = request.args.get('timeframe', '5m')
    limit = int(request.args.get('limit', 500))
    data = data_source(symbol, tf, limit)
    return jsonify(data)

if __name__ == '__main__':
    print("Starting MultiChart Trader on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)