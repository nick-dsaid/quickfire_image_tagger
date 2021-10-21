
# Image Tagger

This program uses A.I. to generate the keywords for describing the images provided.
For example, based on an image, the programs can tell it's about objects captured in the image like ```outdoor bench```,  the theme ```outdoor activity```, 
and characteristic of the image ```colorful```, ```abstract```, ```purple```. 




![Logo](https://i.imgur.com/EaHlWG0.jpeg)

    
## Badges


[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

  
## Authors

- [@nick-dsaid](https://github.com/nick-dsaid)

  
## Demo
![](https://i.imgur.com/isUwrln.jpeg)





  
## Dependencies
If you have installed Anaconda. You will only need to install the following dependencies:
```bash
pip install google-cloud-vision
pip install gooey
```
If you're advanced users who like to create a virtual environment, please use the requirements.txt file.

## Quick Start

Clone this repository to your local disk. The Python script and Jupyter
Notebook are in the "scripts/" folder.


There are three ways to use the program:
- As a GUI-based software. Run the Python [script](https://github.com/nick-dsaid/quickfire_image_tagger/blob/main/scripts/image_tagger.py)

    ```bash
        python image_tagger.py
    ```

![](https://i.imgur.com/ASjLjK7.png)


- As a Jupyter Notebook
    - Run Jupyter [Notebook](https://github.com/nick-dsaid/quickfire_image_tagger/blob/main/scripts/image_tagger.ipynb)


- As a command line program. Run the Python script with *arguments*.

    ```bash
    python image_tagger.py "~/secure/gcp.json" "/home/project/inputs" "/home/project/outputs/generated_tags.csv"
    ```
    - Three positional arguments are needed:
      - filepath to credential file (.json) from Google Cloud Platform cred
      - path to the root folder containing the images to be tagged
      - filepath for the .csv file to be exported
    - See the script "image_tagger.py" for other optional arguments




  


  