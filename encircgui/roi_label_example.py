import sys
import numpy as np
from PyQt5.QtWidgets import QLabel, QApplication, QMainWindow, QVBoxLayout, QWidget, QComboBox, QHBoxLayout, QFormLayout

from roi_label import ROILabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.label = ROILabel(self)
        
        # Load a sample image (replace with your actual image)
        sample_image = np.zeros((480, 640, 3), dtype=np.uint8)
        sample_image[:] = (128, 128, 128)  # Set a gray background

        self.label.set_image(sample_image)

        # Create a combo box for selecting the ROI to edit
        self.roi_selector = QComboBox(self)
        self.roi_selector.addItems(['Edit Red ROI', 'Edit Green ROI', 'Edit Blue ROI', 'Edit Yellow ROI'])
        self.roi_selector.currentIndexChanged.connect(self.on_roi_selection)

        # Create QLabels to display the coordinates of all 4 ROIs
        self.red_roi_label = QLabel(self)
        self.green_roi_label = QLabel(self)
        self.blue_roi_label = QLabel(self)
        self.yellow_roi_label = QLabel(self)

        # Set default text for each ROI label
        self.red_roi_label.setText("Red ROI: N/A")
        self.green_roi_label.setText("Green ROI: N/A")
        self.blue_roi_label.setText("Blue ROI: N/A")
        self.yellow_roi_label.setText("Yellow ROI: N/A")

        # Create a layout for the coordinate display
        coord_layout = QFormLayout()
        coord_layout.addRow("Red ROI Coordinates:", self.red_roi_label)
        coord_layout.addRow("Green ROI Coordinates:", self.green_roi_label)
        coord_layout.addRow("Blue ROI Coordinates:", self.blue_roi_label)
        coord_layout.addRow("Yellow ROI Coordinates:", self.yellow_roi_label)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.roi_selector)

        # Add the coordinate layout to the main layout
        layout.addLayout(coord_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set the ROI change callback to update the coordinate labels
        self.label.on_roi_change = self.update_all_coordinates

    def on_roi_selection(self, index):
        """Handle changing which ROI is being edited"""
        self.label.set_current_roi(index)

    def update_all_coordinates(self, rois):
        """Update the coordinate labels for all 4 ROIs"""
        self.update_coordinates(self.red_roi_label, rois[0], "Red")
        self.update_coordinates(self.green_roi_label, rois[1], "Green")
        self.update_coordinates(self.blue_roi_label, rois[2], "Blue")
        self.update_coordinates(self.yellow_roi_label, rois[3], "Yellow")

    def update_coordinates(self, label, roi, color):
        """Update the coordinates label with the current ROI coordinates"""
        if roi.x1 is not None and roi.y1 is not None and roi.x2 is not None and roi.y2 is not None:
            label.setText(f"{color} ROI: Start ({roi.x1}, {roi.y1}), End ({roi.x2}, {roi.y2})")
        else:
            label.setText(f"{color} ROI: N/A")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
