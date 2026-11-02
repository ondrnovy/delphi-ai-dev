"""Print the UI Automation tree of a running Windows application, optionally with a screenshot.

Start the application:   python dump_tree.py --exe "C:\\build\\App.exe --fake-device" --title-re "Configurator.*"
Attach to a running one: python dump_tree.py --title-re "Configurator.*" --screenshot main.png
"""

import argparse
import sys

from pywinauto import Application


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--title-re", required=True, help="regular expression matching the window title")
    parser.add_argument("--exe", help="command line that starts the application; omit to attach to a running one")
    parser.add_argument("--depth", type=int, help="limit the depth of the printed tree")
    parser.add_argument("--screenshot", help="save a PNG of the window to this path")
    parser.add_argument("--timeout", type=float, default=30.0, help="seconds to wait for the window")
    args = parser.parse_args()

    if args.exe:
        app = Application(backend="uia").start(args.exe)
    else:
        app = Application(backend="uia").connect(title_re=args.title_re, timeout=args.timeout)

    window = app.window(title_re=args.title_re)
    window.wait("visible", timeout=args.timeout)
    window.print_control_identifiers(depth=args.depth)

    if args.screenshot:
        window.capture_as_image().save(args.screenshot)
        print(f"screenshot saved to {args.screenshot}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
