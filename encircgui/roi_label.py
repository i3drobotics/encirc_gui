import cv2
import numpy as np
from dataclasses import dataclass
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import qimage2ndarray


@dataclass
class RegionOfInterest:
    x1: int = None
    y1: int = None
    x2: int = None
    y2: int = None

class ROILabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.start_pos = None
        self.end_pos = None
        self.image = None  # Original image
        self.image_with_rois = None  # Image with ROIs drawn
        self.rois = [RegionOfInterest() for _ in range(4)]  # List of 4 ROIs (Red, Green, Blue, Yellow)
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow
        self.current_roi_index = 0  # Index to select the ROI to edit
        self.on_roi_change = None  # Callback to update the displayed coordinates

    def set_image(self, image: np.ndarray):
        """Set the image and reset any existing ROIs"""
        self.image = image
        self.image_with_rois = image.copy()
        self.rois = [RegionOfInterest() for _ in range(4)]  # Reset all ROIs
        self.update_image()

    def set_current_roi(self, index: int):
        """Set the current ROI being edited"""
        self.current_roi_index = index
        self.update_image()
        # Update the displayed coordinates for all ROIs
        if self.on_roi_change:
            self.on_roi_change(self.rois)

    def update_image(self):
        """Update the QLabel with the current image (with ROIs drawn)"""
        image_copy = self.image.copy()
        # Draw all previously saved ROIs
        for i, roi in enumerate(self.rois):
            if roi.x1 is not None and roi.y1 is not None and roi.x2 is not None and roi.y2 is not None:
                cv2.rectangle(image_copy, (roi.x1, roi.y1), (roi.x2, roi.y2), self.colors[i], 2)
        qt_image = qimage2ndarray.array2qimage(image_copy)
        self.setPixmap(QPixmap.fromImage(qt_image))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.start_pos:
            self.end_pos = event.pos()
            # Redraw image with the current rectangle
            self.image_with_rois = self.image.copy()
            # Draw all previous ROIs
            for i, roi in enumerate(self.rois):
                if roi.x1 is not None and roi.y1 is not None and roi.x2 is not None and roi.y2 is not None:
                    cv2.rectangle(self.image_with_rois, (roi.x1, roi.y1), (roi.x2, roi.y2), self.colors[i], 2)
            # Draw the current ROI dynamically
            cv2.rectangle(
                self.image_with_rois,
                (self.start_pos.x(), self.start_pos.y()),
                (self.end_pos.x(), self.end_pos.y()),
                self.colors[self.current_roi_index], 2
            )
            self.update_image()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.end_pos = event.pos()
            # Store the final ROI in the list with its corresponding color
            self.rois[self.current_roi_index] = RegionOfInterest(
                x1=self.start_pos.x(), y1=self.start_pos.y(),
                x2=self.end_pos.x(), y2=self.end_pos.y()
            )
            self.start_pos = None
            self.end_pos = None
            self.update_image()
            # Update the displayed coordinates for all ROIs
            if self.on_roi_change:
                self.on_roi_change(self.rois)

