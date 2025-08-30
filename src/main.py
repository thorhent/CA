# main.py
#
# Copyright 2025 Taylan Branco Meurer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import ClinicalayudanteWindow
from .preferences import PreferencesWindow


class ClinicalayudanteApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='io.github.thorhent.CA',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path='/io/github/thorhent/CA')
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = ClinicalayudanteWindow(application=self)
        win.present()

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(application_name='Clinical Ayudante',
                                application_icon='io.github.thorhent.CA',
                                developer_name='Taylan Branco Meurer',
                                version='1.8.25',
                                developers=['Taylan Branco Meurer'],
                                copyright='© 2025 Taylan Branco Meurer')
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(_('translator-credits'))
        about.add_credit_section("Orientadores médicos", ['Dra. Lorena Djament'])
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        if not hasattr(self, 'prefs_win') or self.prefs_win is None:
            self.prefs_win = PreferencesWindow()
            self.prefs_win.connect("close-request", self.on_prefs_closed)

        self.prefs_win.present()

    def on_prefs_closed(self, window):
        self.prefs_win = None
        return False  # Permite que la ventana se cierre


    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = ClinicalayudanteApplication()
    return app.run(sys.argv)
