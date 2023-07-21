'''
Frame class to add Frames to UI
'''

from PyQt5.QtWidgets import QFrame, QSizePolicy

class MAD_Frame:

    def __init__(self, widget, name, frame_shape=None,
                                    frame_shadow=None,
                                    stylesheet=None,
                                    max_size=None,
                                    min_size=None):
        self.widget = widget
        self.name = name
        self.frame_shape = frame_shape
        self.frame_shadow = frame_shadow
        self.stylesheet = stylesheet
        self.max_size = max_size
        self.min_size = min_size

    def create_frame(self):
        self.frame = QFrame(self.widget)
        self.frame.setObjectName(self.name)

        if self.stylesheet is not None:
            self.frame.setStyleSheet(self.stylesheet)

        if self.frame_shape is not None:
            self.frame.setFrameShape(self.frame_shape)

        if self.frame_shadow is not None:
            self.frame.setFrameShadow(self.frame_shadow)

        if self.max_size is not None:
            self.frame.setMaximumSize(self.max_size)

        if self.min_size is not None:
            self.frame.setMinimumSize(self.min_size)

    def frame_size_policy(self, x_size_policy, y_size_policy, heightForWidth, horizStretch=0, vertStretch=0):

        self.size_policy = QSizePolicy(x_size_policy, y_size_policy)
        self.size_policy.setHorizontalStretch(horizStretch)
        self.size_policy.setVerticalStretch(vertStretch)

        if heightForWidth:
            self.size_policy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        else:
            self.size_policy.setWidthForHeight(self.frame.sizePolicy().hasWidthForHeight())

        self.frame.setSizePolicy(self.size_policy)