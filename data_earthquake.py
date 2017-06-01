import os
import numpy as np
import datetime
from obspy.clients.fdsn import Client

PATH_DATA = "data/earthquakes"



class Earthquake():
    
    def __init__(self, 
                 loc, 
                 t_beg = None, 
                 t_end = None,
                 area_size = 1., 
                 min_magnitude = 1.,
                 path = PATH_DATA):
        """
        The Earthquake class downloads / loads / processes eathquake data 
        
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
    
        # get data
        self._data  = self._get_events()
        self.dates = self._data["date"]
        self.mags  = self._data["mag"]
        
        # restrict to given time period 
        if (self._t_beg is not None) and (self._t_end is not None):
            self._restrict_to_time_period()
            
        print "loaded {} events".format(len(self.dates))
    
    def _download_events(self):
        """
        get erthquake events around a specific location
        """

        print "download events ..."
        
        # init client
        client = Client("IRIS")

        # load data
        events = client.get_events(minmagnitude = self._min_magnitude, 
                                   minlongitude = self._loc[1] - self._area_size, 
                                   maxlongitude = self._loc[1] + self._area_size,
                                   minlatitude  = self._loc[0] - self._area_size,
                                   maxlatitude  = self._loc[0] + self._area_size)

        # transform to time-sequence
        date_list = []
        mag_list  = []
        for event in events:
            
            # get magnitude of event
            mag_list.append(event.magnitudes[0].mag)
            
            # get date of event
            t = event.origins[0].time
            date = (t.year, t.month, t.day)
            date_list.append(date)
        
        return date_list, mag_list
    
    
    def _save_events(self, date, mag):
        """
        save data on pc
        """
        
        print "save events '{}' ...".format(self._fname)
        
        data = {"date" : date,
                "mag"  : mag}
        
        np.save(self._fname, data)
        
        return data
        
        
    def _load_events(self):
        """
        load data from pc
        """
        
        print "load events '{}' ...".format(self._fname)
        
        data = np.load(self._fname)
        return data[()]
    
    
    def _get_events(self):
        """
        if data already exist: load data from pc
        if data does not exist: download data
        """
        
        # get data
        data = None
        if os.path.isfile(self._fname):
            # load data from pc
            data = self._load_events()
        else:
            # download data
            date_list, mag_list = self._download_events()
            data = self._save_events(date_list, mag_list)
        self._data = data
        
        return data
        
        
    def _restrict_to_time_period(self):
        """
        remove all data from dates outside the period of interest
        """
        
        dates_new = []
        mags_new = []
        
        for mag, date in zip(self.mags, self.dates):
            
            d0 = datetime.date(*self._t_beg)
            d1 = datetime.date(*date)
            d2 = datetime.date(*self._t_end)
            
            if d0 <= d1 <= d2:
                
                dates_new.append(date)
                mags_new.append(mag)
        
        self.mags = mags_new
        self.dates = dates_new
        
    def _occurrence_frequency_vector(self):
        """
        convert Data from events in vector wich only contains the occurrence_frequency
        """
        
        d_beg = datetime.date(*self._t_beg)
        d_end = datetime.date(*self._t_end)
        n_days = (d_end - d_beg).days

        freq_vec = np.zeros(n_days)

        for d in self.dates:
            idx = (d_end - datetime.date(*d)).days
            freq_vec[idx] += 1
            
        return freq_vec
    
    def get_frequency_nearest(self):
        """
        get the earthquake-occurence-frequency-timeline
        freq(t) = 1 / (DELTA_t + 1)
        where DELTA_t is the time to the last earthquake event
        """
        # self.dates...
        
        return dates, freq
    
    
    def get_mean_frequency(self, time_interval = 5):
        """
        get the earthquake-occurence-frequency-timeline
        freq(t) = number_of_earthquakes(t-T/2 < t < t+T/2)
        where T is the time interval in days
        """
        # self.dates...
        
        
        freq_vec = self._occurrence_frequency_vector()
        freq = np.convolve(freq_vec, np.ones((time_interval,))/time_interval)
        
        
        dates_temporarily = self.dates
        dates = dates_temporarily[time_interval/2-1:-time_interval/2]
        

        
        return dates, freq
        