import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import pickle

import plotly.express as px
import plotly.graph_objects as go

# Data for Article Selection

# Load the data dictionary
with open(f"data/DowleyBook6.19.24_data_dict.pkl", "rb") as f:
    data_dict = pickle.load(f)

# Load the topic names
with open(f"data/topic_names.pkl", "rb") as f:
    topic_names = {f"Topic {int(k) + 1}": v for k, v in pickle.load(f).items()}

# Data for Geolocation validation

# Load data
location_corpus = pd.read_csv("data/location_geolocations_for_maps.csv")

# Add a Feedback column if it doesn't exist
if "Feedback" not in location_corpus.columns:
    location_corpus["Feedback"] = ""

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.title = "Late blight 1844-1847 text"

# Create the layout
app.layout = html.Div(
    [
        dcc.Tabs(
            id="tabs",
            value="tab-1",
            children=[
                dcc.Tab(
                    label="Article Analysis",
                    value="tab-1",
                    style={
                        "padding": "10px",
                        "fontWeight": "bold",
                        "fontFamily": "Arial, sans-serif",
                        "backgroundColor": "#f0f0f0",
                        "borderRadius": "5px",
                        "margin": "5px",
                    },
                    selected_style={
                        "padding": "10px",
                        "fontWeight": "bold",
                        "fontFamily": "Arial, sans-serif",
                        "backgroundColor": "#d0d0d0",
                        "borderRadius": "5px",
                        "margin": "5px",
                    },
                ),
                dcc.Tab(
                    label="Geolocation Feedback",
                    value="tab-2",
                    style={
                        "padding": "10px",
                        "fontWeight": "bold",
                        "fontFamily": "Arial, sans-serif",
                        "backgroundColor": "#f0f0f0",
                        "borderRadius": "5px",
                        "margin": "5px",
                    },
                    selected_style={
                        "padding": "10px",
                        "fontWeight": "bold",
                        "fontFamily": "Arial, sans-serif",
                        "backgroundColor": "#d0d0d0",
                        "borderRadius": "5px",
                        "margin": "5px",
                    },
                ),
            ],
            style={
                "display": "flex",
                "justifyContent": "center",
                "backgroundColor": "#e0e0e0",
                "padding": "10px",
                "borderRadius": "10px",
                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
            },
        ),
        html.Div(id="tabs-content"),
    ],
    style={
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f9f9f9",
        "padding": "20px",
        "margin": "0 auto",
        "maxWidth": "1200px",
        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
    },
)


# Callback to render the content of each tab
@app.callback(Output("tabs-content", "children"), Input("tabs", "value"))
def render_content(tab):
    if tab == "tab-1":
        return html.Div(
            [
                html.H1(
                    "Display articles from the Dowley Book (Farmers Gazette scans)"
                ),
                html.P(
                    "Select an article from the dropdown to view the article content, location on the map, topic mix, and sentiment score."
                ),
                dcc.Dropdown(
                    id="article-dropdown",
                    options=[
                        {"label": f"{idx + 1}. {pd.to_datetime(data_dict[idx]["Clean Date"]).strftime("%Y-%m-%d")} - {data_dict[idx]['Title']}", "value": idx}
                        for idx in data_dict.keys()
                    ],
                    placeholder="Select an article",
                ),
                html.Br(),  # Add a line break for space
                html.Div(
                    [
                        html.Div(
                            id="article-content",
                            style={
                                "width": "50%",
                                "display": "inline-block",
                                "verticalAlign": "top",
                                "padding": "10px",  # Added padding around the text
                            },
                        ),
                        html.Div(
                            [
                                dcc.Graph(id="location-map"),
                                dcc.Graph(id="topic-mix"),
                                dcc.Graph(id="sentiment-score"),
                            ],
                            style={
                                "width": "40%",
                                "display": "inline-block",
                                "verticalAlign": "top",
                            },
                        ),
                    ]
                ),
            ],
            style={
                "fontFamily": "Arial, sans-serif",
                "backgroundColor": "#f9f9f9",
                "padding": "20px",
                "margin": "0 auto",
                "maxWidth": "1200px",
                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
            },
        )
    elif tab == "tab-2":
        return html.Div(
            [
                html.H3("Geolocations extracted from the Farmers Gazette scans"),
                html.P(
                    "Use the map to review and select locations. The report below will update to show the article text for the selected location, and you can use the feedback box to provide feedback on the selected location."
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="map", style={"width": "65%", "display": "inline-block"}
                        ),
                        html.Div(
                            [
                                html.H4("Provide feedback on the selected point(s):"),
                                dcc.Textarea(
                                    id="feedback",
                                    style={"width": "100%", "height": 200},
                                ),
                                html.Button("Submit", id="submit-feedback", n_clicks=0),
                                html.Div(id="feedback-message"),
                            ],
                            style={
                                "width": "25%",
                                "display": "inline-block",
                                "verticalAlign": "top",
                                "padding": "20px",
                            },
                        ),
                    ]
                ),
                html.Div(id="report", style={"marginTop": "20px"}),
            ],
            style={
                "fontFamily": "Arial, sans-serif",
                "backgroundColor": "#f9f9f9",
                "padding": "20px",
                "margin": "0 auto",
                "maxWidth": "1200px",
                "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
            },
        )


# Callback to update the article content
@app.callback(Output("article-content", "children"), Input("article-dropdown", "value"))
def update_article_content(article_idx):
    if article_idx is None:
        return ""
    article = data_dict[article_idx]
    clean_date = pd.to_datetime(article["Clean Date"]).strftime("%Y-%m-%d")
    content = f"""
    **Article {article_idx + 1}.** {article['Title']}

    **Date:** {clean_date}
    
    {article['Main Text']}
    
    {article['Signature'] if article['Signature'] == article["Signature"] else ''}

    """
    return dcc.Markdown(content)


# Callback to update the location map
@app.callback(Output("location-map", "figure"), Input("article-dropdown", "value"))
def update_location_map(article_idx):
    if article_idx is None or "Geolocations" not in data_dict[article_idx]:
        return go.Figure(
            layout={"xaxis": {"visible": False}, "yaxis": {"visible": False}}
        )
    else:
        geolocations = pd.DataFrame(
            [loc for loc in data_dict[article_idx]["Geolocations"]]
        )
        # Set lat and lon to floats
        geolocations["lat"] = geolocations["lat"].astype(float)
        geolocations["lon"] = geolocations["lon"].astype(float)

        if len(geolocations) > 1:
            max_distance = geolocations.apply(
                lambda row: geolocations.apply(
                    lambda r: (
                        (row["lat"] - r["lat"]) ** 2 + (row["lon"] - r["lon"]) ** 2
                    )
                    ** 0.5,
                    axis=1,
                ).max(),
                axis=1,
            ).max()
            zoom = 5 - min(max_distance, 4)
        else:
            zoom = 5

        fig = px.scatter_mapbox(
            lat=geolocations["lat"],
            lon=geolocations["lon"],
            hover_name=geolocations["display_name"],
            zoom=zoom,
        )

        fig.update_traces(marker=dict(size=10), hoverlabel=dict(bgcolor="white"))
        fig.update_layout(hoverlabel=dict(font_size=12))
        fig.update_layout(mapbox_style="open-street-map")
        return fig


# Callback to update the topic mix
@app.callback(Output("topic-mix", "figure"), Input("article-dropdown", "value"))
def update_topic_mix(article_idx):
    if article_idx is None:
        return go.Figure(
            layout={"xaxis": {"visible": False}, "yaxis": {"visible": False}}
        )

    topics = data_dict[article_idx]["Topics"]
    filtered_topics = {k: v for k, v in topics.items() if v > 0.01}

    # Define a consistent color mapping for topics
    topic_colors = {
        f"Topic {i+1}": px.colors.qualitative.T10[i % len(px.colors.qualitative.T10)]
        for i in range(len(topic_names))
    }

    fig = go.Figure(
        go.Pie(
            labels=list(filtered_topics.keys()),
            values=list(filtered_topics.values()),
            marker=dict(
                colors=[topic_colors[topic] for topic in filtered_topics.keys()]
            ),
            hole=0.4,  # This makes it a donut plot
        )
    )
    fig.update_layout(title="Topic Mix")
    # Add topic names below the plot with corresponding colors
    filtered_topic_names = {k: topic_names[k] for k in filtered_topics.keys()}
    topic_names_list = []
    for i, (idx, words) in enumerate(filtered_topic_names.items()):
        words_str = ", ".join(words)
        words_split = words_str.split(", ")
        words_lines = [
            ", ".join(words_split[j : j + 8]) for j in range(0, len(words_split), 8)
        ]
        words_formatted = "<br>".join(words_lines)
        topic_names_list.append(
            f"<span style='color:{topic_colors[idx]}'>{idx}: {words_formatted}</span>"
        )
    topic_names_str = "<br>".join(topic_names_list)
    fig.add_annotation(
        text=topic_names_str,
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.7,  # Adjusted to ensure the topics are below the plot
        showarrow=False,
        font=dict(size=10),
        align="center",
    )
    fig.update_layout(
        margin=dict(b=180)
    )  # Add margin to the bottom to accommodate the annotation
    return fig


# Callback to update the sentiment score
@app.callback(Output("sentiment-score", "figure"), Input("article-dropdown", "value"))
def update_sentiment_score(article_idx):
    if article_idx is None:
        return go.Figure(
            layout={"xaxis": {"visible": False}, "yaxis": {"visible": False}}
        )

    sentiment = data_dict[article_idx]["Sentiment"]
    prev_sentiment = data_dict[article_idx - 1]["Sentiment"] if article_idx > 0 else 0
    color = "#4682B4" if sentiment > 0 else "#FF6347"
    sentiment_label = "Positive" if sentiment > 0 else "Negative"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=sentiment,
            delta={
                "reference": prev_sentiment,
                "increasing": {"color": "#4682B4"},
                "decreasing": {"color": "#FF6347"},
            },
            gauge={"axis": {"range": [-1, 1]}, "bar": {"color": color}},
            title={"text": sentiment_label},
        )
    )
    fig.update_layout(title="Sentiment Score")
    return fig


# Create the map
@app.callback(Output("map", "figure"), Input("map", "relayoutData"))
def update_map(relayoutData):
    location_corpus["Status"] = location_corpus["Feedback"].apply(
        lambda x: "Reviewed" if x == x else "Pending"
    )
    fig = px.scatter_mapbox(
        location_corpus,
        lat="lat",
        lon="lon",
        hover_name="Title",
        hover_data={
            "Clean Date": True,
            "Snippet": True,
            "" "Status": False,
            "lat": False,
            "lon": False,
        },
        zoom=3,
        color="Status",
        color_discrete_map={
            "Pending": "#FF6347",
            "Reviewed": "#4682B4",
        },  # Tomato red and Steel blue
    )
    fig.update_traces(marker=dict(opacity=0.8))  # Add transparency to the points
    fig.update_traces(
        marker=dict(size=10), hoverlabel=dict(bgcolor="white", namelength=-1)
    )
    fig.update_layout(hoverlabel=dict(font_size=12))
    fig.update_layout(mapbox_style="open-street-map")

    if relayoutData and "mapbox.center" in relayoutData:
        fig.update_layout(mapbox_center=relayoutData["mapbox.center"])
    if relayoutData and "mapbox.zoom" in relayoutData:
        fig.update_layout(mapbox_zoom=relayoutData["mapbox.zoom"])
        fig.update_layout(mapbox=dict(layers=[]))
    return fig


# Update report based on map selection
@app.callback(Output("report", "children"), Input("map", "clickData"))
def update_report(clickData):
    if clickData:
        point = clickData["points"][0]
        filtered_location_corpus = location_corpus[
            (location_corpus["lat"] == point["lat"])
            & (location_corpus["lon"] == point["lon"])
        ]
        if not filtered_location_corpus.empty:
            return html.Div(
                [
                    html.Div(
                        [
                            html.H4(f"{record['Title']}"),
                            html.P(f"{record['Clean Date']}"),
                            html.P(f"{record['Snippet']}"),
                            html.P(f"{record['Main Text']}"),
                            html.P(
                                f"{record['Signature'] if record['Signature'] == record['Signature'] else ''}"
                            ),
                            html.P(
                                f"Feedback: {record['Feedback'] if record['Feedback'] == record['Feedback'] else 'No feedback provided'}"
                            ),
                            html.Hr(),
                        ]
                    )
                    for _, record in filtered_location_corpus.iterrows()
                ]
            )
    return html.P("Click on a point on the map to see the report.")


# Save feedback
@app.callback(
    Output("feedback-message", "children"),
    Input("submit-feedback", "n_clicks"),
    State("feedback", "value"),
    State("map", "clickData"),
)
def save_feedback(n_clicks, feedback, clickData):
    if n_clicks > 0 and clickData:
        point = clickData["points"][0]
        idx = location_corpus[
            (location_corpus["lat"] == point["lat"])
            & (location_corpus["lon"] == point["lon"])
        ].index[0]
        location_corpus.at[idx, "Feedback"] = feedback
        location_corpus.to_csv("data/location_geolocations_for_maps.csv", index=False)
        return "Feedback submitted!", ""
    return "", ""


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=80)
