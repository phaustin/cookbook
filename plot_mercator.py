"""
   plot an SST map from a monthly CFMIP5 ts file
"""
from matplotlib import pyplot as plt
plt.switch_backend('MacOSX') #interactive
#plt.switch_backend('Qt4Agg') #interactive
#plt.switch_backend('Agg') #batch
import numpy as np
from netCDF4 import Dataset,num2date,date2num
import netCDF4 as nc4
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import Normalize
from matplotlib import cm
from util import find_index_sorted
from constants import warm_pool as wp
from constants import tropics as tp
import datetime as dt

#
# Task 1: make a map of tropical SSTs averaged from
# May 1, 1976 to June 1, 1989
#

data_dir='/Users/phil/repos/feedback_scripts'
amip_sst='ts_Amon_CanAM4_amip_r1i1p1_195001-200912.nc'
file_name='%s/%s' % (data_dir,amip_sst)

nc_data=Dataset(file_name)
lats=nc_data.variables['lat'][...]
lons=nc_data.variables['lon'][...]
#
# lat/lon points of box corners are stored in a named_tuple
# in constants.py
#
lat_slice=find_index_sorted(lats,[wp.ll.lat,wp.ur.lat])
lat_slice[1]+=1
lon_slice=find_index_sorted(lons,[wp.ll.lon,wp.ur.lon])
lon_slice[1]+=1

lat_slice=slice(*lat_slice)
lon_slice=slice(*lon_slice)

the_lats=lats[lat_slice]
the_lons=lons[lon_slice]
#
# now get the time slice
#
nc_times=nc_data.variables['time']
the_times=nc_times[:]
#
# first convert to netcdftime datetime objects
#
the_dates=num2date(the_times,nc_times.units,nc_times.calendar)
#
# netCDF4 bug(?) means that netcdftime objects can't be compared/sorted
# so convert to python datetime objects
#
py_dates=[dt.datetime(*item.timetuple()[:6]) for item in the_dates]
py_dates=np.array(py_dates)
#
# 
#
start_date=dt.datetime(1976,5,1,0,0,0)
stop_date=dt.datetime(1989,6,1,0,0,0)
time_slice=find_index_sorted(py_dates,[start_date,stop_date])
time_slice=slice(*time_slice)
#
#  get the slice
#
amip_sst=nc_data.variables['ts'][time_slice,lat_slice,lon_slice]
#
# time average
#
amip_box=np.mean(amip_sst,axis=0)

plt.close('all')
fig=plt.figure(1)
fig.clf()
ax1=fig.add_subplot(111)
cmap=cm.RdBu_r
cmap.set_over('y')
cmap.set_under('k')

vmin= 290
vmax= 305
the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)

params=dict(projection='merc',
            llcrnrlon=80,llcrnrlat=-15.,urcrnrlon=170,urcrnrlat=20.,
            resolution='c',lat_0=0,lon_0=120.,lat_ts=0.)

m = Basemap(**params)
x, y = m(*np.meshgrid(the_lons, the_lats))
im=m.pcolormesh(x,y,amip_box,cmap=cmap,norm=the_norm,ax=ax1)
cb=m.colorbar(im,extend='both',location='bottom')
ticks=np.arange(vmin,vmax,2.)
cb.set_ticks(ticks)
cb.set_ticklabels(ticks)
cb.update_ticks()
#
# draw a box around the warm pool with coordinates
# defined in constants.py
#
corner_lats=[wp.ll.lat,wp.lr.lat,wp.ur.lat,wp.ul.lat,wp.ll.lat]
corner_lons=[wp.ll.lon,wp.lr.lon,wp.ur.lon,wp.ul.lon,wp.ll.lon]
x,y=m(corner_lons,corner_lats)
m.plot(x,y,lw=5.,ax=ax1)
m.drawcoastlines()
#m.fillcontinents(color='coral',lake_color='aqua')
# draw parallels and meridians.
m.drawparallels(np.arange(-35.,35.,10.))
m.drawmeridians(np.arange(80.,280.,10.))
start_string=start_date.strftime("%Y-%b-%d")
stop_string=stop_date.strftime("%Y-%b-%d")
ax1.set_title('AMIP surface temps (K) %s to %s' % (start_string,stop_string))
fig.tight_layout()
fig.canvas.draw()
outfile='sst_pacific.png'
fig.savefig(outfile)
#
# now plot the timeseries
#
amip_time=np.mean(amip_sst,axis=1) #lat average
amip_time=np.mean(amip_time,axis=1) #lon_average
fig=plt.figure(2)
fig.clf()
ax1=fig.add_subplot(111)
ax1.plot(py_dates[time_slice],amip_time)
ax1.set_title('average tropical surface temps (K) %s to %s' % (start_string,stop_string))
fig.tight_layout()
fig.canvas.draw()
fig.savefig('sst_average.png')

plt.show()
 


