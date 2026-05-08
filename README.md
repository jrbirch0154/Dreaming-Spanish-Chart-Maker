# Dreaming Spanish Progress Viewer

A Streamlit web app that pulls your personal watch history from [Dreaming Spanish](https://www.dreaminspanish.com/) and visualizes your comprehensible input progress over time.

**Live App: [dreaming-spanish-chart-maker.streamlit.app](https://dreaming-spanish-chart-maker.streamlit.app/)**

---

## Features

- **Cumulative hours line chart** — tracks total hours over time with milestone markers at 50, 150, 300, 600, 1000, and 1500 hours
- **Daily minutes bar chart** — shows input per day, color-coded by whether your daily goal was met, with a 7-day rolling average overlay
- **Monthly hours bar chart** — aggregated monthly view with a 3-month rolling average
- **Day-of-week violin plot** — shows your distribution of input by weekday so you can spot patterns
- **Key stats dashboard** — total hours, current streak, best day, best month, average minutes/day vs. goal
- **CSV export** — download your full watch history as a CSV

---

## Usage

1. Open the [live app](https://dreaming-spanish-chart-maker.streamlit.app/)
2. Retrieve your auth token from Dreaming Spanish (instructions are built into the app):
   - Log into [app.dreaming.com](https://app.dreaming.com)
   - Open browser DevTools (`F12`) → **Network** tab
   - Refresh the page and filter requests for `dayWatchedTime`
   - Copy the `authorization` header value (starts with `Bearer eyJ...`)
3. Paste your token into the app
4. Optionally enter a starting hours offset (if you have pre-tracked hours) and a daily goal in minutes
5. Click **Run**

### Your auth token is used only to fetch your data directly from Dreaming Spanish. It is never stored or transmitted anywhere else. Be very mindful of where you enter it.

---

## Running Locally
For those that would prefer to run locally, the steps are provided below. This way your auth token never leaves your system.

```bash
git clone https://github.com/jrbirch0154/Dreaming-Spanish-Chart-Maker.git
cd Dreaming-Spanish-Chart-Maker
pip install -r requirements.txt
streamlit run dream_track.py
```

---

## Dependencies

- `streamlit`
- `pandas`
- `plotly`
- `requests`

---

## Notes

This tool is built for personal use by Dreaming Spanish learners who want more insight into their comprehensible input habits than the platform natively provides. It is not affiliated with or endorsed by Dreaming Spanish.
