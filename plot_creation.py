import plotly.graph_objs as go
import json
import plotly


def get_graph(data):
    graphs = []
    for day_data in data:
        # Extracting the sunrise and sunset hours
        sunrise_hour = day_data['sunrise_hour']
        sunset_hour = day_data['sunset_hour']

        # Creating the x-axis (hours) based on sunrise and sunset
        hours = list(range(sunrise_hour, sunset_hour + 1))

        # Creating the graph
        graph = go.Figure(data=[
            go.Scatter(
                x=hours,
                y=day_data['predicted_results_array'],
                mode='lines+markers',
                name='Predicted Results'
            )
        ])

        # Adding title and labels
        graph.update_layout(
            title=f"Day {data.index(day_data) + 1} Predicted Results",

            yaxis_title="Predicted Value",
            legend_title="Legend"
        )

        # Adding total increase and discharge as annotations
        graph.add_annotation(
            x=0.5,
            y=-0.15,
            showarrow=False,
            text=f"Total Increase: {day_data['total_increase']}%, Discharge: {day_data['discharge']}%",
            xref="paper",
            yref="paper"
        )

        # Converting the graph to JSON
        graph_json = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)
        graphs.append(graph_json)
    return graphs