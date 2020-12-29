# DropNot Homework

This solution completes tasks 1.1 and 1.2, and also completes bonus task 1.

## Setup (Normal)

1. `git clone https://github.com/OscarVanL/DropNot-Homework`

2. `cd DropNot-Homework`

3. `conda create --name DropNot python=3.8`

4. `conda activate DropNot`

5. `pip install -r requirements.txt`

Launch Server: `python main.py --server <SYNC-TARGET-DIR>`

Launch Client: `python main.py --client <DIR-TO-SYNC> --target <SERVER-ADDRESS>`

## Setup (Dockerised Server)

1. `git clone https://github.com/OscarVanL/DropNot-Homework`

2. `cd DropNot-Homework`

3. `mkdir sync`

4. `docker build -t dropnot-server -f Dockerfile .`

5. `docker run -d -p 5000:5000 -v $PWD:/dropnot --restart=always --name dropnot-server dropnot-server`

## Run Unit Tests

`python -m unittest discover tests`

## Improvements

* To detect file changes, native OS libraries like the win32 API could be used. However, this adds complexity for multi-OS compatibility.

* Not all file metadata is preserved, just the 'modified' time.

* Base64 is used for the file binary encoding, however using BSON or Google Protocol Buffers would result in efficiency gains.

* File transfers happen sequentially. Simultaneous transfers could speed up synchronisation.

* I am using Flask in development mode (unsuitable for production).

* If a file or folder is renamed, the directory listener isn't smart enough to know this, so it will be processed as a 'deletion' followed by a 'creation'.

* There's **no encryption**.

* Bonus task 2 is not implemented. 