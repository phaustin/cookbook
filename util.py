from __future__ import division
import collections
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt

def copy_attrs(varin,varout):
    """copy attributes from ncvar
    """
    for attr_name in varin.ncattrs():
        varout.setncattr(attr_name,varin.getncattr(attr_name))

def find_index_sorted(vec_vals,target,ascend=True):
    """
       given a sorted list of values, find the first index 
       greater than or equal to the target     
       example:  find_index_sorted(lats,120.)
          will return the first index in the lats vector >= 120
    """
    target=np.array(target)  #turn list or scalar in to numpy vector
    index_list=[]
    for item in target:
        if ascend:
            hit=vec_vals >= item
        else:
            hit=vec_vals <= item
        first_index=np.where(hit)[0][0]
        index_list.append(first_index)
    return index_list

        
def find_index_unsorted(vec_vals,target,tol=1.):
    """
      usage: lat_slice=find_index(lats,[lowlat,highlat])
    
      given a 1-D numpy array vec_vals, find the
      index that is within tol of target

      If vec_vals is sorted in ascending order, use
      find_index_sorted
    """
    target=np.array(target) #make sure it's iterable
    index_list=[]
    for item in target:
        hit=(np.abs(vec_vals - item) < tol)
        index_vals=np.where(hit)[0]
        if len(index_vals) > 2:
            raise Exception('trouble in find_index, found > 2 vals')
        elif len(index_vals) == 0:
            raise Exception('trouble in find_index, no hits')
        else:
            index_vals=index_vals[0]
        index_list.append(index_vals)
    return index_list

def box_average_from_files(nc_var,nc_area,var_name,press_lev,month_slice,lat_slice,lon_slice):
    """
        usage: wap_850_avg=box_average(nc_omega,nc_area,var_name,press_lev,month_slice,lat_slice,lon_slice)

        input:
        
        nc_var is a 4D netCDF4 dataset [time,pressure,lat,lon]
        nc_area is a an areacella_fx_CanESM2_esmControl_r0i0p0.nc Dataset
        var_name is the variable name (i.e. 'hur')
        month_slice, lat_slice, lon_slice are python slice objects with the low,high indices for the slice

        return:

        area-weighted average value of the field over the lat/lon box
        
    """
    plevs=nc_var.variables['plev'][...]
    areas=nc_area.variables['areacella'][lat_slice,lon_slice]
    press_index=find_index(plevs,press_lev,tol=5)[0]
    the_field=nc_var.variables[var_name][month_slice,press_index,lat_slice,lon_slice].squeeze()
    the_field=the_field*areas
    the_field=np.sum(the_field,axis=1)
    the_field=np.sum(the_field,axis=1)
    total_area=np.sum(areas.flat)
    the_field_avg=the_field/total_area
    return the_field_avg

def box_average_from_fields(the_field,the_areas):
    """
        usage: wap_850_avg=box_average_from_fields(wap_850,the_areas)

        input:
        
        the_field is a 3-d  [time,lat,lon] field to be averaged
        the_areas is  the 2-d [lat,lon] set of cell areas

        return:

        area-weighted average value of the field over the lat/lon box
        
    """
    the_field=the_field*the_areas
    the_field=np.sum(the_field,axis=1)
    the_field=np.sum(the_field,axis=1)
    total_area=np.sum(the_areas.flat)
    the_field_avg=the_field/total_area
    return the_field_avg

def calc_press(nc_data,lat_slice,lon_slice,can=False):
    ap=nc_data.variables['ap'][:]
    if can:
        ap=ap/100.
    b=nc_data.variables['b'][:]
    ps=nc_data.variables['ps'][:,lat_slice,lon_slice] #get all times
    ps=np.mean(ps.ravel())  #average all times an locations
    return ap + b*ps

def seasonal_avg(var_nc,the_season,lat_slice=None,lon_slice=None):
    """given a 4-d [time,plev,lat,lon] nc_var
       and a list of months staring with jan=0 (e.g. mam=[2,3,4],jja=[5,6,7], etc.
       and a masked array accumulate to hold intermediate slices,
       calculate the lat/lon/time average

       To average DJF use winter_average()
    """ 
    the_season=np.array(the_season,dtype=np.int32)
    if (lat_slice is None) and (lon_slice is None):
        num_lats=var_nc.shape[2]
        num_lons=var_nc.shape[3]
        lat_slice=slice(0,num_lats)
        lon_slice=slice(0,num_lons)
    else:
        if lat_slice.stop is None:
            num_lats=var_nc.shape[2]
        else:
            num_lats=lat_slice.stop - lat_slice.start
        if lon_slice.stop is None:
            num_lons=var_nc.shape[3]
        else:
            num_lons=lon_slice.stop - lon_slice.start
    num_levs=var_nc.shape[1]
    accumulate=ma.zeros([num_levs,num_lats,num_lons],dtype=var_nc.dtype)
    num_years=var_nc.shape[0]//12

    for the_year in np.arange(0,num_years):
        the_slice=var_nc[the_season,:,lat_slice,lon_slice]
        the_slice=ma.mean(the_slice,axis=0)
        accumulate+=the_slice
        the_season=the_season+12
    accumulate=accumulate/num_years    
    the_avg=ma.mean(accumulate,axis=1)
    the_avg=ma.mean(the_avg,axis=1)
    return the_avg

def winter_avg(var_nc,lat_slice=None,lon_slice=None):
    """given a 4-d [time,plev,lat,lon] nc_var
       calculate the lat/lon/time average
       for the special case of dec,jan,feb,
       which crosses calendar year
    """ 
    #
    # accumulate in shape [plev,lat,lon]
    #
    # use the whole array if slice objects are missing
    #
    if (lat_slice is None) and (lon_slice is None):
        num_lats=var_nc.shape[2]
        num_lons=var_nc.shape[3]
        lat_slice=slice(0,num_lats)
        lon_slice=slice(0,num_lons)
        print "in winter avg: ",lat_slice,lon_slice
    else:
        num_lats=lat_slice.stop - lat_slice.start
        num_lons=lon_slice.stop - lon_slice.start
    num_levs=var_nc.shape[1]
    accumulate=ma.zeros([num_levs,num_lats,num_lons],dtype=var_nc.dtype)
    #
    # year 0 is special case since it doesn't have a december
    #
    djf0=np.array([0,1],dtype=np.int32)  #january and feburary
    the_slice=var_nc[djf0,:,lat_slice,lon_slice]
    the_slice=ma.mean(the_slice,axis=0)  #average over the two months
    accumulate+=the_slice
    num_years=var_nc.shape[0]//12
    #
    # now year 1 has year 0's december
    #
    djf=np.array([11,12,13],dtype=np.int32)
    #
    # iterate one year less because we've alread
    # done year zero as a special case
    #
    for the_year in np.arange(0,num_years-1):
        the_slice=var_nc[djf,:,lat_slice,lon_slice]
        the_slice=ma.mean(the_slice,axis=0)
        accumulate+=the_slice
        djf=djf+12
    accumulate=accumulate/num_years    
    the_avg=ma.mean(accumulate,axis=1)
    the_avg=ma.mean(the_avg,axis=1)
    return the_avg

def make_lat_lon_slice(nc_file,corners=None):
    """
       given a netcdf Dataset with lat and lon
       variables and a named tuple generated
       by my_named_tuple (see constants.py), return
       lat lon slice objects and lat lon vectors

       
    """
    lat_nc=nc_file.variables['lat']
    lon_nc=nc_file.variables['lon']
    full_lats=lat_nc[...]
    full_lons=lon_nc[...]
    if corners is None:
        lat_slice=[0,lat_nc.shape[0]]
        lon_slice=[0,lon_nc.shape[0]]
    else:
        lat_slice=find_index_sorted(full_lats,[corners.ll.lat,corners.ur.lat])
        lat_slice[1]+=1
        lon_slice=find_index_sorted(full_lons,[corners.ll.lon,corners.ur.lon])
        lon_slice[1]+=1
    lat_slice=slice(*lat_slice)
    lon_slice=slice(*lon_slice)

    the_lats=full_lats[lat_slice]
    the_lons=full_lons[lon_slice]
    return (lat_slice,lon_slice,the_lats,the_lons)

def drawit(fignum=1,xlabel=" ",ylabel=" ",xvar=None,
           yvar=None,title=" ",ylimit=None,
           xlimit=None):
    """
       construct a figure with single line and return
       the figure,axis and line objects
       example: fig,ax,line=drawit(**drawopts)
    """
    fig=plt.figure(fignum)
    fig.clf()
    ax1=fig.add_subplot(111)
    line=ax1.plot(xvar,yvar)
    ax1.set_xlim(xlimit)
    ax1.set_ylim(ylimit)
    ax1.set_title(title)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    fig.tight_layout()
    fig.canvas.draw()
    return fig,ax1,line[0]

#http://stackoverflow.com/questions/1606436/adding-docstrings-to-namedtuples-in-python
from collections import namedtuple

def my_namedtuple(typename, field_names, verbose=False,
                 rename=False, docstring=''):
    '''Returns a new subclass of namedtuple with the supplied
       docstring appended to the default one.

    >>> Point = my_namedtuple('Point', 'x, y', docstring='A point in 2D space')
    >>> print Point.__doc__
    Point(x, y):  A point in 2D space
    '''
    # create a base class and concatenate its docstring and the one passed
    _base = namedtuple(typename, field_names, verbose, rename)
    _docstring = ''.join([_base.__doc__, ':  ', docstring])

    # fill in template to create a no-op subclass with the combined docstring
    template = '''class subclass(_base):
        %(_docstring)r
        pass\n''' % locals()

    # execute code string in a temporary namespace
    namespace = dict(_base=_base, _docstring=_docstring)
    try:
        exec template in namespace
    except SyntaxError, e:
        raise SyntaxError(e.message + ':\n' + template)

    return namespace['subclass']  # subclass object created
    

    
