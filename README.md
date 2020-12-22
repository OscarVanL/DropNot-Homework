# Pexip DropNot Homework

## Setup

1. `git clone https://github.com/OscarVanL/Pexip-Dropbox-Homework`

2. `cd Pexip-Dropbox-Homework`

3. `conda create --name DropNot python=3.8`

4. `conda activate DropNot`

5. `pip install -r requirements.txt`

## Launch Client

`python main.py --client <DIR-TO-SYNC>`

## Launch Server

`python main.py --server <SYNC-TARGET-DIR>`

## Run Tests

`python -m unittest discover tests`


# Improvements

* To detect changes, native OS libraries like the win32 API could be used. However, this adds complexity for multi-OS compatibility.

* Not all file metadata is transferred, so it's not a 1:1 copy of a file.

* Base64 is used for the file binary encoding, however using BSON or Google Protocol Buffers would result in efficiency gains.

* I am using Flask in development mode, this isn't suitable for production.

* There's **no encryption**.

