import yfinance as yf
import datetime
import requests
import re




def is_nasdaq_ticker(ticker):
    try:
        stock_info = yf.Ticker(ticker).info
        exchange = stock_info.get('exchange', None)
        if exchange in ["NMS", "NASDAQ"]:  # "NMS" stands for NASDAQ Stock Market
            return True
        else:
            return False
    except Exception as e:
        print(f"Error retrieving data for ticker {ticker}: {e}")
        return False

def is_nyse_ticker(ticker):
    try:
        stock_info = yf.Ticker(ticker).info
        exchange = stock_info.get('exchange', None)
        if exchange in ["NYQ", "NYE", "NYSE"]:  # "NYQ" stands for NYSE (New York Stock Exchange)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error retrieving data for ticker {ticker}: {e}")
        return False


def get_exchange(ticker):
    if is_nasdaq_ticker(ticker) == True:
        return "NASDAQ"
    elif is_nyse_ticker(ticker) == True:
        return "NYSE"

    #add functionality for non-USA stocks later
    else:
        print("This stock is not supported yet")
        return None


def format_ticker(ticker):
    exchange = get_exchange(ticker)
    return f"{exchange}:{ticker}"


def get_company_name_from_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        company_name = stock.info['longName']
        return company_name
    except KeyError:
        return ""
    except Exception as e:
        return ""

def get_ticker_from_company_name(company_name):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "SYMBOL_SEARCH",
        "keywords": company_name,
        "apikey": "JIHXVRY5SPIH16C9"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "bestMatches" in data and data["bestMatches"]:
            # Retrieve the first matching symbol
            ticker = data["bestMatches"][0]["1. symbol"]
            return ticker
        else:
            return "Ticker not found"
    except Exception as e:
        return f"An error occurred: {e}"


############### parsing dates

def parse_av_dates(date_str):
    date_obj = datetime.datetime.strptime(date_str, "%Y%m%dT%H%M%S")
    unix_timestamp = int(date_obj.timestamp())
    return unix_timestamp

def format_av_dates(date):
    date = re.sub("-", "", date)
    date = re.sub(" ", "", date)
    date = re.sub(":", "", date)
    return date


def parse_google_dates(date_string):
    
    """Parses dates from Google News"""

    dt = datetime.datetime.strptime(date_string, "%a, %d %b %Y %H:%M:%S %Z")
    unix_timestamp = int(dt.timestamp())
    return unix_timestamp


############# generate uuid


def generate_uuid(item):

    """Alphavantage does not have uuid; this is a function to generate it"""

    date = str(parse_av_dates(item["time_published"]))
    source = item["source"][0].lower()
    return f"av_{source}_{date}"