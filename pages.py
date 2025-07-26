# pages.py (fixed with clean background and styled buttons on Page2)
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QHBoxLayout,
    QSizePolicy, QTextEdit, QSplitter, QGraphicsOpacityEffect  ,QApplication ,QMessageBox
)
from PyQt5.QtGui import QPixmap, QPainter, QPalette, QBrush
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QRect
import pyttsx3
import os
import zipfile
import re
import threading
#import speech_recognition as sr

from components import apply_button_style 
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer, QMetaObject, Q_ARG
import speech_recognition as sr
# Text-to-Speech
import whisper
import tempfile
import sounddevice as sd
import numpy as np
import wave
from scipy.io.wavfile import write
g_yml_FileName = ""

class Page1(QWidget):
    def __init__(self, switch_page_callback):
        super().__init__()
        self.switch_page_callback = switch_page_callback
        self.animation_started = False
        self.setup_ui()
        self.start_animation()
        
    def setup_ui(self):
        # Set the background color of the page
        self.setStyleSheet("background-color: white;")
        # Define image sizes for animation
        self.large_width = 550
        self.large_height = 550
        self.small_width = 550
        self.small_height = 550

        # Create main vertical layout
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop)

        # QLabel to display the image/logo
        self.image_label = QLabel()
        self.pixmap = QPixmap(r"C:\Users\user\Desktop\TechMiya_Self_Assessment\images\techlogo.png")
        self.image_label.setPixmap(self.pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(self.large_width, self.large_height)

        # Add image to the layout (centered)
        main_layout.addWidget(self.image_label, alignment=Qt.AlignHCenter)

        # Create the "Take Self-Assessment" button
        self.button = QPushButton("Take Self-Assessment")
        apply_button_style(self.button)
        self.button.setFixedSize(300, 60)  # Reasonable button size
        self.button.setVisible(False)
        self.button.clicked.connect(self.switch_page_callback)

        # Wrap the button in a horizontal layout to center it
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.button)
        button_layout.addStretch()
        # Add button layout below the image
        main_layout.addLayout(button_layout)

        end_btn = QPushButton("Exit")
        end_btn.clicked.connect(QApplication.quit)
        end_btn.setFixedSize(160, 40)
        apply_button_style(end_btn, "#001f3f")
        main_layout.addWidget(end_btn,alignment=Qt.AlignRight)
    
        # Set the main layout for the widget
        self.setLayout(main_layout)

    def resizeEvent(self, event):
        if not self.animation_started:
            center_x = (self.width() - self.large_width) // 2
            center_y = (self.height() - self.large_height) // 2
            self.image_label.setGeometry(center_x, center_y, self.large_width, self.large_height)

    def start_animation(self):
        QTimer.singleShot(3000, self.animate_image)

    def animate_image(self):
        self.animation_started = True

        center_x = (self.width() - self.small_width) // 2
        center_y = (self.height() - self.small_height) // 2 - 30

        self.animation = QPropertyAnimation(self.image_label, b"geometry")
        self.animation.setDuration(1500)
        self.animation.setStartValue(QRect(
            (self.width() - self.large_width) // 2,
            (self.height() - self.large_height) // 2,
            self.large_width, self.large_height
        ))
        self.animation.setEndValue(QRect(center_x, center_y, self.small_width, self.small_height))
        self.animation.start()
        QTimer.singleShot(1700, self.show_button)

    def show_button(self):
        self.button.setVisible(True)
# Page 2

class Page2(QWidget):
    def __init__(self,back_callback, exit_callback, page4_callback):
        super().__init__()
        self.back_callback = back_callback
        self.page4_callback = page4_callback
        self.proceed_callback = page4_callback
        self.setWindowTitle("AI Interviewer")
        self.resize(600, 500)
        self.questions = []
        self.video_paths = []
        self.answers = {}
        self.current_index = 0
        self.temp_dir = tempfile.mkdtemp()
        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.init_ui()

    def init_ui(self):
        print("Initializing UI...")
        layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        hZ_layout = QHBoxLayout()
        hBut_layout = QHBoxLayout()
        v_layout = QVBoxLayout()

        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(400, 300)
        self.video_widget.setSizePolicy(self.video_widget.sizePolicy().Expanding, self.video_widget.sizePolicy().Expanding)
        self.video_widget.setFocusPolicy(Qt.StrongFocus)
        self.media_player.setVideoOutput(self.video_widget)
        layout.addWidget(self.video_widget)

        # --- File Path Label ---
        self.file_path_label = QLabel("No file selected")
        self.file_path_label.setAlignment(Qt.AlignCenter)
        self.file_path_label.setFixedSize(1150, 40)
        self.file_path_label.setStyleSheet("""
            font-size: 14px;
            padding: 10px;
            color: #2c3e50;
            background-color: #ecf0f1;
            border: 1px solid #ccc;
            border-radius: 6px;
        """)

        self.load_yaml_btn = QPushButton("📄 Load YAML")
        self.load_yaml_btn.clicked.connect(self.load_yaml)
        self.load_yaml_btn.setFixedSize(160, 40)
        apply_button_style(self.load_yaml_btn, "#001f3f")
        #layout.addWidget(self.load_yaml_btn,alignment=Qt.AlignRight|Qt.AlignTop)
        
        h_layout.addWidget(self.file_path_label)
        h_layout.addWidget(self.load_yaml_btn)
        layout.addLayout(h_layout)

        self.zipfile_path_label = QLabel("No zip file selected")
        self.zipfile_path_label.setAlignment(Qt.AlignCenter)
        self.zipfile_path_label.setFixedSize(1150, 40)
        self.zipfile_path_label.setStyleSheet("""
            font-size: 14px;
            padding: 8px;
            color: #2c3e50;
            background-color: #ecf0f1;
            border: 1px solid #ccc;
            border-radius: 5px;
        """)

        self.load_zip_btn = QPushButton("🗜️ Load Video ZIP")
        self.load_zip_btn.clicked.connect(self.load_zip)
        self.load_zip_btn.setFixedSize(160, 40)
        apply_button_style(self.load_zip_btn, "#001f3f")

        hZ_layout.addWidget(self.zipfile_path_label)
        hZ_layout.addWidget(self.load_zip_btn)
        layout.addLayout(hZ_layout)

        

        self.label = QLabel("Load YAML and ZIP to start interview")
        self.label.setStyleSheet("font-size: 16px; color: green")
        layout.addWidget(self.label,alignment=Qt.AlignCenter)

        self.start_btn = QPushButton("▶️ Start Interview")
        self.start_btn.clicked.connect(self.start_interview)
        self.start_btn.setVisible(False)
        self.start_btn.setFixedSize(160, 40)
        apply_button_style(self.start_btn, "#001f3f")
        layout.addWidget(self.start_btn,alignment=Qt.AlignCenter)
        

        #--- Back Buttons ---
        self.back_button = QPushButton("Back")
        self.back_button.setFixedSize(160, 40)
        apply_button_style(self.back_button, "#001f3f")
        hBut_layout.addWidget(self.back_button,alignment=Qt.AlignLeft)
        self.back_button.clicked.connect(self.back_callback)

        self.proceed_button = QPushButton("Check Result")
        self.proceed_button.setFixedSize(160, 40)
        apply_button_style(self.proceed_button, "#001f3f")
        hBut_layout.addWidget(self.proceed_button,alignment=Qt.AlignCenter)
        self.proceed_button.clicked.connect(self.proceed_clicked)
        self.proceed_button.setVisible(False)

        # timer_box = QLabel("Timer: 30")
        # timer_box.setFixedSize(100, 40)
        # timer_box.setStyleSheet("font-size: 16px; font-weight: bold; background-color: #f0f0f0; border: 1px solid #ccc; padding: 5px;")
        # self.timer_label = timer_box
        # hBut_layout.addWidget(self.timer_label,alignment=Qt.AlignRight)

        # self.remaining_time = 30
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_timer)
        # self.timer.start(1000)

        self.end_btn = QPushButton("Exit")
        self.end_btn.clicked.connect(QApplication.quit)
        self.end_btn.setFixedSize(160, 40)
        apply_button_style(self.end_btn, "#001f3f")
        hBut_layout.addWidget(self.end_btn,alignment=Qt.AlignRight)
        layout.addLayout(hBut_layout)

        self.setLayout(layout)


    def load_yaml(self):
        global g_yml_FileName
        print("Loading YAML...")
        path, _ = QFileDialog.getOpenFileName(self, "Select YAML", "", "YAML Files (*.yml *.yaml)")
        g_yml_FileName = path
        if path:
            self.path = path
            self.file_path_label.setText(f"Selected: {path}")
            with open(path, 'r') as file:
                lines = file.readlines()
                self.questions = [line[3:].strip() for line in lines if line.strip().startswith("--")]
            QMessageBox.information(self, "Loaded", f"{len(self.questions)} questions loaded.")
        # file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*.*)")
        

    def load_zip(self):
        print("Loading ZIP...")
        zip_path, _ = QFileDialog.getOpenFileName(self, "Select videos.zip", "", "ZIP Files (*.zip)")
        if zip_path:
            self.zip_path = zip_path
            self.zipfile_path_label.setText(f"Selected: {zip_path}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)

            def extract_question_number(filename):
                match = re.search(r"question_(\d+)", filename)
                return int(match.group(1)) if match else float('inf')

            videos = [
                os.path.join(self.temp_dir, f)
                for f in os.listdir(self.temp_dir)
                if f.lower().endswith(('.mp4', '.mov'))
            ]

            self.video_paths = sorted(
                videos, key=lambda x: extract_question_number(os.path.basename(x))
            )

            QMessageBox.information(self, "ZIP Loaded", f"{len(self.video_paths)} videos extracted.")
            self.start_btn.setVisible(True)


    def start_interview(self):
        print("Starting interview...")
        if not self.questions or not self.video_paths:
            QMessageBox.warning(self, "Error", "Load YAML and ZIP first.")
            return

        if len(self.questions) != len(self.video_paths):
            QMessageBox.warning(self, "Mismatch", "Number of questions and videos do not match.")
            return

        self.current_index = 0
        self.answers = {}
        self.ask_question()

    def ask_question(self):
        print("asking quetions")
        if self.current_index >= len(self.questions):
            self.save_output()
            QMessageBox.information(self, "Done", "Interview finished!")
            self.proceed_button.setVisible(True)
            return

        question = self.questions[self.current_index]
        video_path = self.video_paths[self.current_index]

        self.label.setText(f"Question {self.current_index + 1}: {question}")

        url = QUrl.fromLocalFile(video_path)
        self.media_player.setMedia(QMediaContent(url))
        self.video_widget.show()
        self.media_player.play()
        print("play vedio")
        try:
            self.media_player.mediaStatusChanged.disconnect()
        except :
            pass

        self.media_player.mediaStatusChanged.connect(self.on_video_end)

    def on_video_end(self, status):
        print("on vedio")
        if status == QMediaPlayer.EndOfMedia:
            self.media_player.stop()
            threading.Thread(target=self.record_and_continue).start()

    def update_timer(self):
        self.remaining_time -= 1
        self.timer_label.setText(f"Timer: {self.remaining_time}")
        if self.remaining_time <= 0:
            self.timer.stop()
            self.current_index += 1

    def record_and_continue(self):
        answer = self.record_audio()
        self.answers[self.questions[self.current_index]] = answer
        self.current_index += 1
        # ✅ Safely call GUI method from the main thread
        QTimer.singleShot(0, self.ask_question)


    def record_audio(self, duration=5, fs=44100):
        print("recording")
        while True:
            try:
                self.label.setText("Recording answer...")
                QApplication.processEvents()

                audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
                sd.wait()

                wav_path = os.path.join(tempfile.gettempdir(), "temp_answer.wav")
                write(wav_path, fs, audio)

                r = sr.Recognizer()
                with sr.AudioFile(wav_path) as source:
                    audio_data = r.record(source)
                    text = r.recognize_google(audio_data)

                    print("Recorded:", text)
                return text
            except Exception as e:
                print("Recording error:", e)

            # ✅ Use QTimer.singleShot to safely show a popup on the main thread
                QTimer.singleShot(0, lambda: QMessageBox.warning(
                    self,
                    "Couldn't Hear Clearly",
                    "Please repeat your answer."
                ))

    def save_output(self):
        with open("output.yml", 'w', encoding='utf-8') as f:
            for question, answer in self.answers.items():
                f.write(f"--{question}\n -{answer}\n\n")

    def proceed_clicked(self):
        self.proceed_callback()


class Page4(QWidget):
    def __init__(self, back_callback, exit_callback):
        super().__init__()
        self.back_callback = back_callback
        self.exit_callback = exit_callback
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet("background-color: white;")
        main_layout = QVBoxLayout()
        # Title
        title = QLabel("📄 Final Results")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: bold; padding: 2px;")
        title.setFixedSize(300, 60)
        main_layout.addWidget(title)

        # Question (left) and Answer (right) boxes
        self.qbox = QTextEdit()
        self.abox = QTextEdit()
        self.qbox.setReadOnly(True)
        self.abox.setReadOnly(True)
        self.qbox.setStyleSheet("font-size: 16px; padding: 10px;")
        self.abox.setStyleSheet("font-size: 16px; padding: 10px;")

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.qbox)
        splitter.addWidget(self.abox)
        splitter.setSizes([500, 500])

        main_layout.addWidget(splitter)

        # Buttons
        button_layout = QHBoxLayout()
        back_button = QPushButton("Back to Home")
        back_button.setFixedSize(150, 40)
        apply_button_style(back_button, "#f39c12")
        back_button.clicked.connect(self.back_callback)

        exit_button = QPushButton("Exit")
        exit_button.setFixedSize(100, 40)
        apply_button_style(exit_button, "#e74c3c")
        exit_button.clicked.connect(self.exit_callback)

        button_layout.addStretch()
        button_layout.addWidget(back_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(exit_button)
        button_layout.addStretch()

        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def load_results(self):
        # Load question file
        global g_yml_FileName
        print("g_yml_FileName = ",g_yml_FileName)
        try:
            filename = g_yml_FileName
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            questions = [line.strip().replace("-- ", "") for line in lines if line.startswith("--")]
            print("Questions loaded:", questions)
            actual_ans = [line.strip().replace(" -", "") for line in lines if line.startswith(" -")]
            print("actual_ans loaded:", actual_ans)
        except Exception as e:
            questions = []
            print("Error loading questions:", e)

        # Load answers
        try:
            with open("output.yml", "r", encoding="utf-8") as f:
                lines = f.readlines()
                answers = [line.strip().replace(" -", "") for line in lines if line.startswith(" -")]
            print("Answers loaded:", answers)
        except Exception as e:
            answers = []
            print("Error loading answers:", e)

        left_output = ""
        right_output = ""
        
        for i, question in enumerate(questions):
            left_output += f"Q{i+1}: {question}\nanswer: {actual_ans[i]}\n"

            if i < len(answers):
                right_output += f"Q{i+1}: {question}\nYour Answer: {answers[i]}\n\n"
            else:
                right_output += f"Q{i+1}: {question}\nYour Answer: Not answered\n\n"

        self.qbox.setText(left_output)
        self.abox.setText(right_output)