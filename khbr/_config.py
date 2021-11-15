import os

DEBUG_LOCATIONS = []

DIAGNOSTICS = True
GENERATE_IDENTICON = False

KH2_DIR = os.environ["USE_KH2_GITPATH"] if "USE_KH2_GITPATH" in os.environ else "extracted_data"

LIMITED_SIZE = 15.0

DEBUG_HEALTH = False
DEBUG_PRINT = False

HARDCAP = "65000"