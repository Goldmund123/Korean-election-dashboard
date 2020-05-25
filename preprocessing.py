from processing.geo_map import processing_map
from processing import data

def process_map():
    _map = processing_map()
    _map.load_data()
    _map.correct_inputs()
    _map.group_by_district()
    _map.save_json()

def process_data():
    data.votes_by_candidates_districts()
    data.votes_by_candidates_towns()
    data.votes_by_districts()
    data.cal_ratios()

if __name__ == '__main__':
    # process_map()
    process_data()