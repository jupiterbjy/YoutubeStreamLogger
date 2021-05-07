"""
I decided to change file after finding out that stream ID also contains underscore.
This recursively check and fix to new naming convention.
"""

import pathlib


ROOT = pathlib.Path(__file__).parent.absolute()


def recursive_convert(path_: pathlib.Path):
    for subdir in path_.iterdir():
        if subdir.is_dir():
            print("Entering ", {subdir})
            recursive_convert(subdir)

        elif subdir.suffix in ".pdf .json":

            name = subdir.name.replace(subdir.suffix, "")

            # strip both end until underscore and remove underscore at both side
            stream_id = name.strip("0123456789-")[1:-1]

            split = name.split("_")

            date, unix_time = split[0], split[-1]

            subdir.rename(subdir.with_name(f"{date}_{unix_time}_{stream_id}{subdir.suffix}"))

            print(f"Renamed {name}{subdir.suffix} to {subdir.name}")


recursive_convert(ROOT)
