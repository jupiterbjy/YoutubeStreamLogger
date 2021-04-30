#!/usr/bin/python3

"""
Simple plot viewer for my own accumulated data.
"""

import itertools
import pathlib
import json
import argparse
from array import array
from typing import Union

from matplotlib import pyplot
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MaxNLocator


ABS_DIR = pathlib.Path(__file__).absolute().parent

prop = FontProperties(fname=ABS_DIR.joinpath("Font/NotoSansCJKkr-Regular.ttf").as_posix())
# pyplot.rcParams["font.family"] = "Noto Sans CJK KR"


def calculate_delta(source) -> array:
    """
    Calculate possible viewer gain/lose from fluctuation of total view and live-viewers.

    :param source: Any sequence containing data over time.
    :return: int array for each approximate gain/lose of live viewers.
    """

    def view_diff_gen(source_):
        yield 0

        iterator = zip(source_, itertools.islice(source_, 1, None))

        for previous, current in iterator:
            yield current - previous

    # originally supplied data is unsigned long "L", but fluctuation won't be that huge.
    try:
        return array("l", view_diff_gen(source))
    except TypeError:
        # Data is hidden by streamer
        return array("i", (0 for _ in range(len(source))))


def plot_main(mapping, save_as_img: Union[None, pathlib.Path] = None):
    """
    Dirty main. Check this dirt out, it's extra dirty.
    Plots giving data.

    :param mapping: data satisfying structure generated by log_stat.py
    :param save_as_img: save path for image. Set None to disable image saving.
    """

    title = mapping["stream_title"]
    interval = mapping["interval"]

    data = mapping["data"]
    gain_total = max(data["viewCount"]) - min(data["viewCount"])

    # Calculate delta. Fluctuation? Delta? whatever it fits.
    view_gain = calculate_delta(data["viewCount"])
    live_fluctuation = calculate_delta(data["concurrentViewers"])

    like_cast = calculate_delta(data["likeCount"])
    dislike_cast = calculate_delta(data["dislikeCount"])

    # some old data don't have this.
    try:
        if not data["subscriberCount"]:
            raise KeyError

        sub_change = calculate_delta(data["subscriberCount"])
    except KeyError:
        sub_change = None

    figure, axes = pyplot.subplots(3, 1, figsize=(16, 8))

    fig_manager = pyplot.get_current_fig_manager()
    fig_manager.set_window_title(
        f"Samples: {len(view_gain)} / "
        f"Duration: {len(view_gain) * interval / 60:0.2f}m / "
        f"Gain total: {gain_total}"
    )

    # Plot 1
    axes[0].set_title(title, fontproperties=prop)
    axes[0].plot(data["viewCount"], color="cornflowerblue", label="Total views")
    axes[0].plot(data["concurrentViewers"], color="orange", label="Live viewers")
    axes[0].plot(data["likeCount"], color="green", label="Upvote")
    axes[0].plot(data["dislikeCount"], color="red", label="Downvote")
    axes[0].legend()

    # determine min-max viewers
    max_val = max(data["viewCount"])
    # axes[0].set_yticks(tuple(n for n in range(0, max_val + 1, max_val // 5)))

    # Plot 2
    axes[1].plot(view_gain, color="cornflowerblue", label="Total view increment")
    axes[1].plot(live_fluctuation, color="coral", label="Live view fluctuation")
    axes[1].legend()

    # Plot 3 - up/downvote, subscriber plot
    axes[2].plot(like_cast, color="green", label=f"Upvote casted")
    axes[2].plot(dislike_cast, color="red", label=f"Downvote casted")
    if sub_change:
        axes[2].plot(sub_change, color="cyan", label="Sub. fluctuation")

    axes[2].legend()

    axes[2].set_xlabel(f"time({interval}sec unit)")

    # enforce axis to be integer
    for idx in range(3):
        axes[idx].yaxis.set_major_locator(MaxNLocator(integer=True))

    figure.tight_layout()

    if save_as_img is not None:
        save_file = save_as_img.parent.joinpath(save_as_img.stem + ".pdf")
        pyplot.savefig(save_file)
    else:
        pyplot.show()


def main():
    """
    Driver that deals with file loading.
    """

    if args.path.is_dir():
        iterator = (path for path in args.path.iterdir() if path.suffix == ".json")
        time_ordered = sorted(iterator, reverse=True, key=lambda p: p.stat().st_ctime)

        for file in time_ordered:
            try:
                with open(file, encoding="utf8") as fp:
                    loaded_data = json.load(fp)

                plot_main(loaded_data, file if args.save else None)
                return

            except (json.JSONDecodeError, KeyError):
                print(f"File {file.name} has wrong format.")

        print(f"No suitable file was found in {args.path}")
        return

    try:
        with open(args.path, encoding="utf8") as fp:
            loaded_data = json.load(fp)

        plot_main(loaded_data, args.path if args.save else None)
        return
    except (json.JSONDecodeError, KeyError):
        print(f"File {args.path.name} has wrong format.")
        return


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Opens generated .json data.")
    parser.add_argument(
        "path",
        metavar="PATH",
        nargs="?",
        type=pathlib.Path,
        default=ABS_DIR.joinpath("Records"),
        help="Path to .json file or folder contains it. "
             "Will use default path '__file__/Records' if omitted.",
    )
    parser.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Save as pdf. Name will be same as json file opened.",
    )

    args = parser.parse_args()

    try:
        main()
    except KeyboardInterrupt:
        pass
