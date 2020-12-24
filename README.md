# Pexip DropNot Homework

## About

This solution completes tasks 1.1 and 1.2, and also completes bonus task 1.

## Setup

1. `git clone https://github.com/OscarVanL/Pexip-Dropbox-Homework`

2. `cd Pexip-Dropbox-Homework`

3. `conda create --name DropNot python=3.8`

4. `conda activate DropNot`

5. `pip install -r requirements.txt`

## Launch Server

`python main.py --server <SYNC-TARGET-DIR>`

## Launch Client

`python main.py --client <DIR-TO-SYNC>`

## Run Tests

`python -m unittest discover tests`


# Improvements

* To detect changes, native OS libraries like the win32 API could be used. However, this adds complexity for multi-OS compatibility.

* My solution rebuilds only the 'modified' file metadata on the server. Not all metadata is transferred.

* Base64 is used for the file binary encoding, however using BSON or Google Protocol Buffers would result in efficiency gains.

* File transfers happen sequentially. A few simultaneous transfers could speed up synchronisation.

* I am using Flask in development mode, this isn't suitable for production.

* If a file or folder is renamed, the directory listener isn't smart enough to know this, so it will be processed as a 'deletion' followed by a 'creation'.

* There's **no encryption**.

