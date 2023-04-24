

import os
import json
import numpy as np
import PySimpleGUI as sg

import twopTools as tpt

sg.theme('Default1')

def cellReviewGUI(stat_path):

    s2p_dir = os.path.split(stat_path)[0]

    stat = np.load(stat_path, allow_pickle=True)
    
    ops_path = os.path.join(s2p_dir, 'ops.npy')
    ops = np.load(ops_path, allow_pickle=True)

    F_path = os.path.join(s2p_dir, 'F.npy')
    F = np.load(F_path)

    Fneu_path = os.path.join(s2p_dir, 'Fneu.npy')
    Fneu = np.load(Fneu_path)

    iscell_path = os.path.join(s2p_dir, 'iscell.npy')
    iscell = np.load(iscell_path)

    inds = np.arange(np.size(iscell,0))
    goodcells = inds[iscell[:,0]==1]

    # pivot cell data
    stats = {
        'prob': np.zeros(len(inds))*np.nan,
        'rad': np.zeros(len(inds))*np.nan,
        'aspect': np.zeros(len(inds))*np.nan,
        'cmpt': np.zeros(len(inds))*np.nan,
        'std': np.zeros(len(inds))*np.nan,
        'ovrlap': np.zeros(len(inds))*np.nan,
        'snr': np.zeros(len(inds))*np.nan,
        'auto_label': np.zeros(len(inds))*np.nan,
        'hand_label': np.zeros(len(inds))*np.nan,
        'hand_label_iters': {}
    }
    for n in inds:
        stats['prob'][n] = iscell[n][1]
        stats['rad'][n] = stat[n]['radius']
        stats['aspect'][n] = stat[n]['aspect_ratio']
        stats['cmpt'][n] = (1/stat[n]['compact'])*100
        stats['std'][n] = stat[n]['std']
        stats['ovrlap'][n] = np.sum(stat[n]['overlap']) / len(stat[n]['overlap'])
        stats['snr'][n] = np.median(F[n,:] / Fneu[n,:])

    Fsub = np.empty(F.shape)*np.nan
    for n in inds:
        Fsub[n,:] = F[n,:].copy() - Fneu[n,:].copy()

    recdict = {
        'stat': stat,
        'ops': ops,
        'F': F,
        'Fneu': Fneu,
        'Fsub': Fsub,
        'iscell': iscell,
        'stats': stats,
        'goodcells': goodcells
    }

    num_complete_iters = 0

    # check to see if the directory already exists
    preening_path = os.path.join(s2p_dir, 'preening')
    if not os.path.exists(preening_path):
        os.makedirs(preening_path)

    while True:

        # pick 20 random cells
        not_reviewed = np.isnan(stats['hand_label'])
        possible_inds = [i for i in goodcells if not_reviewed[i]==True]
        check_inds = np.random.choice(possible_inds, 20, replace=False)

        # one iteration of a cell review
        labels = tpt.cell_iter(recdict, check_inds)

        # save labels
        for i,l in enumerate(labels):
            recdict['stats']['hand_label'][check_inds[i]] = l

        # update thresholds and apply them to the full population
        # thresholds, labeling_result = tpt.threshold(recdict)

        # # summarize the population using new thresholds
        # finalized = tpt.pop_iter(recdict, thresholds, labeling_result)

        num_complete_iters += 1

        _savepath = os.path.join(preening_path, 'hand_label_iter_{}.json'.format(num_complete_iters))
        _savedata = {
            'cell_ids': check_inds.tolist(),
            'labels': labels.tolist(),
            'stats': recdict['stats']
        }
        with open(_savepath, 'w') as f:
            json.dump(_savedata, f, indent=4)
        
        # if the user is satisfied, exit the loop
        # if finalized == True:
        #     break

if __name__ == '__main__':

    stat_path = sg.popup_get_file('Get stat.npy file',
                      file_types=(('Numpy Files', '*.npy'),),
                      no_window=True)

    # stat_path = r'F:\treadmill_gaze_control\recordings\230306_DMM_DMM001_eyecams\R01\TwoPhotonTimeSeries\suite2p\plane0\stat.npy'
    cellReviewGUI(stat_path)