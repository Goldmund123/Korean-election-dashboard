import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from config import config

scatter_variables = ['sum', 'election_day', 'early_voting', 'absentee', 'early_in_person', 'Difference(election day - early voting)']
variable_type = config.variable_type
metro_province = config.metro_province

# dashboard1 style
df_center = pd.read_csv(config.center)
provinces = df_center['province'].unique()

dashboard1 = html.Div(
    [   
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
       
        html.Div(
            [
                html.Div(
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    html.B("2020 Korean Legislative Election"),
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Detailed Overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    html.A(
                        html.Img(src='/static/GitHub-Mark-64px.png', width=40, height=40, style={'margin-left': '330px', 'margin-top':'30px'}),
                        id="github",
                        href='https://github.com/Goldmund123/Korean-election-dashboard'
                    ),
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P("Province:", className="control_label"),
                        dcc.Dropdown(
                            id="province",
                            options=[{"label": i, "value": i} for i in metro_province.keys()],
                            value='Korea',
                            className="dcc_control",
                        ),

                        html.P("Metropolitan area:", className="control_label"),
                        dcc.Dropdown(id="metropolitan", className="dcc_control"),

                        html.P("Filter by variable type:", className="control_label"),
                        dcc.RadioItems(
                            id="variable_type_selector",
                            options=[
                                {"label": "Overall", "value": "overall"},
                                {"label": "더불어민주당", "value": "democrate"},
                                {"label": "미래통합당", "value": "unification"},
                                {"label": "Differences", "value": "differences"},
                            ],
                            value="overall",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        dcc.Dropdown(id="variable", className="dcc_control"),

                        html.P("Highest/Lowest:", className="control_label"),
                        dcc.RadioItems(
                            id="highlow",
                            options=[
                                {"label": "Highest ", "value": "highest"},
                                {"label": "Lowest ", "value": "lowest"},
                            ],
                            value="highest",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [html.H6(id="democrate_text"), html.P("더불어민주당")],
                                    id="democrate",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="unification_text"), html.P("미래통합당")],
                                    id="unification",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="justice_text"), html.P("정의당")],
                                    id="justice",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="no_party_text"), html.P("무소속")],
                                    id="no_party",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="bar_graph")],
                            id="barGraphContainer",
                            className="pretty_container",
                        ),
                    ],
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id="mapbox_graph",
                    clickData={'points': [{'customdata': ['Seoul', '종로구']}]})],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="radar_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P('Please choose two variables:', className="control_label", style={'padding-left': '5px'}),
                        dcc.Dropdown(
                            id='scatter_variables',
                            options=[{'label': ' '.join(i.split('_')).capitalize() if i!='sum' else 'Vote', 'value': i} for i in scatter_variables],
                            value=['election_day', 'early_voting'],
                            multi=True
                        ),
                        dcc.Graph(id="scatter_graph")
                    ],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="histogram1"),
                    dcc.Graph(id="histogram2")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)