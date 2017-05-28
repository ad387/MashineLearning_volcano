import os
import numpy as np
import wget
import h5py
import urllib2
import datetime
from tqdm import tqdm

DATA_PATH     = "data/SO2_satelite"
URL           = "https://avdc.gsfc.nasa.gov/pub/data/satellite/Suomi_NPP/NMSO2-PCA-L2/"
ARRAY_IDS     = ["SO2_PBL", "SO2_STL", "SO2_TRL", "SO2_TRM", "SO2_TRU"]
BOX_SIZE      = 1.5
INVALID_VAL   = -999.0
DATE_BEG      = (2012, 1, 1)
DATE_END      = (2017, 5, 16)
GRANULE_SHAPE = (400, 36)

def get_download_links(date):

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


def download_files(links):
    
    existing_files = os.listdir(DATA_PATH)
    
    for link in links:
        fname = link.split("/")[-1]
        if fname not in existing_files:
            wget.download(link, DATA_PATH)


def load_arrays(date, array_ids = ARRAY_IDS):
    
    # download h5 files
    links = get_download_links(date)
    download_files(links)
    
    # get arrays for every array id
    arrays = {}
    for array_id in array_ids:
        arrays[array_id] = []
        
        # get different stipes
        for link in links:
            
            # read in array
            try:
                fname = link.split("/")[-1]
                fname = os.path.join(DATA_PATH, fname)
                f = h5py.File(fname, "r")
                arrays[array_id].append(np.array(f['OMPSSO2PCA'][array_id]))
                f.close()
                
            except:
                # print "error with file {}".format(fname)
                # print "could not load date {}, array_id {}".format(date, array_id)
                arrays[array_id].append(np.ones(GRANULE_SHAPE) * INVALID_VAL)
    
    return arrays


def get_pos_of_interest(date,
                        pos,
                        box_size = BOX_SIZE,
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
    
    lat_extend = (pos[0] - box_size, pos[0] + box_size)
    lon_extend = (pos[1] - box_size, pos[1] + box_size)
    
    array_ids_ext = ["Latitude", "Longitude"] + array_ids
    arrays = load_arrays(date, array_ids = array_ids_ext)
    
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
        

def get_time_sequence(pos,
                      box_size = BOX_SIZE,
                      date_beg  = DATE_BEG, 
                      date_end  = DATE_END,
                      array_ids = ARRAY_IDS,
                      mode      = "sum"):
    """
    get time sequence of values around position of interest
    
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
    
    date_beg = datetime.date(*date_beg)
    date_end   = datetime.date(*date_end)
    time_delta = (date_end - date_beg).days
    
    time_sequence = {key: value for (key, value) in zip(array_ids, [[]] * len(array_ids))}
    dates = []
    
    for t in tqdm(range(time_delta)):
        
        date = date_beg + datetime.timedelta(t)
        dates.append(date)
        date = (date.year, date.month, date.day)
        
        vals = get_pos_of_interest(date,
                                   pos,
                                   box_size = BOX_SIZE,
                                   array_ids = ARRAY_IDS,
                                   mode = mode)
        
        for array_id in array_ids:
            v = vals[array_id]
            time_sequence[array_id] = time_sequence[array_id] + [v]

    return time_sequence, dates
    
    
    
    
    