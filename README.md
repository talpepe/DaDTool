# Dark and Darker Map Tool

## Description

The Dark and Darker Map Tool is a Python app designed to help new players orient themselves in the map. 
Select current map rotation, define the minimap region through the tool, and start scanning!
The tool uses openCV's feature matching to find your location on the map from the minimap and display it to you.

## Features

- Select and load maps for processing. This is helpful when maps rotate.
- Can grab screenshots of interactive maps from sites like https://darkanddarker.map.spellsandguns.com/
- Add your own POIs to them
- Some settings for user convinence such as always on top toggle or opacity range
  
## Requirements

- Python 3.6 or higher

## Setup Instructions

You may either download the game from here or clone the repo. 

In the directory of this project, run the following:

python -m pip install -r requirements.txt
python gui.py

>Note: Replace python with the proper executable name. On Windows, this is usually py and on other systems, it's usually python3.

## Configuration

Settings contain some settings for user convenience.

  -Update interval: Interval between updates in seconds. Lower number means faster refreshes and higher CPU usage. 
  
  -Map scalar: Scalar for resizing the map image. 
  
  -Map opacity: Opacity of the map window.
  
  -Always on top: Whether the map window should always stay on top



## Usage

  1. Select Maps: Click "Select Maps" and select current maps in rotation. The app will run through all of them once to find the best match.
  2. Select Minimap Region: Define the region of the minimap. **IMPORTANT**: Being symmterical around the player icon on the minimap will improve accuracy on the large map.
     Try to get as much of the map without the UI itself.
  4. Start Scanning: Click "Start Scanning" to begin the continuous scanning of the minimap. Only click this when minimap is already shown
  5. Settings: Some user convenience options
  6. Help: Access the help function for additional guidance.






If all goes well, this is how it should look!

![image](https://github.com/talpepe/DaDTool/assets/10613298/0e2952ea-ce43-4ac1-8da5-54f1707edfe7)


https://github.com/talpepe/DaDTool/assets/10613298/4a05bc55-2c0c-468a-af8c-7c69d4cc02e8

