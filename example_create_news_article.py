from urllib.parse import quote_plus

from imgapi.imgapi import ImgAPI
from imgapi.print_tools import *

##############################################################################################


def delete_article(article):
    """ Example of how to delete an article
    """
    article_id = article['news'][0]['id']

    print_b(" Delete news article " + article_id)
    json_res = api.api_call("/news/rm?id=" + article_id, test=True)

    # Check if the API was successful, API will return state="deleted" if successful
    if not api.check_result(json_res, expected_state="deleted"):
        exit()

    print_json(json_res)
    print_g(" Deletion was succesful ")


api = ImgAPI()

api.setup(config_file=".config.json")

# Search first for our Test article to see if it is already indexed

test_url = "https://linkslog.org"
api_params = "link=" + quote_plus(test_url)

json_in = api.api_call("/news/query?" + api_params, test=True)
if not json_in:
    exit()

print_json(json_in)

# If there is an article with this link, delete it

if len(json_in['news']) > 0:
    print_r("THERE ARE ALREADY NEWS ON THE SYSTEM WITH THIS LINK")
    delete_article(json_in)

# Dummy article to upload

article = {
    'link': test_url,
    'title': "THIS IS A TEST",
    'external_uuid': "7bb12c17-a872-3080-ae2a-b56e967f2455",
    'publisher': "API_TEST",
    'articles': ["We are uploading a test", "AI tell us a JOKE"],
    'related_exchange_tickers': ["NASDAQ:TOTHEMOON", "NYE:GPUTOP"],
    'source': "IMG-API-PYTHON-API",
    'experiment': "img-api-demo-example",
    'status': "INDEXED",
}

# Call to create and upload a new article.
res = api.api_call("/news/create", data=article)

if api.check_result(res, expected_state="success"):
    delete_article(res)
    print_json(res)
    print_g("================================= ")
    print_g(" FETCH FINISHED ")
else:
    print_e(" FETCH FINISHED WITH ERRORS ")