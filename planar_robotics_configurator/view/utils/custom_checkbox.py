from kivy.properties import AliasProperty
from kivy.uix.behaviors import ToggleButtonBehavior

from planar_robotics_configurator.view.utils import CustomIconButton


class CustomCheckbox(ToggleButtonBehavior, CustomIconButton):
    """
    A custom checkbox. Has the same functionality as the default Kivy checkbox but uses custom icons.
    """

    def _get_active(self):
        return self.state == 'down'

    def _set_active(self, value):
        self.state = 'down' if value else 'normal'

    active = AliasProperty(_get_active, _set_active, bind=('state',), cache=True)

    def __init__(self, **kwargs):
        self.icon = "checkbox-blank-outline"
        self.fbind('state', self._on_state)
        self.bind(active=self._on_active)
        super(CustomCheckbox, self).__init__(**kwargs)

    def _on_active(self, instance, value):
        if value:
            self.icon = "checkbox-marked"
        else:
            self.icon = "checkbox-blank-outline"

    def _on_state(self, instance, value):
        if self.group and self.state == 'down':
            self._release_group(self)

    def on_group(self, *largs):
        super(CustomCheckbox, self).on_group(*largs)
        if self.active:
            self._release_group(self)
