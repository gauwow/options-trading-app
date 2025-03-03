# Stock and Options Tracker

A Python-based desktop application for real-time tracking of stock prices and options data using the `yfinance` library. This tool displays stock price history, call and put options, and price changes in a graphical user interface (GUI) built with `tkinter` and `matplotlib`.

## Overview

The Stock and Options Tracker fetches and displays the following:
- **Real-Time Stock Data**: Current price, bid, ask, mid, and last close for a user-specified ticker symbol.
- **Options Data**: Call and put options for the nearest expiration date, including contract details like last price, volume, open interest, and strike price.
- **Price History**: A candlestick chart of hourly stock prices over the past 5 weekdays.
- **Price Changes**: A table tracking the latest price updates with timestamps and changes.

The default ticker is "SPY" (S&P 500 ETF), but users can input any valid ticker symbol to monitor different stocks.

## Requirements

- **Python 3.6+**
- Required Python libraries:
  - `yfinance` - Fetches stock and options data from Yahoo Finance.
  - `pandas` - Handles data manipulation.
  - `tkinter` - Creates the GUI (typically bundled with Python).
  - `matplotlib` - Plots the stock price chart.

## Installation

1. **Clone or Download the Code**
   - Download the script or clone this repository to your local machine.

2. **Install Dependencies**
   - Ensure you have Python installed, then run the following command to install required libraries:
     ```bash
     pip install yfinance pandas matplotlib
     ```
   - `tkinter` is usually included with Python; no separate installation is needed unless you're using a minimal Python setup.

3. **Run the Application**
   - Save the script as `option-trading-app.py` (or any name you prefer).
   - Open a terminal, navigate to the script's directory, and run:
     ```bash
     python option-trading-app.py
     ```

## Usage

1. **Launch the Application**
   - Execute the script, and a GUI window titled "Stock and Options Tracker" will appear.

2. **Enter a Ticker Symbol**
   - In the "Enter Ticker Symbol" field at the top, type a valid stock ticker (e.g., "AAPL" for Apple, "TSLA" for Tesla).
   - Press the "Submit" button to fetch data for the new ticker. The default is "SPY".

3. **View Data**
   - **Stock Info**: Current price, bid, mid, ask, and last close are shown at the top, updated every 5 seconds. The price color indicates if it’s above (green) or below (red) the last close.
   - **Chart**: A candlestick chart on the left displays hourly price history for the past 5 weekdays.
   - **Call Options**: A table lists call option contracts with details.
   - **Put Options**: A table lists put option contracts with details.
   - **Price Changes**: A table shows the last 10 price updates with timestamps and changes.
   - **Summary**: Total contracts, calls, puts, and the largest call/put contracts by volume are displayed below the stock info.

4. **Exit the Application**
   - Close the window to stop the program cleanly.

## Features

- **Real-Time Updates**: Stock and options data refresh every 5 seconds in a background thread.
- **Interactive GUI**: Built with `tkinter` for simplicity and native look-and-feel.
- **Candlestick Chart**: Visualizes hourly stock price movements using `matplotlib`.
- **Error Handling**: Gracefully handles missing or invalid data with "N/A" placeholders.
- **Dynamic Ticker Switching**: Users can change the ticker symbol at any time, resetting and fetching new data.

## Troubleshooting

- **No Data Displayed**: Ensure you have an internet connection and the ticker symbol is valid (e.g., "SPY", "AAPL"). Check the console for error messages.
- **Chart Not Updating**: If the chart doesn’t appear, verify `matplotlib` is installed correctly.
- **Slow Performance**: Frequent updates (every 5 seconds) may slow down on older systems; consider increasing the `time.sleep(5)` value in `fetch_data_loop()`.
- **Options Data Missing**: Some tickers may not have options data available via `yfinance`. Try popular ETFs or stocks like "SPY" or "MSFT".

## Limitations

- Relies on `yfinance`, which may occasionally fail due to Yahoo Finance API changes or rate limits.
- Options data is limited to the nearest expiration date.
- Historical data is restricted to 5 weekdays with hourly intervals.

## Contributing

Feel free to fork this project, submit pull requests, or suggest improvements via issues. Potential enhancements include:
- Adjustable update intervals.
- Support for multiple expiration dates in options data.
- Customizable chart periods or styles.

## License

This project is open-source and available under the [MIT License](LICENSE). Use it freely, but at your own risk.
