from .knmi import config as knmi_config
from .factory_zero import config as fz_config

config = {
    "upload_dir": "./data/",
    "datasets_configs": {
        "factory zero": fz_config,
        "knmi": knmi_config
    }
}