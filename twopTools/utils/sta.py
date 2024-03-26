
import numpy as np
import matplotlib.pyplot as plt


def calc_spike_triggered_avg(spikes, stimvid, lags='zero', variance=False):
    """ Calculate the spike-triggered average from 2P data.

    Parameters
    ----------
    spikes : np.ndarray
        A 1D array of binary spike events.
    stimvid : np.ndarray
        A 3D array of the stimulus video.
    lags : str
        How many lags to calculate the STA over. Options are
        'zero' for doing no lag adjustements (default), or
        'range' for calculating the STA over a range of lags,
        which uses the range -4 to 4. The indexing is shifted by
        microscope frames (so 10 Hz).
    variance : bool
        Default is False. When set to True, instead of calculating the
        spike triggered average, the spike triggered variance is calculated.
    """

    if variance is True:
        mean_sq_img_norm = np.mean(stimvid**2, axis=0)
        
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

            if variance is False:
                sta = sta - np.mean(sta)
            elif variance is True:
                sta = sta - mean_sq_img_norm

            all_sta[c,l,:,:] = sta

    return all_sta