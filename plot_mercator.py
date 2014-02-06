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
from slice_nc import find_index, get_var_2D


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
 
 

