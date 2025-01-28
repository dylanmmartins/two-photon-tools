
import argparse
import PySimpleGUI as sg
sg.theme('Default1')

import twopTools as tpt


def quickRF(s2p_path=None, stim_path=None):

    if s2p_path is None:
        print('Select suite2p directory')
        s2p_path = sg.popup_get_file(
            'Select suite2p directory',
            no_window=True
        )
    else:
        s2p_path = args.s2p_path

    if stim_path is None:
        print('Select stimulus .mat file')
        stim_path = sg.popup_get_file(
            'Select the Stimulus.mat file',
            file_types=(('MATLAB files', '*.mat'),),
            no_window=True
        )
    else:
        stim_path = args.stim_path

    stimvid = tpt.loadmat(stim_path)['noise_image']

    dff = tpt.loadmat(_path)['data']

    fluor_sig, spikes = tpt.spike_inference(dff)

    sta = tpt.calc_spike_triggered_avg(spikes, stimvid)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-s2p', '--s2p_path', type=str, default=None)
    parser.add_argument('-stim', '--stim_path', type=str, default=None)
    args = parser.parse_args()
    
    quickRF()
