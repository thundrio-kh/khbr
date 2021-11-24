from khbr._config import *

def print_debug(msg, override=False):
    if override or DEBUG_PRINT:
        print(msg)
