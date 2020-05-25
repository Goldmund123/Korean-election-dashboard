import geopandas as gpd
import pandas as pd
import numpy as np
import sqlite3
from config import config
con = sqlite3.connect('../data/korea_election_regional_21.sqlite')
district_map = gpd.read_file(config.district_map)
# town_map = gpd.read_file(config.town_map)
votes_cand_dist = config.votes_cand_dist
votes_cand_town = config.votes_cand_town
votes_dist = config.votes_dist

mapping = {'전국': 'Korea', '서울': 'Seoul', '경기': 'Gyeonggi', '인천': 'Incheon', '강원': 'Gangwon',
        '대전': 'Daejeon', '충북': 'Chungbuk', '충남': 'Chungnam', '세종': 'Sejong', 
        '전남': 'Jeonnam', '전북': 'Jeonbuk', '광주': 'Gwangju', '경북': 'Gyeongbuk', '대구': 'Daegu',
        '경남': 'Gyeongnam', '부산':'Busan', '울산':'Ulsan', '제주':'Jeju'}

def votes_by_candidates_districts():
    '''
    Calculate votes and relative ratios by parties.
    The final result will contain the following columns
    province | district | party | candidate | absentee | early_in_person | early_voting | election_day | sum | rank_pre | rank_elec | rank_sum | index
    The index column can be used to draw mapbox style graphs.
    This fuction will generate two different files. 
    One contains numbers of votes, and the other has relative votes ratios between different parties.
    '''

    def load_df():
        df = pd.read_sql("""
                            SELECT a.*, a1.name as province, a2.name as district,
                            a3.name as cat
                            FROM (SELECT candidate.name as candidate, party.name as party, vote.vote, vote.area
                            FROM candidate, party, vote
                            WHERE candidate.party = party.uid
                            AND candidate.uid = vote.candidate) as a
                            inner join area3 as a3 on a3.uid = a.area
                            left join area2 as a2 on a2.uid = a3.area2
                            left join area1 as a1 on a1.uid = a2.area1
                            
                            """, con)
        df[['district', 'other']] = df.district.str.split('-', expand=True)
        df = pd.pivot_table(df, values='vote', index=['province', 'district', 'party', 'candidate'],
                            columns=['cat'], aggfunc=np.sum).reset_index()
        
        return df

    def load_prevote_in():
        df = pd.read_sql("""
                            SELECT a.*, a1.name as province, a2.name as district
                            FROM (SELECT candidate.name as candidate, party.name as party, vote.vote as prevote_in, vote.area
                            FROM candidate, party, vote
                            WHERE candidate.party = party.uid
                            AND candidate.uid = vote.candidate) as a
                            inner join area4 as a4 on a.area = a4.uid
                            left join area3 as a3 on a3.uid = a4.area3
                            left join area2 as a2 on a2.uid = a3.area2
                            left join area1 as a1 on a1.uid = a2.area1
                            
                            where a4.name = 'prevote_in'
                            
                            """, con)
        df[['district', 'other']] = df.district.str.split('-', expand=True)
        df = df.groupby(['province', 'district', 'party', 'candidate']).sum().reset_index()
        df.pop('area')

        return df

    df = load_df()
    prevote_in = load_prevote_in()

    df = df.merge(prevote_in, on=['province', 'district', 'party', 'candidate'])
    df.rename(columns={'prevote_in':'early_in_person', 'prevote_out':'absentee'}, inplace=True)
    df['early_voting'] = df['early_in_person'] + df['absentee']
    df['election_day'] = df['합계'] - (df['absentee'] + df['early_in_person'] + df['거소·선상투표']
                            + df['국외부재자투표'] + df['국외부재자투표(공관)'])
    df.rename(columns={"합계": "sum"}, inplace=True)

    # df['rank_sum'] = df.groupby(['province', 'district'])['sum'].rank("dense", ascending=False).astype(int)
    # df['rank_elec'] = df.groupby(['province', 'district'])['election_day'].rank("dense", ascending=False).astype(int)
    # df['rank_pre'] = df.groupby(['province', 'district'])['prevote'].rank("dense", ascending=False).astype(int)

    cols = ['province', 'district', 'party', 'candidate', 'absentee', 'early_in_person', 'early_voting', 'election_day', 'sum']#, 'rank_pre', 'rank_elec', 'rank_sum']
    df = df[cols]
    df = df.merge(district_map[['province', 'district', 'index']], how='left', on=['province', 'district'])
    df['province'] = pd.Categorical(df['province']).rename_categories(mapping)
    df.to_csv(votes_cand_dist, index=False)


def votes_by_candidates_towns():
    '''
    Calculate votes and relative ratios by parties.
    The final result will contain the following columns
    province | district | town | party | candidate | early_in_person | election_day | sum | rank_pre | rank_reg | rank_sum | index
    The index column can be used to draw mapbox style graphs.
    This fuction will generate two different files. 
    One contains numbers of votes, and the other has relative votes ratios between different parties.
    '''

    def load_df():
        df = pd.read_sql("""
                            SELECT a1.name as province, a2.name as district, a3.name as town, candidate, party, sum(vote) as election_day
                            FROM (SELECT candidate.name as candidate, party.name as party, vote.vote as vote, vote.area
                            FROM candidate, party, vote
                            WHERE candidate.party = party.uid
                            AND candidate.uid = vote.candidate) as a
                            inner join area4 as a4 on a.area = a4.uid
                            left join area3 as a3 on a3.uid = a4.area3
                            left join area2 as a2 on a2.uid = a3.area2
                            left join area1 as a1 on a1.uid = a2.area1
                            
                            where a4.name != 'prevote_in'
                            group by province, district, town, candidate, party
                            order by area
                            
                            """, con)
        df[['district', 'other']] = df.district.str.split('-', expand=True)
        del df['other']
        
        return df

    def load_prevote_in():
        df = pd.read_sql("""
                            SELECT a.*, a1.name as province, a2.name as district, a3.name as town
                            FROM (SELECT candidate.name as candidate, party.name as party, vote.vote as prevote_in, vote.area
                            FROM candidate, party, vote
                            WHERE candidate.party = party.uid
                            AND candidate.uid = vote.candidate) as a
                            inner join area4 as a4 on a.area = a4.uid
                            left join area3 as a3 on a3.uid = a4.area3
                            left join area2 as a2 on a2.uid = a3.area2
                            left join area1 as a1 on a1.uid = a2.area1
                            
                            where a4.name = 'prevote_in'
                            
                            """, con)
        df[['district', 'other']] = df.district.str.split('-', expand=True)
        del df['area'], df['other']

        return df

    df = load_df()
    prevote_in = load_prevote_in()

    df = df.merge(prevote_in, on=['province', 'district', 'town', 'party', 'candidate'])
    df.rename(columns={'prevote_in':'early_in_person', 'prevote_out':'absentee'}, inplace=True)
    df['sum'] = df['election_day'] + df['early_in_person']

    # df['rank_sum'] = df.groupby(['province', 'district', 'town'])['sum'].rank("dense", ascending=False).astype(int)
    # df['rank_elec'] = df.groupby(['province', 'district', 'town'])['election_day'].rank("dense", ascending=False).astype(int)
    # df['rank_pre'] = df.groupby(['province', 'district', 'town'])['early_in_person'].rank("dense", ascending=False).astype(int)

    cols = ['province', 'district', 'town', 'party', 'candidate', 'early_in_person', 'election_day', 'sum']#, 'rank_pre', 'rank_elec', 'rank_sum']
    df = df[cols]
    df['province'] = pd.Categorical(df['province']).rename_categories(mapping)
    df.to_csv(votes_cand_town, index=False)


def votes_by_districts():

    def load_candidates():
        df = pd.read_sql("""
                        SELECT a.*, a1.name as province, a2.name as district,
                        a3.name as cat
                        FROM (SELECT candidate.name as candidate, party.name as party, vote.vote, vote.area
                        FROM candidate, party, vote
                        WHERE candidate.party = party.uid
                        AND candidate.uid = vote.candidate
                        AND party.name in ('더불어민주당', '미래통합당', '정의당', '무소속')) as a
                        inner join area3 as a3 on a3.uid = a.area
                        left join area2 as a2 on a2.uid = a3.area2
                        left join area1 as a1 on a1.uid = a2.area1
                        where cat = '합계'
                        """, con)

        party = []
        for i, c in df.iterrows():
            if c['party'] != '무소속':
                party.append(c['party'])
            else:
                if party[-1] not in ('무소속1', '무소속2', '무소속3'):
                    party.append('무소속1')
                elif party[-1] == '무소속1':
                    party.append('무소속2')
                else:
                    party.append('무소속3')

        df.party = party

        df[['district', 'other']] = df.district.str.split('-', expand=True)
        df = pd.pivot_table(df, values='vote', index=['province', 'district'],
                            columns=['party'], aggfunc=np.sum, fill_value=0).reset_index()
        
        return df

    def load_prevote_in():
        df = pd.read_sql("""
                            SELECT a1.name as province, a2.name as district,
                            a3.name as cat, a3.uid as cat_uid, a4.uid as polls_id, 
                            a4.sum_vote+a4.sum_novote as sum,
                            a4.sum_vote-a4.sum_invalid as val,
                            a4.sum_invalid as inv
                            
                            FROM area4 as a4 
                            left join area3 as a3 on a3.uid = a4.area3
                            left join area2 as a2 on a2.uid = a3.area2
                            left join area1 as a1 on a1.uid = a2.area1
                            
                            WHERE prevote = 1
                            """, con)

        df[['district', 'other']] = df.district.str.split('-', expand=True)
        del df['cat_uid'], df['polls_id']
        df = df.groupby(['province', 'district']).sum().reset_index()
        df.columns = [c+'|early_in_person' if c not in ('province', 'district') else c for c in df.columns]

        return df

    def load_df():
        df = pd.read_sql("""
                            SELECT a1.name as province, a2.name as district,
                            a3.name as cat, a3.uid as cat_uid, a3.sum_people as sum, 
                            a3.sum_vote - a3.sum_invalid as val, 
                            a3.sum_invalid as inv
                            
                            FROM area3 as a3 
                            left join area2 as a2 on a3.area2 = a2.uid
                            left join area1 as a1 on a2.area1 = a1.uid
                            
                            WHERE cat in ('prevote_out', '합계', '거소·선상투표', '국외부재자투표', '국외부재자투표(공관)')
                            
                            """, con)

        df[['district', 'other']] = df.district.str.split('-', expand=True)
        df = pd.pivot_table(df, values=['sum', 'val', 'inv'], index=['province', 'district'],
                                columns=['cat'], aggfunc=np.sum, fill_value=0).reset_index()
        df.rename(columns={'prevote_out':'absentee'}, inplace=True)
        df.columns = df.columns.map('|'.join).str.strip('|')
        df['inv|other'] = df['inv|거소·선상투표']+df['inv|국외부재자투표']+df['inv|국외부재자투표(공관)']
        df['sum|other'] = df['sum|거소·선상투표']+df['sum|국외부재자투표']+df['sum|국외부재자투표(공관)']
        df['val|other'] = df['val|거소·선상투표']+df['val|국외부재자투표']+df['val|국외부재자투표(공관)']
        df = df.drop(['inv|거소·선상투표', 'inv|국외부재자투표', 'inv|국외부재자투표(공관)',
                    'sum|거소·선상투표', 'sum|국외부재자투표', 'sum|국외부재자투표(공관)',
                    'val|거소·선상투표', 'val|국외부재자투표', 'val|국외부재자투표(공관)'], axis = 1)
        
        return df

    df = load_df()
    prevote_in = load_prevote_in()
    candidates = load_candidates()

    df = df.merge(prevote_in, on=['province', 'district'])
    df = df.merge(candidates, on=['province', 'district'])

    votes_dist_df = df[['province', 'district']]
    votes_dist_df['win_party'] = df.iloc[:, -6:].idxmax(axis=1)
    votes_dist_df['win_party'] = votes_dist_df['win_party'].str.replace('\d+', '')
    votes_dist_df['turnout'] = ((df['val|합계'] + df['inv|합계'])/df['sum|합계']).round(4)
    votes_dist_df['election_day'] = ((df['val|합계'] + df['inv|합계'] 
                                - df['val|early_in_person'] - df['val|absentee'] - df['val|other']
                                - df['inv|early_in_person'] - df['inv|absentee'] - df['inv|other'])/df['sum|합계']).round(4)
    votes_dist_df['early_voting'] = ((df['val|early_in_person'] + df['val|absentee'] + 
                                df['inv|early_in_person'] + df['inv|absentee'])/df['sum|합계']).round(4)

    votes_dist_df = votes_dist_df.merge(district_map[['province', 'district', 'index']], how='left', on=['province', 'district'])
    votes_dist_df['province'] = pd.Categorical(votes_dist_df['province']).rename_categories(mapping)

    votes_cand_dist_df = pd.read_csv(votes_cand_dist)
    votes_dist_df = votes_dist_df.merge(votes_cand_dist_df[votes_cand_dist_df.party=='더불어민주당'][['province', 'district', 'early_voting', 'election_day']], how='left', on = ['province', 'district'], suffixes=['', '_'])
    votes_dist_df['더불어민주당_vote'] = df['더불어민주당'] / df['val|합계']
    votes_dist_df['더불어민주당_early_voting'] = votes_dist_df['early_voting_'] / (df['val|early_in_person'] + df['val|absentee'])
    votes_dist_df['더불어민주당_election_day'] = votes_dist_df['election_day_'] / (df['val|합계'] + df['inv|합계'] 
                                - df['val|early_in_person'] - df['val|absentee'] - df['val|other']
                                - df['inv|early_in_person'] - df['inv|absentee'] - df['inv|other'])
    del votes_dist_df['early_voting_'], votes_dist_df['election_day_']

    votes_dist_df = votes_dist_df.merge(votes_cand_dist_df[votes_cand_dist_df.party=='미래통합당'][['province', 'district', 'early_voting', 'election_day']], how='left', on = ['province', 'district'], suffixes=['', '_'])
    votes_dist_df['미래통합당_vote'] = df['미래통합당'] / df['val|합계']
    votes_dist_df['미래통합당_early_voting'] = votes_dist_df['early_voting_'] / (df['val|early_in_person'] + df['val|absentee'])
    votes_dist_df['미래통합당_election_day'] = votes_dist_df['election_day_'] / (df['val|합계'] + df['inv|합계'] 
                                - df['val|early_in_person'] - df['val|absentee'] - df['val|other']
                                - df['inv|early_in_person'] - df['inv|absentee'] - df['inv|other'])
    del votes_dist_df['early_voting_'], votes_dist_df['election_day_']

    votes_dist_df.fillna(0, inplace=True)
    votes_dist_df['vote(더불어민주당 - 미래통합당)'] = votes_dist_df['더불어민주당_vote'] - votes_dist_df['미래통합당_vote']
    votes_dist_df['early_voting(더불어민주당 - 미래통합당)'] = votes_dist_df['더불어민주당_early_voting'] - votes_dist_df['미래통합당_early_voting']
    votes_dist_df['election_day(더불어민주당 - 미래통합당)'] = votes_dist_df['더불어민주당_election_day'] - votes_dist_df['미래통합당_election_day']

    votes_dist_df.to_csv(votes_dist, index=False)

def cal_ratios():

    # calculate ratios of votes_cand_dist file.
    votes_cand_dist_df = pd.read_csv(votes_cand_dist)
    cols = ['province', 'district', 'absentee', 'early_in_person', 'early_voting', 'election_day', 'sum']
    sum_df = votes_cand_dist_df[cols].groupby(['province', 'district']).transform('sum')
    cols = ['absentee', 'early_in_person', 'early_voting', 'election_day', 'sum']
    votes_cand_dist_df[cols] = votes_cand_dist_df[cols]/sum_df[cols]

    votes_cand_dist_df['Difference(election day - early voting)'] = votes_cand_dist_df['election_day'] - votes_cand_dist_df['early_voting']

    votes_cand_dist_df = votes_cand_dist_df[votes_cand_dist_df.party.isin(["더불어민주당", "미래통합당", "정의당", "무소속"])]
    votes_cand_dist_df['party'] = pd.Categorical(votes_cand_dist_df['party'], ["더불어민주당", "미래통합당", "정의당", "무소속"])
    votes_cand_dist_df = votes_cand_dist_df.sort_values(['province', 'district', 'party', 'sum'], ascending=(True, True, True, False))
    votes_cand_dist_df.to_csv(votes_cand_dist, index=False)

    # calculate ratios of votes_cand_town file.
    votes_cand_town_df = pd.read_csv(votes_cand_town)
    cols = ['province', 'district', 'town', 'early_in_person', 'election_day', 'sum']
    sum_df = votes_cand_town_df[cols].groupby(['province', 'district', 'town']).transform('sum')
    cols = ['early_in_person', 'election_day', 'sum']
    votes_cand_town_df[cols] = votes_cand_town_df[cols]/sum_df[cols]

    votes_cand_town_df = votes_cand_town_df[votes_cand_town_df.party.isin(["더불어민주당", "미래통합당", "정의당", "무소속"])]
    votes_cand_town_df['party'] = pd.Categorical(votes_cand_town_df['party'], ["더불어민주당", "미래통합당", "정의당", "무소속"])
    votes_cand_town_df = votes_cand_town_df.sort_values(['province', 'district', 'town', 'party', 'sum'], ascending=(True, True, True, True, False))
    votes_cand_town_df.to_csv(votes_cand_town, index=False)