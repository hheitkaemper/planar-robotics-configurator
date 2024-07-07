import hydra

from planar_robotics_configurator.model.config import Config
from planar_robotics_configurator.model.configurator_model import ConfiguratorModel


@hydra.main(version_base=None, config_path='../.config', config_name='config')
def main(config: Config) -> None:
    ConfiguratorModel().load_config(config)
    from planar_robotics_configurator.view.configurator_app import ConfiguratorApp
    ConfiguratorApp().run()


if __name__ == '__main__':
    main()
