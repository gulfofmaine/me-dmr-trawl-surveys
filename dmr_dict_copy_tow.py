#! /usr/bin/env python
from __future__ import  print_function
# -*- coding: iso-8859-1 -*-
import os
import argparse
import csv
from DMRTrawlInfo import DMRTrawlInfo

######################################
def rm_dup_tow_flds(inflds, towflds):
  """
  remove elements in towflds but not in inflds to avoid duplicate fields in the CSV
    - convert lists to sets
    - subtract in_set from tow_set to remove elements in tow_set but not in in_set
  """
  in_set = set(inflds)
  tow_set = set(towflds)
  return( list(tow_set - in_set) )

######################################
def csv_file_copy(f, outfile, num_flds, output, verbose=False):
  """
  Make a CSV copy for ERDDAP input.
  CREATES A reformated OUT_<f>.csv file.
  Minimal or Full TowInfo data is appended to the OUT_<f>.csv file
  - f        : FP to open input csv file
  - outfile  : output CSV file name to be created.
  - num_flds : number of fields in the input CSV file.
  - output   : 'min' or 'full' how many of the DMRTrawlInfo fields to append.
  - verbose  : print debug info. Not yet implemented.
  """
  DMRInfo = DMRTrawlInfo()
  row_length = num_flds

  reader = csv.DictReader(f, restkey="Extra")
  # NOTE:  fieldnames is just a list, not a dict
  in_flds = reader.fieldnames
  if verbose: print(in_flds)

  # These are the minimum fields from the TowInfomation file needed for ERDDAP. latitude, longitude, times and Ashley year and season.
  min_tow_info_flds = ['START_LATITUDE', 'START_LONGITUDE', 'ISO_START_TIME', 'ISO_END_TIME', 'YEAR', 'SEASON']

  # rm_dup_tow will remove duplicates. All input files have DMR_TRIP_ID and DMR_EFFORT_ID 
  all_tow_info_flds = ['EFFORT_END_DATE', 'EFFORT_END_TIME', 'EFFORT_SEQ_NO', 'EFFORT_START_DATE', 'EFFORT_START_TIME', 'END_DEPTH', 'END_LATITUDE', 'END_LONGITUDE', 'GEAR_CONDITION', 'GRID_ID', 'LENGTH_TOW_TIME', 'SALINITY', 'START_DEPTH', 'START_LATITUDE', 'START_LONGITUDE', 'STATION_TYPE', 'SURFACE_SALINITY', 'SURFACE_TEMP_C', 'TOW_LENGTH_NM', 'TOW_QUALITY', 'WATER_TEMP_C', 'WAVE_HEIGHT', 'WIND', 'WIND_DIRECTION']

  # this script caculates these fields from the tow _DATE and _TIME fields, iso time strings are required by ERDDAP.
  # YEAR and SEASON are from the DMR_TRIP_IDENTIFIER, e.g. FL09
  calc_tow_info_flds = [ 'ISO_END_TIME', 'ISO_START_TIME', 'YEAR', 'SEASON']

  append_flds = []
  # remove duplicate fields from this CSV input fields from the tow fields
  if output == 'min':
    min_tow_info_flds = rm_dup_tow_flds(in_flds, min_tow_info_flds)
    out_flds = in_flds[:] + min_tow_info_flds
    append_flds = min_tow_info_flds
  else:
    all_tow_info_flds = rm_dup_tow_flds(in_flds, all_tow_info_flds)
    out_flds = in_flds[:] + all_tow_info_flds + calc_tow_info_flds
    append_flds = all_tow_info_flds + calc_tow_info_flds
  writer = csv.DictWriter(open(outfile, 'wb'), delimiter=',', fieldnames = out_flds )
  writer.writeheader()
  for csv_row in reader:
    if len(csv_row) != row_length:
      print(len(csv_row))
      print(row_length)
      print(row_length + len(csv_row["Extra"]))
      print("Length wrong at line:",)
      print(reader.line_num)
      return None
    orow = {}
    # These names are the same for all CSV files.
    dmr_trip_id = csv_row['DMR_TRIP_IDENTIFIER']
    dmr_effort_id = csv_row['DMR_EFFORT_IDENTIFIER']
    # Biological data has records for SP18 while TowInfo does not.
    # so skipping these
    if dmr_trip_id == 'SP18':
       break
    trawlinfo_row = DMRInfo.getRow(dmr_trip_id, dmr_effort_id)
    # copy the existing data to the outfile
    for fld in in_flds:
      orow[fld] = csv_row[fld]

    # add data from DMRTrawlInfo
    # HERE: this needs a fix.
    for fld in append_flds:
      orow[fld] = trawlinfo_row[fld]

    writer.writerow(orow)

  if verbose: print("Created:", outfile)
  return outfile
######################################
def run():
  ap = argparse.ArgumentParser()
  ap.add_argument("csv_file", help="CSV filename")
  ap.add_argument("num_flds", help="Number of fields in the CSV. EXPCatch: 15, EXPLenFreq: 11, Biological: 15, Lobster 10")
  ap.add_argument("-o", "--output", help=" Type of output file: 'full' or 'min'. Default: 'min'", default="min")
  ap.add_argument("-v", "--verbose", action="store_true", help=" verbose output.")
  args = ap.parse_args()
  
  infile = args.csv_file
  num_flds = int(args.num_flds)
  print(args.output)
  if args.output == 'min':
    outfile = 'OUT_MIN_TOW_' + os.path.basename(args.csv_file)
  else:
    outfile = 'OUT_FULL_TOW_' + os.path.basename(args.csv_file)

  f = open(infile, 'rb')
  if f:
    ret = csv_file_copy(f, outfile, num_flds, args.output, verbose=args.verbose )
    print(ret)

if __name__ == "__main__":
  run()
