from os.path import join, dirname
from json import load


class ConfigLoader:
    def __init__(self):
        self.config_directory = join(dirname(dirname(__file__)), 'config')

    def load_qgis_config(self):
        """
        Load the QGIS configuration

        :return: Configuration dictionary.
        :rtype: dict
        """

        return self.load_config('qgis_config.json')

    def load_resources_config(self):
        """
        Load the resource configuration

        :return: Configuration dictionary.
        :rtype: dict
        """

        return self.load_config('resource_config.json')

    def load_config(self, filename):
        """
        Load the configuration from the JSON file at config_path

        :return: Configuration dictionary.
        :rtype: dict
        """
        file_path = join(self.config_directory, filename)
        with open(file_path, 'r') as file:
            config = load(file)
        return config
