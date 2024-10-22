# encirc_gui

## Installing Requirements
```
pip install -r requirements.txt
```

## Running the GUI
```
python encircgui
```

## Using the GUI
![alt text](/images/encirc_gui_screenshot.PNG)

### Regions of Interest
Four regions of interest are specified in the bottom right corner.

A region of interest is defined by two coordinate pairs: (x1, y1) is one point in the image, and (x2, y2) is another. A rectangular box is created between these two positions, which represents the region of interest.

### Default parameters

When the program is closed, if any of the user specified values have changed, you will be prompted to update the configuration. If you choose to update the configuration, these new values get loaded in next time you run the program.

## Useful regions?
```
self.sample1 = frameROI[120:320,300:500]
self.sample2 = frameROI[120:320,500:850]
self.sample3 = frameROI[120:320,850:1200]
self.sample4 = frameROI[120:320,1200:1600]
```