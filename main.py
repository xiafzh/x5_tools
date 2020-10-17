#encoding:utf-8

import os
import sys

cur_path = os.path.abspath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(0, base_path)

from src.run import *

if __name__ == "__main__":
    run() 