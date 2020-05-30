import geopandas as gpd
import pandas as pd
import json
from config import config
import plotly.graph_objects as go
import os

token = os.environ['MAPBOX_TOKEN']

df = pd.read_csv(config.votes_dist)
df_map = gpd.read_file(config.district_map)
df_map_compressed = gpd.read_file(config.district_map_compressed)
df_center = pd.read_csv(config.center)

provinces = df_center['province'].unique()

rev_mapping = {'Korea':'전국', 'Seoul':'서울', 'Gyeonggi':'경기', 'Incheon':'인천', 'Gangwon':'강원',
            'Daejeon':'대전', 'Chungbuk':'충북', 'Chungnam':'충남', 'Sejong':'세종', 
            'Jeonnam':'전남', 'Jeonbuk':'전북', 'Gwangju':'광주', 'Gyeongbuk':'경북', 'Daegu':'대구',
            'Gyeongnam':'경남', 'Busan':'부산', 'Ulsan':'울산', 'Jeju':'제주'}

metro_province = {'Korea':['All'], 'Seoul-Gyeonggi':['Seoul', 'Incheon', 'Gyeonggi'], 'Gangwon': ['Gangwon'], 
                'Chungcheong': ['Chungbuk', 'Chungnam', 'Daejeon', 'Sejong'], 'Jeolla': ['Jeonbuk', 'Jeonnam', 'Gwangju'], 
                'Gyeongsang': ['Gyeongbuk', 'Gyeongnam', 'Daegu', 'Busan', 'Ulsan'], 'Jeju': ['Jeju']}

def update_geo_graph(province, metropolitan, target):
    if province == 'Korea':
        dff = df
        dff_map = json.loads(df_map_compressed.to_json())
        center = df_center[df_center['province'] == 'Korea'].values[0][1:]
    else:
        if metropolitan == 'All':
            dff = df[(df['province'].isin(metro_province[province]))]
            map_province = [rev_mapping[p] for p in metro_province[province] if p !='All']
            dff_map = json.loads(df_map[df_map['province'].isin(map_province)].to_json())
            center = df_center[df_center['province'] == province].values[0][1:]
        else:
            dff = df[df['province']==metropolitan]
            dff_map = json.loads(df_map[df_map['province']==rev_mapping[metropolitan]].to_json())
            center = df_center[df_center['province'] == metropolitan].values[0][1:]
    
    if target == 'win_party':
        mapping = {'더불어민주당': 1, '미래통합당': 0.6, '정의당': 0.3, '무소속': 0}
        dff['color'] = pd.Categorical(dff['win_party']).rename_categories(mapping)

        parties = ['무소속', '정의당', '미래통합당', '더불어민주당']
        colorscale = [[0, 'gray'], [0.25, 'gray'], [0.25, 'rgb(119, 221, 119)'], [0.5, 'rgb(119, 221, 119)'],
            [0.5, 'rgb(255, 149, 170)'], [0.75, 'rgb(255, 149, 170)'], [0.75, 'rgb(114, 148, 207)'], [1, 'rgb(114, 148, 207)']]

        fig = go.Figure(go.Choroplethmapbox(
                geojson=dff_map, 
                locations=dff['index'], 
                z=dff['color'],
                zmin = 0, 
                zmax = 1,
                colorscale=colorscale, 
                customdata=dff.iloc[:, :2].values,
                hovertemplate='<b>%{customdata[1]}</b><br> Metropolitan: %{customdata[0]}<extra></extra>',
                colorbar={
                        'outlinewidth': 0, 'tickvals': [0.125, 0.375, 0.625, 0.875],
                        'ticktext': parties, 'thickness': 20, 
                        'xanchor': 'right', 'yanchor': 'bottom',
                        'x': 0.98, 'y': 0.03, 
                        'title': {'text': ''},
                        'len': 0.2, 'bgcolor':'rgba(255,255,255,0.6)'},
                marker_opacity=0.8, 
                marker_line_width=0))
        
    else:
        fig = go.Figure(go.Choroplethmapbox(
                geojson=dff_map, 
                locations=dff['index'], 
                z=dff[target],
                zmin=min(df[target]),
                zmax=max(df[target]),
                colorscale='YlGnBu', 
                customdata=dff.iloc[:, :2].values,
                hovertemplate='<b>%{customdata[1]}</b><br> Metropolitan: %{customdata[0]}<extra></extra>',
                colorbar={
                        'outlinewidth': 0, 
                        'len':0.4, 'thickness': 30, 
                        'xanchor': 'right', 'yanchor': 'middle',
                        'x': 0.98, 'y':0.5, 
                        'title': {'text': ''},
                        'bgcolor':'rgba(255,255,255,0.6)'},
                marker_opacity=0.8, 
                marker_line_width=0))

    if province == 'Korea':
        fig.update_traces(marker=dict(line=dict(width=0.5, color='white')))
    else:
        fig.update_traces(marker=dict(line=dict(width=1, color='white')))
    
    fig.update_layout(mapbox_zoom=center[2]-0.3, mapbox_center = {"lon": center[0], "lat": center[1]})
    fig.update_layout(mapbox_style='light', mapbox_accesstoken=token)
    fig.update_layout(margin=dict(l=0, r=0, b=0, t=30))
    fig.update_layout(title={'text':'Geographical Overview', 'x':0.50, 'y':.99})
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    return fig