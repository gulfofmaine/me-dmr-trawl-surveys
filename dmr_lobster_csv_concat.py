#! /usr/bin/env python
"""
read a directory with DMR Lobster Trawl CSV files and concat to a single CSV.
"""
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("dir", help="Directory with Lobster CSV files")
args = parser.parse_args()

if not args.dir.endswith('/'):
  args.dir += '/'

fout = open("ALL_Lobster_LengthFrequency.csv","a")

csv_list = [ f for f in os.listdir(args.dir) if f.endswith(".csv")]
csv_list.sort()
# We want headers from first file.
infile = csv_list.pop(0)
for line in open(args.dir + infile):
  fout.write(line)
for infile in csv_list:
  with open(args.dir + infile) as f:
    f.next()
    for line in f:
      fout.write(line)

fout.close()
exit()
