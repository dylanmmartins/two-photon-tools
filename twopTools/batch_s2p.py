
import os
import argparse
import numpy as np
import PySimpleGUI as sg

import twopTools as tpt

import suite2p

sg.theme('Default1')

def run_batch(path_list):

    ops = suite2p.default_ops()

    db = []
    for p in path_list:
        db.append({
            'data_path': [p],
            'fast_disk': 'C:/BIN', # string which specifies where the binary file will be stored (should be an SSD)
            'tau': 1.2, # specific to different types of gcamp
            'batch_size': 300
        })

    for i, dbi in enumerate(db):
        print('  ----> Starting on time series {}/{} (path= {})'.format(i+1, len(db), dbi['data_path'][0]))
        opsEnd = suite2p.run_s2p(ops=ops, db=dbi)

    print('Done with {}/{} time series'.format(i+1, len(db)))


def get_paths():
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
    # get paths for each time series
    path_list = get_paths()

    # run suite2p on each time series
    run_batch(path_list)

if __name__=='__main__':
    batch_s2p()
