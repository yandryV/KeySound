import sys
import keyboard
import win32gui
import simpleaudio as sa
import ctypes
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QLinearGradient, QColor, QPalette, QIcon
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Establecer el tamaño de la ventana principal
        self.setGeometry(700, 350, 350, 500)

        # Crear los elementos de la interfaz
        self.keyLabel = QLabel("Tecla establecida:", self)
        self.keyEntry = QLineEdit(self)
        self.keyEntry.setMaxLength(1)  # Limitar la longitud de texto a 1 carácter
        self.saveKeyButton = QPushButton("Guardar tecla", self)
        self.resetKeyButton = QPushButton("Restablecer tecla", self)
        self.programLabel = QLabel("Programa seleccionado:", self)
        self.programEntry = QComboBox(self)
        self.saveProgramButton = QPushButton("Guardar programa", self)
        self.resetProgramButton = QPushButton("Restablecer programa", self)
        self.startButton = QPushButton("Iniciar", self)
        self.stopButton = QPushButton("Detener", self)
        self.resumeButton = QPushButton("Reanudar", self)

        # Configurar el diseño de la ventana
        layout = QVBoxLayout()
        layout.addWidget(self.keyLabel)
        layout.addWidget(self.keyEntry)
        layout.addWidget(self.saveKeyButton)
        layout.addWidget(self.resetKeyButton)
        layout.addWidget(self.programLabel)
        layout.addWidget(self.programEntry)
        layout.addWidget(self.saveProgramButton)
        layout.addWidget(self.resetProgramButton)
        layout.addWidget(self.startButton)
        layout.addWidget(self.stopButton)
        layout.addWidget(self.resumeButton)

        # Crear un widget contenedor y establecer el diseño
        widget = QWidget(self)
        widget.setLayout(layout)

        # Establecer el widget contenedor como el widget central de la ventana
        self.setCentralWidget(widget)

        # Conectar los botones a las funciones correspondientes
        self.saveKeyButton.clicked.connect(self.saveKey)
        self.resetKeyButton.clicked.connect(self.resetKey)
        self.saveProgramButton.clicked.connect(self.saveProgram)
        self.resetProgramButton.clicked.connect(self.resetProgram)
        self.programEntry.currentIndexChanged.connect(self.checkConfigComplete)
        self.startButton.clicked.connect(self.startListening)
        self.stopButton.clicked.connect(self.stopSounds)
        self.resumeButton.clicked.connect(self.resumeSounds)

        # Variables para almacenar la tecla y el programa seleccionados
        self.saved_key = ""
        self.saved_program = ""
        self.sound1 = sa.WaveObject.from_wave_file("sound1.wav")
        self.sound2 = sa.WaveObject.from_wave_file("sound2.wav")
        self.sound_toggle = False

        # Bandera para indicar si la configuración está completa
        self.config_complete = False

        # Deshabilitar los botones "Detener" y "Reanudar" al inicio
        self.stopButton.setEnabled(False)
        self.resumeButton.setEnabled(False)

        self.resetKey()
        self.resetProgram()

    def setBackgroundGradient(self):
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#687d6d"))  # Gris oscuro
        gradient.setColorAt(1, QColor("#e6ebe7"))  # Gris claro
        self.setAutoFillBackground(True)
        self.setBackgroundRole(self.backgroundRole())
        palette = QPalette()
        palette.setBrush(self.backgroundRole(), gradient)
        self.setPalette(palette)

    def saveKey(self):
        self.saved_key = self.keyEntry.text()
        if self.saved_key:
            self.keyLabel.setText("Tecla establecida: " + self.saved_key)
            self.checkConfigComplete()
            self.saveKeyButton.setEnabled(False)
            self.resetKeyButton.setEnabled(True)  # Activar el botón "Restablecer tecla"
            self.keyEntry.setText(self.saved_key)  # Actualizar el campo de texto con la tecla seleccionada

    def resetKey(self):
        self.saved_key = ""
        self.keyLabel.setText("Tecla establecida:")
        self.keyEntry.clear()
        self.checkConfigComplete()
        self.keyEntry.setEnabled(True)
        self.saveKeyButton.setEnabled(True)
        self.resetKeyButton.setEnabled(False)  # Desactivar el botón "Restablecer tecla"
        keyboard.unhook_all()  # Eliminar todos los eventos registrados

    def saveProgram(self):
        self.saved_program = self.programEntry.currentText()
        self.programLabel.setText("Programa seleccionado: " + self.saved_program)
        self.checkConfigComplete()
        self.saveProgramButton.setEnabled(False)
        self.resetProgramButton.setEnabled(True)  # Activar el botón "Restablecer tecla"

    def resetProgram(self):
        self.saved_program = ""
        self.programEntry.setCurrentIndex(0)
        self.programLabel.setText("Programa seleccionado:")
        self.checkConfigComplete()
        self.startButton.setEnabled(False)
        self.programEntry.setEnabled(True)
        self.saveProgramButton.setEnabled(True)
        self.stopSounds()  # Detener la reproducción de los sonidos
        self.resetProgramButton.setEnabled(False)  # Desactivar el botón "Restablecer tecla"
        keyboard.unhook_all()  # Eliminar todos los eventos registrados

    def checkConfigComplete(self):
        self.config_complete = bool(self.saved_key) and bool(self.saved_program)
        self.startButton.setEnabled(self.config_complete)

    def startListening(self):
        if not self.config_complete:
            return

        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.resumeButton.setEnabled(False)
        self.keyEntry.setEnabled(False)
        self.programEntry.setEnabled(False)
        keyboard.on_press_key(self.saved_key, self.playSound)

    def playSound(self, event):
        active_program = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if active_program and self.saved_program in active_program:
            self.toggleSound()
            if self.sound_toggle:
                self.sound1.play()
            else:
                self.sound2.play()

    def stopSounds(self):
        self.stopButton.setEnabled(False)
        self.resumeButton.setEnabled(True)
        keyboard.unhook_all()
        self.startButton.setEnabled(True)  # Activar el botón "Iniciar" al detener los sonidos

    def resumeSounds(self):
        self.stopButton.setEnabled(True)
        self.resumeButton.setEnabled(False)
        keyboard.on_press_key(self.saved_key, self.playSound)

    def toggleSound(self):
        self.sound_toggle = not self.sound_toggle

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(open("styles.css").read())  # Cargar los estilos CSS desde el archivo
    # Cambiar el ícono de la ventana
    app_icon = QIcon("dawn.ico")  # Path to the icon file
    app.setWindowIcon(app_icon)
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("dawn.png")
    app.setWindowIcon(app_icon)
    app.setApplicationDisplayName("KeySound")

    window = MainWindow()

    # Obtener los títulos de las ventanas de la barra de tareas
    def getActivePrograms():
        active_programs = []
        # Obtener los títulos de las ventanas activas en la barra de tareas
        def enum_windows_callback(hwnd, window_titles):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    program_name = title.split(" - ")[-1]  # Obtener solo el nombre del programa
                    window_titles.append(program_name)

        window_titles = []
        win32gui.EnumWindows(enum_windows_callback, window_titles)

        # Rellenar el desplegable de programas solo con los títulos de las ventanas activas
        unique_programs = list(set(window_titles))  # Eliminar duplicados
        window.programEntry.clear()
        window.programEntry.addItems(unique_programs)

    # Obtener y mostrar solo los programas activos en la barra de tareas
    getActivePrograms()

    # Establecer el fondo con gradiente
    window.setBackgroundGradient()

    window.show()
    sys.exit(app.exec_())
