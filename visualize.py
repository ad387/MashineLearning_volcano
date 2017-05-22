import os
import matplotlib.pylab as plt
import inspect, re
import numpy as np
import cv2


def out(p):
    """
    function prints variable name and value. good for debugging
    """
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
        m = re.search(r'\bout\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
        if m:
            print m.group(1), ":  ", p


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
    
    