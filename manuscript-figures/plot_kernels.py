import galois
import numpy as np
GF = galois.GF(2)
import matplotlib.pyplot as plt
import datetime
import pickle

cmap = plt.get_cmap('viridis')
colors = cmap(np.arange(0,1,1/3.5))

import matplotlib.font_manager as font_manager
from matplotlib import rcParams

# font_dir = ['/$YOURDIRECTORY/fonts/Source_Sans_Pro']
# for font in font_manager.findSystemFonts(font_dir):
#     font_manager.fontManager.addfont(font)
# rcParams['font.family'] = 'Source Sans Pro'
SIZE=9
rcParams['font.family'] = 'Source Sans Pro'
rcParams['font.size']=SIZE
rcParams['axes.titlesize']=SIZE
rcParams['axes.labelsize']=SIZE
rcParams['xtick.labelsize']=SIZE
rcParams['ytick.labelsize']=SIZE
rcParams['legend.fontsize']=SIZE
rcParams['figure.titlesize']=SIZE
markers = np.array(['o','D','^'])
marker_size = .6*np.array([1.5,1.5])
elinewidth = .5
capsize = 0

alpha = 1
alpha1 = .8
alpha2 = .1
lw = 1.25
lw2 = 1.75

linestyle = np.empty(4,'object')
linestyle[0] = dict(
    linewidth=lw,
    dash_capstyle='round',
    solid_capstyle='round',
    linestyle='-',
    alpha=alpha
)
linestyle[1] = dict(
    linewidth=lw,
    linestyle=':',
    dash_capstyle='round',
    solid_capstyle='round',
    alpha=alpha,
)
aspect_ratio = 3.8/9
pad=0.5
width = 426.79 * 0.01389 # pt
figsize = (width, aspect_ratio*width)

fig,ax = plt.subplots(1,2,figsize=figsize)


#### qrc construction
q = 103 
m = 2*q 
r = int((q+1)/2)
n = q+r
E = 1000
nH = 100

today = '2023-12-04'
ns = np.arange(q,q+r,10)

# single meyer
pickleFilename =  "data/"+ today +\
                 f"_kernels_single_meyer_qrc_E={E}_q={q}_m={m}_nH={nH}.pickle"

with open(pickleFilename, 'rb') as pickleFile:
    print("Write data to  ", pickleFilename, " ...")
    Pars = pickle.load(pickleFile)
    ns = pickle.load(pickleFile)
    allKernelsG = np.array(pickle.load(pickleFile))
    allKernelsH = np.array(pickle.load(pickleFile))
m = Pars['m']
q = Pars['q']
r = (q+1)/2

allKernelsG = allKernelsG.reshape((len(ns),nH*E))
allKernelsH = allKernelsH.reshape((len(ns),nH*E))
mean_diff = np.mean(allKernelsG- allKernelsH,axis=1)
std_diff = np.std(allKernelsG - allKernelsH,axis=1)

mean_kerG = np.mean(allKernelsG,axis=1)
std_kerG = np.std(allKernelsG,axis=1)
ax[0].plot(ns,mean_kerG,**linestyle[0],color=colors[2],label=r'dim(ker G)')
ax[0].fill_between(ns,mean_kerG - std_kerG,mean_kerG + std_kerG,color=colors[2],linewidth=0,alpha = alpha2)
ax[0].plot(ns,np.min(allKernelsG,axis=1),color=colors[2],**linestyle[1],label=f'min dim(ker G)')

ax[0].plot(ns,mean_diff,**linestyle[0],color=colors[0],label=f'dim (ker G / ker H)')
ax[0].fill_between(ns,mean_diff - std_diff, mean_diff+std_diff,color=colors[0],alpha = alpha2,linewidth=0)
ax[0].plot(ns,ns - m/2,**linestyle[0],color=(237/255,16/255,118/255),label=r'$m - n/2$')
ax[0].legend(frameon=False)
ax[0].set_xlabel(r'n')
ax[0].set_ylabel(r'dim(ker G)')

# kfold Meyer
pickleFilename =  "data/"+ today +\
                 f"_kernels_kfold_meyer_qrc_E={E}_q={q}_m={m}_nH={nH}_n=155.pickle"

with open(pickleFilename, 'rb') as pickleFile:
    print("Write data to  ", pickleFilename, " ...")
    Pars = pickle.load(pickleFile)
    ks = pickle.load(pickleFile)
    allKernelsG = np.array(pickle.load(pickleFile))
    allKernelsH = np.array(pickle.load(pickleFile))
allKernelsG = allKernelsG.reshape((len(ks),nH*E))
allKernelsH = allKernelsH.reshape((len(ks),nH*E))
m = Pars['m']
q = Pars['q']
r = (q+1)/2
n = q+r

mean_diff = np.mean(allKernelsG- allKernelsH,axis=1)
std_diff = np.std(allKernelsG - allKernelsH,axis=1)

mean_kerG = np.mean(allKernelsG,axis=1)
std_kerG = np.std(allKernelsG,axis=1)
ax[1].plot(ks,mean_kerG,**linestyle[0],color=colors[2],label=r'dim(ker G)')
ax[1].fill_between(ks,mean_kerG-std_kerG ,mean_kerG + std_kerG,color=colors[2],linewidth=0,alpha = alpha2)

ax[1].plot(ks,1/2**ks*(n - m/2),**linestyle[0],color=(237/255,16/255,118/255),label=r'$2^{-k}(m -n/2)$')
ax[1].legend(frameon=False)
ax[1].set_xlabel(r'k')
ax[1].set_yscale('log')
ax[1].set_xticks(np.arange(8)+1)
fig.tight_layout(pad=pad)
fig.savefig(f'fig/'+today+'_kernel_plot_meyer_attacks.pdf')
