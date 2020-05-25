import geopandas as gpd
import pandas as pd
import json
# from layout import layout
from config import config
import plotly.express as px
import numpy as np
from plotly.subplots import make_subplots

df_votes_cand_dist = pd.read_csv(config.votes_cand_dist)
df_votes_dist = pd.read_csv(config.votes_dist)
df_votes_cand_town = pd.read_csv(config.votes_cand_town)

color_map = config.color_map
metro_province = {'Korea':['All'], 'Seoul-Gyeonggi':['Seoul', 'Incheon', 'Gyeonggi'], 'Gangwon': ['Gangwon'], 
                'Chungcheong': ['Chungbuk', 'Chungnam', 'Daejeon', 'Sejong'], 'Jeolla': ['Jeonbuk', 'Jeonnam', 'Gwangju'], 
                'Gyeongsang': ['Gyeongbuk', 'Gyeongnam', 'Daegu', 'Busan', 'Ulsan'], 'Jeju': ['Jeju']}

def update_panel(province, metropolitan):

    if province == 'Korea':
        dff = df_votes_dist
    else:
        if metropolitan == 'All':
            dff = df_votes_dist[df_votes_dist.province.isin(metro_province[province])]
        else:
            dff = df_votes_dist[df_votes_dist.province == metropolitan]
    counts = dff.groupby(['win_party']).count()['province']
    result = []
    
    for i in ['더불어민주당', '미래통합당', '정의당', '무소속']:
        try:
            n = str(counts[i])
        except:
            n = '0'
        result.append(n)

    return result

def update_bar_top(province, metropolitan, target):

    if province == 'Korea':
        dff = df_votes_dist[df_votes_dist[target]!=0]
    else:
        if metropolitan == 'All':
            dff = df_votes_dist[(df_votes_dist['province'].isin(metro_province[province])) & (df_votes_dist[target]!=0)]
        else:
            dff = df_votes_dist[(df_votes_dist['province']==metropolitan) & (df_votes_dist[target]!=0)]

    if target == 'win_party':
        dff = dff.groupby(['win_party']).count()['district'].reset_index()
        dff.columns = ['win_party', 'N_winners']
        fig = px.bar(dff, x='N_winners', y='win_party', opacity=0.6, orientation='h', 
                    color='win_party', color_discrete_map=color_map, template='plotly_white')
        fig.update_xaxes(title='Number of winners', tickfont=dict(size=9))
        fig.update_yaxes(tickfont=dict(size=9), title=' '.join(target.split('_')).capitalize(), categoryorder='total ascending')
        fig.update_layout(title=dict(text = 'Number of Winners by Party', x = 0.5, y=0.95))
        fig.update_layout(showlegend=True if province == 'Korea' else False)
        fig.update_layout(legend=dict(x = 0.97))
    else:    
        dff.sort_values(by=[target], ascending=False, inplace=True)
        dff = dff.head(10)
        dff.sort_values(by=[target], inplace=True)
        color = 'province' if province == 'Korea' else None
        fig = px.bar(dff, x='district', y=target, opacity=0.6, color=color, template='plotly_white')
        fig.update_xaxes(title='District', tickfont=dict(size=9), categoryorder='total ascending')
        fig.update_yaxes(range=[min(dff[target]-0.01), max(dff[target])+0.01], tickfont=dict(size=9), title=' '.join(target.split('_')).capitalize())
        fig.update_layout(title=dict(text = 'Highest '+' '.join(target.split('_')).capitalize()+' rate by District', x = 0.5, y=0.95))

    fig.update_layout(margin={"b":10})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig

def update_bar_bottom(province, metropolitan, target):
    
    if province == 'Korea':
        dff = df_votes_dist[df_votes_dist[target]!=0]
    else:
        if metropolitan == 'All':
            dff = df_votes_dist[(df_votes_dist['province'].isin(metro_province[province])) & (df_votes_dist[target]!=0)]
        else:
            dff = df_votes_dist[(df_votes_dist['province']==metropolitan) & (df_votes_dist[target]!=0)]

    if target == 'win_party':
        dff = dff.groupby(['win_party']).count()['district'].reset_index()
        dff.columns = ['win_party', 'N_winners']
        fig = px.bar(dff, x='N_winners', y='win_party', opacity=0.8, orientation='h', color='win_party', color_discrete_map=color_map, template='plotly_white')#, height=280)
        fig.update_xaxes(title='Number of winners', tickfont=dict(size=9))
        fig.update_yaxes(tickfont=dict(size=9), title=' '.join(target.split('_')).capitalize(), categoryorder='total ascending')
        fig.update_layout(title=dict(text = 'Number of Winners by Party', x = 0.5, y=0.95))
        fig.update_layout(showlegend=True if province == 'Korea' else False)
        fig.update_layout(legend=dict(x = 0.97))
    else:
        dff.sort_values(by=[target], inplace=True)
        dff = dff.head(10)
        color = 'province' if province == 'Korea' else None
        fig = px.bar(dff, x='district', y=target, opacity=0.6, color=color, template='plotly_white')
        fig.update_xaxes(title='District', tickfont=dict(size=9), categoryorder='total ascending')
        fig.update_yaxes(range=[min(dff[target]-0.01), max(dff[target])+0.01], tickfont=dict(size=9), title=' '.join(target.split('_')).capitalize())
        fig.update_layout(title=dict(text = 'Lowest '+' '.join(target.split('_')).capitalize()+' rate by District', x = 0.5, y=0.95))
        
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig

def update_radar(metropolitan, district):

    candidates = df_votes_cand_dist[(df_votes_cand_dist['sum'] > 0.1) & (df_votes_cand_dist.province==metropolitan) 
                                    & (df_votes_cand_dist.district==district)].candidate
    dff = df_votes_cand_town[(df_votes_cand_town.province==metropolitan) & (df_votes_cand_town.district==district)]
    dff = dff[dff.party.isin(['더불어민주당', '미래통합당', '무소속', '정의당']) & dff.candidate.isin(candidates)]
    fig = px.line_polar(dff, r='sum', range_r=(0,1), theta='town', color='party', 
                    color_discrete_map=color_map, template='plotly_white', line_close=True)
    fig.update_layout(legend=dict(x = 0.98, y = -0.15))
    fig.update_layout(title=dict(text='Vote rate in {} by town'.format(district.capitalize()), x=0.47, y=0.97))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig


def update_scatter(x_col, y_col):
    
    fig = px.scatter(df_votes_cand_dist, x=x_col, y=y_col, color='party', opacity=0.8, color_discrete_map=color_map, template='plotly_white')
    fig.update_layout(margin={"r":50,"t":30,"l":70,"b":20})
    fig.update_layout(legend_title_text='', legend={'y':-0.15, 'x':0.2}, legend_orientation="h")
    fig.update_xaxes(title=dict(text=' '.join(x_col.split('_')).capitalize() if x_col!='sum' else 'Vote'))
    fig.update_yaxes(title=dict(text=' '.join(y_col.split('_')).capitalize() if y_col!='sum' else 'Vote'))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig

def update_histograms(x_col, y_col):
    
    fig1 = px.histogram(df_votes_cand_dist, x=x_col, color='party', nbins=40, color_discrete_map=color_map, template='plotly_white', opacity=0.8, height=250)
    fig2 = px.histogram(df_votes_cand_dist, x=y_col, color='party', nbins=40, color_discrete_map=color_map, template='plotly_white', opacity=0.8, height=250)
    fig1.update_layout(margin={"r":0,"t":30,"l":70,"b":0})
    fig1.update_layout(legend_title_text='', legend={'y':-0.45, 'x':0.05}, legend_orientation="h")
    fig1.update_layout(title=dict(text='Distribution of '+' '.join(x_col.split('_')).capitalize(), x=0.05, y=0.98))
    fig2.update_layout(margin={"r":0,"t":30,"l":70,"b":0})
    fig2.update_layout(legend_title_text='', legend={'y':-0.45, 'x':0.05}, legend_orientation="h")
    fig2.update_layout(title=dict(text='Distribution of '+' '.join(y_col.split('_')).capitalize(), x=0.05, y=0.98))
    fig1.update_xaxes(title=dict(text=' '.join(x_col.split('_')).capitalize() if x_col!='sum' else 'Vote'))
    fig2.update_xaxes(title=dict(text=' '.join(y_col.split('_')).capitalize() if y_col!='sum' else 'Vote'))
    fig1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig1, fig2