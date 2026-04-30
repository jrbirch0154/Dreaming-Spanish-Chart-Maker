# Dreaming Spanish Tracker

#%% Initializing

import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'
pio.templates.default = 'presentation'

URL = 'https://app.dreaming.com/.netlify/functions/dayWatchedTime?language=es'

MILESTONES = {50: "red", 150: "purple", 300: "blue", 600: "cyan", 1000: "green", 1500: "green" }


#%% Requesting

def request_dreaming(headers, URL=URL) -> list:

    response = requests.get(URL,headers=headers)
    
    return response.json()


#%% DF Work

def make_dataframe(data,starting_hours) -> pd.DataFrame:
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'],errors='coerce')
    df['timeMinutes'] = (df['timeSeconds'] / 60).round(2)
    df = df.sort_values(by=['date'],axis=0)
    df['totalHours'] = ((df['timeMinutes'] / 60).cumsum() + starting_hours).round(2)
    
    return df

#%% Plotly

def line_graph(df: pd.DataFrame):
    
    fig = px.line(df,x='date',y='totalHours',title='Total Spanish Hours over Time')
    
    fig.update_layout(xaxis_title='Date',
                      yaxis_title='Hours')
    
    fig.update_traces(fill='tozeroy',fillcolor='rgba(0,0,0,0.1)')
    
    for number,color in MILESTONES.items():
        
        if number >= df['totalHours'].max():
            fig.add_hline(y=number,line_color=color,line_dash='dash')
        else:
            x_intersect = df.loc[df['totalHours'] >= number, 'date'].min()
            
            fig.add_shape(
                type='line',
                x0=df['date'].min(),
                x1=x_intersect,
                y0=number,
                y1=number,
                line=dict(color=color,dash='dash'))
            
            fig.add_scatter(x=[x_intersect],y=[number],
                            mode='markers',
                            marker=dict(color=color, size=10,symbol='star'),
                            showlegend=False,
                            name=number)
    
    # fig.show()
    return fig

def bar_graph(df:pd.DataFrame,daily_goal):
    fig2 = px.bar(df,x='date',y='timeMinutes',color='goalReached')
    
    fig2.add_hline(y=daily_goal,line_color='red',line_dash='dash',
                   #annotation_text='Daily Goal'
                   )
    fig2.update_layout(title='Minutes per Day',
                       xaxis_title='Date',
                       yaxis_title='Minutes')
    
    # fig2.show()
    return fig2




#%% Streamlit

st.set_page_config(page_title='Dreaming Spanish Tracker',
                   layout='wide')

st.title('Dreaming Spanish Hours Chart')

auth_token = st.text_input('Enter your auth token:', type='password')

st.caption('Your auth token is never stored or transmitted anywhere other than directly to Dreaming Spanish.')

with st.expander("How to get your auth token"):
    st.markdown("""
    1. Log into [Dreaming Spanish](https://app.dreaming.com)
    2. Open your browser's developer tools (F12)
    3. Go to the **Network** tab
    4. Click on any request to the Dreaming Spanish API
    5. Look for the **Authorization** header in the request headers
    6. Copy the full value starting with `Bearer ...`
    """)


headers = {'authorization': auth_token}

starting_hours = st.text_input('Enter your starting hours (Optional): ')

daily_goal = st.text_input('Enter your current daily goal in minutes (Optional): ')

if st.button('Run'):
    if (auth_token):
        starting_hours = float(starting_hours) if starting_hours else 0
        daily_goal = float(daily_goal) if daily_goal else 0
        
        try:
            data = request_dreaming(headers)
            
            df = make_dataframe(data,starting_hours)
            st.success('Data found')
            
            line_fig = line_graph(df)
            
            bar_fig = bar_graph(df,daily_goal)
            
            st.plotly_chart(line_fig)
            st.plotly_chart(bar_fig)
            
        except:
            st.error('Data not found')
    else:
        st.warning('Please enter')
        
        
        
        
        
        
        