"""
   plot an average tropical warm pool  SST map from a monthly AMSR-E tos file
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
import datetime as dt

def find_index(vec_vals,target):
    """

    returns the first index of vec_vals that contains the value
    closest to target.

    Parameters
    ----------

    vec_vals: list or 1-d array
    target:   list 1-d array or scalar


    Returns
    -------

    list of len(target) containing the index idx such that
    vec_vals[idx] is closest to each item in target

    Example
    -------

    left_lon,right_lon=find_index(the_lons,[120.,140.])

    """
  
    target=np.atleast_1d(target)  #turn scalar into iterable, no-op if already array
    vec_vals=np.array(vec_vals)  #turn list into ndarray or no-op if already array
    index_list=[]
    for item in target:
        first_index=np.argmin(np.abs(vec_vals - item))
        index_list.append(first_index)
    return index_list


def get_var_2D(file_name,var_name,corners=None,start_date=None,stop_date=None,
                time_name='time',lat_name='lat',lon_name='lon'):
    """

    Given a netcdf file containing a [time,lat,lon] variable with name
    var_name, return a slice with values
    [start_date:stop_date,corners.ll.lat:corners.ur.lat,corners.ll.lon:corners.ur.lon]

    Parameters
    ----------

    filename: str --  name of netcdf (possible including full path) of netcdf file
    varname:  str --  name of [time,lat,lon] netcdf variable (.eg. tos)
    corners:  optional, my_namedtuple -- Box object with latlon corner points
                 if None, defaults to all lats, all lons
    start_date: optional, datetime  -- python datetime object to start slice
                 if None, defaults to time index 0
    stop_date: optional, datetime  -- python datetime object to end slice
                 if None, defaults to last time value

    Returns
    -------

    tuple containing:

    data_nc: netCDF4 Dataset
    var_nc:  netCDF4 variable
    the_times: np.array of datetimes for slice
    the_lats: 1-D np.array of latitudes for slice
    the_lons: 1_D np.array of longitudes for slice
    vararray: 2:D np.array with variable slice

    Example
    -------

    in_file='tos_AMSRE_L3_v7_200206-201012.nc'
    options=dict(corners=warmpool,start_date=dt.datetime(2003,4,1),stop_date=dt.datetime(2006,3,1))
    data_nc,var_nc,the_times,the_lats,the_lons,sst=get_var_2D(in_file,'tos',**options)
    """      
    data_nc=Dataset(file_name)
    var_nc=data_nc.variables[var_name]
    lat_nc=data_nc.variables[lat_name]
    lon_nc=data_nc.variables[lon_name]
    if corners is not None:
    #
    # get all the lats and lons
    #
        lats=lat_nc[...]
        lons=lon_nc[...]  
        crn=corners
        #
        # lat/lon points of box corners are stored in a named_tuple
        # in constants.py
        #
        lat_slice=find_index(lats,[crn.ll.lat,crn.ur.lat])
        lat_slice[1]+=1
        lon_slice=find_index(lons,[crn.ll.lon,crn.ur.lon])
        lon_slice[1]+=1
    else:
        lat_slice=[0,None]
        lon_slice=[0,None]
        
    lat_slice=slice(*lat_slice)
    lon_slice=slice(*lon_slice)

    the_lats=lat_nc[lat_slice]
    the_lons=lon_nc[lon_slice]
    #
    # first convert to netcdftime datetime objects
    #
    time_nc=data_nc.variables['time']
    the_times=time_nc[...]
    the_dates=num2date(the_times,time_nc.units,time_nc.calendar)
    #
    # netCDF4 bug(?) means that netcdftime objects can't be compared/sorted
    # so convert to python datetime objects
    #
    py_dates=[dt.datetime(*item.timetuple()[:6]) for item in the_dates]
    py_dates=np.array(py_dates)
    #
    # 
    #
    if start_date is None:
        start_index=0
    else:
        start_index=find_index(py_dates,start_date)[0]
    if stop_date is not None:
        stop_index=find_index(py_dates,stop_date)[0]

    time_slice=slice(start_index,stop_index)
    the_times=py_dates[time_slice]
    var_array=var_nc[time_slice,lat_slice,lon_slice]
    return data_nc,var_nc,the_times,the_lats,the_lons,var_array

def make_plot(the_lons,the_lats,the_var,fignum=1,vmin=290,vmax=305):
    """

    Make a minimal pcolormexh plot of a [lat,lon] field centered in the tropical
    warm pool.  Return the figure, axis, and basemap for additional
    plotting
    
Parameters
----------

    the_lons: 1d ndarray -- vector of longitudes
    the_lats: 1d ndarray -- vector of lattitudes
    the_var:  2d ndarray of shape [len(the_lons),len(the_lats)] -- field to plot
    vmin: scalar (optional) -- minimum value on colorbar
    vmax: scalar (option)  -- maximum value on colorbar

    Returns
    -------

        fig:  figure object
        ax:   axis object
        map:  Basemap object

    Example
    -------

        fig,ax,map=make_plot(the_lons,the_lats,sst_avg,vmin=301,vmax=303.5)

    """
 
    fig=plt.figure(fignum)
    fig.clf()
    ax1=fig.add_subplot(111)
    cmap=cm.RdBu_r
    cmap.set_over('yellow')
    cmap.set_under('black')
    cmap.set_bad('violet') #set missing pixels to cyan
    the_norm=Normalize(vmin=vmin,vmax=vmax,clip=False)

    params=dict(projection='merc',
                llcrnrlon=80,llcrnrlat=-15.,urcrnrlon=170,urcrnrlat=20.,
                resolution='c',lat_0=0,lon_0=120.,lat_ts=0.)
    #
    #
    #
    m = Basemap(**params)
    #
    # transform to page coordinates
    #
    x, y = m(*np.meshgrid(the_lons, the_lats))
    im=m.pcolormesh(x,y,the_var,cmap=cmap,norm=the_norm,ax=ax1)
    cb=m.colorbar(im,extend='both',location='bottom')
    ticks=np.arange(vmin,vmax,2.)
    cb.set_ticks(ticks)
    cb.set_ticklabels(ticks)
    cb.update_ticks()
    #
    # draw a box around the warm pool with coordinates
    # defined in constants.py
    #
    m.drawcoastlines()
    # draw parallels and meridians.
    m.drawparallels(np.arange(-35.,35.,10.))
    m.drawmeridians(np.arange(80.,280.,10.))
    #fig.tight_layout()
    return fig,ax1,m

if __name__=="__main__":
    #
    # plot 5 year average warm pool ssts
    # ftp://podaac-ftp.jpl.nasa.gov/allData/amsre/L3/sst_1deg_1mo/tos_AMSRE_L3_v7_200206-201012.nc
    # described by http://podaac.jpl.nasa.gov/datasetlist?ids=Sensor:GridSpatialResolution&values=AMSR-E:1.0
    from constants import warm_pool as wp
    
    in_file='tos_AMSRE_L3_v7_200206-201012.nc'
    options=dict(corners=wp,start_date=dt.datetime(2003,4,1),stop_date=dt.datetime(2006,3,1))
    data_nc,var_nc,the_times,the_lats,the_lons,sst=get_var_2D(in_file,'tos',**options)
    sst_avg=sst.mean(axis=0)
    fig,ax,map=make_plot(the_lons,the_lats,sst_avg,vmin=301,vmax=303.5)
    start_string=the_times[0].strftime("%Y-%b-%d")
    stop_string=the_times[-1].strftime("%Y-%b-%d")
    ax.set_title('Mean AMSR-E tropical surface temps (K) %s to %s' % (start_string,stop_string))
    fig.canvas.draw()
    outfile='sst_pacific.png'
    fig.savefig(outfile)
    #
    # now plot the timeseries
    #
    sst_time=sst.mean(axis=1) #lat average
    sst_time=sst_time.mean(axis=1) #lon_average
    fig=plt.figure(2)
    fig.clf()
    ax1=fig.add_subplot(111)
    ax1.plot(the_times,sst_time)
    ax1.set_title('AMSR-E Warm Poool SST (K):  %s to %s' % (start_string,stop_string))
    labels = ax1.get_xticklabels()
    [item.set_rotation(30) for item in labels]
    fig.tight_layout()
    fig.canvas.draw()
    fig.savefig('sst_average.png')

    plt.show()
 
 

