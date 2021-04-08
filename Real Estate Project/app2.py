import pandas as pd
import numpy as np 
import seaborn as sns
import matplotlib.pyplot as plt 
from datetime import datetime 
import plotly.graph_objs as go 
import csv 
import warnings
warnings.filterwarnings('ignore')

''' 
BOROUGH: A digit code Manhattan (1), Bronx (2), Brooklyn (3), Queens (4), and Staten Island (5).
BLOCK; LOT: The combination of borough, block, and lot forms a unique key for property in New York City. Commonly called a BBL.
BUILDING CLASS AT PRESENT and BUILDING CLASS AT TIME OF SALE: The type of building at various points in time. 
'''
#grab data from desktop 
pd.set_option('display.max.columns', 30)
df = pd.read_csv(r'/Users/Dhan004/Desktop/nyc-rolling-sales.csv', low_memory=False)
df['SALE DATE'] = pd.to_datetime(df['SALE DATE'])
df.sort_values('SALE DATE', ascending=False)
df = df[['BOROUGH', 'NEIGHBORHOOD', 'BUILDING CLASS CATEGORY',
       'TAX CLASS AT PRESENT', 'BLOCK', 'LOT', 'EASE-MENT',
       'BUILDING CLASS AT PRESENT', 'ADDRESS', 'APARTMENT NUMBER', 'ZIP CODE',
       'RESIDENTIAL UNITS', 'COMMERCIAL UNITS', 'TOTAL UNITS',
       'LAND SQUARE FEET', 'GROSS SQUARE FEET', 'YEAR BUILT',
       'TAX CLASS AT TIME OF SALE', 'BUILDING CLASS AT TIME OF SALE',
       'SALE PRICE', 'SALE DATE']]
#replace '-' to zero and convert data type to object to integer
df['SALE PRICE'] = df['SALE PRICE'].replace([' -  '], 0)
df['SALE PRICE'].astype('int64')
df['YEAR'] = pd.to_datetime(df['SALE DATE']).dt.year

#Use Plotly Graphs to prebuild analytics  
import dash 
import dash_core_components as dcc 
import dash_html_components as html 
from dash.dependencies import Input, Output 
import dash_table as dt 
import dash_auth 
#first section indictors of average sales price
#2016 Average Sales Price - 2016 
year_2016 = df.loc[df['YEAR'] == 2016]
year_2016['SALE PRICE'].astype('int64')
year_2016['SALE PRICE'] = pd.to_numeric(year_2016['SALE PRICE'])
means_2016 = year_2016['SALE PRICE'].mean()
average_sales_price2016 = np.round(means_2016, decimals=2)
#2017 Average Sale Price - 2017 
year_2017 = df.loc[df['YEAR'] == 2017]
year_2017['SALE PRICE'].astype('int64')
year_2017['SALE PRICE'] = pd.to_numeric(year_2017['SALE PRICE'])
means_2017 = year_2017['SALE PRICE'].mean()
average_sales_price2017 = np.round(means_2017, decimals=2)
indicator1 = go.Figure(data=[go.Indicator(value=average_sales_price2016, title='Average Sale Price - 2016')], layout=go.Layout({'paper_bgcolor':'black', 'font_color': 'white'}))
indicator2 = go.Figure(data=[go.Indicator(value=average_sales_price2017, title='Average Sale Price - 2017')], layout=go.Layout({'paper_bgcolor':'black', 'font_color': 'white'}))

# dash plotly - barchart get total units residential units vs. Commercial Units 
borough = df.groupby(['BOROUGH'])[['RESIDENTIAL UNITS', 'COMMERCIAL UNITS']].agg('sum').reset_index()
colors = ['coral', 'aqua', 'red']

#figure barchart numbers of units by BOROUGH - Residential Units vs. Commercial Units
bar1 = go.Figure(data=[go.Bar(name='Resisential Units', x=borough['BOROUGH'], y=borough['RESIDENTIAL UNITS'], hovertext=borough['RESIDENTIAL UNITS'], marker_color='coral'), 
                      go.Bar(name='Commercial Units', x=borough['BOROUGH'], y=borough['COMMERCIAL UNITS'], hovertext=borough['COMMERCIAL UNITS'], marker_color='aqua')], layout=go.Layout({'barmode':'group','paper_bgcolor':'#111111','plot_bgcolor':'gray'}))

#figure bar horizontal - TOp 10 
borough = df.groupby(['BOROUGH'])[['RESIDENTIAL UNITS', 'COMMERCIAL UNITS']].agg('sum').reset_index()
colors = ['coral', 'aqua', 'red']

#section 2 

#Top 10 Neighbors 
neighborhoods = df.groupby('NEIGHBORHOOD')[['NEIGHBORHOOD', 'TOTAL UNITS']].sum().reset_index().sort_values('TOTAL UNITS', ascending=False).head(10)
bar2 = go.Figure(data=[go.Bar(x=neighborhoods['NEIGHBORHOOD'], y=neighborhoods['TOTAL UNITS'], marker_color='blue')],layout=go.Layout({'paper_bgcolor': 'black', 'plot_bgcolor': 'black', 'font_color': 'white'}))

#Open vs. Closed Properties - Create new Columns - Status (O, C)
df['SALE PRICE'] = pd.to_numeric(df['SALE PRICE'])
conditions = [(df['SALE PRICE'] > 0), df['SALE PRICE'] == 0]
values = ['O', 'C']
df['STATUS'] = np.select(conditions, values)
Status = df['STATUS'].value_counts()
Status_Labels = df['STATUS'].unique()
colors = ['coral', 'aqua']
pie1 = go.Figure(data=[go.Pie(values=Status, labels=Status_Labels, hole=.3, marker={'colors':colors})], layout=go.Layout({'paper_bgcolor': 'black', 'plot_bgcolor':'gray', 'font_color': 'white'}))

#build Map around New York based on zip codes and city 


#dash plotly build 
app = dash.Dash() 

valid_users = {
    'realestate': 'realestatemarketplace'
}

auth = dash_auth.BasicAuth(
    app, 
    valid_users
)

#build layout 
app.layout = html.Div(style={'backgroundColor': 'black', 'color':'white'}, children=[
    html.Div([
        html.H1('Real Estate - Sales Analysis DashBoard')
    ], style={'textAlign': 'center', 'color': 'white'}), 
    html.Div([
        html.H4('Average Sales Price - 2016'), 
        dcc.Graph(id='indicator1', figure = indicator1)
    ], style={'width': '50%', 'display': 'inline-block', 'color': 'white', 'textAlign': 'center'}), 
    html.Div([
        html.H4('Average Sales Price - 2017'), 
        dcc.Graph(id='indicator2', figure = indicator2)
    ], style={'width': '50%', 'display': 'inline-block', 'color': 'white', 'textAlign': 'center'}), 
    html.Div([
        html.H4('Total Numbers of Units - Residential vs. Commercial'), 
        dcc.Graph(id='bar1', figure = bar1) 
    ], style={'width': '33%', 'display': 'inline-block', 'color': 'white', 'textAlign': 'center'}), 
    html.Div([
        html.H4('Top 10 Neighbors'), 
        dcc.Graph(id='bar2', figure = bar2)
    ], style={'width': '33%', 'display': 'inline-block', 'color': 'white', 'textAlign': 'center'}), 
    html.Div([
        html.H4('Open vs. Closed Properties'), 
        dcc.Graph(id='pie1', figure = pie1)
    ], style={'width': '33%', 'display': 'inline-block', 'color': 'white', 'textAlign': 'center'}), 
    html.Div([
        html.H4('Export Data File'), 
        dt.DataTable(
            id='dataTable1', 
            columns = [{'labels': i, 'rows': i} for i in df.columns], 
            data=df.to_dict('records'), 
            editable=True,              # allow editing of data inside all cells
            filter_action="native",     # allow filtering of data by user ('native') or not ('none')
            sort_action="native",       # enables data to be sorted per-column by user or not ('none')
            sort_mode="single",         # sort across 'multi' or 'single' columns
            column_selectable="multi",  # allow users to select 'multi' or 'single' columns
            row_selectable="multi",     # allow users to select 'multi' or 'single' rows
            row_deletable=False,         # choose if user can delete a row (True) or not (False)
            selected_columns=[],        # ids of columns that user selects
            selected_rows=[],           # indices of rows that user selects
            page_action="native",       # all data is passed to the table up-front or not ('none')
            page_current=0,             # page number that user is on
            page_size=6,                # number of rows visible per page
            export_format='csv',
            style_data={                # overflow cells' content into multiple lines
            'whiteSpace': 'normal',
            'height': 'auto'
            }

        )
    ])
])

if __name__ == "__main__":
    app.run_server(port=8050, host='0.0.0.0')