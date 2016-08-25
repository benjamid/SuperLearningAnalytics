#!/usr/bin/python
"""
Author-skarumbaiah
Date-06/18/2016

Script to covert all .avi files to .mp4
Change the src and dest accordingly

example-
-p "C:/Users/skarumbaiah/Desktop/test/"
"""

import os,sys
from genericpath import isfile

import argparse

def main(args):
    """ parse command like argument"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path")

    args = parser.parse_args()

    dirc = args.path
        
    print("Looking in the directory -", dirc)

    for i in range(80):
        j = i+1
        src = dirc + str(j) + '.avi'
        dst = dirc + str(j) + '.mp4'
        if isfile(src):
            print('Converting '+src +' to mp4')
            os.rename(src, dst)
    
if __name__ == "__main__":
    main(sys.argv[1:])