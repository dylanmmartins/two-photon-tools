""" Run Suite2P on batches of two-photon recordings.
twopTools/batch_s2p.py

Functions
---------
run_batch
    Run Suite2P on a batch of time series.
get_paths
    Get filepaths.
batch_s2p
    Run Suite2P on batches of 2P timeseries.

Example usage
-------------
$ python -m twopTools.batch_s2p -d /path/to/data
or
$ python -m twopTools.batch_s2p
to select data directories via a GUI window.


Written by DMM, March 2023
"""


import os
import argparse
import numpy as np
import PySimpleGUI as sg
import suite2p
sg.theme('Default1')

import twopTools as tpt


def run_batch(path_list):
    """ Run Suite2P on a batch of time series.
    """

    ops = suite2p.default_ops()

    db = []
    for p in path_list:
        db.append({
            'data_path': [p],
            # String which specifies where the binary file will be stored (should be an SSD)
            'fast_disk': 'C:/BIN',
            # Specific to different types of gcamp
            'tau': 1.2,
            'batch_size': 300
        })

    for i, dbi in enumerate(db):
        print('  ----> Starting on time series {}/{} (path= {})'.format(i+1, len(db), dbi['data_path'][0]))
        opsEnd = suite2p.run_s2p(ops=ops, db=dbi)

    print('Done with {}/{} time series'.format(i+1, len(db)))


def get_paths():
    """ Get filepaths.
    """

    parser = argparse.ArgumentParser(description='Run Suite2p on a batch of tiffs')
    parser.add_argument('-d', '--data_path', type=str, default=None)
    args = parser.parse_args()

    if args.data_path is not None:

        if os.path.isdir(args.data_path) and (args.data_path[:7]=='TSeries-'):
            path_list = [args.data_path]
        
        elif os.path.isdir(args.data_path) and not (args.data_path[:7]=='TSeries-'):
            
            path_list = []
            for item in os.scandir(args.data_path):

                if os.path.isdir(item) and (item.name[:7]=='TSeries-'):
                    path_list.append(item.path)
        
    elif args.data_path is None:

        path_list = tpt.choose_dirs()

    return path_list


def batch_s2p():
    """ Run Suite2P on a batch of 2P time series.
    """

    # get paths for each time series
    path_list = get_paths()

    # run suite2p on each time series
    run_batch(path_list)


if __name__=='__main__':
    
    batch_s2p()


