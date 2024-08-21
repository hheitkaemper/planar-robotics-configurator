# Planar-Robotics-Configurator

This repository contains an application for the creation of configurations for reinforcement learning algorithms and simulation environments.



## Installation

To install this application run the follwing commands.

```
cd PATH_TO_THIS_PACKAGE
pip install -e . 
```

## Run

To run this application execute the following commands.

```
cd PATH_TO_THIS_PACKAGE
python planar_robotics_configurator/configurator.py
```



## Use of configurations

To use exported configurations the library [hydra](https://hydra.cc/) can be used.
Therefore, it is required to create a config.yaml file with the following configuration.

```
defaults:
  - NAME_OF_ALGORTIHM_CONFIG_FILE
  - NAME_OF_ENVIRONMENT_CONFIG_FILE
```

The names of the configurations must be inserted in this config. 
Therefore, the configurations must be in the same folder as the config.yaml. 

Afterward, the configuration can be used inside a python module.
```
import hydra

@hydra.main(version_base=None, config_path="", config_name="config.yaml")
def main(config):
    env_config = config["env"]
    sim_config = config["algo"]
    ...
    
    
if __name__ == '__main__':
    main()    
```

## Maintainer

This repository is currently maintained by Hannes Heitkämper genannt Höllmann (hannes.heitkaemper@gmail.com).