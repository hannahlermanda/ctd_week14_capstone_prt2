import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sqlite3

# Set global font size
st.markdown("""
    <style>
        p {
            font-size: 18px !important;
        }
        .stApp {
            background-color: #005C12;  /* Pale green */
        }
        
    </style>
""", unsafe_allow_html=True)

#Connect to the database
conn = sqlite3.connect('mlb_hit_pitch_stats.db')

#Title of the Streamlit
st.title("⚾️⚾️ MLB Player Stats ⚾️⚾️")

# Player type selector
player_type = st.sidebar.radio("Select Player Type", ["Hitter", "Pitcher"])

########################################################################
#1st Chart - Home Runs (Hitter Section)
if player_type == "Hitter":
    #Grab the information (name and amount of home runs) from the dataframe in the database
    def load_home_runs():
        df = pd.read_sql('SELECT name, home_runs FROM "mlb_home_runs_all_time_top_1,000_leaders"', conn)
        df['name'] = df['name'].str.title()
        #Descending order; Drop na values (just in case they failed to drop in the cleaning)
        df = df.dropna().sort_values(by='home_runs', ascending=False).reset_index(drop=True)
        df['rank'] = df.index + 1
        return df

    #Load the homeruns dataframe from the mlb_hit_pitch_stats.db
    df = load_home_runs()

    #Player selection in the side bar
    st.sidebar.header("Player Selection")
    selected_player = st.sidebar.selectbox("Choose a player", df['name'])

    #Get the row index of the selected player in the dataframe
    selected_index = df[df['name'] == selected_player].index[0]

    #Title the section
    st.header("Home Run Comparison")
    #The total number of players are the number of unique players in the dataframe from mlb_hit_pitch_stats.db
    total_number_of_players = len(df)
    st.markdown(f"**{selected_player}** ranks **#{int(df.loc[selected_index, 'rank'])}** out of **{total_number_of_players}** players (all time).")

    #Slider for comparisons
    st.subheader(f"How many players should {selected_player} be compared against?")
    compare_count = st.slider("Number of players to compare (odd number)", 3, 19, step=2, value=9)
    #Divide the compare count by two for calculations
    half = compare_count // 2

    #Calculate start and end index for slicing (trying to center selected player on the bar graph)
    start = selected_index - half
    #+1 because slicing is exclusive on end
    end = selected_index + half + 1

    #Adjust if out of bounds (too little players on one side due to rank)
    #Check to see if the starting index for the comparison slice is LESS than 0
    if start < 0:
        #If the starting index  is less than 0, add how many it is off by its opposite (e.g. if it's -1, add +1) to the end to maintain balance
        end += abs(start)
        #Reset start to 0
        start = 0
    #If the last one goes beyond the boundaries of len, have the end be the last entry
    if end > len(df):
        #If the end is greater than len, calculate the difference and subtract that value from start
        start -= (end - len(df))
        #Have end be the same as the last valid index in the dataframe 
        end = len(df)
        #If start is less than 0 and end is still greater than the last valid index in the dataframe
        if start < 0:
            #Have start be reset to 0
            start = 0

    #Create a subset dataframe of players to compare including the selected player, and mark the selected player
    subset = df.iloc[start:end].copy()
    subset['highlight'] = subset['name'] == selected_player

    #Plot
    fig_bar = px.bar(
        subset,
        x='home_runs',
        y='name',
        color='highlight',
        #Chosen player = Red, All other player = white
        color_discrete_map={True: 'red', False: 'white'},
        labels={'home_runs': 'Home Runs', 'name': 'Player'},
        title=f"Home Runs: {selected_player} vs Peers",
        orientation='h',
        hover_data={
            'home_runs': True,
            'rank': True,
            'name': False,
            'highlight': False
        }
    )

    #Home Run Bar Plot Deco
    fig_bar.update_layout(
        yaxis=dict(
            categoryorder='array',
            categoryarray=subset['name'].tolist()[::-1],
            tickfont=dict(color='black')  
        ),
        xaxis=dict(tickfont=dict(color='black')),  
        showlegend=False,
        title_font=dict(size=18, color='black'),         
        yaxis_title_font=dict(size=18, color='black'),   
        xaxis_title_font=dict(size=18, color='black'),  
        font=dict(size=18, color='black'),               
        plot_bgcolor='#D9AC30',
        paper_bgcolor='#D9AC30',
        legend=dict(font=dict(color='black'))
    )

    #Display the bar chart
    st.plotly_chart(fig_bar, use_container_width=True)

 ####2ND CHART Homerun Boxplot
    #Initializes an empty Plotly Figure
    fig_home_run_box = go.Figure()

    #Plot
    fig_home_run_box.add_trace(go.Box(
        y=df['home_runs'],
        boxpoints='outliers',
        name='All Players',
        marker_color='white',  
        hoverinfo='skip' 
    ))

    #Selected player's home run stat
    player_stat = df.loc[df['name'] == selected_player, 'home_runs'].values[0]

    #Calculate percentile of the chosen player
    percentile = np.round(100 * (df['home_runs'] < player_stat).mean(), 1)

    #Make an invisible dot for the legend, but no dot will be placed on the actual plot
    fig_home_run_box.add_trace(go.Scatter(
        x=[None], 
        y=[None],
        mode='markers',
        marker=dict(color='red', size=12),
        name=selected_player,
    ))

    #Add an arrow pointing to player's stat on the boxplot
    fig_home_run_box.update_layout(
        title="Home Runs Distribution",
        yaxis_title="Home Runs",
        showlegend=True,
        xaxis=dict(showticklabels=False),
        yaxis=dict(tickfont=dict(color='black')),
        title_font=dict(size=18, color='black'),
        yaxis_title_font=dict(size=18, color='black'),
        font=dict(size=18, color='black'),
        plot_bgcolor='#D9AC30',
        paper_bgcolor='#D9AC30',
        legend=dict(font=dict(color='black')),
        annotations=[
            dict(
                x=0,
                y=player_stat,
                text="", 
                showarrow=True,
                arrowhead=2,
                ax=40,
                ay=-20,
                arrowcolor='red',
                font=dict(color="red", size=18)
            )
        ],
    )

    #Title of the section
    st.header("Home Runs Distribution")
    st.markdown(f"**{selected_player}** is at the **{percentile}th percentile** of all-time home run hitters.")
    
    #Display the boxplot chart
    st.plotly_chart(fig_home_run_box, use_container_width=True)

    ###3RD CHART - Stolen bases vs Caught
    #Load stolen bases and caught stealing from two tables and merge on name
    def load_base_running():
        #Grab information and shorthand names
        df_stolen = pd.read_sql('SELECT name, stolen_bases AS sb FROM stolen_bases_all_time_leaders_on_baseball_almanac', conn)
        df_caught = pd.read_sql('SELECT name, caught_stealing AS cs FROM caught_stealing_all_time_leaders_on_baseball_almanac', conn)
        #Strip names of unnecessary white space
        df_stolen['name'] = df_stolen['name'].str.title().str.strip()
        df_caught['name'] = df_caught['name'].str.title().str.strip()
        #Make sure the numerical numbers are numeric (double-check for safety)
        df_stolen['sb'] = pd.to_numeric(df_stolen['sb'], errors='coerce')
        df_caught['cs'] = pd.to_numeric(df_caught['cs'], errors='coerce')
        #Inner merge on name for the stolen_bases and caught_stealing tables in the database
        df = pd.merge(df_stolen, df_caught, on='name', how='inner').dropna()
        #Return the new dataframe
        return df

    #Load and prepare base running data (the dataframe we just made)
    merged_df = load_base_running()

    ##Initializes an empty Plotly Figure
    fig_sb_cs = go.Figure()

    #Plot the players as dots
    fig_sb_cs.add_trace(go.Scatter(
        x=merged_df['sb'],
        y=merged_df['cs'],
        mode='markers',
        marker=dict(color='white', size=8),  
        name='All Players',
        hoverinfo='text',
        hovertext=[
        f"{name}<br>Bases stolen: {bs}<br>Times caught stealing: {cs}"
        for name, bs, cs in zip(merged_df['name'], merged_df['sb'], merged_df['cs'])
        ],
    ))

    #Highlight the selected player in red
    if selected_player in merged_df['name'].values:
        selected_stats = merged_df[merged_df['name'] == selected_player]
        fig_sb_cs.add_trace(go.Scatter(
            x=selected_stats['sb'],
            y=selected_stats['cs'],
            mode='markers',
            marker=dict(color='red', size=8),
            name=selected_player,
            hoverinfo='text',
            hovertext=[
                f"{selected_player}<br>Bases stolen: {selected_stats['sb'].values[0]}<br>Times caught stealing: {selected_stats['cs'].values[0]}"
            ]

        ))

    #Plot information
    fig_sb_cs.update_layout(
        title=f"Bases Caught Stealing vs Bases Stolen",
        xaxis_title='Stolen Bases',
        yaxis_title='Caught Stealing',
        showlegend=True,
        title_font=dict(size=18, color='black'),
        xaxis_title_font=dict(size=18, color='black'),
        yaxis_title_font=dict(size=18, color='black'),
        font=dict(size=18, color='black'),
        plot_bgcolor='#D9AC30',
        paper_bgcolor='#D9AC30',
        legend=dict(font=dict(color='black')),
        xaxis=dict(tickfont=dict(color='black')),
        yaxis=dict(tickfont=dict(color='black'))
    )

    #Title of the section
    st.header("Base Running: Bases Caught Stealing vs Bases Stolen")

    #Calculate and display stolen base success rate and rank (based on calculations)
    if selected_player in merged_df['name'].values:
        #Extract the selected player's data row
        player_data = merged_df[merged_df['name'] == selected_player].iloc[0]
        #Player's stolen bases
        sb = player_data['sb']
        #Number of times the player was caught stealing
        cs = player_data['cs']
        #Total attempts is successful steals + unsuccessful steals
        total_attempts = sb + cs
        #If attempts are greater than 0
        if total_attempts > 0:
            #Calculate success rate percentage
            success_rate = round(100 * sb / total_attempts, 1)
        #Otherwise the success rate is 0
        else:
            success_rate = 0
        #Create a new column in the merged dataframe for the success rate
        merged_df['success_rate'] = merged_df['sb'] / (merged_df['sb'] + merged_df['cs'])
        #If the value is NaN, fill it with 0
        merged_df['success_rate'] = merged_df['success_rate'].fillna(0)
        #Sort the dataframe by success rate in descending order and reset index
        merged_df = merged_df.sort_values(by='success_rate', ascending=False).reset_index(drop=True)
        #Get the rank of the selected player by success rate (1-based)
        player_rank = merged_df.index[merged_df['name'] == selected_player].tolist()[0] + 1
        #The total number of players is the length of the merged dataframe
        total_number_of_players = len(merged_df)
        #Display the player's stolen base stats and success rate rank
        st.markdown(
            f"**{selected_player}** successfully stole **{sb}** bases and was caught **{cs}** times.\n\n"
            f"They have a stolen base success rate of **{success_rate}%**, ranking **#{player_rank}** out of {total_number_of_players} players."
        )
    #Plot
    st.plotly_chart(fig_sb_cs, use_container_width=True)




#####################################################################################################################
####CHART 4 -  Games Saved vs Games Pitched
elif player_type == "Pitcher":
    #Load saves and games pitched
    df_saves = pd.read_sql('SELECT name, games AS saves FROM saves_all_time_leaders', conn)
    df_games_pitched = pd.read_sql('SELECT name, games AS games_pitched FROM games_pitched_all_time_leaders', conn)

    #Clean and merge
    df_eff = df_saves.merge(df_games_pitched, on='name')
    #Double check for nuemrical comaptibility
    df_eff[['saves', 'games_pitched']] = df_eff[['saves', 'games_pitched']].apply(pd.to_numeric, errors='coerce')

    #Load ERA data
    df_era = pd.read_sql('SELECT name, era FROM earned_run_average_all_time_leaders', conn)

    #Merge df_eff and df_era to get only pitchers with BOTH data
    df_pitchers = df_eff.merge(df_era, on='name')

    #Single pitcher selector sidebar - only names in BOTH data sets (from the merge from before)
    st.sidebar.header("Player Selection")
    selected_player = st.sidebar.selectbox("Choose a pitcher", df_pitchers['name'].sort_values())

    #Name the chart
    st.header("Games Saved vs Games Pitched")

    #Calculate save percentage
    df_pitchers['save_percentage'] = (df_pitchers['saves'] / df_pitchers['games_pitched']) * 100

    #Display percentile and save percentage message
    #Get the selected player's save percentage from pitchers df
    player_save_pct = df_pitchers.loc[df_pitchers['name'] == selected_player, 'save_percentage'].values[0]
    #Calculate rank based on save_percentage descending (1.0 is highest save %)
    df_pitchers_sorted = df_pitchers.sort_values(by='save_percentage', ascending=False).reset_index(drop=True)
    #Attach a rank column based on the sorted index
    df_pitchers_sorted['rank'] = df_pitchers_sorted.index + 1
    #Get the player's rank from the sorted pitchers df based on their name
    player_rank = df_pitchers_sorted.loc[df_pitchers_sorted['name'] == selected_player, 'rank'].values[0]
    #Total players from the new sorted pitcher dataframe
    total_players = len(df_pitchers_sorted)

    st.markdown(
        f"**{selected_player}** saved **{player_save_pct:.1f}%** of games they pitched in, "
        f"ranking at **#{int(player_rank)}** out of **{total_players}** players."
    )

    #Initializes an empty Plotly Figure
    fig_save_caught = go.Figure()

    #All players scatterplot
    fig_save_caught.add_trace(go.Scatter(
        x=df_pitchers['games_pitched'],
        y=df_pitchers['saves'],
        mode='markers',
        marker=dict(color='white', size=8), 
        name='All Players',
        hoverinfo='text',
        text=[
        f"{name}<br>Games Pitched: {gp}<br>Games Saved: {sv}"
        for name, gp, sv in zip(df_pitchers['name'], df_pitchers['games_pitched'], df_pitchers['saves'])
        ]
    ))

    # Highlight selected player
    player_row = df_pitchers[df_pitchers['name'] == selected_player].iloc[0]
    fig_save_caught.add_trace(go.Scatter(
        x=[player_row['games_pitched']],
        y=[player_row['saves']],
        mode='markers',
        marker=dict(color='red', size=8),
        textposition='top center',
        name=selected_player,
        hoverinfo='text',
        text=[f"{selected_player}<br>Games Pitched: {player_row['games_pitched']}<br>Games Saved: {player_row['saves']}"],
    ))

    #Deco
    fig_save_caught.update_layout(
        xaxis_title='Games Pitched',
        yaxis_title='Games Saved',
        title='Games Saved vs Games Pitched',
        showlegend=True,
        title_font=dict(size=18, color='black'),
        xaxis_title_font=dict(size=18, color='black'),
        yaxis_title_font=dict(size=18, color='black'),
        font=dict(size=18, color='black'),
        plot_bgcolor='#D9AC30',
        paper_bgcolor='#D9AC30',
        legend=dict(font=dict(color='black')),
        xaxis=dict(tickfont=dict(color='black')),
        yaxis=dict(tickfont=dict(color='black'))
    )

    st.plotly_chart(fig_save_caught, use_container_width=True)


#### Chart 5: ERA Distribution ####
    st.header("Earned Run Average (ERA) Distribution")

    #Initializes an empty Plotly Figure
    fig_era_box = go.Figure()

    fig_era_box.add_trace(go.Box(
        y=df_pitchers['era'],
        boxpoints='outliers',
        name='All Pitchers',
        marker_color='white', 
        hoverinfo='skip'
    ))

    #Get the ERA value for the selected player
    era_stat = df_pitchers.loc[df_pitchers['name'] == selected_player, 'era'].values[0]
    #Calculate the percentile of the player based on their ERA
    percentile = np.round(100 * (df_pitchers['era'] > era_stat).mean(), 1)

    #Selected player in the legend
    fig_era_box.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(color='red', size=12),
        name=selected_player,
    ))

    #Deco
    fig_era_box.update_layout(
        title="ERA Distribution",
        yaxis_title="ERA",
        showlegend=True,
        xaxis=dict(showticklabels=False),
        yaxis=dict(tickfont=dict(color='black')),
        title_font=dict(size=18, color='black'),
        yaxis_title_font=dict(size=18, color='black'),
        font=dict(size=18, color='black'),
        plot_bgcolor='#D9AC30',
        paper_bgcolor='#D9AC30',
        legend=dict(font=dict(color='black')),
        annotations=[
            dict(
                x=0,
                y=era_stat,
                text="",
                showarrow=True,
                arrowhead=2,
                ax=40,
                ay=-20,
                arrowcolor='red',
                font=dict(color="red", size=18)
            )
        ],
    )

    st.markdown(f"**{selected_player}** has an ERA of **{era_stat:.2f}** (lower ERA is better), placing them in the **{percentile}th percentile**.")
    st.plotly_chart(fig_era_box, use_container_width=True)
