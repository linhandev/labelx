测试修改
<h1 align="center">
  <img src="labelx/icons/icon.png"><br/>labelx
</h1>

<h4 align="center">
  Image Polygonal Annotation with Python
</h4>

<div align="center">
  <a href="https://pypi.python.org/pypi/labelx"><img src="https://img.shields.io/pypi/v/labelx.svg"></a>
  <a href="https://pypi.org/project/labelx"><img src="https://img.shields.io/pypi/pyversions/labelx.svg"></a>
  <a href="https://github.com/wkentaro/labelx/actions"><img src="https://github.com/wkentaro/labelx/workflows/ci/badge.svg?branch=master&event=push"></a>
  <a href="https://hub.docker.com/r/wkentaro/labelx"><img src="https://img.shields.io/docker/cloud/build/wkentaro/labelx"></a>
</div>

<div align="center">
  <a href="#installation"><b>Installation</b></a> |
  <a href="#usage"><b>Usage</b></a> |
  <a href="https://github.com/wkentaro/labelx/tree/master/examples/tutorial#tutorial-single-image-example"><b>Tutorial</b></a> |
  <a href="https://github.com/wkentaro/labelx/tree/master/examples"><b>Examples</b></a> |
  <a href="https://www.youtube.com/playlist?list=PLI6LvFw0iflh3o33YYnVIfOpaO0hc5Dzw"><b>Youtube FAQ</b></a>
</div>

<br/>

<div align="center">
  <img src="examples/instance_segmentation/.readme/annotation.jpg" width="70%">
</div>

## Description

labelx is a graphical image annotation tool inspired by <http://labelx.csail.mit.edu>.  
It is written in Python and uses Qt for its graphical interface.

<img src="examples/instance_segmentation/data_dataset_voc/JPEGImages/2011_000006.jpg" width="19%" /> <img src="examples/instance_segmentation/data_dataset_voc/SegmentationClassPNG/2011_000006.png" width="19%" /> <img src="examples/instance_segmentation/data_dataset_voc/SegmentationClassVisualization/2011_000006.jpg" width="19%" /> <img src="examples/instance_segmentation/data_dataset_voc/SegmentationObjectPNG/2011_000006.png" width="19%" /> <img src="examples/instance_segmentation/data_dataset_voc/SegmentationObjectVisualization/2011_000006.jpg" width="19%" />  
<i>VOC dataset example of instance segmentation.</i>

<img src="examples/semantic_segmentation/.readme/annotation.jpg" width="30%" /> <img src="examples/bbox_detection/.readme/annotation.jpg" width="30%" /> <img src="examples/classification/.readme/annotation_cat.jpg" width="35%" />  
<i>Other examples (semantic segmentation, bbox detection, and classification).</i>

<img src="https://user-images.githubusercontent.com/4310419/47907116-85667800-de82-11e8-83d0-b9f4eb33268f.gif" width="30%" /> <img src="https://user-images.githubusercontent.com/4310419/47922172-57972880-deae-11e8-84f8-e4324a7c856a.gif" width="30%" /> <img src="https://user-images.githubusercontent.com/14256482/46932075-92145f00-d080-11e8-8d09-2162070ae57c.png" width="32%" />  
<i>Various primitives (polygon, rectangle, circle, line, and point).</i>


## Features

- [x] Image annotation for polygon, rectangle, circle, line and point. ([tutorial](examples/tutorial))
- [x] Image flag annotation for classification and cleaning. ([#166](https://github.com/wkentaro/labelx/pull/166))
- [x] Video annotation. ([video annotation](examples/video_annotation))
- [x] GUI customization (predefined labels / flags, auto-saving, label validation, etc). ([#144](https://github.com/wkentaro/labelx/pull/144))
- [x] Exporting VOC-format dataset for semantic/instance segmentation. ([semantic segmentation](examples/semantic_segmentation), [instance segmentation](examples/instance_segmentation))
- [x] Exporting COCO-format dataset for instance segmentation. ([instance segmentation](examples/instance_segmentation))



## Requirements

- Ubuntu / macOS / Windows
- Python2 / Python3
- [PyQt4 / PyQt5](http://www.riverbankcomputing.co.uk/software/pyqt/intro)


## Installation

There are options:

- Platform agnostic installation: [Anaconda](#anaconda), [Docker](#docker)
- Platform specific installation: [Ubuntu](#ubuntu), [macOS](#macos), [Windows](#windows)
- Pre-build binaries from [the release section](https://github.com/wkentaro/labelx/releases)

### Anaconda

You need install [Anaconda](https://www.continuum.io/downloads), then run below:

```bash
# python2
conda create --name=labelx python=2.7
source activate labelx
# conda install -c conda-forge pyside2
conda install pyqt
pip install labelx
# if you'd like to use the latest version. run below:
# pip install git+https://github.com/wkentaro/labelx.git

# python3
conda create --name=labelx python=3.6
source activate labelx
# conda install -c conda-forge pyside2
# conda install pyqt
# pip install pyqt5  # pyqt5 can be installed via pip on python3
pip install labelx
# or you can install everything by conda command
# conda install labelx -c conda-forge
```

### Docker

You need install [docker](https://www.docker.com), then run below:

```bash
# on macOS
socat TCP-LISTEN:6000,reuseaddr,fork UNIX-CLIENT:\"$DISPLAY\" &
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=docker.for.mac.host.internal:0 -v $(pwd):/root/workdir wkentaro/labelx

# on Linux
xhost +
docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=:0 -v $(pwd):/root/workdir wkentaro/labelx
```

### Ubuntu

```bash
# Ubuntu 14.04 / Ubuntu 16.04
# Python2
# sudo apt-get install python-qt4  # PyQt4
sudo apt-get install python-pyqt5  # PyQt5
sudo pip install labelx
# Python3
sudo apt-get install python3-pyqt5  # PyQt5
sudo pip3 install labelx

# or install standalone executable from:
# https://github.com/wkentaro/labelx/releases
```

### Ubuntu 19.10+ / Debian (sid)

```bash
sudo apt-get install labelx
```

### macOS

```bash
# macOS Sierra
brew install pyqt  # maybe pyqt5
pip install labelx  # both python2/3 should work

# or install standalone executable/app from:
# https://github.com/wkentaro/labelx/releases
```

### Windows

Install [Anaconda](https://www.continuum.io/downloads), then in an Anaconda Prompt run:

```bash
# python3
conda create --name=labelx python=3.6
conda activate labelx
pip install labelx
```


## Usage

Run `labelx --help` for detail.  
The annotations are saved as a [JSON](http://www.json.org/) file.

```bash
labelx  # just open gui

# tutorial (single image example)
cd examples/tutorial
labelx apc2016_obj3.jpg  # specify image file
labelx apc2016_obj3.jpg -O apc2016_obj3.json  # close window after the save
labelx apc2016_obj3.jpg --nodata  # not include image data but relative image path in JSON file
labelx apc2016_obj3.jpg \
  --labels highland_6539_self_stick_notes,mead_index_cards,kong_air_dog_squeakair_tennis_ball  # specify label list

# semantic segmentation example
cd examples/semantic_segmentation
labelx data_annotated/  # Open directory to annotate all images in it
labelx data_annotated/ --labels labels.txt  # specify label list with a file
```

For more advanced usage, please refer to the examples:

* [Tutorial (Single Image Example)](examples/tutorial)
* [Semantic Segmentation Example](examples/semantic_segmentation)
* [Instance Segmentation Example](examples/instance_segmentation)
* [Video Annotation Example](examples/video_annotation)

### Command Line Arguments
- `--output` specifies the location that annotations will be written to. If the location ends with .json, a single annotation will be written to this file. Only one image can be annotated if a location is specified with .json. If the location does not end with .json, the program will assume it is a directory. Annotations will be stored in this directory with a name that corresponds to the image that the annotation was made on.
- The first time you run labelx, it will create a config file in `~/.labelxrc`. You can edit this file and the changes will be applied the next time that you launch labelx. If you would prefer to use a config file from another location, you can specify this file with the `--config` flag.
- Without the `--nosortlabels` flag, the program will list labels in alphabetical order. When the program is run with this flag, it will display labels in the order that they are provided.
- Flags are assigned to an entire image. [Example](examples/classification)
- Labels are assigned to a single polygon. [Example](examples/bbox_detection)

## FAQ

- **How to convert JSON file to numpy array?** See [examples/tutorial](examples/tutorial#convert-to-dataset).
- **How to load label PNG file?** See [examples/tutorial](examples/tutorial#how-to-load-label-png-file).
- **How to get annotations for semantic segmentation?** See [examples/semantic_segmentation](examples/semantic_segmentation).
- **How to get annotations for instance segmentation?** See [examples/instance_segmentation](examples/instance_segmentation).


## Testing

```bash
pip install hacking pytest pytest-qt
flake8 .
pytest -v tests
```


## Developing

```bash
git clone https://github.com/wkentaro/labelx.git
cd labelx

# Install anaconda3 and labelx
curl -L https://github.com/wkentaro/dotfiles/raw/master/local/bin/install_anaconda3.sh | bash -s .
source .anaconda3/bin/activate
pip install -e .
```


## How to build standalone executable

Below shows how to build the standalone executable on macOS, Linux and Windows.  

```bash
# Setup conda
conda create --name labelx python==3.6.0
conda activate labelx

# Build the standalone executable
pip install .
pip install pyinstaller
pyinstaller labelx.spec
dist/labelx --version
```


## Acknowledgement

This repo is the fork of [mpitid/pylabelx](https://github.com/mpitid/pylabelx),
whose development has already stopped.


## Cite This Project

If you use this project in your research or wish to refer to the baseline results published in the README, please use the following BibTeX entry.

```bash
@misc{labelx2016,
  author =       {Kentaro Wada},
  title =        {{labelx: Image Polygonal Annotation with Python}},
  howpublished = {\url{https://github.com/wkentaro/labelx}},
  year =         {2016}
}
```
