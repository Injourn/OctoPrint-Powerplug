/*
 * View model for OctoPrint-Powerplug
 *
 * Author: Injourn
 * License: AGPL-3.0-or-later
 */
$(function() {
    function PowerplugViewModel(parameters) {
        var self = this;
        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        self.settingsViewModel = parameters[0];
        self.light_indicator = $("#power_indicator");
    	self.isOn = ko.observable(undefined);

        self.onBeforeBinding = function() {
            self.settings = self.settingsViewModel.settings;
        };

    	self.onDataUpdaterPluginMessage = function(plugin, data) {
            if (plugin != "powerplug") {
                return;
            }

            if (data.isOn !== undefined) {
                self.isOn(data.isOn);
            }
        };

        self.onStartup = function () {
            setInterval(() => {
                OctoPrint.simpleApiGet("powerplug?action=status");
            },10 * 1000);
            self.isOn.subscribe(function() {
                if (self.isOn()) {
                    self.light_indicator.removeClass("fa-toggle-off").addClass("fa-toggle-on");
                } else {
                    self.light_indicator.removeClass("fa-toggle-on").addClass("fa-toggle-off");
                }
            });
            OctoPrint.simpleApiGet("powerplug?action=status");
        }
        // TODO: Implement your plugin's view model here.
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/main/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: PowerplugViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: [ /* "loginStateViewModel",*/ "settingsViewModel"],
        // Elements to bind to, e.g. #settings_plugin_powerplug, #tab_plugin_powerplug, ...
        elements: [ "#navbar_plugin_powerplug_1","#settings_plugin_octolight"]
    });
});
