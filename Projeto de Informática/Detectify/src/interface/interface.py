from collections import OrderedDict
from PIL import Image
from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal, QCoreApplication, QPoint, QPointF, QRect, Qt, QThread
from PyQt6.QtGui import QColor, QCursor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import (QAbstractItemView, QComboBox, QColorDialog, QDialog, QFileDialog, QFormLayout, QFrame, QHBoxLayout, 
                            QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QProgressBar, QPushButton, 
                            QScrollArea, QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget)
from utils.dxf_graph import DXF_Graph
from utils.dxf_interpreter import DXF_Interpreter
from utils.utils import Utils
import ctypes, cv2, json, os, shutil, uuid



Image.MAX_IMAGE_PIXELS = None



class ProgressWindow(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detectify")
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(300, 100)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)

        layout = QVBoxLayout(self)
        self.label = QLabel("Executing Detectify...", self)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setRange(0, 0)
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)



class OpenRecent(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Detectify")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'logo.png')))
        self.setFixedSize(300, 300)
        self._parent = parent

        self.folder_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache')

        layout = QVBoxLayout(self)
     
        self.file_list = QListWidget(self)
        self.file_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.file_list)

        self.load_files()

        self.select_button = QPushButton("OK", self)
        self.select_button.clicked.connect(self.confirm_selection)
        self.select_button.setFixedSize(100, 40)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.select_button)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(button_layout)  

        self.selected_file = None


    def load_files(self):
        if os.path.exists(self.folder_path):
            self.file_list.clear()

            for file_name in sorted(os.listdir(self.folder_path)):
                self.add_item_with_delete_button(file_name)


    def add_item_with_delete_button(self, file_name):
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget) 

        file_label = QLabel(file_name)
        file_label.setStyleSheet("""
            font-size: 14px; 
            font-weight: bold;
            padding-left: 10px;
            border-radius: 5px;
        """)

        item_layout.addWidget(file_label)

        if not hasattr(self._parent, 'cable_name') or file_name != self._parent.cable_name:
            delete_button = QPushButton("❌")
            delete_button.setFixedSize(25, 25)
            delete_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            delete_button.clicked.connect(lambda: self.delete_file(file_name, item_widget))

            item_layout.addWidget(delete_button)

        list_item = QListWidgetItem(self.file_list)
        list_item.setSizeHint(item_widget.sizeHint())

        self.file_list.addItem(list_item)
        self.file_list.setItemWidget(list_item, item_widget)


    def delete_file(self, file_name, item_widget):
        file_path = os.path.join(self.folder_path, file_name)

        if os.path.exists(file_path):
            confirm = QMessageBox.question(self, "Detectify", f"Are you sure you want to delete the cable '{file_name}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self._parent.clear_cache(file_name)

            else:
                return

            for index in range(self.file_list.count()):
                item = self.file_list.item(index)
                if self.file_list.itemWidget(item) == item_widget:
                    self.file_list.takeItem(index)
                    break


    def confirm_selection(self):
        selected_item = self.file_list.currentItem()

        if selected_item:
            item_widget = self.file_list.itemWidget(selected_item)
            file_label = item_widget.findChild(QLabel)
            self.selected_file = file_label.text() if file_label else None
            self.accept()

        else:
            if not self._parent.check_cache():
                self.reject()

            else:
                QMessageBox.warning(self, "Detectify", "Please, select a folder.")



class FileSelectionDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detectify")
        self.resize(350, 150)

        self.files = []

        self.layout = QVBoxLayout(self)
        self.form_layout = QFormLayout()

        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)

        self.add_file_input()
        self.add_file_input()

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addStretch()

        self.layout.addLayout(self.form_layout)
        self.layout.addLayout(self.button_layout)


    def add_file_input(self):
        file_path = QLineEdit(self)
        file_path.setReadOnly(True) 
        file_button = QPushButton("Browse", self)
        file_button.clicked.connect(lambda: self.browse_file(file_path))

        h_layout = QHBoxLayout()
        h_layout.addWidget(file_button)
        h_layout.addWidget(file_path)
        
        self.form_layout.addRow(h_layout)

        self.ok_button.setEnabled(False)
        file_button.setFocus()

        self.files.append((file_path, file_button))


    def browse_file(self, _file_path):
        file_path, _ = QFileDialog.getOpenFileName(self, "Detectify", "", "DXF Files (*.dxf)")

        if file_path:
            _file_path.setText(file_path)

            chosen_files = [(fp, fb) for (fp, fb) in self.files if fp.text() != '']
                            
            if len(chosen_files) > 1:
                self.ok_button.setEnabled(True)


    def file_paths(self):
        return [file_path.text() for file_path, _ in self.files]



class InfoSquare(QDialog):

    def __init__(self, cursor, clicked_id=None, classes=None, detections=None, box_holder=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detectify")
        self.setFixedSize(220, 260)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
        self.setModal(True)
        self._parent = parent
        self._cursor = cursor

        if clicked_id is not None:
            detection = detections[clicked_id]
            id_label = detection.get('label', '')
            class_label = detection['class']
            self.x1, self.y1 = detection['x1'], detection['y1']
            self.x2, self.y2 = detection['x2'], detection['y2']

        else:
            id_label = ''
            class_label = ''

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)  
        layout.setSpacing(10)

        self.detections = detections
        self.clicked_id = clicked_id

        id_layout = QHBoxLayout()
        id_label_widget = QLabel("ID")
        id_label_widget.setStyleSheet("font-size: 13px; font-weight: bold;")
        self.id_input = QLineEdit()
        self.id_input.setText(id_label)
        self.id_input.setStyleSheet("""
            font-size: 12px; padding: 4px; border-radius: 5px;
            border: 1px solid
        """)

        id_layout.addWidget(id_label_widget)
        id_layout.addWidget(self.id_input)
        layout.addLayout(id_layout)

        class_layout = QHBoxLayout()
        self.class_combobox = QComboBox()
        self.class_combobox.addItems(classes)
        self.class_combobox.setCurrentText(class_label)
        self.class_combobox.setStyleSheet("""
        QComboBox {
            font-size: 12px;  
            padding: 4px; 
            border-radius: 5px;
            border: 1px solid #000;
        }
        """)

        class_layout.addWidget(self.class_combobox)
        layout.addLayout(class_layout)
        coord_layout = QVBoxLayout()
        coord_layout.setSpacing(4)

        if self.clicked_id is not None:
            coord_layout.addWidget(self.create_coord_label(f"x1 : {self.x1}"))
            coord_layout.addWidget(self.create_coord_label(f"y1 : {self.y1}"))
            coord_layout.addWidget(self.create_coord_label(f"x2 : {self.x2}"))
            coord_layout.addWidget(self.create_coord_label(f"y2 : {self.y2}"))

        else:
            x1_r, y1_r, x2_r, y2_r = box_holder.left(), box_holder.top(), box_holder.right(), box_holder.bottom()
            self.x1_o, self.y1_o, width_o, height_o = self._parent.calculate_reverse_factors(x1_r, y1_r, x2_r - x1_r, y2_r - y1_r)
            self.x2_o = self.x1_o + width_o
            self.y2_o = self.y1_o + height_o

            coord_layout.addWidget(self.create_coord_label(f"x1 : {self.x1_o}"))
            coord_layout.addWidget(self.create_coord_label(f"y1 : {self.y1_o}"))
            coord_layout.addWidget(self.create_coord_label(f"x2 : {self.x2_o}"))
            coord_layout.addWidget(self.create_coord_label(f"y2 : {self.y2_o}"))

        layout.addLayout(coord_layout)

        button_layout = QHBoxLayout()
        confirm_button = QPushButton("OK")
        confirm_button.setStyleSheet("""
            font-size: 10px;
            padding: 4px 8px;
            border-radius: 5px;
            border: 1px solid #000;
        """)
        
        button_layout.addWidget(confirm_button)

        if self.clicked_id is not None:
            delete_button = QPushButton()
            delete_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'trash.png')))
            delete_button.setStyleSheet("""
                font-size: 10px;
                padding: 4px 8px; border-radius: 5px;
                border: 1px solid #000;
            """)

            button_layout.addWidget(delete_button)
            delete_button.clicked.connect(self.on_delete)

        layout.addLayout(button_layout)
        confirm_button.clicked.connect(self.on_confirm)


    def create_coord_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
            font-size: 12px; 
            padding: 4px; border-radius: 4px; 
            border: 1px solid #000;
        """)

        return label


    def on_confirm(self):
        new_id = self.id_input.text()
        new_class = self.class_combobox.currentText()

        if self.clicked_id is not None:
            self.detections[self.clicked_id]['class'] = new_class

            if new_id != '':                        
                self.detections[self.clicked_id]['label'] = new_id

            else:
                if 'label' in self.detections[self.clicked_id]:
                    self.detections[self.clicked_id].pop('label')

            self._parent.selected_id = None

        else:
            id = str(uuid.uuid4())
            self._parent.selected_id = id
            self.detections[id] = {
                'class': new_class,
                'x1': self.x1_o,
                'y1': self.y1_o,
                'x2': self.x2_o,
                'y2': self.y2_o,
            }

            if new_id != '':
                self.detections[id]['label'] = new_id

        self._parent.setCursor(QCursor(self._cursor))
        self._parent.update_tables()
        self.accept()


    def on_delete(self):
        if 'wire_box' in self.detections[self.clicked_id]:
            self.detections[self.detections[self.clicked_id]['wire_box']].pop('object')

        elif 'object' in self.detections[self.clicked_id]:
            self.detections[self.detections[self.clicked_id]['object']].pop('wire_box')

        self.detections.pop(self.clicked_id)
        if self.clicked_id in self._parent.boxes:
            self._parent.boxes.pop(self.clicked_id)

        self._parent.setCursor(QCursor(self._cursor))
        self._parent.update_tables()
        self._parent.selected_id = None

        self.reject()


    def closeEvent(self, event):
        self._parent.setCursor(QCursor(self._cursor))
        self._parent.selected_id = None
        self.accept_id = None
        self.accept_class = None
        
        self.reject()
        event.accept()



class InferenceThread1(QThread):

    inference_done = pyqtSignal(object, str, str, object)


    def __init__(self, parent, src, file, configs, cable_name, cache, dxf):
        super().__init__()
        self._parent = parent
        self.src = src
        self.file = file
        self.configs = configs
        self.cable_name = cable_name
        self.cache = cache
        self.dxf = dxf


    def load_material(self):
        if self.dxf:
            self._parent.clear_cache(self.cable_name)
            self._parent.create_dirs()

            self.image = Utils.pdf_to_png(self.file, os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'images'))

            shutil.copy(self.file, os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'PDF'))

            self.dxf_interpreter = DXF_Interpreter(self.src[0], self.src[1], self.image, self.configs)
            self.dxf_interpreter.process_dxf_file()
            self.red_lines = self.dxf_interpreter.get_red_lines()

            red_lines_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'detections', 'red_lines.json')

            with open(red_lines_path, 'w', encoding='utf-8') as file:
                json.dump(self.red_lines, file)

        elif self.cache:
            image_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'images')
            self.image = [os.path.join(image_dir, file) for file in os.listdir(image_dir) if 'rescale' not in file][0]
            
            self.detections = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'detections', f'{self.cable_name}.json')))
            
            list_red_lines = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'detections', 'red_lines.json')))
            self.red_lines = [list(map(tuple, sublist)) for sublist in list_red_lines]

            self.file = [os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'PDF', file) for file in os.listdir(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'PDF'))][0]


    def run(self):
        self.load_material()

        if not self.cache:
            if self.dxf:
                graph = DXF_Graph(self.dxf_interpreter.detections, self.red_lines, self.configs)
                graph.build_graph()
                self.dxf_interpreter.process_pos_graph(graph.get_leaf_nodes())
                self.detections = self.dxf_interpreter.detections

                self.inference_done.emit(self.detections, self.image, self.file, graph)

            else:
                with open(self.src, "r") as detections_file:
                    self.detections = json.load(detections_file)

                list_red_lines = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'detections', 'red_lines.json')))
                self.red_lines = [list(map(tuple, sublist)) for sublist in list_red_lines]
                graph = DXF_Graph(self.detections, self.red_lines, self.configs)
                graph.build_graph()

                self.inference_done.emit(self.detections, self._parent.image, self._parent.file, graph)
         
        else:
            graph = DXF_Graph(self.detections, self.red_lines, self.configs)
            graph.build_graph()
            self.inference_done.emit(self.detections, self.image, self.file, graph)



class NoScrollScrollArea(QScrollArea):

    def __init__(self, parent, label):
        super().__init__(parent)
        self._parent = parent
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.zoom_enabled = False
        self.label = label


    def wheelEvent(self, event):
        if self.zoom_enabled:
            cursor_pos = self.label.mapFromGlobal(event.globalPosition().toPoint())
            if event.angleDelta().y() > 0:
                self.label.zoom_in(cursor_pos, self)

            else:
                self.label.zoom_out(cursor_pos, self)



class ClassesWindow(QDialog):

    def __init__(self, configs_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Detectify")
        self.resize(500, 350)
        self.configs_path = configs_path
        self._parent = parent

        layout = QVBoxLayout(self)

        self.class_list = QListWidget()
        self.class_list.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        layout.addWidget(self.class_list)

        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton()
        self.add_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'add.png')))
        
        button_layout.addWidget(self.add_button)

        self.save_button = QPushButton("Save")
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.add_button.clicked.connect(self.add_editable_class)
        self.save_button.clicked.connect(self.save_and_close)

        self.load_classes()


    def closeEvent(self, event):
        event.accept()


    def load_classes(self):
        self.config_data = self._parent.configs
        self.classes = sorted([key for key, value in self.config_data.items() if 'color' in value])
        self.update_class_list()


    def update_class_list(self):
        self.class_list.clear()

        for class_name in self.classes:
            color = self.config_data[class_name]['color']
            is_fixed = self.config_data[class_name]['fix']

            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(10, 0, 0, 0)

            class_label = QLabel(class_name)
            class_label.setStyleSheet("padding-left: 20px;")
            item_layout.addWidget(class_label)

            if not is_fixed:
                remove_button = QPushButton()
                remove_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'trash.png')))
                remove_button.setFixedSize(24, 24)
                remove_button.clicked.connect(lambda _, cls=class_name: self.remove_class(cls))
                item_layout.addWidget(remove_button)

            color_button = QPushButton()
            color_button.setFixedSize(24, 24)
            color_button.setStyleSheet(f"background-color: rgb({color[0]}, {color[1]}, {color[2]});")
            color_button.clicked.connect(lambda _, cls=class_name: self.change_color(cls))
            item_layout.addWidget(color_button)

            list_item = QListWidgetItem(self.class_list)
            list_item.setSizeHint(item_widget.sizeHint())
            self.class_list.addItem(list_item)
            self.class_list.setItemWidget(list_item, item_widget)


    def add_editable_class(self):
        self.add_button.setEnabled(False)
        self.save_button.setEnabled(False)

        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(10, 0, 0, 0)

        class_input = QLineEdit()
        class_input.setPlaceholderText("Class name")
        class_input.setStyleSheet("padding-left: 20px;")
        item_layout.addWidget(class_input)

        save_button = QPushButton()
        save_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'check.png')))
        save_button.clicked.connect(lambda: self.save_new_class(class_input, color_button))
        item_layout.addWidget(save_button)

        remove_button = QPushButton()
        remove_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'trash.png')))
        remove_button.setFixedSize(24, 24)
        remove_button.clicked.connect(lambda: self.remove_temporary_class(item_widget))
        item_layout.addWidget(remove_button)

        color_button = QPushButton()
        color_button.setFixedSize(24, 24)
        color_button.setStyleSheet("background-color: rgb(0, 0, 0);")
        color_button.clicked.connect(lambda: self.change_color_directly(color_button))
        item_layout.addWidget(color_button)

        list_item = QListWidgetItem(self.class_list)
        list_item.setSizeHint(item_widget.sizeHint())
        self.class_list.addItem(list_item)
        self.class_list.setItemWidget(list_item, item_widget)


    def save_new_class(self, class_input, color_button):
        new_class = class_input.text().strip()

        if new_class and new_class not in self.classes:
            color = color_button.palette().color(color_button.backgroundRole()).getRgb()[:3]

            self.classes.append(new_class)
            self.config_data[new_class] = {
                "color": list(color), 
                "fix": False
            }

            self.add_button.setEnabled(True)
            self.save_button.setEnabled(True)
            self.update_class_list()

        elif not new_class:
            QMessageBox.warning(self, "Detectify", "The class name can not be empty.")

        else:
            QMessageBox.warning(self, "Detectify", "The class already exists.")


    def remove_temporary_class(self, item_widget):
        self.add_button.setEnabled(True)
        self.save_button.setEnabled(True)

        for index in range(self.class_list.count()):
            item = self.class_list.item(index)
            widget = self.class_list.itemWidget(item)
            if widget == item_widget:
                self.class_list.takeItem(index)
                break


    def change_color_directly(self, color_button):
        color = QColorDialog.getColor(QColor(0, 0, 0), self, "Detectify")
        if color.isValid():
            color_button.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")


    def remove_class(self, class_name):
        if self.config_data[class_name]['fix']:
            QMessageBox.warning(self, "Detectify", "This class can not be removed.")

        else:
            self.classes.remove(class_name)
            self.config_data.pop(class_name, None)
            self.update_class_list()


    def change_color(self, class_name):
        current_color = self.config_data[class_name]["color"]
        color = QColorDialog.getColor(QColor(*current_color), self, "Detectify")
        
        if color.isValid():
            self.config_data[class_name]["color"] = [color.red(), color.green(), color.blue()]
            self.update_class_list()


    def save_classes(self):
        with open(self.configs_path, 'w', encoding='utf-8') as file:
            json.dump(self.config_data, file, ensure_ascii=False, indent=4)


    def save_and_close(self):
        self.save_classes()
        self.accept()



class DraggableLabel(QLabel):

    def __init__(self, parent=None, max_size=None, cable_name=None, detections=None, configs=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.drag_enabled = False
        self.dragging = False
        self.draw_enabled = False
        self.drawing = False
        self.arrow_enabled = False
        self.arrowing = False
        self.boxes = {}
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.zoom = 1.65888
        self.image = None
        self.detections = detections
        self.max_size = max_size
        self.rescale_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.cable_name = cable_name
        self.load_image()
        self.set_current_image()
        self._parent = parent
        self.configs = configs
        self.selected_id = None
        self.factors = None
        self.box_holder = None
        self.delete_box = False
        self.selected_classes = []
        self.last_delta = QPointF()


    def load_image(self):
        images_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'images')
        images = [os.path.join(images_path, img) for img in os.listdir(images_path)]

        if len(images) == 1:
            path, self.rescale_factor = Utils.verify_resolution(images[0])
            self.image = QPixmap(path)

        else:
            original, rescaled = None, None

            for image in images:
                if 'rescale' in os.path.basename(image):
                    rescaled = image

                else:
                    original = image

            self.image = QPixmap(rescaled)
            self.calculate_rescale_factor(original, rescaled)


    def calculate_rescale_factor(self, original, rescaled):
        image = Image.open(original)
        image_rescaled = Image.open(rescaled)

        self.rescale_factor = image_rescaled.size[0] / image.size[0]


    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        self.draw_boxes(painter)

        if self.draw_enabled and self.delete_box == False:
            _painter = QPainter(self)
            pen = QPen(Qt.GlobalColor.black, 2)
            _painter.setPen(pen)
            self.box_holder = self.generate_box()
            _painter.drawRect(self.box_holder)
        
        elif self.delete_box:
            self.box_holder = None

        elif self.arrowing:
            _painter = QPainter(self)
            pen = QPen(Qt.GlobalColor.black, 2)
            _painter.setPen(pen)
            painter.drawLine(self.start_point * self.zoom, self.end_point * self.zoom)


    def generate_box(self):
        new_start_point = QPoint(min(self.start_point.x(), self.end_point.x()), min(self.start_point.y(), self.end_point.y()))
        new_end_point = QPoint(max(self.start_point.x(), self.end_point.x()), max(self.start_point.y(), self.end_point.y()))

        return QRect(new_start_point * self.zoom, new_end_point * self.zoom)


    def draw_boxes(self, painter):
        self.calculate_factors()
        x_arrow, y_arrow = None, None
        drilling_points = []
        in_wire = False

        x_ratio, y_ratio, x_offset, y_offset = self.factors

        for id, det in self.detections.items():
            _class = det['class']

            if _class in self.configs and 'color' in self.configs[_class]:
                _width = (det['x2'] - det['x1']) * self.rescale_factor
                _height = (det['y2'] - det['y1']) * self.rescale_factor

                x1 = (det['x1'] * self.rescale_factor * x_ratio) + x_offset
                y1 = (det['y1'] * self.rescale_factor * y_ratio) + y_offset
                width = _width * x_ratio
                height = _height * y_ratio

                x2 = x1 + width
                y2 = y1 + height

                self.boxes[id] = {
                    'x1': int(x1),
                    'y1': int(y1),
                    'x2': int(x2),
                    'y2': int(y2)
                }

                if 'arrow_pointer' in det:
                    x_arrow = int((det['arrow_pointer'][0] * self.rescale_factor * x_ratio) + x_offset)
                    y_arrow = int((det['arrow_pointer'][1] * self.rescale_factor * y_ratio) + y_offset)

                if 'drilling_points' in det:
                    for dp in det['drilling_points']:
                        drilling_points.append((int((dp[0] * self.rescale_factor * x_ratio) + x_offset), int((dp[1] * self.rescale_factor * y_ratio) + y_offset)))

            if self.selected_id != None and 'object' in self.detections[self.selected_id] and self.detections[self.selected_id]['object'] == id:
                in_wire = True

            if self.selected_id == id or ('object' in det and self.selected_id == det['object']) or in_wire or _class in self.selected_classes:
                if self.selected_id == id or ('object' in det and self.selected_id == det['object']) or in_wire:
                    pen = QPen(Qt.GlobalColor.black, 2)
                
                else:
                    _class = det['class']
                    color_list = self.configs[_class]['color']
                    pen = QPen(QColor(color_list[0], color_list[1], color_list[2]), 2)

                painter.setPen(pen)
                painter.drawRect(QRect(int(x1), int(y1), int(width), int(height)))

                if x_arrow != None:
                    radius = int(1.5 * self.zoom)               
                    path = QPainterPath()
                    path.addEllipse(x_arrow - radius, y_arrow - radius, radius * 2, radius * 2)

                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    painter.setPen(Qt.PenStyle.NoPen)  
                    painter.fillPath(path, pen.color())

                for drilling_point in drilling_points:
                    pen = QPen(QColor(190, 20, 120), 2)
                    radius = int(1.5 * self.zoom)
                    path = QPainterPath()
                    path.addEllipse(drilling_point[0] - radius, drilling_point[1] - radius, radius * 2, radius * 2)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    painter.setPen(Qt.PenStyle.NoPen)  
                    painter.fillPath(path, pen.color())
                    
            x_arrow, y_arrow = None, None
            drilling_points = []
            in_wire = False


    def calculate_factors(self):
        original = self.image.size()
        curr = self.size()

        aspect_ratio_original = original.width() / original.height()
        aspect_ratio_curr = curr.width() / curr.height()

        if aspect_ratio_original > aspect_ratio_curr:
            x_ratio = curr.width() / original.width()
            y_ratio = x_ratio
            x_offset = 0
            y_offset = int((curr.height() - original.height() * y_ratio) / 2)

        else:
            y_ratio = curr.height() / original.height()
            x_ratio = y_ratio
            y_offset = 0
            x_offset = int((curr.width() - original.width() * x_ratio) / 2)

        self.factors = x_ratio, y_ratio, x_offset, y_offset


    def calculate_reverse_factors(self, x1_resized, y1_resized, width_resized, height_resized):
        x_ratio, y_ratio, x_offset, y_offset = self.factors
   
        x1_original = (x1_resized - x_offset) / (x_ratio * self.rescale_factor)
        y1_original = (y1_resized - y_offset) / (y_ratio * self.rescale_factor)
        width_original = width_resized / (x_ratio * self.rescale_factor)
        height_original = height_resized / (y_ratio * self.rescale_factor)

        return int(x1_original), int(y1_original), int(width_original), int(height_original)


    def zoom_in(self, cursor_pos, scroll_area):
        if self.zoom < 10:
            self.change_zoom(1.2, cursor_pos, scroll_area)


    def zoom_out(self, cursor_pos, scroll_area):
        if self.zoom > 0.9:
            self.change_zoom(1 / 1.2, cursor_pos, scroll_area)


    def change_zoom(self, factor, cursor_pos, scroll_area):
        self.zoom *= factor

        old_width = self.pixmap().width()
        old_height = self.pixmap().height()

        self.set_current_image()

        new_width = self.pixmap().width()
        new_height = self.pixmap().height()
     
        scroll_h = scroll_area.horizontalScrollBar()
        scroll_v = scroll_area.verticalScrollBar()

        scroll_h.setRange(0, max(0, int(new_width * self.zoom))) 
        scroll_v.setRange(0, max(0, int(new_height * self.zoom))) 

        cursor_widget_pos = self.mapTo(scroll_area.widget(), cursor_pos)

        cursor_x = max(0, min(cursor_widget_pos.x(), old_width))
        cursor_y = max(0, min(cursor_widget_pos.y(), old_height))

        delta_x = (cursor_x / old_width) * (new_width - old_width) if old_width > 0 else 0
        delta_y = (cursor_y / old_height) * (new_height - old_height) if old_height > 0 else 0

        new_scroll_h_value = scroll_h.value() + delta_x
        new_scroll_v_value = scroll_v.value() + delta_y

        scroll_h.setValue(int(new_scroll_h_value))
        scroll_v.setValue(int(new_scroll_v_value))


    def set_current_image(self):
        scaled_pixmap = self.image.scaled(self.max_size * self.zoom, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pixmap)
        self.update()


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.draw_enabled:
                self.drawing = True
                self.delete_box = False
                self.start_point = event.pos() / self.zoom
                self.end_point = self.start_point

            elif self.drag_enabled:
                self.dragging = True
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                self.start_point = event.pos() / self.zoom

            if self.arrow_enabled:
                self.arrowing = True
                self.delete_box = False
                self.start_point = event.pos() / self.zoom
                self.end_point = self.start_point

        elif event.button() == Qt.MouseButton.RightButton:
            if self.drag_enabled:
                clicked_box_id = None
                click_pos = event.pos() 

                for id, box in self.boxes.items():
                    if (box['x1'] <= click_pos.x() <= box['x2']) and (box['y1'] <= click_pos.y() <= box['y2']):
                        clicked_box_id = id
                        break  

                if clicked_box_id is not None:
                    self.selected_id = clicked_box_id
                    
                    layout_ = self.layout()
                    
                    if layout_ is None: 
                        layout_ = QVBoxLayout(self)
                        self.setLayout(layout_)

                    if layout_ is not None:
                        while layout_.count():
                            item = layout_.takeAt(0)
                            if item.widget() and isinstance(item.widget(), InfoSquare):
                                item.widget().deleteLater()
                                layout_.removeItem(item)

                    if self.detections[clicked_box_id] is not None:
                        detection_infos = InfoSquare(Qt.CursorShape.OpenHandCursor, clicked_box_id, [key for key, value in self.configs.items() if 'color' in value], self.detections, self.box_holder, self)
                        detection_infos.exec()
                        self.dragging = False
                        self.update()

            elif self.arrow_enabled:
                self.start_point = event.pos() / self.zoom
                self.end_point = self.start_point


    def mouseMoveEvent(self, event):
        self.end_point = event.pos() / self.zoom

        if self.drawing or self.arrowing:
            self.update()

        elif self.dragging:
            raw_delta = QPointF(self.end_point - self.start_point) * self.zoom  
        
            smoothing_factor = 0.45 
            delta = self.last_delta * (1 - smoothing_factor) + raw_delta * smoothing_factor
            self.last_delta = delta

            scroll_h = self._parent.scroll_area.horizontalScrollBar()
            scroll_v = self._parent.scroll_area.verticalScrollBar()

            value_h = scroll_h.value() - delta.x()
            value_v = scroll_v.value() - delta.y()

            scroll_h.setValue(int(value_h))
            scroll_v.setValue(int(value_v))

            self.start_point = self.end_point


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.drag_enabled:
                self.dragging = False
                self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))

            elif self.draw_enabled:
                self.drawing = False

                dialog = InfoSquare(Qt.CursorShape.CrossCursor, None, [key for key, value in self.configs.items() if 'color' in value], self.detections, self.box_holder, self)
                dialog.exec()
        
                self.delete_box = True
                self.update()

            elif self.arrow_enabled:
                self.arrowing = False
                self.delete_box = False

                selected_id = None

                for id, box in self.boxes.items():
                    if (box['x1'] <= self.start_point.x() * self.zoom  <= box['x2']) and (box['y1'] <= self.start_point.y() * self.zoom <=  box['y2']):
                        selected_id = id
                        break

                if selected_id is not None:
                    _class = self.detections[id]['class']
                    if _class in ['tubo', 'splice']:
                        end_x, end_y, _, _ = self.calculate_reverse_factors(self.end_point.x() * self.zoom, self.end_point.y() * self.zoom, 0, 0)
                        self.detections[id]['arrow_pointer'] = end_x, end_y
                        self.selected_id = selected_id

                    elif _class == 'wire_box':
                        end_id = None

                        for id, box in self.boxes.items():
                            if (box['x1'] <= self.end_point.x() * self.zoom  <= box['x2']) and (box['y1'] <= self.end_point.y() * self.zoom <=  box['y2']):
                                end_id = id
                                break

                        if end_id is not None:
                            if self.configs[self.detections[end_id]['class']]['is_labeled']:                            
                                self.detections[selected_id]['object'] = end_id
                                self.selected_id = end_id

                        else:
                            QMessageBox.warning(self, "Detectify", "Couldn't connect the box with a valid object.")

                    elif self.configs[_class]['is_labeled']:
                        end_id = None

                        for id, box in self.boxes.items():
                            if (box['x1'] <= self.end_point.x() * self.zoom  <= box['x2']) and (box['y1'] <= self.end_point.y() * self.zoom <=  box['y2']):
                                end_id = id
                                break

                        if end_id is not None:
                            if self.detections[end_id]['class'] == 'wire_box':
                                self.detections[end_id]['object'] = selected_id
                                self.selected_id = selected_id

                        else:
                            QMessageBox.warning(self, "Detectify", "Couldn't connect the object with a valid box.")

                    else:
                        QMessageBox.warning(self, "Detectify", "Couldn't find a valid object.")

                else:
                    QMessageBox.warning(self, "Detectify", "Couldn't find an object.")

        elif event.button() == Qt.MouseButton.RightButton:
            if self.arrow_enabled:
                selected_id = None

                for id, box in self.boxes.items():
                    if (box['x1'] <= self.start_point.x() * self.zoom  <= box['x2']) and (box['y1'] <= self.start_point.y() * self.zoom <=  box['y2']):
                        selected_id = id
                        break

                if selected_id is not None:
                    _class = self.detections[id]['class']
                    
                    if _class == 'wire_box':
                        end_id = None

                        for id, box in self.boxes.items():
                            if (box['x1'] <= self.end_point.x() * self.zoom  <= box['x2']) and (box['y1'] <= self.end_point.y() * self.zoom <=  box['y2']):
                                end_id = id
                                break

                        if end_id is not None:
                            if self.configs[self.detections[end_id]['class']]['is_labeled']:
                                if 'object' in self.detections[selected_id]:
                                    self.detections[selected_id].pop('object')
                                self.selected_id = end_id

                    elif self.configs[_class]['is_labeled']:
                        end_id = None

                        for id, box in self.boxes.items():
                            if (box['x1'] <= self.end_point.x() * self.zoom  <= box['x2']) and (box['y1'] <= self.end_point.y() * self.zoom <=  box['y2']):
                                end_id = id
                                break

                        if end_id is not None:
                            if self.detections[end_id]['class'] == 'wire_box':
                                if 'object' in self.detections[end_id]:
                                    self.detections[end_id].pop('object')
                                    
                                self.selected_id = selected_id

        self.update()


    def update_tables(self):
        self._parent.update_summary_tab()
        self._parent.clear_search_bar()


    def handle_suggestion(self, sugg_id, sugg_content):
        self.selected_id = sugg_id
        self.update()

        self.detections[sugg_id] = sugg_content
        dialog = InfoSquare(Qt.CursorShape.ArrowCursor, sugg_id, [key for key, value in self.configs.items() if 'color' in value], self.detections, self.box_holder, self)
        dialog.exec()



class GraphLabel(QLabel):

    def __init__(self, parent=None, max_size=None, nodes=None, edges=None, wires=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.connect_enabled = False
        self.connecting = False
        self.drag_enabled = False
        self.dragging = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.zoom = 1.5552
        self._parent = parent
        self.max_size = max_size
        self.nodes = nodes
        self.edges = edges
        self.wires = wires
        self.factors = None
        self.last_delta = QPointF()
        self.load_image()
        self.points = {}
        self.current_edges = []
        self.selected_wires = {}


    def load_image(self):
        self.image = QPixmap(self._parent._parent.image_label.image)
        self.rescale_factor = self._parent._parent.image_label.rescale_factor
        self.set_image()


    def set_image(self):
        scaled_pixmap = self.image.scaled(self.max_size * self.zoom, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pixmap)
        self.update()


    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        self.draw_graph(painter)

        if self.connecting:
            _painter = QPainter(self)
            pen = QPen(Qt.GlobalColor.black, 2)
            _painter.setPen(pen)
            painter.drawLine(self.start_point * self.zoom, self.end_point * self.zoom)


    def draw_graph(self, painter):
        self.calculate_factors()

        x_ratio, y_ratio, x_offset, y_offset = self.factors

        for node_id, (x, y) in self.nodes.items():
            scaled_x = int((x * self.rescale_factor * x_ratio) + x_offset)
            scaled_y = int((y * self.rescale_factor * y_ratio) + y_offset)

            self.points[node_id] = {
                'x': scaled_x,
                'y': scaled_y
            }

            radius = int(4 * self.zoom)               
            path = QPainterPath()
            path.addEllipse(scaled_x - radius, scaled_y - radius, radius * 2, radius * 2)

            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)  
            painter.fillPath(path, Qt.GlobalColor.blue)

        edges_iter = self.current_edges if self.current_edges else list(self.edges)
        for edge_id in edges_iter:
            nodes = self.edges[edge_id]

            node1_x, node1_y = self.points[nodes['node1']]['x'], self.points[nodes['node1']]['y']
            node2_x, node2_y = self.points[nodes['node2']]['x'], self.points[nodes['node2']]['y']

            pen = QPen(Qt.GlobalColor.red, int(self.zoom))
            painter.setPen(pen)
            painter.drawLine(QPoint(node1_x, node1_y), QPoint(node2_x, node2_y))


    def calculate_factors(self):
        original = self.image.size()
        curr = self.size()

        aspect_ratio_original = original.width() / original.height()
        aspect_ratio_curr = curr.width() / curr.height()

        if aspect_ratio_original > aspect_ratio_curr:
            x_ratio = curr.width() / original.width()
            y_ratio = x_ratio
            x_offset = 0
            y_offset = int((curr.height() - original.height() * y_ratio) / 2)

        else:
            y_ratio = curr.height() / original.height()
            x_ratio = y_ratio
            y_offset = 0
            x_offset = int((curr.width() - original.width() * x_ratio) / 2)

        self.factors = x_ratio, y_ratio, x_offset, y_offset


    def zoom_in(self, cursor_pos, scroll_area):
        if self.zoom < 10.5:
            self.change_zoom(1.2, cursor_pos, scroll_area)


    def zoom_out(self, cursor_pos, scroll_area):
        if self.zoom > 0.80:
            self.change_zoom(1 / 1.2, cursor_pos, scroll_area)


    def change_zoom(self, factor, cursor_pos, scroll_area):
        self.zoom *= factor

        old_width = self.pixmap().width()
        old_height = self.pixmap().height()

        self.set_image()

        new_width = self.pixmap().width()
        new_height = self.pixmap().height()
     
        scroll_h = scroll_area.horizontalScrollBar()
        scroll_v = scroll_area.verticalScrollBar()

        scroll_h.setRange(0, max(0, int(new_width * self.zoom))) 
        scroll_v.setRange(0, max(0, int(new_height * self.zoom))) 

        cursor_widget_pos = self.mapTo(scroll_area.widget(), cursor_pos)

        cursor_x = max(0, min(cursor_widget_pos.x(), old_width))
        cursor_y = max(0, min(cursor_widget_pos.y(), old_height))

        delta_x = (cursor_x / old_width) * (new_width - old_width) if old_width > 0 else 0
        delta_y = (cursor_y / old_height) * (new_height - old_height) if old_height > 0 else 0

        new_scroll_h_value = scroll_h.value() + delta_x
        new_scroll_v_value = scroll_v.value() + delta_y

        scroll_h.setValue(int(new_scroll_h_value))
        scroll_v.setValue(int(new_scroll_v_value))


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.drag_enabled:
                self.dragging = True
                self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
                self.start_point = event.pos() / self.zoom

            elif self.connect_enabled:
                self.connecting = True
                self.start_point = event.pos() / self.zoom
                self.end_point = self.start_point

        elif event.button() == Qt.MouseButton.RightButton:
            if self.connect_enabled:
                self.start_point = event.pos() / self.zoom


    def mouseMoveEvent(self, event):
        if self.dragging:
            self.end_point = event.pos() / self.zoom
            raw_delta = QPointF(self.end_point - self.start_point) * self.zoom  
        
            smoothing_factor = 0.45 
            delta = self.last_delta * (1 - smoothing_factor) + raw_delta * smoothing_factor
            self.last_delta = delta

            scroll_h = self._parent.scroll_area.horizontalScrollBar()
            scroll_v = self._parent.scroll_area.verticalScrollBar()

            value_h = scroll_h.value() - delta.x()
            value_v = scroll_v.value() - delta.y()

            scroll_h.setValue(int(value_h))
            scroll_v.setValue(int(value_v))

            self.start_point = self.end_point

        elif self.connecting:
            self.end_point = event.pos() / self.zoom
            self.update()


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.drag_enabled:
                self.dragging = False
                self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))

            elif self.connect_enabled:
                self.connecting = False

                if ((start_id := self.is_inside_point(self.start_point)) is not None) and ((end_id := self.is_inside_point(self.end_point)) is not None):                
                    if start_id != end_id:
                        edge_id = self._parent._parent.graph.add_edge(start_id, end_id)

                        if edge_id is not None:
                            self.current_edges = []
                            self.selected_wires = {}
                            self.update()

                        else:
                            QMessageBox.warning(self, "Detectify", "The edge already exists.")

                    else:
                        QMessageBox.warning(self, "Detectify", "Can only create an edge between two different nodes.")

                else:
                    QMessageBox.warning(self, "Detectify", "Couldn't find two valid nodes.")

        elif event.button() == Qt.MouseButton.RightButton and self.connect_enabled:
            self.end_point = event.pos() / self.zoom

            if ((start_id := self.is_inside_point(self.start_point)) is not None) and ((end_id := self.is_inside_point(self.end_point)) is not None):
                deleted_edge = False
                
                for edge_id, nodes in self.edges.items():
                    if (start_id == nodes['node1'] and end_id == nodes['node2']) or (start_id == nodes['node2'] and end_id == nodes['node1']):
                        self._parent._parent.graph.remove_edge(edge_id)
                        self.current_edges = []
                        self.selected_wires = {}
                        deleted_edge = True
                        break

                if deleted_edge == True:
                    self.update()

                else:
                    QMessageBox.warning(self, "Detectify", "Couldn't find a valid edge.")

            else:
                QMessageBox.warning(self, "Detectify", "Couldn't find two valid nodes.")

            self.update()


    def is_inside_point(self, point):
        for node_id, center in self.points.items():
            distance = ((int(point.x() * self.zoom) - center['x']) ** 2 + (int(point.y() * self.zoom) - center['y']) ** 2) ** 0.5
            if distance <= int(4 * self.zoom):
                return node_id

        return None



class GraphWindow(QMainWindow):

    def __init__(self, parent, cable_name, wires):
        super().__init__()
        self.setWindowTitle("Detectify")
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'logo.png')))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Detectify')

        self.showMaximized()

        self._parent = parent
        self.cable_name = cable_name
        self.wires = sorted(wires, key=lambda x: x[0])

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.main_content()


    def main_content(self):
        self.delete_content()

        QCoreApplication.processEvents()

        self.image_label = GraphLabel(self, self.central_widget.size(), self._parent.graph.positions, self._parent.graph.edges, self.wires)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scroll_area = NoScrollScrollArea(self, self.image_label)
        self.scroll_area.setWidget(self.image_label)

        self.image_layout = QVBoxLayout()
        self.image_layout.setSpacing(5)
        self.image_layout.setContentsMargins(0, 0, 0, 0)
        self.image_layout.addWidget(self.scroll_area)

        self.toolbox_layout = QHBoxLayout()

        self.drag_button = QPushButton()
        self.drag_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'drag.png')))
        self.connect_button = QPushButton()
        self.connect_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'connection.png')))
        self.reset_button = QPushButton()
        self.reset_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'reset.png')))
        self.save_button = QPushButton()
        self.save_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'save.png')))
        
        self.toolbox_layout.addWidget(self.drag_button)
        self.toolbox_layout.addWidget(self.connect_button)
        self.toolbox_layout.addWidget(self.reset_button)
        self.toolbox_layout.addWidget(self.save_button)

        self.image_layout.addLayout(self.toolbox_layout)

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addLayout(self.image_layout, 75)

        self.create_wires_table()
        self.horizontal_layout.addWidget(self.wires_table, 25)

        self.layout.addLayout(self.horizontal_layout)

        self.drag_button.clicked.connect(self.toggle_drag)
        self.connect_button.clicked.connect(self.toggle_connect)
        self.reset_button.clicked.connect(self.reset_wires)
        self.save_button.clicked.connect(self.save_graph)


    def toggle_drag(self):
        self.image_label.drag_enabled = not self.image_label.drag_enabled
        self.scroll_area.zoom_enabled = not self.scroll_area.zoom_enabled

        if self.image_label.drag_enabled:
            self.drag_button.setStyleSheet("background-color: lightblue;")  
            self.image_label.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            self.connect_button.setStyleSheet("")
            self.image_label.connect_enabled = False

        else:
            self.drag_button.setStyleSheet("")  
            self.image_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))


    def toggle_connect(self):
        self.image_label.connect_enabled = not self.image_label.connect_enabled

        if self.image_label.connect_enabled:
            self.connect_button.setStyleSheet("background-color: lightblue;")
            self.image_label.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.drag_button.setStyleSheet("")
            self.image_label.drag_enabled = False
            self.scroll_area.zoom_enabled = False

        else:
            self.connect_button.setStyleSheet("")
            self.image_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))


    def create_wires_table(self):
        self.wires_table = QTableWidget()
        self.wires_table.setRowCount(len(self.wires))
        self.wires_table.setColumnCount(3)
        self.wires_table.setHorizontalHeaderLabels(['Wire', 'Node 1', 'Node 2'])
        self.wires_table.horizontalHeader().setStretchLastSection(True)
        self.wires_table.itemClicked.connect(self.choose_wire)

        for row, (wire, node1, node2) in enumerate(self.wires):
            wire_item = QTableWidgetItem(wire)
            wire_item.setFlags(wire_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.wires_table.setItem(row, 0, wire_item)

            node1_item = QTableWidgetItem(node1)
            node1_item.setFlags(node1_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.wires_table.setItem(row, 1, node1_item)

            node2_item = QTableWidgetItem(node2)
            node2_item.setFlags(node2_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.wires_table.setItem(row, 2, node2_item)

        self.layout.addWidget(self.wires_table)


    def delete_content(self):
        if hasattr(self, 'image_label'):
            while self.horizontal_layout.count():
                item = self.horizontal_layout.takeAt(0)
            
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())
        
            self.layout.removeItem(self.horizontal_layout)
            self.horizontal_layout.deleteLater()
            del self.horizontal_layout


    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())


    def choose_wire(self, item):
        wire_id = self.wires_table.item(item.row(), 0).text()

        if wire_id not in self.image_label.selected_wires:
            self.get_wire_path(wire_id)
            self.image_label.update()


    def get_wire_path(self, wire_id):
        for wire, node1, node2 in self.wires:
            if wire_id == wire:
                shortest_path = self._parent.graph.get_shortest_path(node1, node2)
                if shortest_path is not None:
                    self.image_label.selected_wires[wire_id] = shortest_path

                    for edge in shortest_path:
                        if edge not in self.image_label.current_edges:
                            self.image_label.current_edges.append(edge)

                else:
                    self.image_label.current_edges = []
                    self.image_label.selected_wires = {}
                    QMessageBox.warning(self, "Detectify", "Couldn't find a valid path.")

                break


    def reset_wires(self):
        self.image_label.current_edges = []
        self.image_label.selected_wires = {}
        self.image_label.update()


    def save_graph(self):
        file_path, _ = QFileDialog.getSaveFileName(None, "Detectify", "", "PNG Files (*.png);;All Files (*)")

        if not file_path:
            return

        image = cv2.imread(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'images', f'{self.cable_name}.png'))

        edges_iter = self.image_label.current_edges if self.image_label.current_edges else list(self.image_label.edges)
        for edge_id in edges_iter:
            node1 = self.image_label.edges[edge_id]['node1']
            node2 = self.image_label.edges[edge_id]['node2']
            
            cv2.line(image, tuple(map(int, self.image_label.nodes[node1])), tuple(map(int, self.image_label.nodes[node2])), (0, 0, 255), 8)

        for _, (x, y) in self.image_label.nodes.items():
            cv2.circle(image, (int(x), int(y)), 32, (255, 0, 0), -1)

        cv2.imwrite(file_path, image)



class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'interface.ui'), self)
        self.setWindowTitle('Detectify')
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'logo.png')))
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('Detectify')

        self.showMaximized()

        self.init_content()

        self.configs_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'configs', 'class_configs.json')
        self.configs = self.load_configs()
        
        self.actionOpen.triggered.connect(self.info_content)
        self.actionOpen_Recent.triggered.connect(self.open_recent)
        self.actionSave_2.setEnabled(False)
        self.actionSave_2.triggered.connect(self.save_cache)
        self.menuSave_As.setEnabled(False)
        self.actionPNG_file.triggered.connect(self.save_png)
        self.actionJSON_file.triggered.connect(self.save_json)
        self.actionExit.triggered.connect(self.close_app)
        self.menuRun.setEnabled(False)
        self.actionImport_JSON.triggered.connect(self.select_json)
        self.actionExport_Perforations.triggered.connect(self.export_perforations)
        self.menuBuild.setEnabled(False)
        self.actionBuild_Graph.triggered.connect(self.build_graph)
        self.actionClasses.triggered.connect(self.classes)

        self.check_cache()
        self.welcome_content()


    def init_content(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.separator_line = QFrame()
        self.separator_line.setFrameShape(QFrame.Shape.HLine)
        self.separator_line.setFrameShadow(QFrame.Shadow.Sunken)
        self.separator_line.setStyleSheet("height: 1px;")
        self.layout.addWidget(self.separator_line)


    def welcome_content(self):
        self.welcome_label = QLabel("Welcome to Detectify!\nOpen a cable project to start the application.")
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_label.setStyleSheet("font-size: 15px;")
        
        self.layout.addWidget(self.welcome_label)


    def load_configs(self):
        with open(self.configs_path, "r") as configs_file:
            configs = json.load(configs_file)

        return configs


    def open_recent(self):
        dialog = OpenRecent(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cable_name = dialog.selected_file
            self.run_app('cache', self.cable_name)

        else:
            return


    def save_png(self):
        file_path, _ = QFileDialog.getSaveFileName(None, "Detectify", "", "PNG Files (*.png);;All Files (*)")

        if not file_path:
            return
            
        image = cv2.imread(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'images', f'{self.cable_name}.png'))

        for detection in self.detections.values():
            _class = detection['class']
            if _class in self.configs and 'color' in self.configs[_class] and _class in self.image_label.selected_classes:
                list_color = self.configs[_class]['color']
                color = list_color[2], list_color[1], list_color[0]
                if _class == 'drilling_point':
                    x_center = detection['center'][0]
                    y_center = detection['center'][1]
                    detection['x1'] = None
                    detection['y1'] = None
                    detection['x2'] = None
                    detection['y2'] = None
                else:
                    x_center, y_center = None, None

                Utils.draw_detection(image, _class, color, detection['x1'], detection['y1'], detection['x2'], detection['y2'], x_center, y_center)

        cv2.imwrite(file_path, image)


    def save_json(self):
        file_path, _ = QFileDialog.getSaveFileName(None, "Detectify", "", "JSON Files (*.json);;All Files (*)")

        if file_path:
            with open(file_path, 'w', encoding='utf-8') as output:
                json.dump(self.detections, output, ensure_ascii=False, indent=4, default=Utils.convert_to_serializable)


    def save_cache(self):
        if self.save_file:
            with open(self.save_file, 'w', encoding='utf-8') as output:
                json.dump(self.detections, output, ensure_ascii=False, indent=4, default=Utils.convert_to_serializable)


    def ensure_detections_cache(self):
        detections_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'detections')

        if  len(os.listdir(detections_dir)) < 2:
            detections_file_path = os.path.join(detections_dir, f'{self.cable_name}.json')

            with open(detections_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.detections, file, ensure_ascii=False, indent=4, default=Utils.convert_to_serializable)


    def classes(self):
        self.classes_window = ClassesWindow(self.configs_path, self)
        self.classes_window.exec()
        if hasattr(self, 'image_label'):
            self.configs = self.load_configs()
            self.image_label.configs = self.configs

    
    def actions_status(self, status):
        self.actionSave_2.setEnabled(status)
        self.menuSave_As.setEnabled(status)
        self.menuRun.setEnabled(status)
        self.actionExport_Perforations.setEnabled(status)
        self.menuBuild.setEnabled(status)


    def info_content(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("PDF Files (*.pdf)")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()

            if selected_files:
                self.file = selected_files[0]
                self.cable_name = os.path.splitext(os.path.basename(self.file))[0]

                dialog = FileSelectionDialog(self)
        
                if dialog.exec():
                    self.actions_status(False)

                    self.run_app('dxf', dialog.file_paths())


    def main_content(self):
        self.delete_content()

        self.image_label = DraggableLabel(self, self.central_widget.size(), self.cable_name, self.detections, self.configs)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.scroll_area = NoScrollScrollArea(self, self.image_label)
        self.scroll_area.setWidget(self.image_label)

        self.image_layout = QVBoxLayout()
        self.image_layout.setSpacing(5)
        self.image_layout.setContentsMargins(0, 0, 0, 0)
        self.image_layout.addWidget(self.scroll_area)

        self.toolbox_layout = QHBoxLayout()

        self.drag_button = QPushButton()
        self.drag_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'drag.png')))
        self.draw_button = QPushButton()
        self.draw_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'draw.png')))
        self.arrow_button = QPushButton()
        self.arrow_button.setIcon(QIcon(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'images', 'arrow.png')))

        self.toolbox_layout.addWidget(self.drag_button)
        self.toolbox_layout.addWidget(self.draw_button)
        self.toolbox_layout.addWidget(self.arrow_button)

        self.image_layout.addLayout(self.toolbox_layout)

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addLayout(self.image_layout, 80)

        self.create_detections_table()
        self.horizontal_layout.addWidget(self.detections_table, 20)

        self.layout.addLayout(self.horizontal_layout)
        
        self.drag_button.clicked.connect(self.toggle_drag)
        self.draw_button.clicked.connect(self.toggle_draw)
        self.arrow_button.clicked.connect(self.toggle_arrow)

        self.actions_status(True)


    def delete_content(self):
        if hasattr(self, 'welcome_label'):
            self.layout.removeWidget(self.welcome_label)
            self.welcome_label.deleteLater()
            del self.welcome_label

        else:
            while self.horizontal_layout.count():
                item = self.horizontal_layout.takeAt(0)
            
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())
    
            self.layout.removeItem(self.horizontal_layout)
            self.horizontal_layout.deleteLater()
            del self.horizontal_layout


    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())


    def toggle_drag(self):
        self.image_label.drag_enabled = not self.image_label.drag_enabled
        self.scroll_area.zoom_enabled = not self.scroll_area.zoom_enabled

        if self.image_label.drag_enabled:
            self.drag_button.setStyleSheet("background-color: lightblue;")  
            self.image_label.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            self.draw_button.setStyleSheet("")
            self.arrow_button.setStyleSheet("")
            self.image_label.draw_enabled = False
            self.image_label.arrow_enabled = False

        else:
            self.drag_button.setStyleSheet("")  
            self.image_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))


    def toggle_draw(self):
        self.image_label.draw_enabled = not self.image_label.draw_enabled

        if self.image_label.draw_enabled:
            self.draw_button.setStyleSheet("background-color: lightblue;")
            self.image_label.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.drag_button.setStyleSheet("")
            self.arrow_button.setStyleSheet("")
            self.image_label.drag_enabled = False
            self.image_label.arrow_enabled = False  
            self.scroll_area.zoom_enabled = False

        else:
            self.draw_button.setStyleSheet("")
            self.image_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))


    def toggle_arrow(self):
        self.image_label.arrow_enabled = not self.image_label.arrow_enabled

        if self.image_label.arrow_enabled:
            self.arrow_button.setStyleSheet("background-color: lightblue;")
            self.image_label.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            self.drag_button.setStyleSheet("")
            self.draw_button.setStyleSheet("")
            self.image_label.drag_enabled = False
            self.image_label.draw_enabled = False  
            self.scroll_area.zoom_enabled = False

        else:
            self.arrow_button.setStyleSheet("")
            self.image_label.setCursor(QCursor(Qt.CursorShape.ArrowCursor))


    def calculate_class_totals(self):
        class_totals = {}

        for detection in self.detections.values():
            class_name = detection['class']
            if class_name in self.configs and 'color' in self.configs[class_name]:
                if class_name not in class_totals:
                    class_totals[class_name] = 0
                class_totals[class_name] += 1

        return OrderedDict(sorted(class_totals.items()))
    

    def create_detections_table(self):
        self.detections_table = QTabWidget()

        class_totals = self.calculate_class_totals()

        self.summary_tab = QTableWidget()
        self.summary_tab.setRowCount(len(class_totals))
        self.summary_tab.setColumnCount(2)
        self.summary_tab.setHorizontalHeaderLabels(['Class', 'Total'])
        self.summary_tab.horizontalHeader().setStretchLastSection(True)
        self.summary_tab.itemClicked.connect(self.highlight_class)
        
        for row, (class_name, total) in enumerate(class_totals.items()):
            class_item = QTableWidgetItem(class_name)
            class_item.setFlags(class_item.flags() & ~Qt.ItemFlag.ItemIsEditable) 
            self.summary_tab.setItem(row, 0, class_item)
    
            total_item = QTableWidgetItem(str(total))
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  
            self.summary_tab.setItem(row, 1, total_item)
        
        self.detections_table.addTab(self.summary_tab, 'Summary')

        tab_container = QWidget()
        self.tab_layout = QVBoxLayout(tab_container)

        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_table)

        self.objects_tab = QTableWidget()
        self.objects_tab.setColumnCount(1)
        self.objects_tab.setColumnWidth(0, 80)
        self.objects_tab.setHorizontalHeaderLabels(['ID'])
        self.objects_tab.horizontalHeader().setStretchLastSection(True)
        self.objects_tab.itemClicked.connect(self.highlight_detection)

        counter = 0
        label_list = []
        for id, detection in self.detections.items():
            if 'label' in detection:
                label_list.append((detection['label'], id))

        self.objects_tab.setRowCount(len(label_list))

        for label, id in sorted(label_list, key=lambda x: x[0]):
            id_item = QTableWidgetItem(label)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            id_item.setData(Qt.ItemDataRole.UserRole, id)
            self.objects_tab.setItem(counter, 0, id_item)
            counter += 1

        self.tab_layout.addWidget(self.search_bar)
        self.tab_layout.addWidget(self.objects_tab)
        
        self.detections_table.addTab(tab_container, 'Objects')
        self.layout.addWidget(self.detections_table)


    def update_summary_tab(self):
        class_totals = self.calculate_class_totals()
        self.summary_tab.setRowCount(len(class_totals))

        for row, (class_name, total) in enumerate(class_totals.items()):
            class_item = QTableWidgetItem(class_name)
            class_item.setFlags(class_item.flags() & ~Qt.ItemFlag.ItemIsEditable) 
            self.summary_tab.setItem(row, 0, class_item)
    
            total_item = QTableWidgetItem(str(total))
            total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  
            self.summary_tab.setItem(row, 1, total_item)


    def update_objects_tab(self, filtered_data=None):
        detections_to_display = filtered_data if filtered_data else self.detections

        if filtered_data:
            row_count = len(detections_to_display)
            
        else:
            if self.search_bar.text() != '':
                row_count = 0

            else:
              row_count = len([value for _, value in self.detections.items() if 'label' in value])
           
        self.objects_tab.setRowCount(row_count)

        counter = 0
        label_list = []
        for id, detection in detections_to_display.items():
            if 'label' in detection:
                label_list.append((detection['label'], id))

        for label, id in sorted(label_list, key=lambda x: x[0]):
            id_item = QTableWidgetItem(label)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            id_item.setData(Qt.ItemDataRole.UserRole, id)
            self.objects_tab.setItem(counter, 0, id_item)
            counter += 1


    def filter_table(self, text):    
        text = text.lower()

        if not text:
            self.update_objects_tab()
            return
    
        filtered_detections = {
            id: detection
            for id, detection in self.detections.items()
            if text in detection.get('label', '').lower()
        }

        self.update_objects_tab(filtered_detections)


    def clear_search_bar(self):
        self.search_bar.clear()
        self.update_objects_tab()


    def highlight_class(self, item):
        class_name = self.summary_tab.item(item.row(), 0).text()
        
        if class_name in self.image_label.selected_classes:
            self.image_label.selected_classes.remove(class_name)

        else:
            self.image_label.selected_classes.append(class_name)
            self.image_label.selected_id = None

        self.image_label.update()


    def highlight_detection(self, item):
        detection_id = item.data(Qt.ItemDataRole.UserRole)

        if detection_id == self.image_label.selected_id:
            self.image_label.selected_id = None

        else:
            self.image_label.selected_id = detection_id
        
        self.image_label.update()


    def close_app(self):
        self.close()


    def select_json(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("JSON Files (*.json)")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()

            if selected_files:
                self.run_app('json', selected_files[0])


    def export_perforations(self):
        drilling_points = []

        for _, det in self.detections.items():
            if 'drilling_points' in det:
                for drilling_point in det['drilling_points']:
                    drilling_points.append(drilling_point)

        if not drilling_points:
            QMessageBox.warning(self, "Detectify", "No drilling points detected.")
            return

        file_path, _ = QFileDialog.getSaveFileName(None, "Detectify", "", "JSON Files (*.json);;All Files (*)")

        if file_path:
            with open(file_path, 'w', encoding='utf-8') as output:
                json.dump(drilling_points, output, ensure_ascii=False, indent=4, default=Utils.convert_to_serializable)


    def run_app(self, code, src):
        self.progress_window = ProgressWindow(self)
        self.progress_window.show()
        QCoreApplication.processEvents()

        self.setEnabled(False)
        self.save_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'detections', f'{self.cable_name}.json')

        if code == 'dxf':
            self.inference_thread1 = InferenceThread1(self, src, self.file, self.configs, self.cable_name, False, True)

        elif code == 'cache':
            self.inference_thread1 = InferenceThread1(self, src, None, self.configs, self.cable_name, True, False)
        
        else:
            self.inference_thread1 = InferenceThread1(self, src, self.file, self.configs, self.cable_name, False, False)
            self.save_file = src

        self.inference_thread1.inference_done.connect(self.on_inference1_done)
        self.inference_thread1.start()


    def create_dirs(self):
        os.makedirs(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}'), exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'images'), exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'detections'), exist_ok=True)
        os.makedirs(os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{self.cable_name}', 'PDF'), exist_ok=True)


    def on_inference1_done(self, detections, image, file, graph):
        self.progress_window.close()
        self.setEnabled(True)

        self.detections = detections
        self.ensure_detections_cache()
        self.image = image
        self.file = file
        self.graph = graph

        self.check_cache()

        self.main_content()


    def build_graph(self):
        self.graph.update_detections(self.detections)
        self.graph_window = GraphWindow(self, self.cable_name, DXF_Interpreter.get_wire_connections(self.detections))
        self.graph_window.show()


    def check_cache(self):
        folder_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache')
        folder_list = os.listdir(folder_path)

        if folder_list:
            self.actionOpen_Recent.setEnabled(True)
            return True
        
        self.actionOpen_Recent.setEnabled(False)
        return False
    

    def clear_cache(self, filename):
        folder_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'cache', f'{filename}')
        
        if os.path.exists(folder_path):
            for folder in os.listdir(folder_path):
                shutil.rmtree(os.path.join(folder_path, folder), ignore_errors=True)
            os.rmdir(folder_path)
        
        self.check_cache()


    def resizeEvent(self, event):
        if hasattr(self, 'image_label'):
            self.main_content()

        super().resizeEvent(event)


    def closeEvent(self, event):
        event.accept()