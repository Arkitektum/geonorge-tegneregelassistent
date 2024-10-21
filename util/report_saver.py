import datetime
from os.path import join, exists, dirname
from os import makedirs
from .config_loader import ConfigLoader


class ReportSaver:
    def __init__(self):

        self.base_path = None
        config_loader = ConfigLoader()
        self.config = config_loader.load_qgis_config()
        save_report = self.config['report']['save_report']
        if save_report:
            base_path = self.config['report']['report_base_path']
            if base_path is None:
                base_path = join(
                    dirname(dirname(__file__)), 'reports')
            self.base_path = base_path

    def create_directory_structure(self):

        directory_path = self.base_path

        # Create the directories if they do not exist
        if not exists(directory_path):
            makedirs(directory_path)

        return directory_path

    def save_report_as_csv(self, report_content, report_file_name=None):
        """
        Save the report content as a CSV file.
        input:
            report_content: DataFrame
            report_file_name: str
        """
        # Save report if configured to do so
        if self.base_path is None:
            return

        self.create_directory_structure()

        if not report_file_name:
            # Create file name
            timestamp = datetime.datetime.now().strftime("%Y%m%d")
            report_file_name = "{0}_{1}.csv".format(
                report_content['DatasetName'][0], timestamp)

        # Define the full path for the report file
        file_path = join(self.base_path, report_file_name)

        # Save the report content to the file
        report_content.to_csv(file_path, index=False, sep=';',
                              encoding='utf-16')

        print(f"Report saved to: {file_path}")

        return
