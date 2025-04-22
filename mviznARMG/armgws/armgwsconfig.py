#version:1
SYSTEM_NAME = "ARMG mVizn VA System Event Reporting"
VERSION = "1.50"
VERSION_DATE = "2020-04-16"
SYSTEM_TYPES = ['HNCDS', 'TCDS', 'CLPS']

CLPS_IMG_DIR = "sample_data/CLPS"
TCDS_IMG_DIR = "sample_data/TCDS"
HNCDS_IMG_DIR = "sample_data/HNCDS"

#ITbasepath = "/opt/psa/rel/opslogs/VRS/reports/"
ITbasepath = "10.66.200.20/report"

# shift1 for 07:30:00.000 to 19:29:59.999 and shift2 – 19:30:00.000 to 07:29:59.999
SHIFT1_START = '07:30:00.000'
SHIFT2_START = '19:30:00.000'
