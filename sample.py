# -*- coding: utf-8 -*-
import argparse
import cv2
from pylab import *
from detect_iphone import *


def imresize(im, width=0, height=0):
    if width > 0 and height > 0:
        dim = (width, height)
    elif width > 0:
        r = width*1.0 / im.shape[1]
        dim = (width, int(im.shape[0] * r))
    elif height > 0:
        r = height*1.0 / im.shape[0]
        dim = (int(im.shape[1] * r), height)
    else:
        return im
    return cv2.resize(im, dim, interpolation=cv2.INTER_AREA)


def out_cnts(im, cnts, winname='result', color=(0, 0, 255)):
    cv2.drawContours(im, [cnts], -1, color, 3)
    cv2.imshow(winname, im)
    cv2.waitKey(0)


if __name__ == "__main__":
    # argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument("-q", "--query", required=True,
                    help="Path to the query image")
    ap.add_argument("-v", "--version", required=True,
                    help="Set iPhone Version")
    args = vars(ap.parse_args())

    # read and resize image
    im = cv2.imread(args["query"])

    u"""
    Making image smaller by resize it to reduce processing time.
    But it causes missing fine changes.
    """
    im = imresize(im, height=300)

    finder = DetectIPhone(im)
    if(args["version"] == '5'):
        detects = finder.detect5S()
    else:
        detects = finder.detect4S()

    if len(detects) > 0:
        for cnt in detects:
            out_cnts(im, cnt)
    else:
        print('iPhone is not detected')
