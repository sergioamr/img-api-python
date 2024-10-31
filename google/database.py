import datetime
import re
from download_news import *

def parse_google_dates(date_str):
    
    """Parses dates from Google News"""

    parsed_date = datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %Z")
    # Format the date into the desired format
    formatted_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_date

def format_google_dates(date):
    date = re.sub("-", "", date)
    date = re.sub(" ", "", date)
    date = re.sub(":", "", date)
    return date


def google_pipeline_process(db_ticker):
    try:
        news = get_google_news(db_ticker)
        db_ticker.set_state("PROCESSING GOOGLE")

        for item in news:
            update = False
            db_news = DB_News.objects(external_uuid=item["id"]).first()
            if db_news:
                # We don't update news that we already have in the system
                print_b(" ALREADY INDEXED " + item['link'])
                update = True
                #continue
        
            raw_data_id = 0
            try:
                # It should go to disk or something, this is madness to save it on the DB
        
                news_data = DB_DynamicNewsRawData(**item)
                news_data.save()
                raw_data_id = str(news_data['id'])
            except Exception as e:
                print_exception(e, "SAVE RAW DATA")
        
            #standardize between the different news sources
            #alpha vantage doesn't have related tickers*
            myupdate = {
                        "date": parse_google_dates(item["published"]),
                        "title": item["title"],
                        "link": item["link"],
                        "external_uuid": item["id"],
                        "publisher": item["source"]
                    }
            
        
            extra = {
                'source': 'GOOGLE',
                'status': 'WAITING_INDEX',
                'raw_data_id': raw_data_id
            }
        
            myupdate = {**myupdate, **extra}
        
            if not update:
                db_news = DB_News(**myupdate).save(validate=False)
            
            google = Google()
            article = google.google_process_news(db_news)
        db_ticker.set_state("GOOGLE PROCESSED")

    except Exception as e:
        print_exception(e, "CRASH ON GOOGLE NEWS PROCESSING")

    return db_ticker

