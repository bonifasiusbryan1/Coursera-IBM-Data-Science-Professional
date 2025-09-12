# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Build dropdown options (Task 1)
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())
]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Launch Site dropdown
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=site_options,
                                    value='ALL',
                                    placeholder='Select a Launch Site here',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Pie chart
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Range slider for payload
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Scatter chart
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2: callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Sum of successes per site
        df_agg = spacex_df.groupby('Launch Site', as_index=False)['class'].sum()
        fig = px.pie(df_agg, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        df_site = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success vs failure for selected site
        fig = px.pie(df_site, names='class',
                     title=f'Success vs Failure for {entered_site}')
    return fig

# TASK 4: callback for scatter plot
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def get_scatter(entered_site, payload_range):
    low, high = payload_range
    df_range = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                         (spacex_df['Payload Mass (kg)'] <= high)]
    if entered_site != 'ALL':
        df_range = df_range[df_range['Launch Site'] == entered_site]

    # Color by Booster Version Category (as per lab spec)
    color_col = 'Booster Version Category' if 'Booster Version Category' in df_range.columns else 'Booster Version'

    title = 'Payload vs. Outcome for All Sites' if entered_site == 'ALL' else f'Payload vs. Outcome for {entered_site}'
    fig = px.scatter(
        df_range, x='Payload Mass (kg)', y='class',
        color=color_col, hover_data=['Launch Site'],
        title=title
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run()