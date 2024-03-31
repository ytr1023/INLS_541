import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

data = pd.read_excel('CRIME.xlsx')
race_data = pd.read_csv('table-data.csv')
social_data = pd.read_excel('social_data.xlsx')
data.columns = ['State', 'City', 'Year', 'Population', 'ViolentCrime', 'Murder', 'Rape', 'Robbery', 'AggravatedAssault', 'PropertyCrime', 'Burglary', 'LarcenyTheft', 'MotorVehicleTheft', 'Arson', 'Unnamed14', 'Unnamed15', 'Unnamed16']

data = data.drop(['Unnamed14', 'Unnamed15', 'Unnamed16'], axis=1)
columns_to_convert = ['Population', 'ViolentCrime', 'Murder', 'Rape', 'Robbery', 'AggravatedAssault', 'PropertyCrime', 'Burglary', 'LarcenyTheft', 'MotorVehicleTheft', 'Arson']

for column in columns_to_convert:
    data[column] = pd.to_numeric(data[column], errors='coerce')
year_options = [
    {'label': 'All Years', 'value': 'All'},
    {'label': '2008', 'value': 2008},
    {'label': '2009', 'value': 2009}
]
state_crime_totals = data
state_crime_totals.head()
state_abbreviations = {
    'ALABAMA': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
    'District of Columbia': 'DC', 'U.S. total': 'US'
}

state_abbreviations_upper = {k.upper(): v for k, v in state_abbreviations.items()}
state_crime_totals['State'] = state_crime_totals['State'].map(state_abbreviations_upper)
race_data['State'] = race_data['State'].str.upper()
race_data['State'] = race_data['State'].map(state_abbreviations_upper)
social_data['State'] = social_data['State'].str.upper()
social_data['State'] = social_data['State'].map(state_abbreviations_upper)
state_crime_totals["Population"].fillna(method='ffill', inplace=True)
state_crime_totals['vio_crime_per_thousand'] = state_crime_totals['ViolentCrime'] / state_crime_totals['Population'] * 1000
state_violent_crime_totals = state_crime_totals.groupby('State')['vio_crime_per_thousand'].sum().reset_index()


state_crime_totals.head()
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.H1('Crime Statistics Dashboard', style={'textAlign': 'center', 'marginBottom': '20px'}),

    html.Div([
        dcc.Dropdown(
            id='year-dropdown',
            options=year_options,
            value='All', 
            clearable=False,
            style={'width': '200px', 'minHeight': '30px', 'height': '30px', 'lineHeight': '30px'}
        ),
    ], style={'width': '200px', 'display': 'inline-block', 'padding': '10px'}),
    
    dcc.Graph(id='us-map'), 
    dcc.Graph(id='crime-bar-chart'),
    dcc.Graph(id='crime-type-chart'),
    html.Div([
        dcc.Graph(id='race-distribution-chart')
    ], style={'width': '50%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='social-chart')
    ], style={'width': '50%', 'display': 'inline-block'})
])

@app.callback(
    Output('us-map', 'figure'),
    [Input('year-dropdown', 'value')])
def update_map(selected_year):
    if selected_year == 'All':
        filtered_data = state_crime_totals
    else:
        filtered_data = state_crime_totals[state_crime_totals['Year'] == selected_year]
    
    state_violent_crime_totals = filtered_data.groupby('State')['vio_crime_per_thousand'].sum().reset_index()
    
    map_fig = px.choropleth(state_violent_crime_totals, 
                            locations='State', 
                            locationmode="USA-states", 
                            color='vio_crime_per_thousand', 
                            scope="usa",
                            color_continuous_scale=['#feedde', '#fdbe85', '#fd8d3c', "#d94701"]) 
    
    map_fig.update_layout(
        title_text='Violent Crime per Thousand People by State', 
        title_x=0.5,
    )
    return map_fig


@app.callback(
    [Output('crime-bar-chart', 'figure'),
     Output('crime-type-chart', 'figure')],
    [Input('us-map', 'clickData'),
     Input('year-dropdown', 'value')])
def update_charts(clickData, selected_year):
    state = 'AL'
    if clickData is not None:
        state = clickData['points'][0]['location']
    if selected_year == 'All':
        filtered_data = state_crime_totals[state_crime_totals['State'] == state]
        filtered_data['Year'] = filtered_data['Year'].astype(str)
    else:
        filtered_data = state_crime_totals[(state_crime_totals['State'] == state) & (state_crime_totals['Year'] == selected_year)]
        filtered_data['Year'] = filtered_data['Year'].astype(str)
        
    
    bar_fig = px.bar(filtered_data, x='City', y='vio_crime_per_thousand', title=f'{state} Violent Crime per Thousand People', 
                     barmode='group', color='Year', color_discrete_sequence=['#9BBBE1', "#F09BA0"])  # 指定颜色
    bar_fig.update_layout(yaxis_title='Violant Crimes per thousand people')
    crime_types = ['Murder', 'Rape', 'Robbery', 'AggravatedAssault']
    type_fig = px.bar(filtered_data, x='City', y=crime_types, title=f'{state} total Crime Types', barmode='group', color_discrete_sequence=['#8ECFC9', "#FFBE7A", "#FA7F6F", "#82B0D2"])
    type_fig.update_layout(yaxis_title='Number of Incidents')
    type_fig.update_layout(legend_title_text='Violent Crime Type')
    
    return bar_fig, type_fig


@app.callback(
    [Output('race-distribution-chart', 'figure')],
    [Input('us-map', 'clickData')])
def update_charts(clickData):
    state = 'AL'
    if clickData is not None:
        state = clickData['points'][0]['location']

    filtered_data = race_data[race_data['State'] == state]
    
    race_types = ["WhiteTotalPerc", "BlackTotalPerc", 'IndianTotalPerc', 'AsianTotalPerc', 'HawaiianTotalPerc', 'OtherTotalPerc']
    values = [filtered_data[col].values[0] for col in race_types]
    names = ['White', 'Black', 'Indian', 'Asian', 'Hawaiian', 'Other']
    race_fig = px.pie(values=values, names=names, title=f'Race Distribution in {state}')
    race_fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return [race_fig]

@app.callback(
    [Output('social-chart', 'figure')],
    [Input('us-map', 'clickData')]
)
def update_social_charts(clickData):
    state = 'AL' 
    if clickData is not None:
        state = clickData['points'][0]['location']

    fig = make_subplots(rows=2, cols=2, subplot_titles=("Unemployment_rate", "Education_rate", "Median_Income", "Poverty_rate"))

    indicators = ["Unemployment_rate", "Education_rate", "Median_Income", "Poverty_rate"]
    row_col_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
    
    for index, (indicator, position) in enumerate(zip(indicators, row_col_positions)):
        state_value = social_data[social_data['State'] == state][indicator].values[0]
        us_average_value = social_data[social_data['State'] == 'US'][indicator].values[0]

        state_trace = go.Bar(name=state, x=[indicator], y=[state_value], marker_color='#a7c957', showlegend=index == 0)
        us_trace = go.Bar(name='US Average', x=[indicator], y=[us_average_value], marker_color='#eca77f', showlegend=index == 0)
        
        fig.add_trace(state_trace, row=position[0], col=position[1])
        fig.add_trace(us_trace, row=position[0], col=position[1])
    
    fig.update_layout(height=450, width=774.5, title_text=f'{state} Social Data', barmode='group')
    return [fig]

if __name__ == '__main__':
    app.run_server(debug=True)
