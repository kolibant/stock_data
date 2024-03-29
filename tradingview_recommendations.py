# Import dependencies
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import yahoo_fin.stock_info as si

# Parameters
tickers = ['DDOG', 'NVDA', 'PTON', 'RH', 'ROKU', 'SE', 'SQ', 'TSLA', 'TTD']
interval = '1W'

# Lists of tickers
nasdaq = pd.read_csv('../nasdaq_tickers.csv')['Ticker'].tolist()
nyse = pd.read_csv('../nyse_tickers.csv')['Ticker'].tolist()
amex = pd.read_csv('../amex_tickers.csv')['Ticker'].tolist()

# List of valid time intervals
type_intervals = ['1m', '5m', '15m', '1h', '4h', '1D', '1W', '1M']

# Set up chromedriver
options = Options()
options.add_argument("--headless")
webdriver = webdriver.Chrome(executable_path='../chromedriver', options=options)

# Loop through the tickers
for ticker in tickers:
    analysis = []
    try:
        # Determine the exchange of the ticker
        if ticker in nasdaq:
            exchange = 'NASDAQ'
        elif ticker in nyse:
            exchange = 'NYSE'
        elif ticker in amex:
            exchange = 'AMEX'
        else:
            print(f"Could not find the exchange for {ticker}")
        
        # Get the current price of the ticker
        price = round(si.get_live_price(ticker), 2)
        
        # Retrieve technical analysis data from TradingView
        webdriver.get("https://www.tradingview.com/symbols/{}-{}/technicals".format(exchange, ticker))
        time.sleep(1)
        
        # Print out the ticker, interval, and price
        print('Ticker: ' + ticker)
        print('Interval: ' + interval)
        print('Price: ' + str(price))
        
        # Click on the specified time interval
        numbers = [1, 2, 3, 4, 5, 6, 7, 8]
        for type_interval, n in zip(type_intervals, numbers):
            if interval == type_interval:
                element = webdriver.find_element_by_xpath(f'//*[@id="technicals-root"]/div/div/div[1]/div/div/div[1]/div/div/div[{n}]')
                element.click()
            else:
                continue
        
        time.sleep(1)
        
        # Overall Recommendation
        recommendation_elements = webdriver.find_elements_by_class_name("speedometerSignal-pyzN--tL")
        analysis.append(recommendation_elements[1].get_attribute('innerHTML'))
        counter_elements = webdriver.find_elements_by_class_name("counterNumber-3l14ys0C")
        analysis.append(int(counter_elements[3].get_attribute('innerHTML')))
        analysis.append(int(counter_elements[4].get_attribute('innerHTML')))
        analysis.append(int(counter_elements[5].get_attribute('innerHTML')))
        df = pd.DataFrame.from_records([tuple(analysis)], columns=['Recommendation', '# of Sell Signals', '# of Neutral Signals', '# of Buy Signals'])
        print('\nOverall Recommendation: ')
        print(df.set_index('Recommendation').T)
        
        # Oscillator Recommendation
        analysis.append(recommendation_elements[0].get_attribute('innerHTML'))
        counter_elements = webdriver.find_elements_by_class_name("counterNumber-3l14ys0C")
        analysis.append(int(counter_elements[0].get_attribute('innerHTML')))
        analysis.append(int(counter_elements[1].get_attribute('innerHTML')))
        analysis.append(int(counter_elements[2].get_attribute('innerHTML')))
        df = pd.DataFrame.from_records([tuple(analysis[4:8])], columns=['Recommendation', '# of Sell Signals', '# of Neutral Signals', '# of Buy Signals'])
        print ('\nOscillator Recommendation: ')
        print (df.set_index('Recommendation').T)
    
        # Moving Average Recommendation
        analysis.append(recommendation_elements[2].get_attribute('innerHTML'))
        counter_elements = webdriver.find_elements_by_class_name("counterNumber-3l14ys0C")
        analysis.append(int(counter_elements[6].get_attribute('innerHTML')))
        analysis.append(int(counter_elements[7].get_attribute('innerHTML')))
        analysis.append(int(counter_elements[8].get_attribute('innerHTML')))
        df = pd.DataFrame.from_records([tuple(analysis[8:12])], columns=['Recommendation', '# of Sell Signals', '# of Neutral Signals', '# of Buy Signals'])
        print ('\nMoving Average Recommendation: ')
        print (df.set_index('Recommendation').T)
        
        # Use pandas.read_html to get tables
        html = webdriver.page_source
        tables = pd.read_html(html, attrs = {'class': 'table-1YbYSTk8'})
        
        # Set variable names to tables
        oscillator_table = tables[0]
        ma_table = tables[1]
        pivots_table = tables[2]
        
        # Rename dataframe columns
        oscillator_table.columns = ['Name', 'Value', 'Action']
        ma_table.columns = ['Name', 'Value', 'Action']
        pivots_table.columns = ['Pivot', 'Classic', 'Fibonacci', 'Camarilla', 'Woodie', 'DM']
    except Exception as e:
        print (f'Could not retrieve stats for {ticker} because {e}')

# Close the chromedriver
webdriver.close()