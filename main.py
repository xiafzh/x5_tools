#encoding:utf-8

import os
import sys
import cgitb

cur_path = os.path.abspath(__file__)
base_path = os.path.dirname(os.path.dirname(cur_path))
sys.path.insert(0, base_path)

import clr
clr.AddReference('x51_tools')

from src.run import *

if __name__ == "__main__":
    log_file = os.getcwd() + "/core"
    if not os.path.exists(log_file):
        os.mkdir(log_file)
    elif not os.path.isdir(log_file):
        os.remove(log_file)
        os.mkdir(log_file)
    
    cgitb.enable(logdir=log_file, display=False, format='text')
    run() 