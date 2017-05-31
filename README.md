# Is It Metal?

A classifier for metal music. This will tell you how metal your music is.

## Running

First install the dependencies. Make sure you have virtualenv, python3, and pip.
Then install the python dependencies into a virtual environment.

```
# Create a virtual environment
virtualenv .venv --python=python3

# Activate the virtual environment
source .venv/bin/activate

# Install the requirements into that virtual environment
pip install -r requirements.txt
```

The program is installed, if you have the datasets you can run. Otherwise go to
getting the datasets.

```
# Launch the program
./launch
```

If the launch program is not executable on your system, run this to make it
executable.

```
chmod +x ./launch
```

The website should be now be running at your localhost: [http://localhost:8000/](http://localhost:8000/).

## Getting the Dataset

The dataset should end up under the root directory of the project the folders:

```
[~/metal-project]$ tree -L 1 audio_dataset
audio_dataset
├── Classical
├── Electronic
├── Jazz
└── Metal
```

Or more explicitly, metal music ends up in audio_dataset/Metal, etc...

At the bare minimum you need Metal and another genre. The genres can be changed
within the classify.py file.

To get the dataset, we will download them from the
[http://freemusicarchive.org/](http://freemusicarchive.org/) using downloader.py.
If you run it, it will start downloading all the music for you. Please note, it
can be restarted half-way through, it creates checkpoints and stores meta
information in text files like `Metal.txt`. The filenames are also the hash of
the file, this helps reduce problems and duplicate downloads (which exist in the
archive).
