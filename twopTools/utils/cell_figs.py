
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def draw_figure(canvas, figure):
    
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

    return figure_canvas_agg

def imnorm(im):
    return (im - im.min()) / (im.max() - im.min())


def plot_cell_props(stats, goodcells, cell_id):

   fig, [[ax0,ax1],[ax2,ax3],[ax4,ax5]] = plt.subplots(3,2, figsize=(5,6), dpi=300)

   ax0.hist(stats['prob'], bins=np.linspace(0,1,31),
            histtype='stepfilled', color='tab:blue', linewidth=1,
            alpha=0.2, label='bad cells')
   h, _, _ = ax0.hist(stats['prob'][goodcells], bins=np.linspace(0,1,31),
            histtype='stepfilled', color='tab:blue', linewidth=1,
            label='good cells')
   ax0.vlines(stats['prob'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
            label='cell {}'.format(cell_id))
   ax0.legend(fontsize=6, loc='upper left')
   ax0.set_xlim([0,1])
   ax0.set_xlabel('probability')
   ax0.set_ylabel('cells')

   _usemax = np.max(stats['rad'][goodcells])+3
   ax1.hist(stats['rad'], bins=np.linspace(0,_usemax,31),
            histtype='stepfilled', color='tab:blue', linewidth=1,
            alpha=0.2, label='bad cells')
   h, _, _ = ax1.hist(stats['rad'][goodcells], bins=np.linspace(0,_usemax,31),
               histtype='stepfilled', color='tab:blue', linewidth=1, label='good cells')
   ax1.vlines(stats['rad'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
            label='cell {}'.format(cell_id))
   ax1.set_xlim([0, _usemax])
   ax1.set_ylabel('cells')
   ax1.set_xlabel('radius (pixels)')

   _usemin = np.min(stats['aspect'][goodcells])
   _usemax = np.max(stats['aspect'][goodcells])
   ax2.hist(stats['aspect'], bins=np.linspace(_usemin,_usemax,31),
            color='tab:blue', linewidth=1, alpha=0.2, label='bad cells',
               histtype='stepfilled')
   h, _, _ = ax2.hist(stats['aspect'][goodcells], bins=np.linspace(_usemin,_usemax,31),
               color='tab:blue', linewidth=1, label='good cells', histtype='stepfilled')
   ax2.vlines(stats['aspect'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
               label='cell {}'.format(cell_id))
   ax2.set_xlim([_usemin, _usemax])
   ax2.set_ylabel('cells')
   ax2.set_xlabel('major:minor axis ratio')

   _usemin = np.min(stats['cmpt'][goodcells])
   ax3.hist(stats['cmpt'], bins=np.linspace(_usemin,100,31), histtype='stepfilled',
            color='tab:blue', linewidth=1, alpha=0.2, label='bad cells')
   h, _, _ = ax3.hist(stats['cmpt'][goodcells], bins=np.linspace(_usemin,100,31),
                     color='tab:blue', linewidth=1, label='good cells', histtype='stepfilled')
   ax3.vlines(stats['cmpt'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
               label='cell {}'.format(cell_id))
   ax3.set_xlim([_usemin, 100])
   ax3.set_ylabel('cells')
   ax3.set_xlabel('compactness (%)')

   _usemin = np.min(stats['snr'][goodcells])
   _usemax = np.max(stats['snr'][goodcells])
   ax4.hist(stats['snr'], bins=np.linspace(_usemin,_usemax,31),
            color='tab:blue', linewidth=1, alpha=0.2, label='bad cells',
               histtype='stepfilled')
   h, _, _ = ax4.hist(stats['snr'][goodcells], bins=np.linspace(_usemin,_usemax,31),
               color='tab:blue', linewidth=1, label='good cells', histtype='stepfilled')
   ax4.vlines(stats['snr'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
                  label='cell {}'.format(cell_id))
   ax4.set_xlim([_usemin, _usemax])
   ax4.set_ylabel('cells')
   ax4.set_xlabel('median SNR')

   _usemax = np.max(stats['std'][goodcells])
   ax5.hist(stats['std'], bins=np.linspace(0,_usemax,31),
            color='tab:blue', linewidth=1, alpha=0.2, label='bad cells',
               histtype='stepfilled')
   h, _, _ = ax5.hist(stats['std'][goodcells], bins=np.linspace(0,_usemax,31),
               color='tab:blue', linewidth=1, label='good cells', histtype='stepfilled')
   ax5.vlines(stats['std'][cell_id], 0, np.max(h), color='tab:red', linewidth=1,
                  label='cell {}'.format(cell_id))
   ax5.set_xlim([0, _usemax])
   ax5.set_ylabel('cells')
   ax5.set_xlabel('std(Fsub)')

   fig.tight_layout()
   return fig


def plot_fluor(F, Fneu, Fsub):

   fakeT = np.linspace(0, 3530/10/60, np.size(F, 1))

   fig, [ax0,ax1] = plt.subplots(2,1, figsize=(7,3.5), dpi=300)

   ax0.plot(fakeT, F, linewidth=0.5, color='tab:purple', label='F')
   ax0.plot(fakeT, Fneu, linewidth=0.5, color='tab:red', label='Fneu')
   ax0.set_ylim([0, np.max([np.max(F), np.max(Fneu)])])
   ax0.legend(fontsize=6)
   ax0.set_xlim([0, fakeT[-1]])
   ax0.set_xticks(np.arange(0, fakeT[-1], np.round(fakeT[-1]/6, 1)).astype(int), labels=[])

   ax1.plot(fakeT, Fsub, linewidth=0.5, color='tab:blue', label='F - Fneu')
   # ax1.set_ylim(0, np.max(Fsub))
   ax1.legend(fontsize=6)
   ax1.set_xlim([0, fakeT[-1]])
   ax1.set_xticks(np.arange(0, fakeT[-1], np.round(fakeT[-1]/6, 1)).astype(int))
   ax1.set_xlabel('time (min)')

   fig.tight_layout()
   return fig

def plot_cell_imgs(stat, ops, cell_id):

   t2b = np.zeros([256, 4])
   t2b[:,0] = np.ones(256)
   t2b[:,3] = np.linspace(0, 1, 256)
   t2b = ListedColormap(t2b)

   xy = np.stack([stat[cell_id]['xpix'], stat[cell_id]['ypix']])
   d = stat[cell_id]['radius'] * 3
   bbox_x = ([np.min(xy[0,:]-d), np.max(xy[0,:])+d])
   bbox_y = ([np.max(xy[1,:])+d, np.min(xy[1,:]-d)])

   maxproj = ops.item()['max_proj'].copy()
   meanim = ops.item()['meanImg'].copy()

   cell_mask = np.zeros(meanim.shape)
   cell_mask[xy[1,:], xy[0,:]] = 1

   fig, [ax0, ax1, ax2] = plt.subplots(1,3, figsize=(7,2.5), dpi=300)
   ax0.imshow(maxproj, cmap='gray', vmin=0)
   ax0.plot(np.median(xy[0,:]),
            np.median(xy[1,:]),'x', color='tab:red', markersize=4)
   ax0.axis('off')

   ax1.imshow(meanim, cmap='gray')
   ax1.imshow(cell_mask, cmap=t2b, alpha=0.35)
   ax1.set_xlim(bbox_x)
   ax1.set_ylim(bbox_y)
   ax1.axis('off')

   ax2.imshow(maxproj, cmap='gray')
   ax2.set_xlim(bbox_x)
   ax2.set_ylim(bbox_y)
   ax2.axis('off')

   fig.tight_layout()
   return fig
