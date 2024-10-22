#!/usr/bin/env python

import cv2
import numpy as np
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

from utils import region_dict


class ROIManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.rois = [region_dict(0, 0, 0, 0) for _ in range(4)]
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
        self.rois = [region_dict(0, 0, 0, 0) for _ in range(4)]
        self.update_image()

    def update_current_roi_index(self, index):
        """Update the current ROI index based on the selection from the combo box."""
        self.current_roi_index = index
        self.update_image()

    def update_roi_from_spin(self, index):
        """Update the ROI when the spin boxes change."""
        self.rois[index] = self._spinbox_to_roi(index)
        self.update_image()

    def _spinbox_to_roi(self, index: int) -> dict[str, int]:
        """Get the values from spin boxes as a region dictionary."""
        roi_control = self.roi_controls[index]
        x_low = min(roi_control[0].value(), roi_control[2].value())
        y_low = min(roi_control[1].value(), roi_control[3].value())
        x_high = max(roi_control[0].value(), roi_control[2].value())
        y_high = max(roi_control[1].value(), roi_control[3].value())
        return region_dict(
            x_low=x_low, y_low=y_low, x_high=x_high, y_high=y_high
            )

    def update_image(self):
        """Update the QLabel with the current image (with ROIs drawn)."""
        if self.image is None:
            return

        image_copy = self.image.copy()
        for i, roi in enumerate(self.rois):
            if roi['x_low'] is not None and roi['y_low'] is not None and roi['x_high'] is not None and roi['y_high'] is not None:
                cv2.rectangle(image_copy, (roi['x_low'], roi['y_low']), (roi['x_high'], roi['y_high']), self.colors[i], 2)

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
                x_low = min(self.start_pos.x(), self.end_pos.x())
                y_low = min(self.start_pos.y(), self.end_pos.y())
                x_high = max(self.start_pos.x(), self.end_pos.x())
                y_high = max(self.start_pos.y(), self.end_pos.y())
                self.rois[self.current_roi_index] = region_dict(
                    x_low=x_low, y_low=y_low, x_high=x_high, y_high=y_high
                    )
                self.update_image()
                self.update_spin_box_from_drag()  # Ensure spin boxes reflect final ROI

            # Reset positions
            self.start_pos = None
            self.end_pos = None

    def update_spinbox(self, index: int, roi: dict[str, int]):
        """Update the spin boxes at the given index based on the provided ROI."""
        x1_spin, y1_spin, x2_spin, y2_spin = self.roi_controls[index]
        x1_spin.setValue(roi['x_low'])
        y1_spin.setValue(roi['y_low'])
        x2_spin.setValue(roi['x_high'])
        y2_spin.setValue(roi['y_high'])

    def update_spin_box_from_drag(self):
        """Update the spin boxes based on the current drag positions."""
        if self.start_pos is not None and self.end_pos is not None:
            x_low = min(self.start_pos.x(), self.end_pos.x())
            y_low = min(self.start_pos.y(), self.end_pos.y())
            x_high = max(self.start_pos.x(), self.end_pos.x())
            y_high = max(self.start_pos.y(), self.end_pos.y())

            roi = region_dict(x_low=x_low, y_low=y_low, x_high=x_high, y_high=y_high)
            self.update_spinbox(self.current_roi_index, roi)

    def get_roi(self, index: int):
        return self.rois[index]
    
    def set_roi(self, index: int, roi: dict[str, int]):
        """
        Set the region dictionary at the specified index.
        The image display and appropriate spin box are updated to reflect the changes.

        Parameters:
            index (int): The index of the ROI to set.
            roi (dict[str, int]): The region dictionary to set at the index.
        """
        self.rois[index] = roi
        self.update_image()
        self.update_spinbox(index, roi)

    def get_rois(self):
        return self.rois
    
    def set_rois(self, rois: list[dict[str, int]]):
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
        region_dict(x_low=0, y_low=0, x_high=100, y_high=100),
        region_dict(x_low=100, y_low=100, x_high=200, y_high=200),
        region_dict(x_low=200, y_low=200, x_high=300, y_high=300),
        region_dict(x_low=300, y_low=300, x_high=400, y_high=400),
    ]
    window.set_rois(rois)
    window.show()
    sys.exit(app.exec_())
