import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

data = pd.read_excel('CRIME.xlsx')

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
    'District of Columbia': 'DC'
}

state_abbreviations_upper = {k.upper(): v for k, v in state_abbreviations.items()}
state_crime_totals['State'] = state_crime_totals['State'].map(state_abbreviations_upper)
state_crime_totals["Population"].fillna(method='ffill', inplace=True)
state_crime_totals['vio_crime_per_thousand'] = state_crime_totals['ViolentCrime'] / state_crime_totals['Population'] * 1000
state_violent_crime_totals = state_crime_totals.groupby('State')['vio_crime_per_thousand'].sum().reset_index()


state_crime_totals.head()
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(children=[
    html.Div([
        dcc.Dropdown(
            id='year-dropdown',
            options=year_options,
            value=year_options[0]['value'], 
            clearable=False
        )
    ]),
    dcc.Graph(id='us-map'),
    dcc.Graph(id='crime-bar-chart'),
    dcc.Graph(id='crime-type-chart')
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
                            scope="usa")
    return map_fig

app.layout = html.Div(children=[
    html.Div([
        dcc.Dropdown(
            id='year-dropdown',
            options=year_options,
            value='All', 
            clearable=False
        )
    ]),
    dcc.Graph(id='us-map'), 
    dcc.Graph(id='crime-bar-chart'),
    dcc.Graph(id='crime-type-chart')
])

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
        
    
    bar_fig = px.bar(filtered_data, x='City', y='vio_crime_per_thousand', title=f'{state} Violent Crime per thoudand perple', barmode='group', color='Year')
    bar_fig.update_layout(yaxis_title='Violant Crimes per thousand people')
    crime_types = ['Murder', 'Rape', 'Robbery', 'AggravatedAssault']
    type_fig = px.bar(filtered_data, x='City', y=crime_types, title=f'{state} total Crime Types', barmode='group')
    type_fig.update_layout(yaxis_title='Number of Incidents')
    type_fig.update_layout(legend_title_text='Violent Crime Type')
    
    return bar_fig, type_fig

if __name__ == '__main__':
    app.run_server(debug=True)
