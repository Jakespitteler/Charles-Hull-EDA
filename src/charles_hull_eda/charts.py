"""Plot construction lives here, not in the notebook."""

import pandas as pd
import plotly.graph_objects as go


def equipment_hours_figure(report, *, report_date: str | None = None) -> go.Figure:
    frame = report.hours
    figure = go.Figure()
    label = "SYNTHETIC DEMONSTRATION" if report.synthetic else "REAL DATA — exploratory"
    if frame.empty:
        figure.update_layout(title=f"{label} · No supported equipment data")
        return figure
    report_date = report_date or min(frame["date"])
    selected = frame.loc[frame["date"] == report_date]
    if selected.empty:
        raise ValueError(f"No equipment records for {report_date}")
    for shift in ("day", "night"):
        rows = selected.loc[selected["shift"] == shift]
        figure.add_bar(
            name=shift, x=rows["asset"].tolist(),
            y=[None if pd.isna(v) else v for v in rows["hours"]],
            customdata=rows[["value_state", "cell"]].to_numpy().tolist(),
            hovertemplate="%{x}<br>%{y} hours<br>%{customdata[0]} · %{customdata[1]}<extra>%{fullData.name}</extra>",
        )
    figure.update_layout(
        title=f"{label} · Equipment shift hours · {report_date}",
        barmode="group", xaxis_title="Reported asset label", yaxis_title="Operating hours (h)",
        template="plotly_white",
        annotations=[dict(text="Missing values are gaps, not zero. Hours do not establish utilisation.",
                          x=0, y=1.12, xref="paper", yref="paper", showarrow=False)],
        margin=dict(t=130, b=160),
    )
    return figure
