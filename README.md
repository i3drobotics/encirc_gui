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

## Saving format

Data is saved in JSON format:

```JSON
[
    {
        "timestamp": "2024-10-23 10:12:26.195981",
        "exposure": 2,
        "dataSum1": 1564548,
        "dataSum2": 1871599,
        "dataSum3": 787807,
        "dataSum4": 691330,
        "result": "REJECT"
    },
    {
        "timestamp": "2024-10-23 10:12:26.282915",
        "exposure": 2,
        "dataSum1": 2380169,
        "dataSum2": 2854905,
        "dataSum3": 1220305,
        "dataSum4": 1081558,
        "result": "REJECT"
    }
]
```

Here is an example with two entries, representing two frames of data. Files are named "measurement_0.json", "measurement_1.json" etc. Each file contains up to 500 entries. Once 500 entries are reached, a new file is created (if the last file was "measurement_4.json", the new file will be "measurement_5.json"). This prevents individual files from becoming too large and unwieldy.

An individual entry shows:
- the timestamp of the frame (format code "%Y-%m-%d %H:%M:%S.%f")
- the exposure used to capture it
- the sum of pixels in region 1
- the sum of pixels in region 2
- the sum of pixels in region 3
- the sum of pixels in region 4
- the result (NO_BOTTLE, ACCEPT, INSPECT, or REJECT)

## Dev Zone

### Build
Run:
```
build.bat
```
This will make a directory called `encirc_GUI` in dist, containing an exe file and an _internal directory.

Zip the `encirc_GUI` directory and add it to GitHub releases.

### Useful regions?
```
self.sample1 = frameROI[120:320,300:500]
self.sample2 = frameROI[120:320,500:850]
self.sample3 = frameROI[120:320,850:1200]
self.sample4 = frameROI[120:320,1200:1600]
```