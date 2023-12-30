import os
import pathlib
from typing import Optional

import fire

from src.cython2skeleton import Cython2Skeleton


def traverse_through_directroy(src_dir: str, target_dir: Optional[str] = None, print_unknown: bool = True,
                               searched_file_extensions: Optional[str] = None, store_all_strings: bool = False):
    """
    Traverses through a directory and retrieves as many info about the orig python from
    the compiled cython files as possible

    :param src_dir: directory to traverse through
    :param target_dir: directory where the quasi skeleton files should be stored.
        If None, the files will be stored in the same directory as the original file, with the extension .skel
    :param print_unknown: print strings that could be from python but are not mapped to a python entity type
    :param searched_file_extensions: comma separated list of filenames to filter for e.g. ".so,.elf"
    :param store_all_strings: store all strings in the skeleton file, not only the ones that are related to a python entity type
    :return:
    """
    for root, dirs, files in os.walk(src_dir):
        for filename in files:

            if searched_file_extensions:
                if filename not in searched_file_extensions.split(","):
                    continue

            if filename.endswith(".skel"):
                continue
            print(os.path.join(root, filename))
            c2s = Cython2Skeleton(os.path.join(root, filename))
            c2s.process()
            if target_dir:
                target_dir = pathlib.Path(target_dir)
                orig_path = pathlib.Path(os.path.join(root, filename))
                rel_path = orig_path.relative_to(src_dir)
                p = target_dir / rel_path
                p.parent.mkdir(parents=True, exist_ok=True)
                target_filepath = str(p) + ".skel"
            else:
                target_filepath = os.path.join(root, filename) + ".skel"

            c2s.persist_pseudo_skeleton(target_filepath, print_unknown=print_unknown,
                                        store_all_strings=store_all_strings)


if __name__ == "__main__":
    fire.Fire(traverse_through_directroy)
