
import PySimpleGUI as sg

sg.theme('Default1')

def choose_dirs():
    # get base directory
    base_path = sg.popup_get_folder('Choose initial directory')

    # get path list
    path_list = []

    layout = [
        [sg.Button('Add a path', k='add', enable_events=True),
        sg.Button('Done', k='done', enable_events=True)],
        [sg.Listbox(path_list, size=(80, 20), key='pathlist',
                    enable_events=True, horizontal_scroll=True)]
    ]

    w = sg.Window('List paths', layout)

    while True:
        event, values = w.read(timeout=100)

        if event in (None, 'Exit'):
            break

        elif event == 'add':

            _add = sg.popup_get_folder('Choose a directory',
                                        initial_folder=base_path,
                                        no_window=True)
            
            if type(_add) != list:
                _add = [_add]
            w['pathlist'].update(w['pathlist'].Values + _add)
            
        elif event == 'done':
            path_list = w['pathlist'].Values
            break
            
    w.close()

    return path_list