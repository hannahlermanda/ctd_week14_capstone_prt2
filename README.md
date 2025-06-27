# MLB Career Stats Streamlit Project - CTD Week 14 Capstone Part 2

## Summary
This Streamlit app visualizes career statistics for MLB hitters and pitchers, including home run comparisons, stolen base vs caught stealing, saves vs games pitched, and ERA distribution. Users select a player to see interactive charts highlighting that player in red with customized Plotly styling.

## Features

- 🔄 **Player Type Toggle:** Choose between Hitter and Pitcher statistics.
- 📊 **Interactive Charts:**
  - Bar chart comparing a selected player's home runs with surrounding ranks.
  - Box plot showing a player’s percentile in home run distribution.
  - Scatter plot of stolen bases vs. caught stealing (with success rate rank).
  - Scatter plot of games saved vs. games pitched.
  - Box plot showing ERA distribution and rank.
- 🎯 **Highlighting:** Selected players are visually emphasized in red.
- 📈 **Percentile and Rank Insights:** See how players rank compared to others.

## Setup Instructions

```bash
# 1. Clone the Repository
git clone https://github.com/hannahlermanda/ctd_week14_capstone_prt2.git
cd ctd_week14_capstone_prt2

# 2. Create and Activate a Virtual Environment
python -m venv .venv
# On Mac/Linux
source .venv/bin/activate
# On Windows
.venv\Scripts\activate

# 3. Install Dependencies
pip install -r requirements.txt

# 4. Run the Streamlit App
streamlit run app.py

The app will open in your default browser at `http://localhost:8501/`.

# 5. Make sure you have the SQLite database file
# Ensure that 'mlb_hit_pitch_stats.db' is present in the project root directory.
```
## Screenshot

![MLB Player Stats_Streamlit App Preview - Hitters](https://github.com/user-attachments/assets/68757ddd-ff66-4aa3-9161-07193a31855d)

![MLB Player Stats_Streamlit App Preview - Pitchers](https://github.com/user-attachments/assets/e4e3b453-a5fe-4ff6-8b2a-96143474cdc5)

