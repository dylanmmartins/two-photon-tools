


def plot_STV(goodcells, movInterp, img_norm, worldT):
    """
    plot spike-triggererd varaince
    INPUTS
        goodcells: ephys dataframe
        movInterp: interpolator for worldcam movie
        img_norm: normalized worldcam video
        worldT: world timestamps
    OUTPUTS
        stvAll: spike triggered variance for all units
        fig: figure
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
    nk = nks[0]*nks[1]
    model_vid = np.zeros((len(model_t),nk))
    
    for i in range(len(model_t)):
        model_vid[i,:] = np.reshape(movInterp(model_t[i]+model_dt/2), nk)

    model_vid = model_vid**2
    lag = 2
    stvAll = np.zeros((n_units, np.shape(img_norm)[1], np.shape(img_norm)[2]))
    
    fig = plt.subplots(int(np.ceil(n_units/10)), 10,
                       figsize=(20,np.int(np.ceil(n_units/3))), dpi=50)
    
    for c, ind in enumerate(goodcells.index):

        sp = model_nsp[c,:].copy()
        sp = np.roll(sp, -lag)
        sta = np.nan_to_num(model_vid,0).T @ sp
        sta = np.reshape(sta, nks)
        nsp = np.sum(sp)

        plt.subplot(int(np.ceil(n_units/10)), 10, c+1)

        if nsp > 0:
            sta = sta / nsp
        else:
            sta = np.nan

        if pd.isna(sta) is True:
            plt.imshow(np.zeros([120,160]))
        else:
            plt.imshow(sta - np.mean(img_norm**2,axis=0),
                       vmin=-1, vmax=1)

        stvAll[c,:,:] = sta - np.mean(img_norm**2, axis=0)

        plt.axis('off')

    plt.tight_layout()

    return stvAll, fig