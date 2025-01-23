from dash import dcc, html


def upload_component() -> "html.Div":
    """File upload component."""
    return html.Div(
        [
            dcc.Upload(
                id="file-upload",
                children=html.Div(["Drag and Drop or ", html.A("Select a File")]),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=False,
            ),
        ],
    )
