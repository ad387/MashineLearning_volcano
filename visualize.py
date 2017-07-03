import os
import matplotlib.pylab as plt
import inspect, re
import numpy as np
import datetime
import matplotlib.gridspec as gridspec  # for unequal plot boxes

#import cv2


def disp(img_list, title_list = None, fname = None):
    """
    display a list of images
    """

    plt.figure()

    for idx, img in enumerate(img_list):

        plt.subplot(1, len(img_list), idx+1)
        if title_list is not None:
            plt.title(title_list[idx])
        plt.imshow(img.astype(np.uint8), vmax = img.max(), vmin = img.min())
        plt.axis("off")
    
    if fname is not None:
        plt.savefig(fname)
        
    plt.show()

def show_earthquake_timeline(dates, mags):
    
    d = [datetime.date(*date) for date in dates]
    m = np.copy(np.array(mags))
    
    plt.figure()
    plt.scatter(d, m)
    plt.xlabel("date")
    plt.ylabel("magnitude")
    plt.show()
    
    
    
def show_so2_sat_timeline(dates, so2):
    
    s = np.copy(np.array(so2))
    d = np.copy(np.array(dates))
    
    # delete invalid
    d = np.delete(dates, np.where(np.isnan(so2)))
    s = np.delete(so2, np.where(np.isnan(so2)))
    
    # plot
    plt.figure()
    plt.plot(d, s, 'o-')
    plt.xlabel("date")
    plt.ylabel("SO2")
    plt.show()
    

def show_so2_eq_freq_timeline(so2_dates, so2, eq_dates, eq):
    plt.figure()
    fig, ax1 = plt.subplots()
    ax1.plot(so2_dates, so2)
    ax1.set_ylim(bottom=0)
    ax2 = ax1.twinx()
    ax2.plot(eq_dates, eq, color = 'r')
    plt.show()
    
    
def plot_Data(X,Y,Label = None, x_name = "x_name",y_name = "y_name" ):
        fig = plt.figure()
        gs = gridspec.GridSpec(1, 1, height_ratios=[3])
        ax2 = fig.add_subplot(gs[0])
        ax2.set_xlabel("x_name")
        ax2.set_ylabel("y_name")
        plt.errorbar(X,Y,linestyle = "None",fmt='o',label= Label)
        cm = plt.cm.get_cmap('RdYlBu')    
        ax2.legend(loc='lower right', shadow=True)


        plt.grid(True) 
        plt.xticks(rotation='horizontal')
        plt.show()
    
    