import sys

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QApplication

from FaceRecognition import FaceRecognitionThread


class FaceRecognitionSignals(QObject):
    frame_signal = pyqtSignal(QImage)
    name_signal = pyqtSignal(str)
    image_signal = pyqtSignal(QImage)


# Create a UI Class
class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.face_recognition_thread = None
        self.face_recognition_signals = None

        # Setup UI Components
        layout = QHBoxLayout()
        self.setLayout(layout)

        webcam_layout = QVBoxLayout()
        self.webcam_label = QLabel()
        self.webcam_label.setAlignment(Qt.AlignLeft)
        webcam_layout.addWidget(self.webcam_label)

        image_layout = QVBoxLayout()
        self.image_label = QLabel()
        self.name_label = QLabel()
        my_font = QFont('Arial', 25)
        my_font.setBold(True)
        self.name_label.setFont(my_font)
        image_layout.addWidget(self.image_label)
        image_layout.addWidget(self.name_label)

        layout.addLayout(webcam_layout)
        layout.addLayout(image_layout)

        self.face_recognition_signals = FaceRecognitionSignals()
        # Connect the frame signal from the face recognition thread to UI update slot
        self.face_recognition_signals.frame_signal.connect(self.update_frame)
        self.face_recognition_signals.name_signal.connect(self.update_name)
        self.face_recognition_signals.image_signal.connect(self.update_avatar)


    def start_face_recognition(self):
        # Create the face recognition thread
        self.face_recognition_thread = FaceRecognitionThread()
        self.face_recognition_thread.frame_signal.connect(self.face_recognition_signals.frame_signal.emit)
        self.face_recognition_thread.name_signal.connect(self.face_recognition_signals.name_signal.emit)
        self.face_recognition_thread.image_signal.connect(self.face_recognition_signals.image_signal.emit)
        self.face_recognition_thread.start()

    def stop_face_recognition(self):
        if self.face_recognition_thread is not None:
            self.face_recognition_thread.stop()
            self.face_recognition_thread.join()

    @pyqtSlot(QImage)
    def update_frame(self, q_image):
        # Update UI with processed image
        pixmap = QPixmap.fromImage(q_image)
        self.webcam_label.setPixmap(pixmap)

    @pyqtSlot(QImage)
    def update_avatar(self, q_image):
        # Update UI with processed image
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap)

    @pyqtSlot(str)
    def update_name(self, name):
        # Update UI with Name
        print(f'Name: {name}')
        self.name_label.setText(name)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.setGeometry(100, 100, 1300, 800)
    # Start the face recognition thread
    main_window.start_face_recognition()

    main_window.show()

    sys.exit(app.exec_())
