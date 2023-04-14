
import PySimpleGUI as sg
import numpy as np

import twopTools as tpt

def cell_review(cell_id, recdict, page, review_total=20):

    Fsub = recdict['F'][cell_id,:].copy() - recdict['Fneu'][cell_id,:].copy()

    # cell map
    cell_imgs_fig = tpt.plot_cell_imgs(recdict['stat'], recdict['ops'], cell_id)

    # cell props
    cell_props_fig = tpt.plot_cell_props(recdict['stats'], recdict['goodcells'], cell_id)

    # plot cell trace
    cell_trace_fig = tpt.plot_fluor(recdict['F'][cell_id,:], recdict['Fneu'][cell_id,:], Fsub)

    # write cell summary text
    props_list = [
        'suite2P probability: {:.3}%'.format(recdict['stats']['prob'][cell_id]),
        'radius: {:.3} pxls'.format(recdict['stats']['rad'][cell_id]),
        'aspect ratio: {:.3}'.format(recdict['stats']['aspect'][cell_id]),
        'compactness: {:.3}'.format(recdict['stats']['cmpt'][cell_id]),
        'F std: {:.5}'.format(recdict['stats']['std'][cell_id]),
        'ROI overlap: {:.3}%'.format(recdict['stats']['ovrlap'][cell_id]),
        'SNR: {}'.format(recdict['stats']['snr'][cell_id]),
    ]
    multilineprops = ''
    for item in props_list:
        multilineprops.append(item + '\n')

    disable_submit = True
    disable_next = False
    if page == review_total:
        disable_submit = False
        disable_next = True

    disable_prev = False
    if page == 1:
        disable_prev = True

    radlab_bad = False
    radlab_ignore = False
    radlab_good = False
    if recdict['stats']['hand_label'][cell_id] == 0:
        radlab_bad = True
    elif recdict['stats']['hand_label'][cell_id] == 1:
        radlab_ignore = True
    elif recdict['stats']['hand_label'][cell_id] == 2:
        radlab_good = True


    layout = [
        [sg.Text('Cell {} (reviewing {}/{})'.format(cell_id, page, review_total))],
        [sg.Canvas(key='imgs_canvas'), sg.Canvas(key='props_canvas')],
        [sg.Canvas(key='trace_canvas'), sg.Multiline(multilineprops)],
        [sg.Radio('Bad', 'radlab', key='bad', default=radlab_bad),
        sg.Radio('Ignore', 'radlab', key='ignore', default=radlab_ignore),
        sg.Radio('Good', 'radlab', key='good', default=radlab_good)],
        [sg.Button('Previous', allow_events=True, key='prev', disabled=disable_prev),
         sg.Button('Next', allow_events=True, key='next', disabled=disable_next),
         sg.Button('Submit', allow_events=True, key='finish', disabled=disable_submit)]
    ]

    w = sg.Window('Review Cells', layout, finalize=True, element_justification='center')

    tpt.draw_figure(w['imgs_canvas'].TKCanvas, cell_imgs_fig)
    tpt.draw_figure(w['props_canvas'].TKCanvas, cell_props_fig)
    tpt.draw_figure(w['trace_canvas'].TKCanvas, cell_trace_fig)

    retval = None

    while True:
        
        event, values = w.read()

        if event in (None, 'Exit'):
            break

        elif event=='prev':
            retval = 'prev'
            label = values['radlab'].get()

        elif event=='next':
            retval = 'next'
            label = values['radlab'].get()

        elif event=='finish':
            retval = 'finish'
            label = values['radlab'].get()
            
    w.close()

    label_trans = {'bad': 0, 'ignore': 1, 'good': 2}
    label = label_trans[label]

    return label, retval


def cell_iter(check_inds, recdict):

    labels = np.zeros(len(check_inds))

    i = 0

    while True:

        labels[i], retval = cell_review(check_inds[i], recdict, i+1)

        if retval == 'prev':
            i -= 1
        elif retval == 'next':
            i += 1
        elif retval == 'finish':
            break

    return labels