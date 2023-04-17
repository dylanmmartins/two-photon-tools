
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

mpl.rcParams['axes.spines.top'] = False
mpl.rcParams['axes.spines.right'] = False
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.size'] = 6

def draw_figure(canvas, figure):
    
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

    return figure_canvas_agg

def imnorm(im):
    return (im - im.min()) / (im.max() - im.min())

def make_cell_fig(recdict, cell_id):

   # transparency colormap
   t2b = np.zeros([256, 4])
   t2b[:,0] = np.ones(256)
   t2b[:,3] = np.linspace(0, 1, 256)
   t2b = ListedColormap(t2b)

   F = recdict['F'][cell_id,:]
   Fneu = recdict['Fneu'][cell_id,:]
   Fsub = recdict['Fsub'][cell_id,:]
   goodcells = recdict['goodcells']
   stats = recdict['stats']
   stat = recdict['stat']
   ops = recdict['ops']

   # setup cell mask
   xy = np.stack([stat[cell_id]['xpix'], stat[cell_id]['ypix']])
   d = stat[cell_id]['radius'] * 3
   bbox_x = ([np.min(xy[0,:]-d), np.max(xy[0,:])+d])
   bbox_y = ([np.max(xy[1,:])+d, np.min(xy[1,:]-d)])

   maxproj = ops.item()['max_proj'].copy()
   meanim = ops.item()['meanImg'].copy()

   cell_mask = np.zeros(meanim.shape)
   cell_mask[xy[1,:], xy[0,:]] = 1

   # time bins for panels of fluorescence trace over time
   fakeT = np.linspace(0, 3530/10/60, np.size(F, 0))

   fig = plt.figure(constrained_layout=True, figsize=(8.5,4), dpi=150)
   spec = gridspec.GridSpec(nrows=3, ncols=11, figure=fig, wspace=0.05, hspace=0.05)

   im1 = fig.add_subplot(spec[0, 0:2])
   im2 = fig.add_subplot(spec[0, 2:4])
   im3 = fig.add_subplot(spec[0, 4:6])

   trace1 = fig.add_subplot(spec[1,:6])
   trace2 = fig.add_subplot(spec[2,:6])

   prop1 = fig.add_subplot(spec[0,6:8])
   prop2 = fig.add_subplot(spec[0,8:10])
   prop3 = fig.add_subplot(spec[1,6:8])
   prop4 = fig.add_subplot(spec[1,8:10])
   prop5 = fig.add_subplot(spec[2,6:8])
   prop6 = fig.add_subplot(spec[2,8:10])

   prop1.hist(stats['prob'], bins=np.linspace(0,1,31),
            histtype='stepfilled', color='tab:blue', linewidth=1,
            alpha=0.2, label='bad cells')
   h, _, _ = prop1.hist(stats['prob'][goodcells], bins=np.linspace(0,1,31),
            histtype='stepfilled', color='tab:blue', linewidth=1,
            label='good cells')
   prop1.vlines(stats['prob'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
            label='cell {}'.format(cell_id))
   prop1.legend(fontsize=6, loc='upper left')
   prop1.set_xlim([0,1])
   prop1.set_xlabel('probability')
   prop1.set_ylabel('cells')

   _usemax = np.max(stats['rad'][goodcells])+3
   prop2.hist(stats['rad'], bins=np.linspace(0,_usemax,31),
            histtype='stepfilled', color='tab:blue', linewidth=1,
            alpha=0.2, label='bad cells')
   h, _, _ = prop2.hist(stats['rad'][goodcells], bins=np.linspace(0,_usemax,31),
               histtype='stepfilled', color='tab:blue', linewidth=1, label='good cells')
   prop2.vlines(stats['rad'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
            label='cell {}'.format(cell_id))
   prop2.set_xlim([0, _usemax])
   prop2.set_ylabel('cells')
   prop2.set_xlabel('radius (pixels)')

   _usemin = np.min(stats['aspect'][goodcells])
   _usemax = np.max(stats['aspect'][goodcells])
   prop3.hist(stats['aspect'], bins=np.linspace(_usemin,_usemax,31),
            color='tab:blue', linewidth=1, alpha=0.2, label='bad cells',
               histtype='stepfilled')
   h, _, _ = prop3.hist(stats['aspect'][goodcells], bins=np.linspace(_usemin,_usemax,31),
               color='tab:blue', linewidth=1, label='good cells', histtype='stepfilled')
   prop3.vlines(stats['aspect'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
               label='cell {}'.format(cell_id))
   prop3.set_xlim([_usemin, _usemax])
   prop3.set_ylabel('cells')
   prop3.set_xlabel('major:minor axis ratio')

   _usemin = np.min(stats['cmpt'][goodcells])
   prop4.hist(stats['cmpt'], bins=np.linspace(_usemin,100,31), histtype='stepfilled',
            color='tab:blue', linewidth=1, alpha=0.2, label='bad cells')
   h, _, _ = prop4.hist(stats['cmpt'][goodcells], bins=np.linspace(_usemin,100,31),
                     color='tab:blue', linewidth=1, label='good cells', histtype='stepfilled')
   prop4.vlines(stats['cmpt'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
               label='cell {}'.format(cell_id))
   prop4.set_xlim([_usemin, 100])
   prop4.set_ylabel('cells')
   prop4.set_xlabel('compactness (%)')

   _usemin = np.min(stats['snr'][goodcells])
   _usemax = np.max(stats['snr'][goodcells])
   prop5.hist(stats['snr'], bins=np.linspace(_usemin,_usemax,31),
            color='tab:blue', linewidth=1, alpha=0.2, label='bad cells',
               histtype='stepfilled')
   h, _, _ = prop5.hist(stats['snr'][goodcells], bins=np.linspace(_usemin,_usemax,31),
               color='tab:blue', linewidth=1, label='good cells', histtype='stepfilled')
   prop5.vlines(stats['snr'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
                  label='cell {}'.format(cell_id))
   prop5.set_xlim([_usemin, _usemax])
   prop5.set_ylabel('cells')
   prop5.set_xlabel('median SNR')

   _usemax = np.max(stats['std'][goodcells])
   prop6.hist(stats['std'], bins=np.linspace(0,_usemax,31),
            color='tab:blue', linewidth=1, alpha=0.2, label='bad cells',
               histtype='stepfilled')
   h, _, _ = prop6.hist(stats['std'][goodcells], bins=np.linspace(0,_usemax,31),
               color='tab:blue', linewidth=1, label='good cells', histtype='stepfilled')
   prop6.vlines(stats['std'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
                  label='cell {}'.format(cell_id))
   prop6.set_xlim([0, _usemax])
   prop6.set_ylabel('cells')
   prop6.set_xlabel('std(Fsub)')

   trace1.plot(fakeT, F, linewidth=0.5, color='tab:purple', label='F')
   trace1.plot(fakeT, Fneu, linewidth=0.5, color='tab:red', label='Fneu')
   trace1.set_ylim([0, np.max([np.max(F), np.max(Fneu)])])
   trace1.legend(fontsize=6)
   trace1.set_xlim([0, fakeT[-1]])
   trace1.set_xticks(np.arange(0, fakeT[-1], np.round(fakeT[-1]/6, 1)).astype(int), labels=[])

   trace2.plot(fakeT, Fsub, linewidth=0.5, color='tab:blue', label='F - Fneu')
   trace2.legend(fontsize=6)
   trace2.set_xlim([0, fakeT[-1]])
   trace2.set_xticks(np.arange(0, fakeT[-1], np.round(fakeT[-1]/6, 1)).astype(int))
   trace2.set_xlabel('time (min)')

   im1.imshow(maxproj, cmap='gray', vmin=0)
   im1.plot(np.median(xy[0,:]),
            np.median(xy[1,:]),'x', color='tab:red', markersize=4)
   im1.axis('off')

   im2.imshow(meanim, cmap='gray')
   im2.imshow(cell_mask, cmap=t2b, alpha=0.35)
   im2.set_xlim(bbox_x)
   im2.set_ylim(bbox_y)
   im2.axis('off')

   im3.imshow(maxproj, cmap='gray')
   im3.set_xlim(bbox_x)
   im3.set_ylim(bbox_y)
   im3.axis('off')

   return fig

