#! /usr/bin/env python
from __future__ import print_function
import os
import sys
from collections import OrderedDict
import csv
import cPickle as pickle


###################################################################################
# DMRTrawlInfo class
###################################################################################
class DMRTrawlInfo(object):
  """
  DMRTrawlInfo - Class to create and access python dict created from DMR's TowInformation.csv
    the rows are keyed by combination of the  DMR_TRIP_IDENTIFIER  and DMR_EFFORT_IDENTIFIER. E.g. FL00_1 thru SP17_122
    Designed to allow easy lookup of the Tow or Trawl information by the DMR Survey data files:
      EXPCATCH_forGMRI.csv
      Biological_Data.csv
      EXP_LengthFrequency_ForGMRI.csv
    TowInfomation.csv fields: 28
    DMR_TRIP_IDENTIFIER,EFFORT_START_DATE,EFFORT_START_TIME,DMR_EFFORT_IDENTIFIER,START_LATITUDE,START_LONGITUDE,END_LATITUDE,END_LONGITUDE,REGION,STRATUM,STATION_TYPE,START_DEPTH,LENGTH_TOW_TIME,EFFORT_SEQ_NO,TOW_LENGTH_NM,WATER_TEMP_C,SALINITY,END_DEPTH,SURFACE_TEMP_C,SURFACE_SALINITY,TOW_QUALITY,GEAR_CONDITION,EFFORT_END_DATE,EFFORT_END_TIME,WAVE_HEIGHT,WIND,WIND_DIRECTION,GRID_ID

    TRAWLInfo keys:
        DMR_TRIP_IDENTFIER is two letter season code: FL - Fall, SP - Spring, followed by 2 digit year: 00, 2000, thru 17 2017.
        DMR_EFFORT_IDENTFIER 
        e.g.
         "FL00_1", 
         "SP17_122", 
    Calculated Fields:
        In the process we create caculated fields necessary for ERDDAP.
        ISO_START_TIME - YYYY-MM_DDTHH:MM string created from EFFORT_START_DATE EFFORT_START_TIME 
        ISO_END_TIME   - YYYY-MM_DDTHH:MM string created from EFFORT_END_DATE EFFORT_END_TIME 
        YEAR           -  YYYY integer extracted from DMR_TRIP_IDENTIFIER, FLYY or SPYY
        SEASON         -  "Fall" or "Spring" extracted from DMR_TRIP_IDENTIFIER, FLYY or SPYY
  """
  def __init__(self, pfile="trawlinfo_dict.p"):
    """
    Check for existance of trawlino_dict.p pickle if not create a new one from the TowInformation.csv
    :param pfile: The name of the pickle file. trawlinfo_dict.p
    """
    self.ERROR = ''
    if os.path.exists(pfile):
      self.trawlInfoDict = pickle.load( open( pfile, "rb" ) )
    else:
      print(pfile, "not found. updating Pickle()", file=sys.stderr)
      self.updatePickle( pfile=pfile)
      #exit()

    self.pfile = pfile

  #####################
  def getError(self):
    return self.ERROR
  ############### 
  def create_iso_time(self, csv_row):
    """
    combine date and time fields from the csv_row fields to an iso string suitable for ERDDAP
    Both iso_start_time and iso_end_time are returned as a list.
       csv_row['EFFORT_START_DATE']
       csv_row['EFFORT_START_TIME']
    """
  
    start_dt = csv_row['EFFORT_START_DATE']
    s_mn, s_dy, s_yr = [int(f) for f in start_dt.split("/")]
    s_yr += 2000
    s_time = csv_row['EFFORT_START_TIME']
    s_iso_time = "{0}-{1:02d}-{2:02d}T{3}".format( s_yr, s_mn, s_dy, csv_row['EFFORT_START_TIME'] )

    end_dt = csv_row['EFFORT_END_DATE']
    e_mn, e_dy, e_yr = [int(f) for f in end_dt.split("/")]
    e_yr += 2000
    e_time = csv_row['EFFORT_END_TIME']
    e_iso_time = "{0}-{1:02d}-{2:02d}T{3}".format( e_yr, e_mn, e_dy, csv_row['EFFORT_END_TIME'] )
    return(s_iso_time, e_iso_time)
  ############### 
  def create_season_year(self, dmr_trip_id):
    """ split FF00 or SP00 into season string and int year. For ERDDAP search. """
    season = dmr_trip_id[0:2]
    yr = int(dmr_trip_id[2:4])
    yr += 2000
    if season[0] == 'F':
      season = 'Fall'
    if season[0] == 'S':
      season = 'Spring'
    return(season, yr)
  
  ############### 
  def parse_towinfo_csv(self, csv_file):
    towinfo_dict = OrderedDict()
    row_length = 28
  
    try:
      with open(csv_file, 'rb') as f:
        reader = csv.DictReader(f)
        for csv_row in reader:
          if len(csv_row) != row_length:
            print("Length wrong",)
            print(reader.line_num)
            continue
          dmr_trip_id = csv_row['DMR_TRIP_IDENTIFIER']
          dmr_effort_id = csv_row['DMR_EFFORT_IDENTIFIER']
          # Adding iso times for ERDDAP
          s_t, e_t = self.create_iso_time(csv_row)
          csv_row.update(ISO_START_TIME = s_t)
          csv_row.update(ISO_END_TIME = e_t)
          # Adding season string and year integer at Ashley's request to view by seaon and year.
          season, yr = self.create_season_year(dmr_trip_id)
          csv_row.update(SEASON = season)
          csv_row.update(YEAR = yr)
          # key for each row will be DMR_TRIP_ID-DMR_EFFORT_ID
          # Allowing easy lookup for other DMR CSV creation routines.
          towinfo_dict[dmr_trip_id + '_' + dmr_effort_id] = csv_row
  
      # End of with infile
  
    except IOError:
      print("File: '{0}' does not exists.".format(csv_file))
      exit()
    
    return(towinfo_dict)

  ############### 
  def updatePickle(self, csv_file="input_csv/TowInformation.csv", pfile="trawlinfo_dict.p" ):
    """ create a new trawlinfo_dict pickle file by parsing input_csv/TowInformatio csv file """
    self.csv_file = csv_file
    towinfo_dict = self.parse_towinfo_csv(csv_file)
    pfile = pfile
    pickle.dump( towinfo_dict, open( pfile, "wb" ) )
    self.csv_file = csv_file
    self.trawlInfoDict = towinfo_dict

  ############### 
  def rowHeaders(self):
    """ print row headers for first key in dict """
    fk = next(iter(self.trawlInfoDict))
    return sorted((self.trawlInfoDict[fk].keys()))

  ############### 
  def getRow(self, trip_id, effort_id ):
    """ return row with trip_id / effort_id key """
    return(self.trawlInfoDict[trip_id + "_" + effort_id])


####################################################################################
if __name__ == "__main__":
  # This will create the pickle file
  DMRInfo = DMRTrawlInfo()

  """
  # Some tests
  headers = DMRInfo.rowHeaders()
  for h in headers:
    print(h)

  info_dict = DMRInfo.trawlInfoDict
  for k in info_dict.keys():
    print(k, end=' ')
    print(info_dict[k]['ISO_START_TIME'], end=' ')
    print(info_dict[k]['SEASON'], end=' ')
    print(info_dict[k]['YEAR'])

  dmr_trip_id = "SP11"
  dmr_effort_id = "3"
  info_row = DMRInfo.getRow(dmr_trip_id, dmr_effort_id)
  print(info_row['SEASON'], end=' ')
  print(info_row['YEAR'], end=' ')
  print(info_row["LENGTH_TOW_TIME"], end=' ')
  print(info_row["WAVE_HEIGHT"], end=' ')
  print(info_row["WIND"])
  """
