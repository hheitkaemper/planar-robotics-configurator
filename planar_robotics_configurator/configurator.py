import hydra

from planar_robotics_configurator.view.configurator_app import ConfiguratorApp


@hydra.main(version_base=None, config_path='../.config', config_name='config')
def main(config) -> None:
    ConfiguratorApp().run()


if __name__ == '__main__':
    main()
