'''
Module contains layout classes
'''
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout
class MAD_Layout:

    def __init__(self, widget, name, margins=None, spacing=None):
        self.widget = widget
        self.name = name
        self.margins = margins
        self.spacing = spacing

    def horizontal(self):
        self.layout = QHBoxLayout(self.widget)
        self.layout.setObjectName(self.name)



    def vertical(self):
        self.layout = QVBoxLayout(self.widget)
        self.layout.setObjectName(self.name)

    def set_layout_props(self):

        if self.margins is not None:
            self.layout.setContentsMargins(self.margins[0], self.margins[1], self.margins[2], self.margins[3])

        if self.spacing is not None:
            self.layout.setSpacing(self.spacing)