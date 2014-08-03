# -*- coding: utf-8 -*-

import cv2
from itertools import chain


class DetectIPhone(object):
    u""" Find iPhone based on contours """

    DEF_AREA_RATIO_4S = 0.605

    DEF_AREA_RATIO_5S = 0.655

    THRESHOLD = 0.95

    def __init__(self, im):
        self.im = im

    def detect5S(self, threshold=None, ratio=None):
        u""" Find iPhone 5S from contours """
        if threshold is None:
            self.threshold = self.THRESHOLD
        if ratio is None:
            self.ratio = self.DEF_AREA_RATIO_5S
        return self.__detectIPhone()

    def detect4S(self, threshold=None, ratio=None):
        u""" Find iPhone 4S from contours """
        if threshold is None:
            self.threshold = self.THRESHOLD
        if ratio is None:
            self.ratio = self.DEF_AREA_RATIO_4S
        return self.__detectIPhone()

    def findEdges(self, im):
        u""" find edges from image """
        gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

        u"""
        Bilateral Filger (bilateralFilter()) is good for removing noise
        from images while saving actual edges
        """
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        return cv2.Canny(gray, 30, 200)

    def findContours(self, im):
        return cv2.findContours(self.findEdges(im), cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)

    def __detectIPhone(self):
        (im, contours, hierarchy) = self.findContours(self.im)

        objects = []
        for i in range(len(contours)):
            if self.__findRect(contours[i]):
                inner = self.__findInnerRect(i, contours, hierarchy[0])
                if len(inner) > 0:
                    objects.append((i, inner))

        if len(objects) == 0:
            return objects

        iphones = []
        for object in objects:
            abody = cv2.contourArea(contours[object[0]])
            if abody == 0.0:
                continue

            for screen in object[1]:
                ascreen = cv2.contourArea(contours[screen])
                aratio = ascreen/abody
                error = abs(self.ratio-aratio)/self.ratio
                if self.threshold <= (1-error):
                    if object[0] not in iphones:
                        iphones.append(object[0])

        return [contours[i] for i in iphones]

    def __findRect(self, cnt):
        arc = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02*arc, True)

        # rectangle contour case
        return len(approx) == 4

    def __findInnerRect(self, parent_idx, contours, hierarchy):
        rect = []
        node = hierarchy[parent_idx]
        if node[2] != -1:
            # inspect child
            cnode = node[2]
            if self.__findRect(contours[cnode]):
                rect.append([cnode])
            rect.append(self.__findInnerRect(cnode, contours, hierarchy))

        if node[0] != -1:
            # inspect next
            nnode = node[0]
            if self.__findRect(contours[nnode]):
                rect.append([nnode])
            rect.append(self.__findInnerRect(nnode, contours, hierarchy))

        return list(chain.from_iterable(rect))
