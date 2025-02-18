# Standard library imports.
from os.path import basename

# Major package imports.
from pyface.qt import QtCore, QtGui

# Enthought library imports.
from traits.api import (
    Bool, Event, Instance, File, observe, Property, provides, Str,
)
from pyface.tasks.api import Editor

# Local imports.
from i_python_editor import IPythonEditor
from pyface.key_pressed_event import KeyPressedEvent


@provides(IPythonEditor)
class PythonEditor(Editor):
    """ The toolkit specific implementation of a PythonEditor.  See the
    IPythonEditor interface for the API documentation.
    """

    #### 'IPythonEditor' interface ############################################

    obj = Instance(File)

    path = Str

    dirty = Bool(False)

    name = Property(Str, observe="path")

    tooltip = Property(Str, observe="path")

    show_line_numbers = Bool(True)

    #### Events ####

    changed = Event

    key_pressed = Event(KeyPressedEvent)

    def _get_tooltip(self):
        return self.path

    def _get_name(self):
        return basename(self.path) or "Untitled"

    ###########################################################################
    # 'PythonEditor' interface.
    ###########################################################################

    def create(self, parent):
        self.control = self._create_control(parent)

    def load(self, path=None):
        """ Loads the contents of the editor.
        """
        if path is None:
            path = self.path

        # We will have no path for a new script.
        if len(path) > 0:
            with open(self.path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = ""

        self.control.code.setPlainText(text)
        self.dirty = False

    def save(self, path=None):
        """ Saves the contents of the editor.
        """
        if path is None:
            path = self.path

        f = file(path, "w")
        f.write(self.control.code.toPlainText())
        f.close()

        self.dirty = False

    def select_line(self, lineno):
        """ Selects the specified line.
        """
        self.control.code.set_line_column(lineno, 0)
        self.control.code.moveCursor(
            QtGui.QTextCursor.EndOfLine, QtGui.QTextCursor.KeepAnchor
        )

    ###########################################################################
    # Trait handlers.
    ###########################################################################

    @observe("path")
    def _reload_data(self, event):
        if self.control is not None:
            self.load()

    @observe("show_line_numbers")
    def _update_visible_lines(self, event=None):
        if self.control is not None:
            self.control.code.line_number_widget.setVisible(
                self.show_line_numbers
            )
            self.control.code.update_line_number_width()

    ###########################################################################
    # Private interface.
    ###########################################################################

    def _create_control(self, parent):
        """ Creates the toolkit-specific control for the widget.
        """
        from pyface.ui.qt4.code_editor.code_widget import AdvancedCodeWidget

        self.control = control = AdvancedCodeWidget(parent)
        self._update_visible_lines()

        # Install event filter to trap key presses.
        event_filter = PythonEditorEventFilter(self, self.control)
        self.control.installEventFilter(event_filter)
        self.control.code.installEventFilter(event_filter)

        # Connect signals for text changes.
        control.code.modificationChanged.connect(self._toggle_dirty)
        control.code.textChanged.connect(self._toggle_changed_trait)

        # Load the editor's contents.
        self.load()

        return control

    def _toggle_dirty(self, dirty):
        """ Called whenever a change is made to the dirty state of the
            document.
        """
        self.dirty = dirty

    def _toggle_changed_trait(self):
        """ Called whenever a change is made to the text of the document.
        """
        self.changed = True


class PythonEditorEventFilter(QtCore.QObject):
    """ A thin wrapper around the advanced code widget to handle the
    key_pressed Event.
    """

    def __init__(self, editor, parent):
        super().__init__(parent)
        self.__editor = editor

    def eventFilter(self, obj, event):
        """ Reimplemented to trap key presses.
        """
        if (
            self.__editor.control
            and obj == self.__editor.control
            and event.type() == QtCore.QEvent.FocusOut
        ):
            # Hack for Traits UI compatibility.
            self.__editor.control.emit(QtCore.SIGNAL("lostFocus"))

        elif (
            self.__editor.control
            and obj == self.__editor.control.code
            and event.type() == QtCore.QEvent.KeyPress
        ):
            # Pyface doesn't seem to be Unicode aware.  Only keep the key code
            # if it corresponds to a single Latin1 character.
            kstr = event.text()
            try:
                kcode = ord(str(kstr))
            except:
                kcode = 0

            mods = event.modifiers()
            self.key_pressed = KeyPressedEvent(
                alt_down=(
                    (mods & QtCore.Qt.AltModifier) == QtCore.Qt.AltModifier
                ),
                control_down=(
                    (mods & QtCore.Qt.ControlModifier)
                    == QtCore.Qt.ControlModifier
                ),
                shift_down=(
                    (mods & QtCore.Qt.ShiftModifier) == QtCore.Qt.ShiftModifier
                ),
                key_code=kcode,
                event=event,
            )

        return super().eventFilter(obj, event)
