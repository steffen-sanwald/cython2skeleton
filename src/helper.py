import os
import pathlib
from typing import Optional

import fire

from src.cython2skeleton import Cython2Skeleton


def traverse_through_directroy(src_dir: str = "/tmp/target_binaries", target_dir: Optional[str] = "/tmp/target_binaries_skel"):

    for root, dirs, files in os.walk(src_dir):
        for filename in files:
            if filename.endswith(".so") or filename.endswith(".elf"):
                print(os.path.join(root, filename))
                decompiler = Cython2Skeleton(os.path.join(root, filename))
                decompiler.run()
                if target_dir:
                    target_dir = pathlib.Path(target_dir)
                    orig_path = pathlib.Path(os.path.join(root, filename))
                    rel_path= orig_path.relative_to(src_dir)
                    p = target_dir / rel_path
                    p.parent.mkdir(parents=True, exist_ok=True)
                    target_filepath=str(p)+".skel"
                else:
                    target_filepath=os.path.join(root, filename) + ".skel"

                decompiler.persist_pseudo_skeleton(target_filepath)

if __name__ == "__main__":
    fire.Fire(traverse_through_directroy)