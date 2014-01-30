cookbook
========

code demos

to get data file:

1) renew your pcmdi credentials

myproxyclient logon -b -T -s  pcmdi9.llnl.gov -l paustin -o ~/.esg/credentials.pem -C ~/.esg/certificates 

wget --no-check-certificate --certificate=/home/phil/.esg/credentials.pem  http://dapp2p.cccma.ec.gc.ca/thredds/fileServer/esg_dataroot/AR5/CMIP5/output/CCCma/CanAM4/amip/mon/atmos/ts/r1i1p1/ts_Amon_CanAM4_amip_r1i1p1_195001-200912.nc
