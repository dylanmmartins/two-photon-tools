



import argparse
import PySimpleGUI as sg
sg.theme('Default1')

import twopTools as tpt


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-mat', '--mat_path', type=str, default=None)
    parser.add_argument('-stim', 'stim_path', type=str, default=None)
    args = parser.parse_args()

    if args.mat_path is None:
        print('Select registered .mat file')
        mat_path = sg.popup_get_file(
            'Select the .mat file',
            file_types=(('MATLAB files', '*.mat'),),
            no_window=True
        )
    else:
        mat_path = args.mat_path
    if args.stim_path is None:
        print('Select stimulus .mat file')
        stim_path = sg.popup_get_file(
            'Select the Stimulus.mat file',
            file_types=(('MATLAB files', '*.mat'),),
            no_window=True
        )
    else:
        stim_path = args.stim_path

    stimvid = tpt.loadmat(stim_path)

    dff = tpt.loadmat(mat_path)['data']

    fluor_sig, spikes = tpt.spike_inference(dff)

    sta = tpt.calc_spike_triggered_avg(spikes, stimvid)

if __name__ == '__main__':
    main()