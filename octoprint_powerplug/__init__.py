# coding=utf-8
from __future__ import absolute_import
import threading

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import flask
import octoprint.plugin
import requests

class PowerplugPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SimpleApiPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.AssetPlugin
):
    power = False
    timer = None

    def get_template_vars(self):
        return dict(url=self._settings.get(["url"]))
    
    def get_settings_defaults(self):
        return dict(url="http://127.0.0.1")
    
    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False),
            dict(type="settings", custom_bindings=False)
        ]
    
    def get_assets(self):
        return dict(
            js=["js/powerplug.js"]
        )
    def on_api_get(self, request):
        action = request.args.get('action', default="toggle", type=str)

        if action == "toggle":
            self.toggle_plug()
            return flask.jsonify(state=self.power)
        elif action == "turnOn":
            self.turn_on()
            return flask.jsonify(state=self.power)
        elif action == "turnOff":
            self.turn_off()
            return flask.jsonify(state=self.power)
        elif action == "status":
            self.get_power_state()
            return flask.jsonify(state=self.power)

    ## tasmota commands
    def send_command_to_plug(self, command_name):
        res = requests.get(self._settings.get(["url"]) + "/cm?cmnd=" + command_name)
        return res.json()
    
    def toggle_plug(self):
        res = self.send_command_to_plug("Power%20Toggle")
        self.power = self.interpret_response(res)
    
    def turn_on(self):
        res = self.send_command_to_plug("Power%20On")
        self.power = self.interpret_response(res)
    
    def turn_off(self):
        res = self.send_command_to_plug("Power%20Off")
        self.power = self.interpret_response(res)
    
    def get_power_state(self):
        res = self.send_command_to_plug("Power")
        self.power = self.interpret_response(res)

    def interpret_response(self, response):
        powerResponse = False
        if response["POWER"] == "ON":
            powerResponse = True
        self._plugin_manager.send_plugin_message(self._identifier, dict(isOn=powerResponse))
        return powerResponse
    
    def on_after_startup(self):
        self.get_power_state()

    
    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/main/bundledplugins/softwareupdate.html
        # for details.
        return {
            "powerplug": {
                "displayName": "Powerplug Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "Injourn",
                "repo": "OctoPrint-Powerplug",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/Injourn/OctoPrint-Powerplug/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Powerplug Plugin"


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = PowerplugPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
