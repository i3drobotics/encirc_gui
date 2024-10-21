#!/usr/bin/env python

import cv2
import numpy as np
from dataclasses import dataclass
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSpinBox,
    QApplication,
    QComboBox
)
from PyQt5.QtCore import Qt
import qimage2ndarray
from PyQt5.QtGui import QPixmap


@dataclass
class RegionOfInterest:
    x1: int = None
    y1: int = None
    x2: int = None
    y2: int = None


class ROIManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.rois = [RegionOfInterest(0, 0, 0, 0) for _ in range(4)]
        self.current_roi_index = 0
        self.image = None
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Create the label for displaying images
        self.roi_label = QLabel(self)
        self.roi_label.setMouseTracking(True)
        main_layout.addWidget(self.roi_label)

        # Create the ROI selector combo box
        self.roi_selector_combo = QComboBox(self)
        self.roi_selector_combo.addItems([f"ROI {i + 1}" for i in range(4)])
        self.roi_selector_combo.currentIndexChanged.connect(self.update_current_roi_index)
        main_layout.addWidget(self.roi_selector_combo)

        # Creating ROI control widgets for 4 ROIs
        self.roi_controls = []
        for i in range(4):
            roi_layout = QHBoxLayout()
            roi_label = QLabel(f"ROI {i + 1}")
            roi_layout.addWidget(roi_label)

            x1_spin = QSpinBox()
            y1_spin = QSpinBox()
            x2_spin = QSpinBox()
            y2_spin = QSpinBox()
            x1_spin.setRange(0, 2000)
            y1_spin.setRange(0, 2000)
            x2_spin.setRange(0, 2000)
            y2_spin.setRange(0, 2000)

            roi_layout.addWidget(QLabel("x1:"))
            roi_layout.addWidget(x1_spin)
            roi_layout.addWidget(QLabel("y1:"))
            roi_layout.addWidget(y1_spin)
            roi_layout.addWidget(QLabel("x2:"))
            roi_layout.addWidget(x2_spin)
            roi_layout.addWidget(QLabel("y2:"))
            roi_layout.addWidget(y2_spin)

            self.roi_controls.append((x1_spin, y1_spin, x2_spin, y2_spin))
            main_layout.addLayout(roi_layout)

            for spin in (x1_spin, y1_spin, x2_spin, y2_spin):
                spin.valueChanged.connect(lambda _, idx=i: self.update_roi_from_spin(idx))

        self.setLayout(main_layout)
        
        self.roi_label.mousePressEvent = self.mouse_press_event
        self.roi_label.mouseMoveEvent = self.mouse_move_event
        self.roi_label.mouseReleaseEvent = self.mouse_release_event

    def set_image(self, image: np.ndarray):
        """Set the image and reset any existing ROIs."""
        self.image = image
        self.rois = [RegionOfInterest(0, 0, 0, 0) for _ in range(4)]
        self.update_image()

    def update_current_roi_index(self, index):
        """Update the current ROI index based on the selection from the combo box."""
        self.current_roi_index = index
        self.update_image()

    def update_roi_from_spin(self, index):
        """Update the ROI when the spin boxes change."""
        roi_dict = self.get_roi(index).__dict__
        self.rois[index] = RegionOfInterest(**roi_dict)
        self.update_image()

    def get_roi(self, index: int):
        """Get the values from spin boxes as a RegionOfInterest."""
        roi_control = self.roi_controls[index]
        return RegionOfInterest(
            x1=min(roi_control[0].value(), roi_control[2].value()),
            y1=min(roi_control[1].value(), roi_control[3].value()),
            x2=max(roi_control[0].value(), roi_control[2].value()),
            y2=max(roi_control[1].value(), roi_control[3].value()),
        )

    def update_image(self):
        """Update the QLabel with the current image (with ROIs drawn)."""
        if self.image is None:
            return

        image_copy = self.image.copy()
        for i, roi in enumerate(self.rois):
            if roi.x1 is not None and roi.y1 is not None and roi.x2 is not None and roi.y2 is not None:
                cv2.rectangle(image_copy, (roi.x1, roi.y1), (roi.x2, roi.y2), self.colors[i], 2)

        qt_image = qimage2ndarray.array2qimage(image_copy)
        self.roi_label.setPixmap(QPixmap.fromImage(qt_image))

    def mouse_press_event(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.end_pos = event.pos()  # Initialize end position

    def mouse_move_event(self, event):
        if hasattr(self, 'start_pos'):
            self.end_pos = event.pos()
            self.update_image()  # Dynamically update the image with the current rectangle
            
            # Update the spin boxes as the mouse is moved
            self.update_spin_boxes()

    def mouse_release_event(self, event):
        if event.button() == Qt.LeftButton:
            self.end_pos = event.pos()
            if self.start_pos is not None and self.end_pos is not None:  # Check before using the positions
                # Store the final ROI in the list
                self.rois[self.current_roi_index] = RegionOfInterest(
                    x1=self.start_pos.x(), y1=self.start_pos.y(),
                    x2=self.end_pos.x(), y2=self.end_pos.y()
                )
                self.update_image()
                self.update_spin_boxes()  # Ensure spin boxes reflect final ROI

            # Reset positions
            self.start_pos = None
            self.end_pos = None


    def update_spin_boxes(self):
        """Update the spin boxes based on the current drag positions."""
        if hasattr(self, 'start_pos') and self.start_pos is not None and hasattr(self, 'end_pos') and self.end_pos is not None:
            x1 = min(self.start_pos.x(), self.end_pos.x())
            y1 = min(self.start_pos.y(), self.end_pos.y())
            x2 = max(self.start_pos.x(), self.end_pos.x())
            y2 = max(self.start_pos.y(), self.end_pos.y())
            
            # Update the spin boxes for the current ROI
            x1_spin, y1_spin, x2_spin, y2_spin = self.roi_controls[self.current_roi_index]
            x1_spin.setValue(x1)
            y1_spin.setValue(y1)
            x2_spin.setValue(x2)
            y2_spin.setValue(y2)



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = ROIManager()
    # Example of setting an image
    image = np.zeros((1000, 1000, 3), dtype=np.uint8)  # Replace with your image
    window.set_image(image)
    window.show()
    sys.exit(app.exec_())
