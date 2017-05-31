
import os
import numpy as np
import wget
import h5py
import urllib2
import datetime
from tqdm import tqdm

PATH_DATA_IMG = "data/SO2_satelite"
PATH_DATA_PTS = "data/SO2_sat_point"
URL           = "https://avdc.gsfc.nasa.gov/pub/data/satellite/Suomi_NPP/NMSO2-PCA-L2/"
ARRAY_IDS     = ["SO2_PBL", "SO2_STL", "SO2_TRL", "SO2_TRM", "SO2_TRU"]
INVALID_VAL   = -999.0
DATE_BEG      = (2012, 1, 1)
DATE_END      = (2017, 5, 16)
GRANULE_SHAPE = (400, 36)


class SO2_Sat():
    
    def __init__(self, 
                 loc, 
                 t_beg = DATE_BEG, 
                 t_end = DATE_END,
                 area_size = 1., 
                 mode = "sum",
                 array_ids = ARRAY_IDS,
                 path_img = PATH_DATA_IMG,
                 path_pts = PATH_DATA_PTS):
        """
        The SO2_Sat class downloads / loads / processes so2-data from the
        nasa satelites
        
        for more information on the data see https://so2.gsfc.nasa.gov/
        
        Parameters
        ----------
        loc : tuple
            location in the format (latitude, longitude)
        t_beg : tuple
            begining date in the format (year, month, day)
            if not specified data from all dates are loaded
        t_end : tuple
            end date in the format (year, month, day)
            if not specified data from all dates are loaded
        area_size : float
            size of the bounding box around the given location (loc)
            in degrees longitude / latitude
        path_img : string
            path where downloaded sat imgs ar saved in / loaded from
        path_pts : string
            path where the point so2 concentration (retrieved from sat imgs) 
            is saved
        """
        
        # set class variables
        self._loc           = loc
        self._t_beg         = t_beg
        self._t_end         = t_end
        self._area_size     = area_size
        self._mode          = mode
        self._array_ids     = array_ids
        self._path_img      = path_img
        
        # get path for so2 values. Make folder if not existant
        loc_path = str(loc) + "_" + \
                   str(area_size) + "_" + \
                   str(mode) + "_" + \
                   str(array_ids)
                
        self._path_pts = os.path.join(path_pts, loc_path)
        if not os.path.isdir(self._path_pts):
            os.mkdir(self._path_pts)
            
        # get the so2 time sequence
        self.dates, self.so2_timeseq = self._get_so2_timeseq()
        
    def _get_download_links(self, date):

        # get url path
        year  = str(date[0])
        month = str(date[1]).zfill(2)
        day   = str(date[2]).zfill(2)

        url = URL + '/' + year  + '/' + month + '/' + day + '/'

        # get files in path
        response = urllib2.urlopen(url)
        page_source = response.read()

        splits = page_source.split('.h5"')

        links = []
        for split in splits:
            file_name = split.split('href="')[-1]
            if len(file_name) == 62:
                link = url + file_name + '.h5'
                links.append(link)

        return links


    def _download_missing_files(self, links, path):

        existing_files = os.listdir(path)

        for link in links:
            fname = link.split("/")[-1]
            if fname not in existing_files:
                wget.download(link, path)


    def _load_arrays(self, date, array_ids, path):

        # download h5 files
        links = self._get_download_links(date)
        self._download_missing_files(links, path)

        # get arrays for every array id
        arrays = {}
        for array_id in array_ids:
            arrays[array_id] = []

            # get different stipes
            for link in links:

                # read in array
                try:
                    fname = link.split("/")[-1]
                    fname = os.path.join(path, fname)
                    f = h5py.File(fname, "r")
                    arrays[array_id].append(np.array(f['OMPSSO2PCA'][array_id]))
                    f.close()

                except:
                    # print "error with file {}".format(fname)
                    # print "could not load date {}, array_id {}".format(date, array_id)
                    arrays[array_id].append(np.ones(GRANULE_SHAPE) * INVALID_VAL)

        return arrays

    
    def _get_so2_for_loc_from_sat_img(self,
                                      date,
                                      loc,
                                      area_size,
                                      path,
                                      array_ids = ARRAY_IDS,
                                      mode = "sum"):
        """
        get values around position of interest

        Parameters
        ----------
        mode : str
            return mode of values.
            'mean' : return mean of values in box
            'max'  : return max of values in box
            'min'  : return min of values in box
            'sum'  : return sum of values in box
            'all'  : return all values in box
        """

        lat_extend = (loc[0] - area_size, loc[0] + area_size)
        lon_extend = (loc[1] - area_size, loc[1] + area_size)

        array_ids_ext = ["Latitude", "Longitude"] + array_ids
        arrays = self._load_arrays(date, array_ids_ext, path)

        # get vals for every array id
        vals = {}
        for array_id in array_ids:

            vals[array_id] = []

            for stripe_idx in range(len(arrays[array_id])):

                lat_binary = (arrays["Latitude"][stripe_idx] > lat_extend[0]) * \
                             (arrays["Latitude"][stripe_idx] < lat_extend[1])
                lon_binary = (arrays["Longitude"][stripe_idx] > lon_extend[0]) * \
                             (arrays["Longitude"][stripe_idx] < lon_extend[1])
                binary = lat_binary * lon_binary

                if binary.sum() > 0:
                    vals[array_id] = vals[array_id] + \
                         arrays[array_id][stripe_idx][np.where(binary)].tolist()

            # delete invalid
            vals[array_id] = np.array(vals[array_id])
            vals[array_id] = np.delete(vals[array_id], 
                                       np.where(vals[array_id] == INVALID_VAL),
                                       axis = 0)

            if mode == "mean":
                vals[array_id] = vals[array_id].mean()
            elif mode == "max":
                vals[array_id] = vals[array_id].max()
            elif mode == "min":
                vals[array_id] = vals[array_id].min()
            elif mode == "sum":
                vals[array_id] = vals[array_id].sum()
            elif mode == "all":
                pass
            else:
                print "unknown mode {}".format(mode)

        return vals

    
    def _get_so2_for_date(self, date):
        
        fname = os.path.join(self._path_pts, str(date) + ".npy")
        
        if os.path.isfile(fname):
            # load so2
            so2_val = np.load(fname)[()]
        else:
            # get so2 from map
            so2_val = self._get_so2_for_loc_from_sat_img(date, 
                                               self._loc, 
                                               self._area_size,
                                               self._path_img,
                                               array_ids = self._array_ids,
                                               mode = self._mode)
            np.save(fname, so2_val)
            
        return so2_val
    
    
    def _get_so2_timeseq(self):
        
        date_beg = datetime.date(*self._t_beg)
        date_end = datetime.date(*self._t_end)
        date = date_beg
        
        so2_timeseq = {key: [] for key in self._array_ids}
        dates = []
        while date <= date_end:
            
            try:
            
                date = date + datetime.timedelta(1)
                t = (date.year, date.month, date.day)

                dates.append(date)
                
                so2_val = self._get_so2_for_date(t)
                for key in self._array_ids:
                    so2_timeseq[key].append(so2_val[key])
                
            except:
                
                print "error with date {}".format(date)
            
        return dates, so2_timeseq
    
    
    
    