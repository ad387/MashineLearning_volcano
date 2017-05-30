
PATH_DATA = "data/SO2_satelite"
ARRAY_IDS     = ["SO2_PBL", "SO2_STL", "SO2_TRL", "SO2_TRM", "SO2_TRU"]
BOX_SIZE      = 1.5


class SO2_Sat():
    
    def __init__(self, 
                 loc, 
                 t_beg = None, 
                 t_end = None,
                 area_size = 1., 
                 min_magnitude = 1.,
                 path = PATH_DATA):
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
        min_magnitude : float
            min magnitude of earthquake to be loaded
        path : string
            path where downloaded data is saved in / loaded from
        """
        
        # set class variables
        self._loc           = loc
        self._t_beg         = t_beg
        self._t_end         = t_end
        self._area_size     = area_size
        self._min_magnitude = min_magnitude
        self._path          = path
        
        # get fname of data file
        fname = str(loc) + "_" + str(area_size) + "_" + str(min_magnitude) + ".npy"
        self._fname = os.path.join(path, fname)
        

        
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


    def _download_files(self, links):

        existing_files = os.listdir(DATA_PATH)

        for link in links:
            fname = link.split("/")[-1]
            if fname not in existing_files:
                wget.download(link, DATA_PATH)


    def _load_arrays(self, date, array_ids = ARRAY_IDS):

        # download h5 files
        links = self._get_download_links(date)
        self._download_files(links)

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

    
    def _get_so2_for_pos_from_sat_img(self,
                                      date,
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
        arrays = self._load_arrays(date, array_ids = array_ids_ext)

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

    
    def _get_so2_for_pos(self):
        
        if os.path.isfile(self._fname):
            # load so2
        else:
            # get so2 from map
    
    
        
    
    
    
    