""" Fluorescence analysis.
twopTools/utils/fluor.py

Analyze fluorescence and perform spike inference.

Functions
---------
calc_F0
    Calculate baseline fluorescence for a cell.
calc_dFF
    Calculate dF/F for a recording.
spike_inference
    Perform spike inference using OASIS.


Written by DMM, March 2023
"""


import numpy as np
import oasis


def calc_F0(F):
    """ Calculate baseline fluorescence for a cell.

    Parameters
    ----------
    F : array
        Fluorescence signal for an individual cell,
        with the shape (nFrames).

    Returns
    -------
    F0 : float
        Baseline fluorescence value.
    
    """

    _hist, _bins = np.histogram(F, bins=200)
    _bins = _bins + (np.median(np.diff(_bins))/2)

    _F0 = _bins[np.nanargmax(_hist)]

    return _F0


def calc_dFF(F, Fneu, F0, inds=None, r=0.7):
    """ Calculate dF/F for a recording.

    Parameters
    ----------
    F : array
        Fluorescence signal, with shape (nCells, nFrames).
    Fneu : array
        Neuropil signal, with shape (nCells, nFrames).
    F0 : array
        Baseline fluorescence values, with shape (nCells).
    inds : array (optional)
        Indices of cells to analyze. If None, all cells
        are analyzed.
    r : float (optional)
        Neuropil correction factor. Unique to gcamp type(?).

    Returns
    -------
    normF : array
        Neuropil-corrected fluorescence signal, with shape
        (nCells, nFrames).
    rawDFF : array
        Raw dF/F signal, where neuropil correction was
        not applied. Shape is (nCells, nFrames).
    DFF : array
        Neuropil-corrected dF/F signal, with shape
        (nCells, nFrames).

    """

    # If a subset of cells was not given, analyze all
    # cells.
    if inds is None:
        inds = np.arange(np.size(F,0))

    lenT = np.size(F,1)
    nCells = len(inds)
    
    # Initialize arrays.
    normF = np.zeros([nCells, lenT])
    rawDFF = np.zeros([nCells, lenT])
    DFF = np.zeros([nCells, lenT])

    for ni, n in enumerate(inds):

        # Calculate dF/F
        _rawF = F[n,:].copy()
        _rawFneu = Fneu[n,:].copy()
        _F0 = F0[n]

        # Raw DF/F
        rawDFF[ni,:] = (_rawF - _F0) / _F0 * 100 

        # Subtract neuropil
        _normF = _rawF - r * _rawFneu + r * np.nanmean(_rawFneu)

        # dF/F with neuropil correction
        DFF[ni,:] = (_normF - _F0) / _F0 * 100
        normF[ni,:] = _normF

    return normF, rawDFF, DFF


def spike_inference(DFF):
    """ Perform spike inference using OASIS.

    Parameters
    ----------
    DFF : array
        Neuropil-corrected dF/F signal, with shape
        (nCells, nFrames).
    
    Returns
    -------
    fluor_sig : array
        Denoised fluorescence signal, with shape
        (nCells, nFrames).
    spikes : array
        Deconvolved spiking activity, with shape
        (nCells, nFrames). Values will be a spike
        count per bin, not a spike rate.
    
    """

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


