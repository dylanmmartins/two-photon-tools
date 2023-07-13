
import os
import h5py
import numpy as np
import PySimpleGUI as sg

import twopTools as tpt

def preenCells(s2p_path, thresh_vals=None):

    path_last_dir = os.path.split(s2p_path)[1]
    if ('TSeries' in s2p_path) and (path_last_dir != 'plane0'):
        s2p_path = os.path.join(s2p_path, 'suite2p/plane0')

    # load data
    F = np.load(os.path.join(s2p_path,'F.npy'))
    Fneu = np.load(os.path.join(s2p_path,'Fneu.npy'))
    iscell = np.load(os.path.join(s2p_path,'iscell.npy'))
    ops = np.load(os.path.join(s2p_path,'ops.npy'),allow_pickle=True).item()
    stat = np.load(os.path.join(s2p_path,'stat.npy'),allow_pickle=True)

    # cell indices
    inds = np.arange(np.size(iscell,0))

    # Calculate F0 and signal to noise ratio over time
    F0 = np.zeros(len(inds))*np.nan
    SignalToNoise = np.zeros(np.shape(F))*np.nan

    for n in inds:

        _F0 = tpt.calc_F0(F[n,:].copy())

        F0[n] = _F0

        SignalToNoise[n,:] = F[n,:].copy() / _F0

    # some cell properties
    props = {
        'prob': np.zeros(len(inds))*np.nan,
        'rad': np.zeros(len(inds))*np.nan,
        'aspect': np.zeros(len(inds))*np.nan,
        'cmpt': np.zeros(len(inds))*np.nan,
        'std': np.zeros(len(inds))*np.nan,
        'ovrlap': np.zeros(len(inds))*np.nan,
        'meanSNR': np.zeros(len(inds))*np.nan,
        'F0': np.zeros(len(inds))*np.nan
    }
    for n in inds:

        # add props to te dictionary
        props['prob'][n] = iscell[n][1]
        props['rad'][n] = stat[n]['radius']
        props['aspect'][n] = stat[n]['aspect_ratio']
        props['cmpt'][n] = (1/stat[n]['compact'])*100
        props['std'][n] = stat[n]['std']
        props['ovrlap'][n] = np.sum(stat[n]['overlap']) / len(stat[n]['overlap'])
        props['meanSNR'][n] = np.nanmean(SignalToNoise[n,:])
        props['F0'][n] = F0[n]

    if thresh_vals is None:
        # sets which cells should be excluded
        thresh_vals = {
            'prob': '{} < 0.75',
            'meanSNR': '{} < 1.0',
            'aspect': '{} > 1.2',
            'cmpt': '{} < 95.',
            'std': '{} > 100.'
        }

    # bool array of good cells (according to suite2p)
    threshcells = (iscell[:,0]==1).astype(bool)

    for k,evlstm in thresh_vals.items():

        _kbool = np.zeros(len(inds), dtype=bool)
        for n in inds:
            _testval = props[k][n]
            if not np.isnan(_testval):
                if np.isfinite(_testval):
                    _kbool[n] = eval(evlstm.format(_testval))
            else:
                _kbool[n] = False

        threshcells[_kbool.astype(bool)] = False

    # firing rate cannot be zero
    fr0_inds = np.argwhere(np.sum(F, axis=1)==0).T[0]
    threshcells[fr0_inds] = False

    # cells that still pass thresholds (indices)
    useinds = inds[threshcells]

    print('{}/{} cells are still included ({:.3}%)'.format(
        np.sum(threshcells),
        len(threshcells),
        np.sum(threshcells)/len(threshcells)*100))
    
    # calculate dF/F
    normF, rawDFF, DFF = tpt.calc_dFF(F.copy(),
                                     Fneu.copy(),
                                     F0,
                                     inds=useinds)
    
    # spike inference
    fluor, spikes = tpt.spike_inference(DFF)

    # get ready to save data...

    # save dict
    goodcells = {
        's2p_indices': useinds,
        'F0': F0[useinds],
        'prob': props['prob'][useinds],
        'rad': props['rad'][useinds],
        'aspect': props['aspect'][useinds],
        'cmpt': props['cmpt'][useinds],
        'std': props['std'][useinds],
        'ovrlap': props['ovrlap'][useinds],
        'meanSNR': props['meanSNR'][useinds],
        'tau': ops['tau'],
        'recording_Hz': 1/ops['fs'],
        'nframes': ops['nframes'],
        'mean_image': ops['meanImg'],
        'ref_image': ops['refImg'],
        'max_proj': ops['max_proj'],
        'image_xrange': ops['xrange'],
        'image_yrange': ops['yrange'],
        'image_xpix': ops['Lx'],
        'image_ypix': ops['Ly'],

        'F': F[useinds,:],
        'Fneu': Fneu[useinds,:],
        
        'SignalToNoise': SignalToNoise[useinds,:],
        
        'normF': normF,
        'raw_dFF': rawDFF,
        'dFF': DFF,

        'spikes': spikes,
        'denoise_fluor': fluor #,

        # 'cell_mask_xyf': xyl
    }

    for k,v in thresh_vals.items():
        goodcells[k+'_thresh'] = v

    # goodcells['cellmasks'] = {}
    masks = {}
    for ni, n in enumerate(useinds):
        masks['masks_'+str(ni)+'_x'] = stat[n]['xpix'].astype(float)
        masks['masks_'+str(ni)+'_y'] = stat[n]['ypix'].astype(float)
        masks['masks_'+str(ni)+'_fluor'] = stat[n]['lam'].astype(float)

    # save to json
    savepath = os.path.join(s2p_path, 'goodcells.h5')
    
    # save the file as one hdf5 key
    with h5py.File(savepath, 'w') as f:
        for k,v in goodcells.items():
            try:
                f.create_dataset(k, data=v)
            except TypeError:
                print('Could not save {}'.format(k))
        for k,v in masks.items():
            try:
                f.create_dataset(k, data=v)
            except TypeError:
                print('Could not save {}'.format(k))

if __name__ == '__main__':

    # get paths to suite2p output directories

    path_list = tpt.choose_dirs()

    path_list = [p for p in path_list if p!='']

    for p in path_list:
        for sp in tpt.list_subdirs(p):
            if (len(sp)==3) and (sp[0]=='R'):
                os.path.join(p, sp, 'TwoPhotonTimeSeries')



    for i, path in enumerate(path_list):

        print('  ->  Processing recording {}/{} (path={})'.format(
            i+1, len(path_list), path))

        preenCells(path)
    