import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QLineEdit, QSlider,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QProgressBar
)
from PyQt6.QtCore import Qt, QRectF, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QWheelEvent, QIntValidator
from pipeline import run_pipeline
from visualize import visualize


# ================= WORKER THREAD =================
class Worker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, cookie1, cookie2, url, max_data):
        super().__init__()
        self.cookie1 = cookie1
        self.cookie2 = cookie2
        self.url = url
        self.max_data = max_data

    def run(self):
        freq = run_pipeline(
            device_id=self.cookie1,
            session=self.cookie2,
            url=self.url,
            max_data=self.max_data
        )
        self.finished.emit(freq)


# ================= ZOOMABLE IMAGE VIEW =================
class ZoomableGraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def set_image(self, pixmap):
        self.scene().clear()
        item = QGraphicsPixmapItem(pixmap)
        self.scene().addItem(item)
        self.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(item, Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        factor = 1.25 if event.angleDelta().y() > 0 else 0.8
        self.scale(factor, factor)


# ================= MAIN APP =================
class ModernWordCloudApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glints Job SKill WordCloud Analyzer")
        self.setGeometry(100, 50, 1400, 800)
        self.setStyleSheet(self.dark_style())
        self.freq_data = None
        self.init_ui()

    def dark_style(self):
        return """
        QWidget { background-color: #0f172a; color: white; font-size: 14px; }
        QTextEdit, QLineEdit {
            background:#1e293b; border:1px solid #334155;
            padding:8px; border-radius:6px;
        }
        QPushButton {
            background:#6366f1; padding:10px;
            border-radius:8px; font-weight:bold;
        }
        QPushButton:hover { background:#818cf8; }
        """

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        left_panel = QVBoxLayout()

        title = QLabel("🚀 Job Skill WordCloud Tool")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        left_panel.addWidget(title)

        self.cookie1 = QTextEdit()
        self.cookie1.setPlaceholderText("Paste raw device_id #1...")
        left_panel.addWidget(self.cookie1)

        self.cookie2 = QTextEdit()
        self.cookie2.setPlaceholderText("Paste raw session #2...")
        left_panel.addWidget(self.cookie2)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL target...")
        left_panel.addWidget(self.url_input)

        # ===== MAX DATA INPUT =====
        maxdata_label = QLabel("Maximum Data (1 - 500)")
        left_panel.addWidget(maxdata_label)

        self.max_data_input = QLineEdit()
        self.max_data_input.setPlaceholderText("example: 100")
        self.max_data_input.setValidator(QIntValidator(1, 500))
        left_panel.addWidget(self.max_data_input)

        # ===== RUN BUTTON =====
        self.run_btn = QPushButton("▶ RUN ANALYSIS")
        self.run_btn.clicked.connect(self.start_analysis)
        left_panel.addWidget(self.run_btn)

        # ===== LOADING =====
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)
        self.progress.hide()
        left_panel.addWidget(self.progress)

        # ===== THRESHOLD CONTROL =====
        self.threshold_label = QLabel("Frequency Threshold: 1")
        self.threshold_label.hide()
        left_panel.addWidget(self.threshold_label)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(1)
        self.slider.hide()
        self.slider.valueChanged.connect(self.update_label)
        left_panel.addWidget(self.slider)

        self.regen_btn = QPushButton("🔄 REGENERATE WORDCLOUD")
        self.regen_btn.clicked.connect(self.regenerate_wc)
        self.regen_btn.hide()
        left_panel.addWidget(self.regen_btn)

        left_panel.addStretch()

        # ===== RIGHT PANEL =====
        right_panel = QVBoxLayout()
        self.image_view = ZoomableGraphicsView()
        self.image_view.setStyleSheet("background:#0f172a; border:1px solid #334155;")
        right_panel.addWidget(self.image_view)

        main_layout.addLayout(left_panel, 3)
        main_layout.addLayout(right_panel, 5)

    def update_label(self):
        self.threshold_label.setText(f"Frequency Threshold: {self.slider.value()}")

    # ================= START ANALYSIS =================
    def start_analysis(self):
        self.run_btn.setEnabled(False)
        self.progress.show()
        self.threshold_label.hide()
        self.slider.hide()
        self.regen_btn.hide()

        cookie1 = self.cookie1.toPlainText()
        cookie2 = self.cookie2.toPlainText()
        url = self.url_input.text()

        max_data_text = self.max_data_input.text()
        max_data = int(max_data_text) if max_data_text else 100

        self.worker = Worker(cookie1, cookie2, url, max_data)
        self.worker.finished.connect(self.analysis_done)
        self.worker.start()

    # ================= ANALYSIS DONE =================
    def analysis_done(self, freq):
        self.progress.hide()
        self.run_btn.setEnabled(True)

        self.freq_data = freq
        max_freq = max(freq.values())

        self.slider.setMaximum(max_freq)
        self.slider.setValue(1)

        self.threshold_label.show()
        self.slider.show()
        self.regen_btn.show()

        self.generate_wordcloud()

    # ================= REGENERATE =================
    def regenerate_wc(self):
        if self.freq_data:
            self.generate_wordcloud()

    # ================= WORDCLOUD =================
    def generate_wordcloud(self):
        threshold = self.slider.value()
        filtered = {w: c for w, c in self.freq_data.items() if c >= threshold}
        if not filtered:
            return

        visualize(filtered)  # harus save jadi wordcloud.png
        pixmap = QPixmap("wordcloud.png")
        self.image_view.set_image(pixmap)


# ================= RUN APP =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernWordCloudApp()
    window.show()
    sys.exit(app.exec())
