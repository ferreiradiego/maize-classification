# Classification of defects in Zea Mays corn grain samples

Welcome to our repository which tackles corn grain classification using Digital Image Processing (DIP). This repository contains scripts, notebooks, a dataset, and a code for image acquisition using an [ESP-32 CAM module](https://www.espressif.com/en/news/ESP32_CAM).

## Description
This project uses digital image processing techniques for the classification of corn grains of the Zea Mays species through the color of the grains.

## Contents

### Repository contents list

<table style="width:100%; border:1px solid black;">
    <thead>
        <tr>
            <th style="text-align:center; border:1px solid black;"><strong>Folder</strong></th>
            <th style="text-align:center; border:1px solid black;"><strong>Content</strong></th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="border:1px solid black;">img</td>
            <td style="border:1px solid black;">
                <ul>
                    <li>aquisition_device: images of the acquisition device</li>
                    <li>dataset: image database, in grayscale and in RGB, both without background</li>
                </ul>
            </td>
        </tr>
        <tr>
            <td style="border:1px solid black;">src</td>
            <td style="border:1px solid black;">
                <ul>
                    <li>Python and Jupyter Notebook code for preprocessing, model creation, and sample classification</li>
                    <li><strong>aquisition_device</strong>: PlatformIo project in C/C++ to load on ESP-32 CAM</li>
                    <li><strong>tools</strong>: various functions for preprocessing and for the main code</li>
                </ul>
            </td>
        </tr>
        <tr>
            <td style="border:1px solid black;">resources</td>
            <td style="border:1px solid black;">
                Dataset in dataframe format and classification results
            </td>
        </tr>
    </tbody>
</table>


### Dataset

The dataset contains a total of 1314 different images, which are presented in two different color spaces: RGB (color) and grayscale.

The image labels identify the percentages of defects and the quantity of grains in each sample.

<table style="width:100%; border:1px solid black;">
    <caption><strong>Description of items for each image label</strong></caption>
    <thead>
        <tr>
            <th style="text-align:center; border:1px solid black;">Item</th>
            <th style="text-align:center; border:1px solid black;">Description</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td style="border:1px solid black;">first</td>
            <td style="border:1px solid black;">
                - a1 are samples with 30% of defective grains<br>
                - a2 are samples with 25% of defective grains<br>
                - a3 are samples with 20% of defective grains<br>
                - a4 are samples with 15% of defective grains<br>
                - a5 are samples with 10% of defective grains<br>
                - a6 to a11 are samples with all healthy grains
            </td>
        </tr>
        <tr>
            <td style="border:1px solid black;">second</td>
            <td style="border:1px solid black;">Quantity of grains: 50, 60, 70, 80, 90 and 100</td>
        </tr>
        <tr>
            <td style="border:1px solid black;">third</td>
            <td style="border:1px solid black;">Image number, for each defect percentage and grain quantity there are 20 images. Samples with healthy grains have varied quantities of images.</td>
        </tr>
    </tbody>
</table>


## Getting Started

### Acquisition of images for the [dataset](img/dataset/)

The images illustrate the acquisition device, where the grains are placed on the blue background, and the microcontroller at the top captures the image with each new command coming through Serial Communication.

The dimensions of the box are 30x30x30 cm. Two 12 W LED lamps are used for the lighting system

<table>
  <tr>
    <td align="center"> <strong>Front View Setup</strong> </td>
    <td align="center"> <strong>Top View Setup</strong> </td>
  </tr>
  <tr>
    <td><img src="img/aquisition_device/setup_frontView.jpg" alt="Front View Setup" style="width: auto; height: 300px;"></td>
    <td><img src="img/aquisition_device/setup_topView.jpg" alt="Top View Setup" style="width: auto; height: 300px;"></td>
  </tr>
</table>


The code to be loaded into the ESP-32 CAM is [aquisition_device](src/aquisition_device/).

### Preprocessing

After obtaining the images of the samples, preprocessing is applied, which prepares and labels the images for the model creation and classification stages. The resulting images from the preprocessing are shown below, with the grayscale image being used for classification.

<table>
  <tr>
    <td align="center"> <strong>RGB example</strong> </td>
    <td align="center"> <strong>Grayscale example</strong> </td>
  </tr>
  <tr>
    <td><img src="img/dataset/rgb/a1_100_1.jpg" alt="RGB example"></td>
    <td><img src="img/dataset/gray/a1_100_1.jpg" alt="Grayscale example"></td>
  </tr>
</table>


## Installation

### Dependencies

- Python 3.7+
- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [Scikit-learn](https://scikit-learn.org/)
- [Matplotlib](https://matplotlib.org/)
- [Plotly](https://plotly.com/)
- [Seaborn](https://seaborn.pydata.org/)
- [OpenCV](https://opencv.org/)
- [Pandas](https://pandas.pydata.org/)
- [NumPy](https://numpy.org/)


> You can install any missing dependencies with pip.

### How to install

Follow these steps to clone the repository and install the necessary dependencies:

1. **Clone the repository**:

    ```
    git clone https://github.com/ferreiradiego/maize-classification.git
    ```

2. **Navigate into the cloned repository**:

    ```
    cd maize-classification
    ```

3. **Create a virtual environment**:

    ```
    python3 -m venv env
    ```

4. **Activate the virtual environment**:
    - On Windows:
        ```
        .\env\Scripts\activate
        ```
    - On Unix or MacOS:
        ```
        source env/bin/activate
        ```

5. **Install the necessary dependencies**:

    ```
    pip install -r requirements.txt
    ```

## Running the Program

The scripts required for data preprocessing and model training are located in the `src` directory.

You can run Jupyter notebooks in either JupyterLab or Jupyter Notebook


<!-- ### Contributing
We would love your contributions! Please read CONTRIBUTING.md for details on our code of conduct, and the process for submitting pull requests.

### License
This project is licensed under the MIT License - see the LICENSE file for details. VER ISSO -->
