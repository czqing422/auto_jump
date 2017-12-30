#!/usr/bin/python
import argparse
from modes import ManualMode, AutoMode


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--screenshot', action='store_true', dest='is_screenshot', default=False)
    parser.add_argument('--manual_mode', action='store_true', dest='is_manual_mode', default=False)
    parser.add_argument('--auto_mode', action='store_true', dest='is_auto_mode', default=False)

    results = parser.parse_args()
    if results.is_screenshot:
        mode = ManualMode()
        print mode.screenshot()
    elif results.is_manual_mode:
        mode = ManualMode()
        mode.run()
    elif results.is_auto_mode:
        mode = AutoMode()
        mode.run()
    else:
        print 'invalid mode'

