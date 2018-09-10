import signal
import logging
import os
import argparse
import sys
import time

exit_flag = True
checked_files = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('test.log')
formatter = logging.Formatter(
    "%(asctime)s:%(levelname)s:%(threadName)s:%(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def signal_handler(signum, stack):
    """Logs Interrupt and Termination signals"""
    logger.warning("Received signal: {}".format(signum))
    global exit_flag
    if signum == signal.SIGINT:
        exit_flag = False
    if signum == signal.SIGTERM:
        exit_flag = False


def magicWordFinder(directory, magicWord):
    print(directory)
    print(magicWord)
    dir = os.path.abspath(directory)
    text_files = [f for f in os.listdir(dir) if ".txt" in f]
    for file in text_files:
        count = len(open(file).readlines())
        # if the file has not been checked create an empty list for it
        # and search it
        if file not in checked_files:
            checked_files[file] = 0
            logger.info("checking... " + file)
            searchFile(file, magicWord)
        # if the file has been checked
        # check the line count with the value in the key
        # if the check fails, there are new lines in the file
        # and it needs to be searched again.
        # else the file has not changed so dont run through it again.
        elif file in checked_files:
            if checked_files[file] != 0:
                if count != checked_files[file]:
                    logger.infor(
                        "File {} changed, searching again".format(file))
                    searchFile(file, magicWord)
                else:
                    pass


def searchFile(file, magicWord):
    logger.info("searching {} for instances of {}".format(file, magicWord))

    with open(file) as doc:
        content = doc.readlines()
        last_index = 0
        for i, line in enumerate(content):
            last_index += 1
            if magicWord in line:
                logger.info("Match found for {} found on line {} in {}".format(
                    magicWord, i + 1, file))
        checked_files[file] = last_index


def create_parser():
    """Create an argument parser object"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'dir',  help='the directory you are searching through.')
    parser.add_argument(
        '-m', '--magicWord',  help='the word you are searching for.')

    return parser


def main():
    # Hook these two signals from the OS ..

    parser = create_parser()
    args = parser.parse_args()

    if not args:
        parser.print_usage()
        sys.exit(1)

    directory = args.dir
    magicWord = args.magicWord

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends either of these to my
    # process.

    while exit_flag:
        try:
            magicWordFinder(directory, magicWord)
            time.sleep(3)

        except Exception as e:
            logger.exception("cannot run \n" + e)

    # Do my long-running stuff
    # put a sleep inside my while loop so I don't peg the cpu usage at 100%


if __name__ == '__main__':
    main()
