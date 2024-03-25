
import numpy as np
import matplotlib.pyplot as plt


def calc_sta(spikes, stimvid, lags='zero'):
        
    if lags == 'zero':
        lags = [0]
    if lags == 'range':
        lags = np.arange(-4,5,1)
    
    ncells = np.size(spikes, 0)
    
    nks = np.size(stimvid, 0)

    all_sta = np.zeros([
        ncells,
        len(lags),
        np.size(stimvid, 1),
        np.size(stimvid, 2)
    ])

    for l, lag in enumerate(lags):
        for c in range(ncells):

            sp = spikes[c,:].copy()

            sp = np.roll(sp, -lag)
            sta = stimvid.T @ sp
            sta = np.reshape(sta, nks)
            nsp = np.sum(sp)

            sta = sta / nsp
            sta = sta - np.mean(sta)

            all_sta[c,l,:,:] = sta

    return all_sta