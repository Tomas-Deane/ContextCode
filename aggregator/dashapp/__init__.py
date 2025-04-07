from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go

def create_dash_app(flask_server):
    """
    create and return a dash app attached to the flask server
    """
    dash_app = Dash(
        __name__,
        server=flask_server,
        url_base_pathname='/dash/'
    )

    dash_app.layout = html.Div([
        html.Div([
            html.H2("Live Percentage Gauges"),
            html.A("Back to Index", href="/", style={"fontSize": "16px", "marginBottom": "20px"})
        ], style={"textAlign": "center", "marginBottom": "20px"}),
        dcc.Interval(
            id='interval-component',
            interval=5000,  # update every 5 seconds
            n_intervals=0
        ),
        html.Div(
            id='gauges-container',
            style={"display": "flex", "flexWrap": "wrap", "justifyContent": "center"}
        )
    ], style={"backgroundColor": "#303030", "color": "#FFFFFF", "minHeight": "100vh", "padding": "20px"})

    @dash_app.callback(
        Output('gauges-container', 'children'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_gauges(n_intervals):
        """
        update and return the gauge components for dash layout
        """
        # use flask test client to call api endpoints
        try:
            with flask_server.test_client() as client:
                metrics_response = client.get("/api/metrics")
                metrics_data = metrics_response.get_json()
        except Exception as e:
            print("Error fetching metrics:", e)
            metrics_data = []

        try:
            with flask_server.test_client() as client:
                schema_response = client.get("/api/schema")
                schema_data = schema_response.get_json()
        except Exception as e:
            print("Error fetching schema:", e)
            schema_data = []

        # build set of metric ids with "numeric" field type and "percentage" field name
        eligible_metric_ids = set()
        for device in schema_data:
            for metric in device.get("metrics", []):
                for field in metric.get("fields", []):
                    if field["field_name"].lower() == "percentage" and field["field_type"].lower() == "numeric":
                        eligible_metric_ids.add(metric["metric_id"])

        gauge_components = []
        for metric in metrics_data:
            if metric.get("metric_id") in eligible_metric_ids:
                fields = metric.get("fields", {})
                if "percentage" in fields:
                    try:
                        value = float(fields["percentage"])
                    except (ValueError, TypeError):
                        value = 0
                    fig = go.Figure(
                        go.Indicator(
                            mode="gauge+number",
                            value=value,
                            title={'text': f"{metric.get('device')} - {metric.get('metric')}"}
                        )
                    )
                    # Use the dark template and increase margins so the title is fully visible
                    fig.update_layout(
                        template="plotly_dark",
                        margin=dict(l=80, r=80, t=80, b=40),
                        title_x=0.5  # Center the title horizontally
                    )

                    gauge_components.append(
                        html.Div(
                            dcc.Graph(figure=fig, id=f"gauge-{metric.get('metric_id')}"),
                            style={"width": "400px", "margin": "10px"}
                        )
                    )
        if not gauge_components:
            gauge_components = [html.Div("No percentage metrics available.")]
        return gauge_components

    return dash_app
