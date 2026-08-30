from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import QToolTip, QWidget

GRID = QColor("#c9c8c1")
BASELINE = QColor("#9b9a92")
MUTED_TEXT = QColor("#6b6a64")
ACCENT = QColor("#2a78d6")
HIGHLIGHT = QColor("#0ca30c")


class BarChart(QWidget):
    """Small self-drawn bar chart -- no charting dependency, just QPainter.

    Takes (label, value) pairs; draws gridlines, a baseline, rounded bars,
    selective x-axis labels, and a hover tooltip. Redraws to fit whatever
    size the widget is given, so it scales with the window.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items: list[tuple[str, float]] = []
        self.highlight_index: int | None = None
        self.value_format: str = "{:.0f}"
        self.setMinimumHeight(160)
        self.setMouseTracking(True)
        self._bar_rects: list[QRectF] = []

    def set_data(self, items: list[tuple[str, float]], highlight_index: int | None = None) -> None:
        self.items = items
        self.highlight_index = highlight_index
        self._bar_rects = []
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pad_left, pad_right, pad_top, pad_bottom = 30, 10, 10, 24
        plot = QRectF(
            pad_left, pad_top, max(1, self.width() - pad_left - pad_right), max(1, self.height() - pad_top - pad_bottom)
        )

        if not self.items:
            painter.setPen(QPen(MUTED_TEXT))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "No data for this month")
            self._bar_rects = []
            return

        values = [v for _, v in self.items]
        max_val = max(values) if max(values) > 0 else 1

        painter.setPen(QPen(GRID, 1))
        for frac in (0.0, 0.5, 1.0):
            y = plot.bottom() - frac * plot.height()
            painter.drawLine(QPointF(plot.left(), y), QPointF(plot.right(), y))
            painter.setPen(QPen(MUTED_TEXT))
            painter.drawText(QRectF(0, y - 8, pad_left - 4, 16), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, str(round(max_val * frac)))
            painter.setPen(QPen(GRID, 1))

        painter.setPen(QPen(BASELINE, 1))
        painter.drawLine(QPointF(plot.left(), plot.bottom()), QPointF(plot.right(), plot.bottom()))

        n = len(self.items)
        gap = 4
        bar_w = max(3.0, (plot.width() - gap * (n - 1)) / n)
        label_stride = max(1, n // 10)

        self._bar_rects = []
        for i, (label, value) in enumerate(self.items):
            x = plot.left() + i * (bar_w + gap)
            h = (value / max_val) * plot.height()
            bar_rect = QRectF(x, plot.bottom() - h, bar_w, h)
            self._bar_rects.append(bar_rect)

            color = HIGHLIGHT if i == self.highlight_index else ACCENT
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            radius = min(4.0, bar_w / 2)
            painter.drawRoundedRect(bar_rect, radius, radius)

            if n <= 12 or i % label_stride == 0 or i == n - 1:
                painter.setPen(QPen(MUTED_TEXT))
                painter.drawText(
                    QRectF(x - 12, plot.bottom() + 4, bar_w + 24, 16), Qt.AlignmentFlag.AlignCenter, str(label)
                )

    def mouseMoveEvent(self, event) -> None:
        pos = event.position()
        for i, rect in enumerate(self._bar_rects):
            hit = QRectF(rect.x(), 0, rect.width(), self.height())
            if hit.contains(pos):
                label, value = self.items[i]
                QToolTip.showText(event.globalPosition().toPoint(), f"{label}: {self.value_format.format(value)}", self)
                return
        QToolTip.hideText()

    def leaveEvent(self, event) -> None:
        QToolTip.hideText()
        super().leaveEvent(event)
