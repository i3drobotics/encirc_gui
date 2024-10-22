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

        self.start_pos = None
        self.end_pos = None

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
        self.rois[index] = self._spinbox_to_roi(index)
        self.update_image()

    def _spinbox_to_roi(self, index: int) -> RegionOfInterest:
        """Get the values from spin boxes as a RegionOfInterest."""
        roi_control = self.roi_controls[index]
        roi = RegionOfInterest(
            x1=roi_control[0].value(),
            y1=roi_control[1].value(),
            x2=roi_control[2].value(),
            y2=roi_control[3].value(),
        )
        return roi

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
        self.end_pos = event.pos()
        self.update_image()  # Dynamically update the image
        self.update_spin_box_from_drag() # Dynamically update the spin boxes

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
                self.update_spin_box_from_drag()  # Ensure spin boxes reflect final ROI

            # Reset positions
            self.start_pos = None
            self.end_pos = None

    def update_spinbox(self, index: int, roi: RegionOfInterest):
        """Update the spin boxes at the given index based on the provided ROI."""
        x1_spin, y1_spin, x2_spin, y2_spin = self.roi_controls[index]
        x1_spin.setValue(roi.x1)
        y1_spin.setValue(roi.y1)
        x2_spin.setValue(roi.x2)
        y2_spin.setValue(roi.y2)

    def update_spin_box_from_drag(self):
        """Update the spin boxes based on the current drag positions."""
        if self.start_pos is not None and self.end_pos is not None:
            x1 = min(self.start_pos.x(), self.end_pos.x())
            y1 = min(self.start_pos.y(), self.end_pos.y())
            x2 = max(self.start_pos.x(), self.end_pos.x())
            y2 = max(self.start_pos.y(), self.end_pos.y())

            roi = RegionOfInterest(x1=x1, y1=y1, x2=x2, y2=y2)
            self.update_spinbox(self.current_roi_index, roi)

    def get_roi(self, index: int):
        return self.rois[index]
    
    def set_roi(self, index: int, roi: RegionOfInterest):
        """
        Set the RegionOfInterest at the specified index.
        The image display and appropriate spin box are updated to reflect the changes.

        Parameters:
            index (int): The index of the ROI to set.
            roi (RegionOfInterest): The RegionOfInterest object to set at the index.
        """
        self.rois[index] = roi
        self.update_image()
        self.update_spinbox(index, roi)

    def get_rois(self):
        return self.rois
    
    def set_rois(self, rois: list[RegionOfInterest]):
        for i, roi in enumerate(rois):
            self.set_roi(i, roi)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    script_dir = Path(__file__).parent.absolute()

    app = QApplication(sys.argv)
    window = ROIManager()

    # Example of setting an image
    image_bgr = cv2.imread(script_dir / "i3dr_logo.png")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    window.set_image(image_rgb)
    
    # Example of setting ROIs
    rois = [
        RegionOfInterest(x1=0, y1=0, x2=100, y2=100),
        RegionOfInterest(x1=100, y1=100, x2=200, y2=200),
        RegionOfInterest(x1=200, y1=200, x2=300, y2=300),
        RegionOfInterest(x1=300, y1=300, x2=400, y2=400),
    ]
    window.set_rois(rois)
    window.show()
    sys.exit(app.exec_())
