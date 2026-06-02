"""
Reusable Plotly Charts
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def score_trend_chart(data):

    if not data:
        return None

    df = pd.DataFrame(data)

    fig = px.line(

        df,

        x="date",
        y="score",

        markers=True,

        title="Performance Trend"

    )

    return fig


def interview_type_chart(data):

    if not data:
        return None

    df = pd.DataFrame({

        "Type":
            list(data.keys()),

        "Score":
            list(data.values())

    })

    fig = px.bar(

        df,

        x="Type",
        y="Score",

        title="Average Score by Type"

    )

    return fig


def readiness_gauge(score):

    fig = go.Figure(

        go.Indicator(

            mode="gauge+number",

            value=score,

            title={
                "text":
                "Readiness Score"
            },

            gauge={

                "axis": {
                    "range":
                    [0, 100]
                },

                "steps": [

                    {
                        "range": [0, 40],
                        "color": "#ff6b6b"
                    },

                    {
                        "range": [40, 70],
                        "color": "#ffd93d"
                    },

                    {
                        "range": [70, 100],
                        "color": "#6bcb77"
                    }

                ]

            }

        )

    )

    return fig