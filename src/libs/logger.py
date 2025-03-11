from datetime import datetime
import sys

def printinfo(*args):
    print('{} - workers - INFO - {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3], ' - '.join(args)))

def printerror(*args):
    print('{} - workers - ERROR - {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3], ' - '.join(args)),
          file=sys.stderr)