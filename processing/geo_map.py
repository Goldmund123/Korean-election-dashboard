import geopandas as gpd
import pandas as pd
import numpy as np
import json
from config import config
from shapely.geometry import Polygon
from shapely.ops import cascaded_union


class processing_map:

    def __init__(self):
        self.disparity_mapping = config.disparity_mapping
        self.adm_dist_mapping = config.adm_dist_mapping 
        self.geo_data = config.geo_data
        self.district_map = config.district_map
        self.district_map_compressed = config.district_map_compressed

    def load_data(self):
        self.map = gpd.read_file(self.geo_data)
        self.adm_dist_mapping_df = pd.read_excel(self.adm_dist_mapping, '행정동 & 선거구', usecols="A,F")
        self.disparity_mapping_df = pd.read_csv(self.disparity_mapping)

    def correct_inputs(self):
        #fix wrong inputs
        self.map.adm_cd2[self.map.adm_nm=='경기도 의정부시 의정부3동'] = 4115051000
        self.map.adm_nm[self.map.adm_nm=='경기도 의정부시 의정부3동'] = '경기도 의정부시 의정부1동'
        
        #mapping address disparity
        self.adm_dist_mapping_df.columns = ['adm_cd2', 'district1']
        self.map.adm_cd2 = self.map.adm_cd2.astype(np.int64)
        self.map = self.map.merge(self.adm_dist_mapping_df, how='left', on='adm_cd2')

        self.map[['adm_province', 'adm_district', 'adm_town']] = self.map.adm_nm.str.split(' ', expand=True)
        self.map.adm_province = self.map.adm_province.str.strip()
        self.map.district1 = self.map.district1.str.strip()
        self.map = self.map.merge(self.disparity_mapping_df, on=['adm_province', 'district1'])
        self.map.district = self.map.district.str.strip()
        #need to fix for more detailed mapping
        self.map = self.map[['province', 'district', 'adm_town', 'geometry']]

    def group_by_district(self):
        province = self.map.province.unique()
        district = self.map.district.unique()

        district_map = []
        district_map_compressed = []

        for p in province:
            for d in district:
                if len(self.map[(self.map.province == p) & (self.map.district == d)]):
                    group = [geo for geo in self.map[(self.map.province == p) & (self.map.district == d)]['geometry']]
                    merged = cascaded_union(group)
                    merged1 = merged.simplify(0.002, preserve_topology=True)
                    merged2 = merged.simplify(0.02, preserve_topology=True)
                    district_map.append([p, d, merged1])
                    district_map_compressed.append([p, d, merged2])
        self.map = gpd.GeoDataFrame(district_map).reset_index()
        self.map.columns = ['index', 'province', 'district', 'geometry']

        self.map_compressed = gpd.GeoDataFrame(district_map_compressed).reset_index()
        self.map_compressed.columns = ['index', 'province', 'district', 'geometry']

    def save_json(self):
        self.map.to_file(self.district_map, driver="GeoJSON")
        self.map_compressed.to_file(self.district_map_compressed, driver="GeoJSON")
