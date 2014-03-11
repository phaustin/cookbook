import xlrd
import numpy as np
from pandas import DataFrame

filename='standard_output.xls'
workbook = xlrd.open_workbook(filename)
worksheet = workbook.sheet_by_name('Amon')

twod_fields=[]
headers=worksheet.row(14)
colnames=[item.value for item in headers]
for rownum in np.arange(16,66):
    row = worksheet.row(rownum)
    twod_fields.append([item.value for item in row])

twod_df=DataFrame.from_records(twod_fields,columns=colnames)
print twod_df[[u'CMOR variable name',u'long name', u'units ']].to_string()

threed_fields=[]
headers=worksheet.row(14)
colnames=[item.value for item in headers]
for rownum in np.arange(70,98):
    row = worksheet.row(rownum)
    threed_fields.append([item.value for item in row])

threed_df=DataFrame.from_records(threed_fields,columns=colnames)
print threed_df[[u'CMOR variable name',u'long name', u'units ']].to_string()


worksheet = workbook.sheet_by_name('fx')
gridcell_fields=[]
headers=worksheet.row(14)
colnames=[item.value for item in headers]
for rownum in np.arange(15,22):
    row = worksheet.row(rownum)
    gridcell_fields.append([item.value for item in row])

gridcell_df=DataFrame.from_records(gridcell_fields,columns=colnames)
print gridcell_df[[u'CMOR variable name',u'long name', u'units ']].to_string()


worksheet = workbook.sheet_by_name('cfMon')
cfMon_fields=[]
headers=worksheet.row(14)
colnames=[item.value for item in headers]
for rownum in np.arange(15,99):
    row = worksheet.row(rownum)
    cfMon_fields.append([item.value for item in row])

cfMon_df=DataFrame.from_records(cfMon_fields,columns=colnames)
print cfMon_df[[u'CMOR variable name',u'long name', u'units ']].to_string()

    
