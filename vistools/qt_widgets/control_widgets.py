from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import six
from collections import defaultdict
# again importing from matplotlib to not re-write the
# compatibility layer
from matplotlib.backends.qt4_compat import QtGui, QtCore
from .util import mapping_mixin


class TrippleSpinner(QtGui.QGroupBox):
    """
    A class to wrap up the logic for dealing with a min/max/step
    triple spin box.
    """
    # signal to be emitted when the spin boxes are changed
    # and settled
    valueChanged = QtCore.Signal(float, float)

    def __init__(self, title='', parent=None):
        QtGui.QGroupBox.__init__(self, title, parent=parent)

        self._spinbox_min_intensity = QtGui.QDoubleSpinBox(parent=self)
        self._spinbox_max_intensity = QtGui.QDoubleSpinBox(parent=self)
        self._spinbox_intensity_step = QtGui.QDoubleSpinBox(parent=self)

        ispiner_form = QtGui.QFormLayout()
        ispiner_form.addRow("min", self._spinbox_min_intensity)
        ispiner_form.addRow("max", self._spinbox_max_intensity)
        ispiner_form.addRow("step", self._spinbox_intensity_step)
        self.setLayout(ispiner_form)

    # TODO

    @QtCore.Slot(float, float)
    def setValues(self, bottom, top):
        """
        """
        pass

    @QtCore.Slot(float, float)
    def setLimits(self, bottom, top):
        """
        """
        pass

    @QtCore.Slot(float)
    def setStep(self, step):
        """
        """
        pass

    @property
    def values(self):
        return (self._spinbox_min_intensity.value,
                self._spinbox_max_intensity.value)


class DoubleSpinner(QtGui.QGroupBox):
    valueChanged = QtCore.Signal(float)

    def __init__(self, title='', parent=None):
        QtGui.QGroupBox.__init__(self, title, parent=parent)

        self._spinbox_value = QtGui.QDoubleSpinBox(parent=self)
        self._spinbox_step = QtGui.QDoubleSpinBox(parent=self)

        ispiner_form = QtGui.QFormLayout()
        ispiner_form.addRow("value", self._spinbox_min_intensity)
        ispiner_form.addRow("step", self._spinbox_intensity_step)
        self.setLayout(ispiner_form)
    # TODO flesh this out


class ControlContainer(QtGui.QGroupBox, mapping_mixin):
    _delim = '.'

    def __len__(self):
        print('len')
        return len(list(iter(self)))

    def __contains__(self, key):
        print('contains')
        return key in iter(self)

    def __init__(self, title, parent=None):
        # call parent constructor
        QtGui.QGroupBox.__init__(self, title, parent=parent)

        # nested containers
        self._containers = dict()
        # all non-container contents of this container
        self._contents = dict()

        # specialized listings
        # this is a dict keyed on type of dicts
        # The inner dicts are keyed on name
        self._by_type = defaultdict(dict)

        # make the layout
        self._layout = QtGui.QVBoxLayout()
        # add it to self
        self.setLayout(self._layout)

    def __getitem__(self, key):
        print(key)
        # TODO make this sensible un-wrap KeyException errors
        try:
            # split the key
            split_key = key.strip(self._delim).split(self._delim, 1)
        except TypeError:
            raise KeyError("key is not a string")
        # if one element back -> no splitting needed
        if len(split_key) == 1:
            return self._contents[split_key[0]]
        # else, at least one layer of testing
        else:
            # unpack the key parts
            outer, inner = split_key
            # get the container and pass through the remaining key
            return self._containers[outer][inner]

    def create_button(self, key):
        pass

    def create_checkbox(self, key):
        pass

    def create_container(self, key, container_title=None):
        """
        Create a nested container with in this container

        TODO : add rest of GroupBox parameters

        Parameters
        ----------
        key : str
            The key used to identify this container

        container_title : str or None
            The title of the container.
            If None, defaults to the key.
            If you want to title, use ''

        Returns
        -------
        control_container : ControlContainer
           The container created.
        """
        if container_title is None:
            container_title = key
        control_container = ControlContainer(container_title, parent=self)
        self._layout.addWidget(control_container)
        self._containers[key] = control_container
        return control_container

    def create_combobox(self, key, key_list, editable=False):
        pass

    def create_dict_display(self, key, input_dict):
        pass

    def create_doublespinbox(self, key):
        pass

    def create_text(self, key, text):
        """
        Create and add a text label to the control panel
        """
        # create text
        tmp_label = QtGui.QLabel(text)
        self._add_widget(key, tmp_label)

    def create_radiobuttons(self, key):
        pass

    def create_slider(self, key, min_val, max_val,
                     page_size=10):
        """

        Parameters
        ----------
        """

        # set up slider
        slider = QtGui.QSlider(parent=self)
        slider.setRange(min_val, max_val)
        slider.setTracking(True)
        slider.setSingleStep(1)
        slider.setPageStep(page_size)
        # TODO make this configurable
        slider.setOrientation(QtCore.Qt.Horizontal)
        self._add_widget(key, slider)
        return slider

    def create_triplespinbox(self, key):
        pass

    def _add_widget(self, key, in_widget):
        split_key = key.strip(self._delim).rsplit(self._delim, 1)
        # key is not nested, add to this object
        if len(split_key) == 1:
            key = split_key[0]
            # add to the type dict
            self._by_type[type(in_widget)][key] = in_widget
            # add to the contents list
            self._contents[key] = in_widget
            # add to layout
            self._layout.addWidget(in_widget)
        # else, grab the nested container and add it to that
        else:
            container, key = split_key
            self[container]._add_widget(key, in_widget)

    def iter_containers(self):
        return self._iter_helper_container([])

    def get_container(self, key):
        """
        Get a (possibly nested) container (the normal
        iterator skips these).  We may end up with two
        parallel sets of mapping functions.
        """
        split_key = key.strip(self._delim).rsplit(self._delim, 1)
        if len(split_key) == 1:
            return self._containers[split_key[0]]
        return self._containers[split_key[0]].get_containers(split_key[1])

    def _iter_helper(self, cur_path_list):
        """
        Recursively (depth-first) walk the tree and return the names
        of the leaves

        Parameters
        ----------
        cur_path_list : list of str
            A list of the current path
        """
        for k, v in six.iteritems(self._containers):
            for inner_v in v._iter_helper(cur_path_list + [k]):
                yield inner_v
        for k in six.iterkeys(self._contents):
            yield self._delim.join(cur_path_list + [k])

    def _iter_helper_container(self, cur_path_list):
        """
        Recursively (depth-first) walk the tree and return the names
        of the containers

        Parameters
        ----------
        cur_path_list : list of str
            A list of the current path
        """
        for k, v in six.iteritems(self._containers):
            for inner_v in v._iter_helper_container(cur_path_list + [k]):
                yield inner_v
        if len(cur_path_list):
            yield self._delim.join(cur_path_list)

    def __iter__(self):
        return self._iter_helper([])


class DictDisplay(QtGui.QGroupBox):
    """
    A generic widget for displaying dictionaries

    Parameters
    ----------
    title : string
       Widget title

    ignore_list : iterable or None
        keys to ignore

    parent : QWidget or None
        Parent widget, passed up stack
    """
    def __init__(self, title, ignore_list=None, parent=None):
        # pass up the stack, GroupBox takes care of the title
        QtGui.QGroupBox.__init__(self, title, parent=parent)

        if ignore_list is None:
            ignore_list = ()
        # make layout
        self.full_layout = QtGui.QVBoxLayout()
        # set layout
        self.setLayout(self.full_layout)
        # make a set of the ignore list
        self._ignore = set(ignore_list)
        self._disp_table = []

    @QtCore.Slot(dict)
    def update(self, in_dict):
        """
        updates the table

        Parameters
        ----------
        in_dict : dict
            The dictionary to display
        """
        # remove everything that is there
        for c in self._disp_table:
            c.deleteLater()

        # make a new list
        self._disp_table = []

        # add the keys alphabetically
        for k, v in sorted(list(in_dict.iteritems())):
            # if key in the ignore list, continue
            if k in self._ignore:
                continue
            self._add_row(k, v)

    def _add_row(self, k, v):
        """
        Private function

        Adds a row to the table

        Parameters
        ----------
        k : object
           The key

        v : object
           The value
        """
        # make a widget for our row
        tmp_widget = QtGui.QWidget(self)
        tmp_layout = QtGui.QHBoxLayout()
        tmp_widget.setLayout(tmp_layout)

        # add the key and value to the row widget
        tmp_layout.addWidget(QtGui.QLabel(str(k) + ':'))
        tmp_layout.addStretch()
        tmp_layout.addWidget(QtGui.QLabel(str(v)))

        # add the row widget to the full layout
        self.full_layout.addWidget(tmp_widget)
        # add the row widget to
        self._disp_table.append(tmp_widget)
