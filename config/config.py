from pathlib import Path
path = Path().resolve()

# path of maps
disparity_mapping = str(path)+'/data/map/address_disparity_mapping.csv'
adm_dist_mapping = str(path)+'/data/map/address_district_mapping_ver20200314.xlsx'  # https://www.1023labs.com/posts/66
geo_data = str(path)+'/data/map/HangJeongDong_ver20200401.geojson'  # https://github.com/vuski/admdongkor
district_map = str(path)+'/data/map/district_map.geojson'
district_map_compressed = str(path)+'/data/map/district_map_compressed.geojson'

# path of data
votes_cand_dist = str(path)+'/data/votes_by_candidates_districts.csv'
votes_cand_town = str(path)+'/data/votes_by_candidates_towns.csv'
votes_dist = str(path)+'/data/votes_by_districts.csv'
center = str(path)+'/data/center.csv'

# variables
metro_province = {'Korea':['All'], 'Seoul-Gyeonggi':['All', 'Seoul', 'Incheon', 'Gyeonggi'], 'Gangwon': ['All'], 
                'Chungcheong': ['All', 'Chungbuk', 'Chungnam', 'Daejeon', 'Sejong'], 'Jeolla': ['All', 'Jeonbuk', 'Jeonnam', 'Gwangju'], 
                'Gyeongsang': ['All', 'Gyeongbuk', 'Gyeongnam', 'Daegu', 'Busan', 'Ulsan'], 'Jeju': ['All']}

variable_type = {'overall': ['win_party', 'turnout', 'early_voting', 'election_day'],
                'democrate': ['더불어민주당_vote', '더불어민주당_early_voting', '더불어민주당_election_day'],
                'unification': ['미래통합당_vote', '미래통합당_early_voting', '미래통합당_election_day'],
                'differences': ['vote(더불어민주당 - 미래통합당)', 'early_voting(더불어민주당 - 미래통합당)', 'election_day(더불어민주당 - 미래통합당)']}

color_map = {'무소속': 'grey', '정의당': 'rgb(119, 221, 119)', '미래통합당': 'rgb(255, 149, 170)', '더불어민주당':'rgb(114, 148, 207)'}