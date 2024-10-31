import json
from colorama import Fore, Back, Style, init


def print_b(text):
    print(Fore.BLUE + text)


def print_g(text):
    print(Fore.GREEN + text)


def print_r(text):
    print(Fore.RED + text)


def print_e(text):
    print(Back.RED +
          "********************************************************")
    print(Back.RED + text)
    print(Back.RED +
          "********************************************************")

def print_json(json_in):
    print_b(json.dumps(json_in, indent=4))

def print_exception(err, text=''):
    import traceback
    print(Fore.RED + str(err))
    traceback.print_tb(err.__traceback__)
