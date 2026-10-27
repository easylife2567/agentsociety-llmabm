"""图5：原三种子组件干预的同seed配对；不混入新增主实验Full。"""
from paper_plot_style import *


def main():
    data=pd.read_csv(DATA/'ablation_metrics.csv')
    assert len(data)==30 and set(data.seed)=={0,1,2}
    specs=[
        ('a','W19–W22','Total output\n(posts per week)',20,5,'no_b','B = 0'),
        ('b','W19–W22','Memetic-type\nposting rate (%)',65,20,'no_d','D = 1'),
        ('c','W14–W18','Overall\nposting rate (%)',65,20,'no_r','R = 1'),
        ('d','W19–W22','Memetic-type\nsupply share (%)',90,20,'no_r','R = 1'),
        ('e','W19–W22',"Memetic content in\nother authors' feeds (%)",30,10,'no_r','R = 1'),
    ]
    fig,grid=plt.subplots(2,3,figsize=(mm(180),mm(140)))
    fig.subplots_adjust(left=.105,right=.98,top=.90,bottom=.13,wspace=.68,hspace=.74)
    axes=list(grid.flat)[:5]
    markers=['o','^','s']
    for ax,(letter,window,ylabel,upper,step,condition,label) in zip(axes,specs):
        part=data[data.panel.eq(letter)].copy()
        assert len(part)==6 and set(part.condition)=={'full',condition}
        factor=1 if letter=='a' else 100
        expected=(14,18) if letter=='c' else (19,22)
        assert set(part.week_start.str[-2:].astype(int))=={expected[0]}
        assert set(part.week_end.str[-2:].astype(int))=={expected[1]}
        for seed in (0,1,2):
            pair=part[part.seed.eq(seed)].set_index('condition')
            values=pair.loc[['full',condition],'value'].to_numpy(float)*factor
            offset=(seed-1)*.075
            x=np.array([0,1])+offset
            ax.plot(x,values,color='#A8B2BD',lw=.85,zorder=2)
            for xx,yy,color in zip(x,values,['#667482','#0072B2']):
                ax.scatter(xx,yy,marker=markers[seed],s=28,facecolor=color,
                           edgecolor='white',lw=.4,zorder=4)
        for x,cond in enumerate(['full',condition]):
            values=part[part.condition.eq(cond)].value*factor
            mean=values.mean()
            ax.plot([x-.15,x+.15],[mean,mean],color='#17212B',lw=1.65,zorder=5)
            ax.text(x,values.max()+upper*.075,f'{mean:.1f}'+('' if letter=='a' else '%'),
                    ha='center',va='bottom',fontsize=8.4,color='#17212B')
        ax.set_xlim(-.38,1.38)
        ax.set_ylim(0,upper)
        ax.yaxis.set_major_locator(MultipleLocator(step))
        ax.set_xticks([0,1],['Full',label],fontsize=9)
        ax.set_ylabel(ylabel,fontsize=8.5,labelpad=5)
        ax.set_xlabel('Model condition',fontsize=8.5)
        panel(ax,5,letter,window)
    key=grid[1,2];key.axis('off')
    handles=[Line2D([],[],ls='none',marker=m,color='#667482',markersize=4,
                    markeredgecolor='white',markeredgewidth=.4,label=f'Seed {i}')
             for i,m in enumerate(markers)]
    handles.extend([
        Line2D([],[],color='#17212B',lw=1.65,label='Mean'),
        Line2D([],[],color='#A8B2BD',lw=.85,label='Same-seed pair'),
    ])
    key.legend(handles=handles,loc='upper left',fontsize=8.5,
               handlelength=1.9,labelspacing=.75,borderaxespad=0)
    key.text(0,.05,'Numbers: condition means.\nFull: matching seeds 0–2.',
             transform=key.transAxes,ha='left',va='bottom',fontsize=8.2,linespacing=1.45)
    fig.text(.54,.028,'Interest-based regime · 3 paired seeds (n = 3)',
             ha='center',va='bottom',fontsize=9)
    save_figure(fig,'figure_05_bdr_ablation',axes,[f'Fig. 5{x}' for x in 'abcde'])


if __name__=='__main__':main()
