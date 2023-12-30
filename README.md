# cython2skeleton
quickly gather insights into a cython compiled executable/shared library by reconstructing the class/functions names
using simplest way of reverse engineering.
The scripts takes a cython compiled file (.elf, .so) as input and reconstructs the original class and function names
from the python file. Adds as much information as possible into the produced python file, such as docstrings and comments.

## Usage
To run the script, simply run for a single file:
```bash
python cython2skeleton.py --filepath=/tmp/api.so run
```

To run the script over a directory recursively:
```bash
python helper.py --src_dir=/tmp/target_dir --target_dir=/tmp/target_dir_binaries --print_unknown=True --searched_file_extensions=so,elf
```
