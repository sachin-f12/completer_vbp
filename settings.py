import os

# Determine the absolute path to the directory containing this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
INPUT_DIR = os.path.join(BASE_DIR, 'download')
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
print(BASE_DIR)
