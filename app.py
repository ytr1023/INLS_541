import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# 加载数据
data = pd.read_excel('C:/Users/yetia/Downloads/CRIME.xlsx')

# 数据预处理
# 清理列名
data.columns = ['State', 'City', 'Year', 'Population', 'ViolentCrime', 'Murder', 'Rape', 'Robbery', 'AggravatedAssault', 'PropertyCrime', 'Burglary', 'LarcenyTheft', 'MotorVehicleTheft', 'Arson', 'Unnamed14', 'Unnamed15', 'Unnamed16']
# 去除不需要的列和行
data = data.drop(['Unnamed14', 'Unnamed15', 'Unnamed16'], axis=1)
columns_to_convert = ['Population', 'ViolentCrime', 'Murder', 'Rape', 'Robbery', 'AggravatedAssault', 'PropertyCrime', 'Burglary', 'LarcenyTheft', 'MotorVehicleTheft', 'Arson']

# 使用pd.to_numeric转换，遇到无法转换的设置为NaN
for column in columns_to_convert:
    data[column] = pd.to_numeric(data[column], errors='coerce')

# 再次尝试汇总数据
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
state_violent_crime_totals = state_crime_totals.groupby('State')['ViolentCrime'].sum().reset_index()


state_crime_totals.head()
# 构建Dash应用
app = dash.Dash(__name__)

# 地图展示每个州的犯罪数量
map_fig = px.choropleth(state_violent_crime_totals, 
                        locations='State', 
                        locationmode="USA-states", 
                        color='ViolentCrime',  # 或其他犯罪统计作为颜色
                        scope="usa")

app.layout = html.Div(children=[
    dcc.Graph(id='us-map', figure=map_fig),
    dcc.Graph(id='crime-bar-chart'),
    dcc.Graph(id='crime-type-chart')
])

@app.callback(
    [Output('crime-bar-chart', 'figure'),
     Output('crime-type-chart', 'figure')],
    [Input('us-map', 'clickData')])
def update_charts(clickData):
    state = 'AL'  # 默认值
    if clickData is not None:
        state = clickData['points'][0]['location']
    
    # 根据选择的州过滤数据
    filtered_data = state_crime_totals[state_crime_totals['State'] == state]
    
    # 创建柱状图：展示该州的犯罪总数
    bar_fig = px.bar(filtered_data, x='City', y='ViolentCrime', title=f'{state} Violent Crime')
    
    # 创建条形图：展示该州具体的犯罪类型
    crime_types = ['Murder', 'Rape', 'Robbery', 'AggravatedAssault']
    type_fig = px.bar(filtered_data, x='City', y=crime_types, title=f'{state} Crime Types', barmode='group')
    
    return bar_fig, type_fig

if __name__ == '__main__':
    app.run_server(debug=True)
