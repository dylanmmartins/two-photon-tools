""" Make overlay map from widefield sign map.
twopTools/wfMap.py


Written by DMM, Nov 2023
"""


import os
import PySimpleGUI as sg
from scipy.io import loadmat
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

sg.theme('Default1')


def main():

    # get basepath
    base = sg.popup_get_folder('Choose base directory',
                        no_window=True,
                        initial_folder='T:/')
    
    v_path = sg.popup_get_file('Select VFX .mat file',
                      file_types=(('.mat','.mat'),),
                      no_window=True, initial_folder=base)
    
    i_path = sg.popup_get_file('Select tiff reference image.',
                               file_types=(('.tif','.tif'),),
                                no_window=True, initial_folder=base)

    # get savepath
    savepath = sg.popup_get_folder('Choose save directory',
                        no_window=True,
                        initial_folder=base)
    
    name = sg.popup_get_text('Enter animal name.')
    
    matfile = loadmat(v_path)

    im = Image.open(i_path)
    img = np.array(im)

    smlimg = zoom(img, 400/2048)
    smlimg = smlimg.astype(float)
    smlimg = 1-(smlimg-np.min(smlimg))/65535

    overlay = matfile['VFS_raw'].copy()

    t2b = np.zeros([256, 4])
    t2b[:,3] = np.linspace(0, 1, 256)
    t2b = ListedColormap(t2b)

    plt.figure(figsize=(5,5),dpi=300)
    plt.imshow(smlimg, cmap=t2b)
    plt.axis('off')
    plt.set_title(name)
    plt.savefig(os.path.join(savepath, '{}_ref_img.png'.format(name)), dpi=300)

    plt.figure(figsize=(5,5),dpi=300)
    plt.imshow(gaussian_filter(overlay,2), cmap='jet')
    plt.imshow(smlimg, cmap=t2b)
    plt.axis('off')
    plt.set_title(name)
    plt.savefig(os.path.join(savepath, '{}_overlay.png'.format(name)), dpi=300)


if __name__=='__main__':
    
    main()