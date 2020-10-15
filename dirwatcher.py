#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = "Matthew Morris, help from Petes study group"

import sys
import signal
import time
import argparse
import logging
import os

watch_dict = {}
exit_flag = False
logging.basicConfig(format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def search_for_magic(filename, start_line, magic_string):
    # Your code here
    with open(filename) as f:
        file_lines = f.readlines()
        found_lines = []
        for line_num, line in enumerate(file_lines):
            # print(line_num, start_line)
            # print(watch_dict)
            if line_num < start_line:
                continue
            watch_dict[filename] = line_num + 1
            result = line.find(magic_string)
            if result != -1:
                found_lines.append(line_num + 1)
        if len(found_lines) > 0:
            logger.info(f"Magic string {filename} line {found_lines}")
    return


def watch_directory(path, magic_string, extension, interval):
    file_list = os.listdir(path)
    for _file in file_list:
        path_file = path + "/" + _file
        for k in list(watch_dict):
            if k.split('/')[1] not in file_list:
                logger.info(f"File Deleted {k}")
                watch_dict.pop(k)
        if path_file not in watch_dict and path_file.endswith(extension):
            logger.info(f"New file added {path_file}")
            watch_dict[path_file] = 0
        if path_file.endswith(extension):
            search_for_magic(path_file, watch_dict[path_file], magic_string)
    return


def create_parser():
    parser = argparse.ArgumentParser(description="Watch dir for changes")
    parser.add_argument("-e", "--ext", help="extension input")
    parser.add_argument("-d", "--dir", help="directory input")
    parser.add_argument("-i", "--int", default=1,
                        help="polling interval for checking the dir")
    parser.add_argument("-t", "--text", help="magic string search")
    return parser


def signal_handler(sig_num, frame):
    logger.warn('Received ' + signal.Signals(sig_num).name)
    if signal.Signals(sig_num).name == "SIGINT":
        logger.info('Terminating Dirwatcher, keyboard interupted recieved')
    if signal.Signals(sig_num).name == "SIGTERM":
        logger.info('Terminating Dirwatcher, OS interupt received')
    global exit_flag
    exit_flag = True
    return


def main(args):
    ns = create_parser().parse_args()
    # search_for_magic("test.txt", 0, ns.text)
    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    while not exit_flag:
        try:
            watch_directory(ns.dir, ns.text, ns.ext, ns.int)
            pass
        except Exception as e:
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            logger.error(e)
            pass
        time.sleep(ns.int)
    logging.info("____________GoodBye :D!____________")

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start
    return


if __name__ == '__main__':
    main(sys.argv[1:])
