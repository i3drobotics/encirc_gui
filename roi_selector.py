#!/usr/bin/env python

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSpinBox,
    QApplication,
)

from roi import region_dict


class ROISelector(QWidget):
    def __init__(self, parent=None):
        super(ROISelector, self).__init__(parent)

        main_layout = QVBoxLayout()

        # Creating ROI control widgets for 4 ROIs
        self.roi_controls = []
        for i in range(4):
            roi_layout = QHBoxLayout()

            # Label for the region
            roi_label = QLabel(f"ROI {i+1}")
            roi_layout.addWidget(roi_label)

            self.x1_spin = QSpinBox()
            self.y1_spin = QSpinBox()
            self.x2_spin = QSpinBox()
            self.y2_spin = QSpinBox()

            # Setting min/max ranges
            self.x1_spin.setRange(0, 2000)
            self.y1_spin.setRange(0, 2000)
            self.x2_spin.setRange(0, 2000)
            self.y2_spin.setRange(0, 2000)

            roi_layout.addWidget(QLabel("x1:"))
            roi_layout.addWidget(self.x1_spin)
            roi_layout.addWidget(QLabel("y1:"))
            roi_layout.addWidget(self.y1_spin)
            roi_layout.addWidget(QLabel("x2:"))
            roi_layout.addWidget(self.x2_spin)
            roi_layout.addWidget(QLabel("y2:"))
            roi_layout.addWidget(self.y2_spin)

            self.roi_controls.append(
                (self.x1_spin, self.y1_spin, self.x2_spin, self.y2_spin)
            )
            main_layout.addLayout(roi_layout)

        self.setLayout(main_layout)

    def get_roi(self, index: int):
        # Get the values from spin boxes
        roi_control = self.roi_controls[index]

        x_low = min(roi_control[0].value(), roi_control[2].value())
        x_high = max(roi_control[0].value(), roi_control[2].value())

        y_low = min(roi_control[1].value(), roi_control[3].value())
        y_high = max(roi_control[1].value(), roi_control[3].value())

        return region_dict(x_low, y_low, x_high, y_high)

    def get_rois(self):
        rois = []
        for i, roi_control in enumerate(self.roi_controls):
            rois.append(self.get_roi(i))
        return rois

    def set_roi(self, index: int, reg_dict: dict):
        # Set the values in spin boxes
        roi_control = self.roi_controls[index]
        roi_control[0].setValue(reg_dict["x_low"])
        roi_control[1].setValue(reg_dict["y_low"])
        roi_control[2].setValue(reg_dict["x_high"])
        roi_control[3].setValue(reg_dict["y_high"])

    def set_rois(self, rois: list[dict]):
        for i, roi in enumerate(rois):
            self.set_roi(i, roi)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = ROISelector()
    window.show()
    sys.exit(app.exec_())
