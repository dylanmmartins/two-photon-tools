
import PySimpleGUI as sg
import numpy as np

import twopTools as tpt

def cell_review(cell_id, recdict, page, review_total=20):

    # cell figure
    fig = tpt.make_cell_fig(recdict, cell_id)

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
        multilineprops += item + '\n'

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
        [sg.Canvas(key='canvas', size=(100,40))],
        [sg.Multiline(multilineprops, horizontal_scroll=True, size=(25,9)),
         sg.Radio('Bad', 'radlab', key='bad', default=radlab_bad),
          sg.Radio('Ignore', 'radlab', key='ignore', default=radlab_ignore),
          sg.Radio('Good', 'radlab', key='good', default=radlab_good),
         sg.Button('Previous', key='prev', disabled=disable_prev),
          sg.Button('Next', key='next', disabled=disable_next),
          sg.Button('Submit', key='finish', disabled=disable_submit)]
    ]

    # w = sg.Window('Review Cells', layout, finalize=True,
    #               , size=(1400, 1000))

    w = sg.Window('Review Cells', layout,
                  element_justification='center').Finalize()

    tpt.draw_figure(w['canvas'].TKCanvas, fig)
    # tpt.draw_figure(w['props_canvas'].TKCanvas, cell_props_fig)
    # tpt.draw_figure(w['trace_canvas'].TKCanvas, cell_trace_fig)

    retval = None
    label = 1

    while True:
        
        event, values = w.read(timeout=100)

        if event in (None, 'Exit'):
            retval = 'esc'
            break

        elif event=='bad':
            label = 0

        elif event=='ignore':
            label = 1

        elif event=='good':
            label = 2

        elif event=='prev':
            retval = 'prev'
            break

        elif event=='next':
            retval = 'next'
            break

        elif event=='finish':
            retval = 'finish'
            break
            
    w.close()

    return label, retval


def cell_iter(recdict, check_inds):

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
        elif retval == 'esc':
            break

    return labels