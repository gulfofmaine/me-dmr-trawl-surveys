# Maine DMR Fall and Spring Trawl Survey Data Prepared for GMRI

## Summary
The Maine DMR prepared  __Excel/CSV__ files each with a corresponding __MS Word__ description file for use by GMRI. They include data for the years 2000 thru 2017. This repo contains code to prepare the files for import into the GMRI ERDDAP Server [DMR data](http://docker1.gmri.org:8230/erddap/search/index.html?searchFor=DMR). The files were all converted to plain csv and text before processing. The scripts will work if new files are created with additional years of Trawl Surveys.

## Input CSV Files
There are four observation / data files and one metadata file with information about each tow see the [input_csv directory](./input_csv). See the [description files](file_descriptions) for detailed information about each.

1. TowInformation.csv  
   The TowInformation contains detailed information about every tow and including date,time, lat,lon and physical observations.
   The data files are keyed to these files by two fields `DMR_TRIP_IDENTIFIER` and `DMR_EFFORT_IDENTFIER` allowing the TowInformation to be merged with the data files.

1. EXPCATCH_forGMRI.csv  
   Expanded catch data by species.
1. EXP_LengthFrequency_ForGMRI.csv  
   Expanded Length and Frequency data by species.
1. Biological_Data.csv  
   Age and Maturity data by species.
1. ALL_Lobster_LengthFrequency.csv  
   The lobster trawl data was sent in individual Excel files for each season and year.These were concatenated by the [dmr_lobster_csv_concat.py](dmr_lobster_csv_concat.py) script.


## Directories

- [ERDDAP-XML/](./ERDDAP-XML/) -- ERDDAP datasets.xml fragments with full TowInformation appended. 
- [ERDDAP-XM-MINL/](./ERDDAP-XML-MIN/) -- ERDDAP datasets.xml fragments  with minimal TowInformation appened. 
- [input_csv/](./input_csv/)   -- Input CSV files saved from Excel.
- [file_descriptions/](./file_descriptions/)   -- Word Metadata doc files saved as text.

The output files can be created on anywhere but must be copied to Docker1 where the ERDDAP container runs in  
`/home2/data/GMRI/ME_DMR_SEAGRANT/`  

The locations are set in GMRI ERDDAP datasets.xml via `<fileDir>/home2/data/GMRI/ME_DMR_SEAGRANT/</fileDir>` and can be changed.

## Code

`DMRTrawlInfo.py`  
  Parses the TowInformation.csv file and creates a dict of all the row records keyed by DMR_TRIP and DMR_EFFORT ID's for quick lookup by in the `dmr_dict_copy_tow.py` script when converting the data files.  

```
NAME
    DMRTrawlInfo

FILE
    DMRTrawlInfo.py

CLASSES
    
    class DMRTrawlInfo(__builtin__.object)
     |  DMRTrawlInfo - Class to create and access python dict created from DMR's TowInformation.csv
     |    the rows are keyed by combination of the  DMR_TRIP_IDENTIFIER  and DMR_EFFORT_IDENTIFIER. E.g. FL00_1 thru SP17_122
     |    Designed to allow easy lookup of the Tow or Trawl information by the DMR Survey data files:
     |      EXPCATCH_forGMRI.csv
     |      Biological_Data.csv
     |      EXP_LengthFrequency_ForGMRI.csv
     |    TowInfomation.csv fields: 28
     |    DMR_TRIP_IDENTIFIER,EFFORT_START_DATE,EFFORT_START_TIME,DMR_EFFORT_IDENTIFIER,START_LATITUDE,START_LONGITUDE,END_LATITUDE,END_LONGITUDE,REGION,STRATUM,STATION_TYPE,START_DEPTH,LENGTH_TOW_TIME,EFFORT_SEQ_NO,TOW_LENGTH_NM,WATER_TEMP_C,SALINITY,END_DEPTH,SURFACE_TEMP_C,SURFACE_SALINITY,TOW_QUALITY,GEAR_CONDITION,EFFORT_END_DATE,EFFORT_END_TIME,WAVE_HEIGHT,WIND,WIND_DIRECTION,GRID_ID
     |  
     |    TRAWLInfo keys:
     |        DMR_TRIP_IDENTFIER is two letter season code: FL - Fall, SP - Spring, followed by 2 digit year: 00, 2000, thru 17 2017.
     |        DMR_EFFORT_IDENTFIER 
     |        e.g.
     |         "FL00_1", 
     |         "SP17_122", 
     |    Calculated Fields:
     |        In the process we create caculated fields necessary for ERDDAP.
     |        ISO_START_TIME - YYYY-MM_DDTHH:MM string created from EFFORT_START_DATE EFFORT_START_TIME 
     |        ISO_END_TIME   - YYYY-MM_DDTHH:MM string created from EFFORT_END_DATE EFFORT_END_TIME 
     |        YEAR           -  YYYY integer extracted from DMR_TRIP_IDENTIFIER, FLYY or SPYY
     |        SEASON         -  "Fall" or "Spring" extracted from DMR_TRIP_IDENTIFIER, FLYY or SPYY
     |  
     |  Methods defined here:
     |  
     |  __init__(self, pfile='trawlinfo_dict.p')
     |      Check for existance of trawlino_dict.p pickle if not create a new one from the TowInformation.csv
     |      :param pfile: The name of the pickle file. trawlinfo_dict.p
     |  
     |  create_iso_time(self, csv_row)
     |      combine date and time fields from the csv_row fields to an iso string suitable for ERDDAP
     |      Both iso_start_time and iso_end_time are returned as a list.
     |         csv_row['EFFORT_START_DATE']
     |         csv_row['EFFORT_START_TIME']
     |  
     |  create_season_year(self, dmr_trip_id)
     |      split FF00 or SP00 into season string and int year. For ERDDAP search.
     |  
     |  getError(self)
     |      #####################
     |  
     |  getRow(self, trip_id, effort_id)
     |      return row with trip_id / effort_id key
     |  
     |  parse_towinfo_csv(self, csv_file)
     |      ###############
     |  
     |  rowHeaders(self)
     |      print row headers for first key in dict
     |  
     |  updatePickle(self, csv_file='input_csv/TowInformation.csv', pfile='trawlinfo_dict.p')
     |      create a new trawlinfo_dict pickle file by parsing input_csv/TowInformatio csv file
     |  
     |  ----------------------------------------------------------------------
```

`dmr_dict_copy_tow.py`  
This is the main script. Creates both `OUT_FULL_TOW_<csv_input_file>.csv` and `OUT_MIN_TOW_<csv_input_file.csv` which are ready to load into ERDDAP. We are only using the FULL_TOW csv files for loading into ERDDAP.

```
usage: dmr_dict_copy_tow.py [-h] [-o OUTPUT] [-v] csv_file num_flds

positional arguments:
  csv_file              CSV filename
  num_flds              Number of fields in the CSV. EXPCatch: 15, EXPLenFreq:
                        11, Biological: 15, Lobster 10

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Type of output file: 'full' or 'min'. Default: 'min'
  -v, --verbose         verbose output.
```

`dmr_lobster_csv_concat.py`  
This just concatenates the 34 individual Lobster_LengthFrequency.csv files into a single `ALL_Lobster_LengthFrequency.csv` file. Using the first file headers.

```
usage: dmr_lobster_csv_concat.py [-h] dir

positional arguments:
  dir         Directory with Lobster CSV files

optional arguments:
  -h, --help  show this help message and exit
```
