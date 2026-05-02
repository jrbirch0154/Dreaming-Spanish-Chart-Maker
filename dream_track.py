# Dreaming Spanish Tracker

# %% Initializing

import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

pio.renderers.default = "browser"
pio.templates.default = "presentation"

URL = "https://app.dreaming.com/.netlify/functions/dayWatchedTime?language=es"

MILESTONES = {
    50: "red",
    150: "purple",
    300: "blue",
    600: "cyan",
    1000: "green",
    1500: "green",
}


# %% Requesting

@st.cache_data(ttl=3600) # Cache data, expires after 1 hour
def request_dreaming(headers, URL=URL) -> list:

    response = requests.get(URL, headers=headers)

    return response.json()


# %% DF Work


def make_dataframe(data, starting_hours) -> pd.DataFrame:
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["timeMinutes"] = (df["timeSeconds"] / 60).round(2)
    df = df.sort_values(by=["date"], axis=0)
    df["totalHours"] = (
        (df["timeMinutes"] / 60).cumsum() + starting_hours
    ).round(2)
    df['month'] = df['date'].dt.to_period('M')
    

    return df


# %% Plotly


def line_graph(df: pd.DataFrame):

    fig = px.line(
        df, x="date", y="totalHours", title="Total Spanish Hours over Time"
    )

    fig.update_layout(xaxis_title="Date", yaxis_title="Hours")

    fig.update_traces(fill="tozeroy", fillcolor="rgba(0,0,0,0.1)")

    for number, color in MILESTONES.items():

        if number >= df["totalHours"].max():
            fig.add_hline(y=number, line_color=color, line_dash="dash")
        else:
            x_intersect = df.loc[df["totalHours"] >= number, "date"].min()

            fig.add_shape(
                type="line",
                x0=df["date"].min(),
                x1=x_intersect,
                y0=number,
                y1=number,
                line=dict(color=color, dash="dash"),
            )

            fig.add_scatter(
                x=[x_intersect],
                y=[number],
                mode="markers",
                marker=dict(color=color, size=10, symbol="star"),
                showlegend=False,
                name=number,
            )

    # fig.show()
    return fig


def bar_graph_day(df: pd.DataFrame, daily_goal):
    fig2 = px.bar(df, x="date", y="timeMinutes", color="goalReached")

    fig2.add_hline(
        y=daily_goal,
        line_color="red",
        line_dash="dash",
        # annotation_text='Daily Goal'
    )
    fig2.update_layout(
        title="Minutes per Day", xaxis_title="Date", yaxis_title="Minutes"
    )

    # fig2.show()
    return fig2


def box_graph(df: pd.DataFrame, daily_goal):
    fig3 = go.Figure()

    fig3.add_trace(go.Violin(x=df["date"].dt.day_name(), y=df["timeMinutes"],spanmode='hard',meanline_visible=True))

    fig3.add_hline(y=daily_goal, line_dash="dash", line_color="red")
    # annotation_text='Daily goal',annotation_position='top right')

    day_order = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]

    fig3.update_xaxes(categoryorder="array", categoryarray=day_order)
    
    fig3.update_layout(title='Daily Input Averages',
                       xaxis_title='Day of the week',
                       yaxis_title='Minutes of Input')

    return fig3

def bar_graph_month(df: pd.DataFrame, daily_goal):
    df_m = df.groupby('month')['timeMinutes'].sum().reset_index()
    df_m['month'] = df_m['month'].astype(str)
    df_m['timeHours'] = (df_m['timeMinutes']/60).round(2)
    
    fig2 = px.bar(df_m,x='month', y='timeHours',
                  color='timeHours', color_continuous_scale='Viridis',
                  labels={'timeHours': 'Hours'})

    fig2.update_layout(
        title="Hours per month", xaxis_title="Date", yaxis_title="Hours"
    )

    # fig2.show()
    return fig2



# %% Streamlit

st.set_page_config(page_title="Dreaming Spanish Tracker", layout="wide")

st.title("Dreaming Spanish Hours Chart")

auth_token = st.text_input("Enter your auth token:", type="password")

st.caption(
    "Your auth token is never stored or transmitted anywhere other than directly to Dreaming Spanish."
)

with st.expander("How to get your auth token"):
    st.markdown(
        """
    1. Log into [Dreaming Spanish](https://app.dreaming.com)
    2. Open your browser's developer tools by pressing **F12** (or right-click anywhere on the page + **Inspect**)
    3. Click the **Network** tab at the top of the developer tools panel
    4. **Refresh the page** (F5) so requests start appearing in the list
    5. In the filter/search box, type **dayWatchedTime** to narrow down the results
    6. Click on the request that appears
    7. Scroll down to **Request Headers** and find the **authorization** field
    8. Copy the full value. It starts with `Bearer eyJ...`
    """
    )


headers = {"authorization": auth_token}

starting_hours = st.text_input("Enter your starting hours (Optional): ")

daily_goal = st.text_input(
    "Enter your current daily goal in minutes (Optional): "
)

if st.button("Run"): # On hitting run
    if auth_token: # If the auth token is in
        starting_hours = float(starting_hours) if starting_hours else 0
        daily_goal = float(daily_goal) if daily_goal else 0

        try:
            data = request_dreaming(headers)

            df = make_dataframe(data, starting_hours)
            st.success("Data found")
            
            #------------- Metrics math
            start_date = df["date"].min().strftime("%Y-%m-%d")
            days_since_started = (df["date"].max() - df["date"].min()).days

            best_row = df.loc[df["timeMinutes"].idxmax()]

            best_day = best_row["date"].strftime("%Y-%m-%d")
            best_day_minutes = best_row["timeMinutes"]
            best_month = str(df.groupby('month')['timeMinutes'].sum().idxmax())
            best_month_hours = df.groupby('month')['timeMinutes'].sum().max() / 60
            

            current_streak = df[df["timeSeconds"] > 0]["date"].dt.date
            diff = current_streak.diff().dt.days
            streak = 0
            for d in diff.iloc[::-1]:
                if d == 1:
                    streak += 1
                else:
                    break

            total_days = len(df)  # it doesn't include 0 days
            
            csv = df.to_csv(index=False)

            # --------------- ST work
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Hours", f"{df['totalHours'].max():.1f}")
                st.metric("Day started:", f"{start_date}")
                
            with col2:
                st.metric("Total days of input:", total_days)
                st.metric(
                    "Best day:", best_day, delta=f"{best_day_minutes:.0f}m"
                )
                
                
            with col3:
                st.metric("Current streak:", f"{streak} days")
                st.metric(
                    "Best month:", best_month, delta=f"{best_month_hours:.1f}h"
                )
                
 
            with col4:
                st.metric(
                    "Avg Min/Day",
                    f"{df['timeMinutes'].mean():.1f}",
                    delta=f"{df['timeMinutes'].mean() - daily_goal:.1f} vs goal",
                )
                
                
                
                

            line_fig = line_graph(df)
            bar_fig_day = bar_graph_day(df, daily_goal)
            violin_fig = box_graph(df, daily_goal)
            bar_fig_month = bar_graph_month(df,daily_goal)

            st.plotly_chart(line_fig)
            st.plotly_chart(bar_fig_month)
            st.plotly_chart(bar_fig_day)
            st.plotly_chart(violin_fig)
            
            st.download_button(label='Download data as CSV',
                               data=csv,
                               file_name='dreaming_spanish_data.csv',
                               mime='text/csv')

        except:
            st.error("Data not found")

    else:
        st.warning("Please enter auth token")
