
import numpy as np
import oasis

def calc_F0(F):
    _hist, _bins = np.histogram(F, bins=200)
    _F0 = _bins[np.nanargmax(_hist)]
    return _F0


def calc_dFF(F, Fneu, F0, inds=None, r=0.7):

    if inds is None:
        inds = np.arange(np.size(F,0))

    lenT = np.size(F,1)
    nCells = len(inds)
    
    normF = np.zeros([nCells, lenT])
    rawDFF = np.zeros([nCells, lenT])
    DFF = np.zeros([nCells, lenT])

    for ni, n in enumerate(inds):

        # calculate dF/F
        _rawF = F[n,:].copy()
        _rawFneu = Fneu[n,:].copy()
        _F0 = F0[n]

        # raw DF/F
        rawDFF[ni,:] = (_rawF - _F0) / _F0 * 100 

        # subtract neuropil
        _normF = _rawF - r * _rawFneu + r * np.nanmean(_rawFneu)

        DFF[ni,:] = (_normF - _F0) / _F0 * 100
        normF[ni,:] = _normF

    return normF, rawDFF, DFF


def spike_inference(DFF):

    inds = np.arange(np.size(DFF,0))

    lenT = np.size(DFF,1)
    nCells = len(inds)

    # denoised fluorescence signal
    fluor_sig = np.zeros([nCells, lenT])*np.nan
    # deconvolved spiking activity
    spikes = np.zeros([nCells, lenT])*np.nan

    for n in inds:

        _dff = DFF[n,:].copy()

        g = oasis.functions.estimate_time_constant(_dff, 1)

        _fluor_sig, _spikes = oasis.oasisAR1(_dff, g)

        spikes[n,:] = _spikes
        fluor_sig[n,:] = _fluor_sig

    return fluor_sig, spikes
