import yfinance as yf
import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import threading
import queue
import time
from datetime import datetime

# Global variables
root = None
ticker_input = None
ticker_info_label = None
calls_tree = None
puts_tree = None
price_tree = None
summary_label = None
canvas = None
chart_frame = None
current_ticker = "SPY"
data_queue = queue.Queue()
running = False
price_history = []  # List to store price changes for table


def fetch_stock_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        hist = ticker.history(period="2d")
        current_price = info.get('regularMarketPrice', 'N/A')
        bid = info.get('bid', 'N/A')
        ask = info.get('ask', 'N/A')
        # Most recent close
        last_close = hist['Close'].iloc[-1] if not hist.empty else 'N/A'
        # Most recent open
        open_price = hist['Open'].iloc[-1] if not hist.empty else 'N/A'
        return {
            "current_price": current_price,
            "bid": bid,
            "mid": (bid + ask) / 2 if isinstance(bid, (int, float)) and isinstance(ask, (int, float)) else 'N/A',
            "ask": ask,
            "last_close": last_close,
            "open": open_price
        }
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return {"current_price": "N/A", "bid": "N/A", "mid": "N/A", "ask": "N/A", "last_close": "N/A", "open": "N/A"}


def fetch_options_data(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        expiration_dates = ticker.options
        if not expiration_dates:
            print("No expiration dates available from yfinance")
            return None, None, {}
        opt = ticker.option_chain(expiration_dates[0])
        calls = opt.calls[['contractSymbol', 'lastPrice',
                           'volume', 'openInterest', 'strike']]
        puts = opt.puts[['contractSymbol', 'lastPrice',
                         'volume', 'openInterest', 'strike']]
        calls = calls.fillna({'volume': 0, 'openInterest': 0})
        puts = puts.fillna({'volume': 0, 'openInterest': 0})
        total_calls = len(calls)
        total_puts = len(puts)
        total_contracts = total_calls + total_puts
        largest_call = calls.loc[calls['volume'].idxmax(
        )] if total_calls > 0 else None
        largest_put = puts.loc[puts['volume'].idxmax()
                               ] if total_puts > 0 else None
        summary = {
            "total_contracts": total_contracts,
            "total_calls": total_calls,
            "total_puts": total_puts,
            "largest_call": largest_call['contractSymbol'] if largest_call is not None else "N/A",
            "largest_put": largest_put['contractSymbol'] if largest_put is not None else "N/A"
        }
        print(f"Options Data - Calls: {len(calls)}, Puts: {len(puts)}")
        return calls, puts, summary
    except Exception as e:
        print(f"Error fetching options data: {e}")
        return None, None, {}


def fetch_stock_history(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="5d", interval="1h")
        # Filter out weekends (Saturday=5, Sunday=6)
        hist = hist[hist.index.weekday < 5]
        print(f"Stock History (1h, weekdays only): {len(hist)} bars fetched")
        return hist[['Open', 'High', 'Low', 'Close']].dropna()
    except Exception as e:
        print(f"Error fetching stock history: {e}")
        return pd.DataFrame()


def update_display(calls, puts, summary, stock_hist, stock_data):
    global price_history

    for item in calls_tree.get_children():
        calls_tree.delete(item)
    for item in puts_tree.get_children():
        puts_tree.delete(item)
    for item in price_tree.get_children():
        price_tree.delete(item)

    if calls is not None and isinstance(calls, pd.DataFrame):
        for _, row in calls.iterrows():
            calls_tree.insert("", "end", values=(
                row['contractSymbol'], f"${row['lastPrice']:.2f}", int(
                    row['volume']), int(row['openInterest']), f"${row['strike']:.2f}"
            ))

    if puts is not None and isinstance(puts, pd.DataFrame):
        for _, row in puts.iterrows():
            puts_tree.insert("", "end", values=(
                row['contractSymbol'], f"${row['lastPrice']:.2f}", int(
                    row['volume']), int(row['openInterest']), f"${row['strike']:.2f}"
            ))

    if summary:
        summary_text = (
            f"Total Active Contracts: {summary['total_contracts']}\n"
            f"Total Calls: {summary['total_calls']}\n"
            f"Total Puts: {summary['total_puts']}\n"
            f"Largest Call: {summary['largest_call']}\n"
            f"Largest Put: {summary['largest_put']}"
        )
        summary_label.config(text=summary_text)

    if all(isinstance(v, (int, float)) for v in stock_data.values()):
        current_price = stock_data['current_price']
        last_close = stock_data['last_close']
        color = "green" if current_price > last_close else "red"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update price history for table
        if price_history and isinstance(price_history[-1]['price'], (int, float)):
            prev_price = price_history[-1]['price']
            price_change = current_price - \
                prev_price if isinstance(prev_price, (int, float)) else 0
        else:
            price_change = 0
        price_history.append(
            {"time": timestamp, "price": current_price, "change": price_change})
        if len(price_history) > 50:  # Limit to last 50 entries
            price_history.pop(0)

        # Populate price table (last 10 entries)
        for entry in reversed(price_history[-10:]):
            price_tree.insert("", "end", values=(
                entry['time'], f"${entry['price']:.2f}", f"${entry['change']:.2f}"
            ))

        ticker_info_text = (
            f"{current_ticker}: "
            f"${current_price:.2f} | "
            f"Bid: ${stock_data['bid']:.2f} | "
            f"Mid: ${stock_data['mid']:.2f} | "
            f"Ask: ${stock_data['ask']:.2f} | "
            f"Last Market Price: ${stock_data['last_close']:.2f} | "
            f"*Last Updated: {timestamp}*"
        )
        ticker_info_label.config(
            text=ticker_info_text, font=("Arial", 18, "bold"), fg=color)
    else:
        ticker_info_label.config(
            text=f"{current_ticker}: Data N/A", font=("Arial", 18, "bold"))

    if stock_hist is not None and not stock_hist.empty:
        plot_chart(stock_hist)


def plot_chart(stock_hist):
    global canvas
    fig = plt.Figure(figsize=(8, 4), dpi=100)  # Single chart size

    ax = fig.add_subplot(111)
    ax.set_title(f"{current_ticker} Hourly Stock Price (Weekdays Only)")
    for i, row in stock_hist.iterrows():
        color = 'green' if row['Close'] >= row['Open'] else 'red'
        ax.plot([mdates.date2num(i), mdates.date2num(i)],
                [row['Low'], row['High']], color=color)
        ax.plot([mdates.date2num(i), mdates.date2num(i)], [
                row['Open'], row['Close']], color=color, linewidth=5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_ylabel("Price")
    ax.grid(True)
    plt.setp(ax.get_xticklabels(), rotation=45)

    fig.tight_layout()

    if canvas:
        canvas.get_tk_widget().destroy()

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def fetch_data_loop():
    global running, current_ticker
    while running:
        calls, puts, summary = fetch_options_data(current_ticker)
        stock_hist = fetch_stock_history(current_ticker)
        stock_data = fetch_stock_data(current_ticker)
        data_queue.put((calls, puts, summary, stock_hist, stock_data))
        time.sleep(5)


def update_gui_from_queue():
    try:
        while not data_queue.empty():
            calls, puts, summary, stock_hist, stock_data = data_queue.get_nowait()
            update_display(calls, puts, summary, stock_hist, stock_data)
    except queue.Empty:
        pass
    root.after(100, update_gui_from_queue)


def start_updates():
    global running
    if not running:
        running = True
        threading.Thread(target=fetch_data_loop, daemon=True).start()
        update_gui_from_queue()


def stop_updates():
    global running
    running = False


def clear_data():
    global price_history, data_queue
    price_history = []
    with data_queue.mutex:
        data_queue.queue.clear()  # Clear the queue


def on_ticker_submit():
    global current_ticker
    new_ticker = ticker_input.get().upper()
    if new_ticker != current_ticker:
        current_ticker = new_ticker
        stop_updates()  # Stop polling
        clear_data()    # Clear all data
        start_updates()  # Restart polling with new ticker
        # Force immediate data fetch
        threading.Thread(target=lambda: data_queue.put((fetch_options_data(current_ticker)[0], fetch_options_data(current_ticker)[
                         1], fetch_options_data(current_ticker)[2], fetch_stock_history(current_ticker), fetch_stock_data(current_ticker))), daemon=True).start()


def exit_app():
    stop_updates()
    root.quit()
    root.destroy()


def create_ui():
    global root, ticker_input, ticker_info_label, calls_tree, puts_tree, price_tree, summary_label, canvas, chart_frame

    root = tk.Tk()
    root.title("Stock and Options Tracker")
    root.geometry("1200x800")

    root.rowconfigure(0, weight=0)
    root.rowconfigure(1, weight=1)
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    top_frame = tk.Frame(root)
    top_frame.grid(row=0, column=0, columnspan=2,
                   sticky="ew", padx=10, pady=10)
    top_frame.columnconfigure(0, weight=1)
    top_frame.columnconfigure(1, weight=1)

    search_frame = tk.Frame(top_frame)
    search_frame.pack(side=tk.TOP, fill="x")
    tk.Label(search_frame, text="Enter Ticker Symbol:").pack(side=tk.LEFT)
    ticker_input = tk.Entry(search_frame)
    ticker_input.pack(side=tk.LEFT, padx=5)
    ticker_input.insert(0, "SPY")
    tk.Button(search_frame, text="Submit",
              command=on_ticker_submit).pack(side=tk.LEFT)

    ticker_info_label = tk.Label(
        top_frame, text="", justify="left", anchor="w")
    ticker_info_label.pack(side=tk.TOP, fill="x", pady=5)

    lower_frame = tk.Frame(root)
    lower_frame.grid(row=1, column=0, columnspan=2,
                     sticky="nsew", padx=10, pady=10)
    lower_frame.rowconfigure(0, weight=1)
    lower_frame.columnconfigure(0, weight=2)  # Left column for chart
    lower_frame.columnconfigure(1, weight=1)  # Right column for tables

    chart_frame = tk.Frame(lower_frame)
    chart_frame.grid(row=0, column=0, sticky="nsew")

    tables_frame = tk.Frame(lower_frame)
    tables_frame.grid(row=0, column=1, sticky="nsew")
    tables_frame.rowconfigure(0, weight=1)
    tables_frame.rowconfigure(1, weight=1)
    tables_frame.rowconfigure(2, weight=1)

    calls_frame = tk.LabelFrame(tables_frame, text="Call Options")
    calls_frame.grid(row=0, column=0, sticky="nsew", pady=5)
    calls_tree = ttk.Treeview(calls_frame, columns=(
        "Contract", "Last Price", "Volume", "Open Interest", "Strike"), show="headings")
    calls_tree.heading("Contract", text="Contract")
    calls_tree.heading("Last Price", text="Last Price")
    calls_tree.heading("Volume", text="Volume")
    calls_tree.heading("Open Interest", text="Open Interest")
    calls_tree.heading("Strike", text="Strike")
    calls_tree.pack(fill="both", expand=True)

    puts_frame = tk.LabelFrame(tables_frame, text="Put Options")
    puts_frame.grid(row=1, column=0, sticky="nsew", pady=5)
    puts_tree = ttk.Treeview(puts_frame, columns=(
        "Contract", "Last Price", "Volume", "Open Interest", "Strike"), show="headings")
    puts_tree.heading("Contract", text="Contract")
    puts_tree.heading("Last Price", text="Last Price")
    puts_tree.heading("Volume", text="Volume")
    puts_tree.heading("Open Interest", text="Open Interest")
    puts_tree.heading("Strike", text="Strike")
    puts_tree.pack(fill="both", expand=True)

    price_frame = tk.LabelFrame(tables_frame, text="Price Changes")
    price_frame.grid(row=2, column=0, sticky="nsew", pady=5)
    price_tree = ttk.Treeview(price_frame, columns=(
        "Time", "Price", "Change"), show="headings")
    price_tree.heading("Time", text="Time")
    price_tree.heading("Price", text="Price")
    price_tree.heading("Change", text="Change")
    price_tree.pack(fill="both", expand=True)

    summary_label = tk.Label(top_frame, text="", justify="left", anchor="e")
    summary_label.pack(side=tk.TOP, fill="x", pady=5)

    start_updates()
    root.protocol("WM_DELETE_WINDOW", exit_app)
    root.mainloop()


if __name__ == "__main__":
    create_ui()
