# (C) Copyright 2007-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import os
import pathlib
import shutil
import sys
import tempfile
import unittest

import pkg_resources
from pyface.i_gui import IGUI
from traits.api import HasTraits, provides

from envisage.ui.tasks.api import TasksApplication
from envisage.ui.tasks.tasks_application import DEFAULT_STATE_FILENAME

# Decorator for skipping tests that require a GUI
requires_gui = unittest.skipIf(
    os.getenv("ETS_TOOLKIT", default="none") in {"null", "none"},
    "Test requires a non-null GUI backend",
)

# There's a PySide6 end-of-process segfault on Linux that's
# interfering with our CI runs, so we skip the relevant tests
# when running under GitHub Actions CI.
# xref: enthought/envisage#476
skip_with_flaky_pyside = unittest.skipIf(
    (
        os.getenv("GITHUB_ACTIONS") == "true"
        and sys.platform == "linux"
        and os.getenv("ETS_TOOLKIT") == "qt"
    ),
    "Skipping segfault-causing test on Linux. See enthought/envisage#476",
)


@provides(IGUI)
class DummyGUI(HasTraits):
    pass


@unittest.skipIf(
    sys.platform == "linux" and sys.version_info >= (3, 8),
    "xref: enthought/envisage#476",
)
@requires_gui
class TestTasksApplication(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)

    @skip_with_flaky_pyside
    def test_layout_save_with_protocol_3(self):
        # Test that the protocol can be overridden on a per-application basis.
        state_location = self.tmpdir

        # Create application, and set it up to exit as soon as it's launched.
        app = TasksApplication(
            state_location=state_location, layout_save_protocol=3,
        )
        app.on_trait_change(app.exit, "application_initialized")

        memento_file = os.path.join(state_location, app.state_filename)
        self.assertFalse(os.path.exists(memento_file))
        app.run()
        self.assertTrue(os.path.exists(memento_file))

        # Check that the generated file uses protocol 3.
        with open(memento_file, "rb") as f:
            protocol_bytes = f.read(2)
        self.assertEqual(protocol_bytes, b"\x80\x03")

    @skip_with_flaky_pyside
    def test_layout_save_creates_directory(self):
        # Test that state can still be saved if the target directory
        # doesn't exist.
        state_location = pathlib.Path(self.tmpdir) / "subdir"
        state_filename = "memento_test"
        state_path = state_location / state_filename

        self.assertFalse(state_location.exists())
        self.assertFalse(state_path.exists())

        # Create application and set it up to exit as soon as it's launched.
        app = TasksApplication(
            state_location=state_location,
            state_filename=state_filename,
        )
        app.on_trait_change(app.exit, "application_initialized")
        app.run()

        self.assertTrue(state_location.exists())
        self.assertTrue(state_path.exists())

    @skip_with_flaky_pyside
    def test_layout_load(self):
        # Check we can load a previously-created state. That previous state
        # has an main window size of (492, 743) (to allow us to check that
        # we're actually using the file).
        stored_state_location = pkg_resources.resource_filename(
            "envisage.ui.tasks.tests", "data"
        )

        state_location = self.tmpdir
        shutil.copyfile(
            os.path.join(stored_state_location, "application_memento_v2.pkl"),
            os.path.join(state_location, DEFAULT_STATE_FILENAME),
        )

        app = TasksApplication(state_location=state_location)
        app.on_trait_change(app.exit, "application_initialized")
        app.run()

        state = app._state
        self.assertEqual(state.previous_window_layouts[0].size, (492, 743))

    @skip_with_flaky_pyside
    def test_layout_load_pickle_protocol_3(self):
        # Same as the above test, but using a state stored with pickle
        # protocol 3.
        stored_state_location = pkg_resources.resource_filename(
            "envisage.ui.tasks.tests", "data"
        )

        state_location = self.tmpdir
        shutil.copyfile(
            os.path.join(stored_state_location, "application_memento_v3.pkl"),
            os.path.join(state_location, "fancy_state.pkl"),
        )

        # Use a non-standard filename, to exercise that machinery.
        app = TasksApplication(
            state_location=state_location, state_filename="fancy_state.pkl",
        )
        app.on_trait_change(app.exit, "application_initialized")
        app.run()

        state = app._state
        self.assertEqual(state.previous_window_layouts[0].size, (492, 743))

    def test_gui_trait_expects_IGUI_interface(self):
        # Trivial test where we simply set the trait
        # and the test passes because no errors are raised.
        app = TasksApplication()
        app.gui = DummyGUI()
