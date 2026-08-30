import calendar
from datetime import date

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import analytics
from ..db import get_session
from .bar_chart import BarChart

WEEKDAY_SHORT = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class _NumericItem(QTableWidgetItem):
    """Sorts on a numeric/date key instead of the displayed text."""

    def __init__(self, text: str, sort_value):
        super().__init__(text)
        self.sort_value = sort_value

    def __lt__(self, other) -> bool:
        if isinstance(other, _NumericItem):
            return self.sort_value < other.sort_value
        return super().__lt__(other)


def _stat_card(label: str, value: str, sub: str) -> QFrame:
    card = QFrame()
    card.setFrameShape(QFrame.Shape.StyledPanel)
    card.setStyleSheet("QFrame { border: 1px solid palette(mid); border-radius: 10px; padding: 4px; }")
    layout = QVBoxLayout(card)

    label_widget = QLabel(label.upper())
    label_widget.setStyleSheet("color: palette(mid); font-size: 11px; font-weight: 600; letter-spacing: 1px;")
    value_widget = QLabel(value)
    value_widget.setStyleSheet("font-size: 24px; font-weight: 800;")
    sub_widget = QLabel(sub)
    sub_widget.setStyleSheet("color: palette(mid); font-size: 11px;")

    layout.addWidget(label_widget)
    layout.addWidget(value_widget)
    layout.addWidget(sub_widget)
    return card


class DashboardWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Attendance Dashboard")
        self.resize(880, 640)

        self.month_select = QComboBox()
        self.month_select.currentIndexChanged.connect(self.refresh)
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.reload_months)
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.accept)

        header = QHBoxLayout()
        title = QLabel("Attendance Dashboard")
        title.setStyleSheet("font-size: 18px; font-weight: 800;")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(QLabel("Month:"))
        header.addWidget(self.month_select)
        header.addWidget(refresh_button)
        header.addWidget(back_button)

        self.kpi_row = QHBoxLayout()
        self.kpi_row.setSpacing(10)

        self.empty_label = QLabel("No attendance records yet -- take attendance for a few days to see analytics here.")
        self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet("color: palette(mid); padding: 24px;")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.trend_chart = BarChart()
        self.weekday_chart = BarChart()
        self.weekday_chart.value_format = "{:.1f}"
        self.dept_chart = BarChart()

        charts_row = QHBoxLayout()
        charts_row.setSpacing(10)
        charts_row.addLayout(self._chart_box("Daily check-ins this month", self.trend_chart), stretch=3)
        charts_row.addLayout(self._chart_box("By day of week (avg.)", self.weekday_chart), stretch=2)

        self.roster_table = QTableWidget(0, 5)
        self.roster_table.setHorizontalHeaderLabels(["Name", "Roll No.", "Department", "Days Present", "Last Seen"])
        self.roster_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.roster_table.setSortingEnabled(True)
        self.roster_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.addLayout(self.kpi_row)
        content_layout.addWidget(self.empty_label)
        content_layout.addLayout(charts_row)
        content_layout.addLayout(self._chart_box("By department", self.dept_chart))
        content_layout.addWidget(QLabel("Students this month (click a column to sort)"))
        content_layout.addWidget(self.roster_table, stretch=1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)

        outer = QVBoxLayout(self)
        outer.addLayout(header)
        outer.addWidget(scroll)

        self.reload_months()

    def _chart_box(self, title: str, chart: BarChart) -> QVBoxLayout:
        box = QVBoxLayout()
        label = QLabel(title)
        label.setStyleSheet("font-weight: 700;")
        chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        box.addWidget(label)
        box.addWidget(chart)
        return box

    def reload_months(self) -> None:
        session = get_session()
        try:
            months = analytics.list_attendance_months(session)
        finally:
            session.close()

        current_key = date.today().strftime("%Y-%m")
        self.month_select.blockSignals(True)
        self.month_select.clear()
        for key in months:
            year, month = int(key[:4]), int(key[5:7])
            self.month_select.addItem(f"{calendar.month_name[month]} {year}", key)
        if current_key in months:
            self.month_select.setCurrentIndex(months.index(current_key))
        elif months:
            self.month_select.setCurrentIndex(len(months) - 1)
        self.month_select.blockSignals(False)

        self.refresh()

    def refresh(self) -> None:
        key = self.month_select.currentData()
        has_data = key is not None
        self.empty_label.setVisible(not has_data)
        for i in range(self.kpi_row.count()):
            self.kpi_row.itemAt(i).widget().setVisible(has_data)
        if not has_data:
            self.trend_chart.set_data([])
            self.weekday_chart.set_data([])
            self.dept_chart.set_data([])
            self.roster_table.setRowCount(0)
            return

        year, month = int(key[:4]), int(key[5:7])
        session = get_session()
        try:
            summary = analytics.monthly_summary(session, year, month)
        finally:
            session.close()

        self._render_kpis(summary)
        self._render_charts(summary)
        self._render_roster(summary)

    def _clear_kpi_row(self) -> None:
        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _render_kpis(self, summary: analytics.MonthlySummary) -> None:
        self._clear_kpi_row()
        is_current = date.today().strftime("%Y-%m") == f"{summary.year:04d}-{summary.month:02d}"
        best_day_text = summary.best_day.strftime("%b %d") if summary.best_day else "—"
        best_day_sub = f"{summary.best_day_count} check-ins" if summary.best_day else "no data"

        cards = [
            ("Total check-ins", str(summary.total_checkins), calendar.month_name[summary.month]),
            ("Students seen", str(summary.unique_students), "unique this month"),
            ("Avg. per day", f"{summary.avg_per_day:.1f}", f"{summary.elapsed_days} days" + (" so far" if is_current else "")),
            ("Best day", best_day_text, best_day_sub),
        ]
        for label, value, sub in cards:
            self.kpi_row.addWidget(_stat_card(label, value, sub))

    def _render_charts(self, summary: analytics.MonthlySummary) -> None:
        today = date.today()
        is_current = (today.year, today.month) == (summary.year, summary.month)
        trend_items = [(str(d), summary.daily_counts.get(d, 0)) for d in range(1, summary.days_in_month + 1)]
        self.trend_chart.set_data(trend_items, highlight_index=(today.day - 1) if is_current else None)

        weekday_items = [(WEEKDAY_SHORT[i], summary.weekday_avg[name]) for i, name in enumerate(analytics.WEEKDAY_NAMES)]
        self.weekday_chart.set_data(weekday_items)

        dept_items = sorted(summary.department_counts.items(), key=lambda kv: kv[1], reverse=True)
        self.dept_chart.set_data(dept_items)

    def _render_roster(self, summary: analytics.MonthlySummary) -> None:
        self.roster_table.setSortingEnabled(False)
        self.roster_table.setRowCount(len(summary.roster))
        for row, student in enumerate(summary.roster):
            self.roster_table.setItem(row, 0, QTableWidgetItem(student.name))
            self.roster_table.setItem(row, 1, QTableWidgetItem(student.roll_number))
            self.roster_table.setItem(row, 2, QTableWidgetItem(student.department))
            self.roster_table.setItem(
                row, 3, _NumericItem(f"{student.days_present}/{summary.elapsed_days}", student.days_present)
            )
            self.roster_table.setItem(
                row, 4, _NumericItem(student.last_seen.isoformat(), student.last_seen.toordinal())
            )
        self.roster_table.setSortingEnabled(True)
