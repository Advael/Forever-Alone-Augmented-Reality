#!/usr/bin/python

import cv


class AR(object):

    def __init__(self):
        """
        Initialize all class variables getting cascade from an xml, and the
        overlay image from a png file.
        """
        self.window_name = 'AR tests'
        self.cascade = cv.Load('res/haarcascade_frontalface_alt.xml')
        self.image_scale = 2
        self.haar_scale = 1.2
        self.min_neighbors = 2
        self.min_size = (20, 20)
        self.haar_flags = 0
        self.capture = cv.CreateCameraCapture(0)
        self.overlay_image = cv.LoadImage('res/forever_alone.png',
                                         cv.CV_LOAD_IMAGE_UNCHANGED)

    def detect_and_draw(self, image):
        """
        Use the haar object detection to find the face, and after that show the
        image in those coords.
        """
        gray = cv.CreateImage((image.width, image.height), 8, 1)
        small_image = cv.CreateImage((cv.Round(image.width / self.image_scale),
                          cv.Round(image.height / self.image_scale)), 8, 1)

        cv.CvtColor(image, gray, cv.CV_BGR2GRAY)
        cv.Resize(gray, small_image, cv.CV_INTER_LINEAR)
        cv.EqualizeHist(small_image, small_image)

        if self.cascade:
            faces = cv.HaarDetectObjects(small_image, self.cascade,
                                         cv.CreateMemStorage(0),
                                         self.haar_scale, self.min_neighbors,
                                         self.haar_flags, self.min_size)
            if faces and len(faces) == 1:
                (x, y, w, h), n = faces[0]
                # 1.25 is a factor to do the overlay bigget than the face
                width = int(w * self.image_scale * 1.33)
                height = int(h * self.image_scale * 1.33)
                cv.SetImageROI(image, (
                                       int(x * self.image_scale),
                                       # 0.70 to start the image above the head
                                       int(y * self.image_scale * 0.70),
                                       width, height))
                resized = cv.CreateImage((width, height), cv.IPL_DEPTH_8U, 3)
                cv.Convert(resized, resized)
                cv.Resize(self.overlay_image, resized, 2) # CV_INTER_CUBIC
                cv.Add(image, resized, image)
                cv.ResetImageROI(image)

        cv.ShowImage(self.window_name, image)

    def main_loop(self):
        """
        Infinite loop taking images from camera and calling the face detection
        function.
        """
        frame_copy = None
        while True:
            frame = cv.QueryFrame(self.capture)

            if not frame_copy:
                frame_copy = cv.CreateImage((frame.width, frame.height),
                                            cv.IPL_DEPTH_8U, frame.nChannels)

            if frame.origin == cv.IPL_ORIGIN_TL:
                cv.Copy(frame, frame_copy)
            else:
                cv.Flip(frame, frame_copy, 0)

            self.detect_and_draw(frame_copy)

            if cv.WaitKey(15) == 27:
                break

        cv.DestroyWindow(self.window_name)


if __name__ == '__main__':
    ar = AR()
    ar.main_loop()
