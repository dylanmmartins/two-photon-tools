
import numpy as np
import matplotlib.pyplot as plt


def calc_spike_triggered_avg(sps, stim, lag=2):
    """
    sps is of shape (n_cells, n_timepoints). should be inferred spikes
    """


    n_units = len(goodcells)

    # model setup
    model_dt = 0.025
    model_t = np.arange(0, np.max(worldT), model_dt)
    model_nsp = np.zeros((n_units, len(model_t)))
    
    # get binned spike rate
    bins = np.append(model_t, model_t[-1]+model_dt)
    
    for i, ind in enumerate(goodcells.index):
        model_nsp[i,:], bins = np.histogram(goodcells.at[ind,'spikeT'], bins)
    
    # settting up video
    nks = np.shape(img_norm[0,:,:])
    nk = nks[0] * nks[1]
    model_vid = np.zeros((len(model_t),nk))
    
    for i in range(len(model_t)):

        model_vid[i,:] = np.reshape(movInterp(model_t[i]+model_dt/2), nk)
    
    # spike-triggered average
    staAll = np.zeros((n_units,
                       np.shape(img_norm)[1],
                       np.shape(img_norm)[2]))
    model_vid[np.isnan(model_vid)] = 0
    
    if type(lag) == int:

        fig = plt.subplots(int(np.ceil(n_units/10)), 10,
                           figsize=(20,np.int(np.ceil(n_units/3))), dpi=50)
        
        for c, ind in enumerate(goodcells.index):

            sp = model_nsp[c,:].copy()
            sp = np.roll(sp, -lag)
            sta = model_vid.T @ sp
            sta = np.reshape(sta, nks)
            nsp = np.sum(sp)

            plt.subplot(int(np.ceil(n_units/10)), 10, c+1)

            ch = int(goodcells.at[ind,'ch'])

            if ch_count == 64 or ch_count == 128:
                shank = np.floor(ch/32)
                site = np.mod(ch,32)

            else:
                shank = 0
                site = ch

            if show_title:
                plt.title(f'ind={ind!s} nsp={nsp!s}\n ch={ch!s} shank={shank!s}\n site={site!s}',
                          fontsize=5)
            plt.axis('off')

            if nsp > 0:
                sta = sta/nsp
            else:
                sta = np.nan

            if pd.isna(sta) is True:
                plt.imshow(np.zeros([120,160]))

            else:
                plt.imshow((sta - np.mean(sta)),
                           vmin=-0.3, vmax=0.3, cmap='jet')
                
                staAll[c,:,:] = sta

        plt.tight_layout()

        return staAll, fig
    
    else:

        lagRange = lag
        fig = plt.subplots(n_units, 5,
                           figsize=(6,np.int(np.ceil(n_units/2))), dpi=300)
        
        for c, ind in enumerate(goodcells.index):

            for lagInd, lag in enumerate(lagRange):

                sp = model_nsp[c,:].copy()
                sp = np.roll(sp,-lag)
                sta = model_vid.T @ sp
                sta = np.reshape(sta, nks)
                nsp = np.sum(sp)

                plt.subplot(n_units,5,(c*5)+lagInd + 1)

                if nsp > 0:
                    sta = sta/nsp
                else:
                    sta = np.nan

                if pd.isna(sta) is True:
                    plt.imshow(np.zeros([120,160]))

                else:
                    plt.imshow((sta-np.mean(sta)),vmin=-0.3,vmax=0.3,cmap = 'jet')
                
                if c == 0:
                    plt.title(str(np.round(lag*model_dt*1000)) + 'msec',fontsize=5)
                
                plt.axis('off')

            plt.tight_layout()

        return fig
    


    