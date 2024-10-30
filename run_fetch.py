from imgapi.imgapi import ImgAPI
from colorama import Fore, Back, Style, init

init(autoreset=True)

api = ImgAPI()
api.setup("http://tothemoon.life/api", {})

json = api.api_call("/news/query?status=WAITING_INDEX&limit=1&source=YFINANCE&publisher=GlobeNewswire")

print(Fore.BLUE + " FETCH " + str(json))

for article in json['news']:
    print(Fore.GREEN + " FETCH LINK " + article['link'])


print(" TEST ")