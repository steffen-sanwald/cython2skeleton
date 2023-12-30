# cython2skeleton
Quickly gather insights into a cython compiled executable/shared library.
Cython2Skeleton reconstructs the class/functions names with simple techniques of reverse engineering.
The scripts takes a cython compiled file (.elf, .so) as input and reconstructs the original class and function names
from the python file. Adds as much information as possible into the produced python file, such as docstrings and comments.

## Usage
To run the script, simply run for a single file:
```bash
python src/cython2skeleton.py --filepath=/tmp/api.so run_and_store --target_filepath=/tmp/api.so.skel --print_unknown=True --store_all_strings=True 
```

To run the script over a directory recursively:
```bash
python src/helper.py --src_dir=/tmp/src_dir --target_dir=/tmp/target_dir --searched_file_extensions=so,elf --print_unknown=True  --store_all_strings=False
```

If to many irrelevant strings are printed, the parameters only_interesting: bool and min_chars: int can be used to 
adjust the results.