import base64
import mimetypes
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ImageDescriptionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_path = None
        self.api_key = None
        self._load_api_key()

        self.setWindowTitle("AI 이미지 설명 앱")
        self.resize(1100, 760)
        self.setMinimumSize(920, 660)
        self.setStyleSheet(self._build_stylesheet())
        self._init_ui()

    def _load_api_key(self):
        env_path = Path(__file__).resolve().parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        self.api_key = os.getenv("OPENAI_API_KEY")

    def _build_stylesheet(self):
        return """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fdf2f8, stop:0.5 #eef2ff, stop:1 #ecfeff);
                color: #1f2937;
                font-family: "Malgun Gothic", "Segoe UI", sans-serif;
            }

            QWidget#root {
                padding: 20px;
            }

            QLabel#title {
                font-size: 26px;
                font-weight: 700;
                color: #312e81;
                margin-bottom: 6px;
            }

            QLabel#subtitle {
                font-size: 12px;
                color: #4b5563;
                margin-bottom: 18px;
            }

            QFrame#panel {
                background: rgba(255, 255, 255, 0.62);
                border: 1px solid rgba(167, 139, 250, 0.35);
                border-radius: 26px;
                padding: 18px;
            }

            QPushButton {
                border: none;
                border-radius: 16px;
                padding: 12px 18px;
                font-size: 15px;
                font-weight: 600;
                color: #1f2937;
            }

            QPushButton#primary {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #a5b4fc, stop:1 #c4b5fd);
            }

            QPushButton#secondary {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f9a8d4, stop:1 #fcd34d);
            }

            QPushButton:hover {
                filter: brightness(1.04);
            }

            QPushButton:disabled {
                background: #d1d5db;
                color: #6b7280;
            }

            QLabel#preview {
                background: rgba(255,255,255,0.7);
                border: 2px dashed #c7d2fe;
                border-radius: 24px;
                qproperty-alignment: AlignCenter;
            }

            QTextEdit {
                background: rgba(255, 255, 255, 0.72);
                border: 1px solid rgba(147, 197, 253, 0.6);
                border-radius: 20px;
                padding: 16px;
                font-size: 14px;
                color: #1f2937;
            }

            QLabel#status {
                font-size: 12px;
                color: #4f46e5;
                margin-top: 8px;
            }
        """

    def _init_ui(self):
        root = QWidget(objectName="root")
        self.setCentralWidget(root)

        main_layout = QVBoxLayout(root)
        main_layout.setContentsMargins(24, 18, 24, 18)
        main_layout.setSpacing(18)

        title = QLabel("사진을 업로드하면 내용을 설명해 드려요")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("OpenAI Vision 모델을 사용해 이미지의 주요 내용, 상황, 배경, 감정을 한글로 설명합니다.")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        panel = QFrame(objectName="panel")
        panel_layout = QHBoxLayout(panel)
        panel_layout.setSpacing(24)

        left_col = QVBoxLayout()
        left_col.setSpacing(16)

        self.preview_label = QLabel("이미지를 선택해 주세요")
        self.preview_label.setObjectName("preview")
        self.preview_label.setMinimumSize(480, 420)
        self.preview_label.setMaximumSize(480, 420)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("font-size: 16px; color: #6b7280; font-weight: 600;")

        button_row = QHBoxLayout()
        button_row.setSpacing(12)

        self.upload_btn = QPushButton("이미지 업로드")
        self.upload_btn.setObjectName("primary")
        self.upload_btn.clicked.connect(self.select_image)

        self.analyze_btn = QPushButton("설명 생성")
        self.analyze_btn.setObjectName("secondary")
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self.analyze_image)

        button_row.addWidget(self.upload_btn)
        button_row.addWidget(self.analyze_btn)

        self.status_label = QLabel("대기 중")
        self.status_label.setObjectName("status")

        left_col.addWidget(self.preview_label)
        left_col.addLayout(button_row)
        left_col.addWidget(self.status_label)

        right_col = QVBoxLayout()
        right_col.setSpacing(10)

        result_title = QLabel("분석 결과")
        result_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #312e81; margin-bottom: 4px;")

        self.output_edit = QTextEdit()
        self.output_edit.setPlaceholderText("업로드한 이미지의 설명이 여기에 표시됩니다.")
        self.output_edit.setReadOnly(True)

        right_col.addWidget(result_title)
        right_col.addWidget(self.output_edit)

        panel_layout.addLayout(left_col)
        panel_layout.addLayout(right_col)
        main_layout.addWidget(panel)

    def select_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "이미지 선택",
            str(Path.home()),
            "이미지 파일 (*.png *.jpg *.jpeg *.bmp *.webp)",
        )
        if not file_name:
            return

        self.image_path = file_name
        self._show_preview(file_name)
        self.analyze_btn.setEnabled(True)
        self.status_label.setText("이미지 로드 완료. 설명을 생성할 수 있습니다.")

    def _show_preview(self, file_name):
        pixmap = QPixmap(file_name)
        if pixmap.isNull():
            self.preview_label.setText("이미지를 불러오지 못했습니다.")
            return

        scaled = pixmap.scaled(
            self.preview_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview_label.setPixmap(scaled)

    def _encode_image(self, image_path):
        with open(image_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    def analyze_image(self):
        if not self.image_path:
            QMessageBox.warning(self, "알림", "먼저 이미지를 업로드해 주세요.")
            return

        if not self.api_key:
            self.output_edit.setPlainText(".env 파일에 OPENAI_API_KEY가 없습니다. 키를 확인해 주세요.")
            self.status_label.setText("API 키가 설정되지 않았습니다.")
            return

        self.analyze_btn.setEnabled(False)
        self.status_label.setText("이미지 분석 중... 잠시만 기다려 주세요.")
        self.output_edit.clear()

        try:
            ext = mimetypes.guess_type(self.image_path)[0] or "image/jpeg"
            encoded = self._encode_image(self.image_path)
            image_url = f"data:{ext};base64,{encoded}"

            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": (
                                    "이 이미지를 한국어로 상세하게 설명해 주세요. "
                                    "이미지에 보이는 주요 객체, 배경, 색상, 분위기, 감정, "
                                    "상황을 중심으로 5~7문장으로 정리해 주세요. "
                                    "필요하면 사진의 의미까지 함께 설명해 주세요."
                                ),
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": image_url},
                            },
                        ],
                    }
                ],
                max_tokens=400,
                temperature=0.4,
            )

            result = response.choices[0].message.content.strip()
            self.output_edit.setPlainText(result)
            self.status_label.setText("분석 완료")

        except Exception as exc:
            self.output_edit.setPlainText(f"이미지 설명 생성 중 오류가 발생했습니다.\n\n오류 내용: {exc}")
            self.status_label.setText("오류 발생")
        finally:
            self.analyze_btn.setEnabled(bool(self.image_path))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ImageDescriptionApp()
    window.show()
    sys.exit(app.exec())
