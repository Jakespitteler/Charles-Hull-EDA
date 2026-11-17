from charles_hull_eda.charts import equipment_hours_figure
from charles_hull_eda.report import analyse_workbook, export_report
from test_equipment import example


def test_export_and_chart_preserve_missing_values_and_synthetic_label(tmp_path):
    path = tmp_path / "example.xlsx"
    example(path)
    report = analyse_workbook(path)
    fig = equipment_hours_figure(report)
    assert "SYNTHETIC" in fig.layout.title.text
    assert len(fig.data) == 2
    assert any(value is None for trace in fig.data for value in trace.y)
    export_report(report, tmp_path / "output")
    assert (tmp_path / "output" / "inventory.json").exists()
    assert '"hours":null' in (tmp_path / "output" / "equipment-hours.json").read_text()
    assert (tmp_path / "output" / "equipment-hours.html").exists()
