from .logging_setup import logger as log
from .schema_utils import SchemaUtils
from pandas import DataFrame, concat
from xml.etree.ElementTree import parse
from .style_utils import LayerStylesUpdater as lsu
from .layers_utils import LayersUtils as lu


class GMLProcessor:
    def __init__(self, ui_helpers):
        self.ui_helpers = ui_helpers
        self.schema_utils = SchemaUtils()

    def process_gml_files(self, gml_layers_dataFrame_group):

        total_gml_files = len(gml_layers_dataFrame_group)
        progress_message_bar, progress_bar = self.ui_helpers.show_progress_bar(
            total_gml_files, "Processing '{}' GML Files"
            .format(total_gml_files))

        current_step = 0

        self.schema_utils.fetch_geonorge_schemas()
        layer_styles_df = DataFrame()

        # Check if there are any schemas fetched from Geonorge
        if self.schema_utils.geonorge_schemas is None:
            self.ui_helpers.message_bar_critial(
                "Kan ikke hente skjemaer fra Geonorge.")
            return layer_styles_df

        # Iterate through each group to get the schema and styles
        log.info("=== Extracting schema and styles from GML files ===")
        for root_filename, group in gml_layers_dataFrame_group:
            progress_bar.setValue(current_step)
            current_step += 1
            progress_message_bar.setText(
                "Processing GML Files: {}/{}".format(
                    current_step, total_gml_files))
            log.info("Processing GML file '{}' ({}/{})"
                     .format(root_filename, current_step, total_gml_files))

            group_layers_dataFrame = DataFrame(group)

            gml_file_path = group_layers_dataFrame['File_Path'].iloc[0]
            gml_schema_locations = self.get_gml_schemalocations(gml_file_path)

            # Get schema identifiers from Geonorge based on gml file schema locations
            if gml_schema_locations is None:
                self.ui_helpers.log_message_warning(
                    "Ingen schema funnet i GML-filen '{}'"
                    .format(root_filename))
                log.debug("No schemalocations found in the GML file: '{}' "
                          .format(gml_file_path))
                continue
            schema_identifier = (
                self.schema_utils.find_geonorge_schema_identifier(gml_schema_locations))

            if not schema_identifier:
                self.ui_helpers.log_message_warning(
                    "Ingen samsvarende skjema funnet i Geonorge "
                    "skjemaregisteret for GML-filen '{}'."
                    .format(root_filename)
                )
                continue
            # Add the schema identifier to the group
            group_layers_dataFrame['schema_identifier'] = schema_identifier

            # Get the styles for the selected layers
            theme_styles_dataFrame = lsu.get_styles_for_theme(
                schema_identifier)
            if theme_styles_dataFrame is None:
                log.debug("No styles found for theme '{}'."
                          .format(schema_identifier))
                self.ui_helpers.message_bar_warning(
                    "Kunne ikke finne tegneregel i Geonorge for '{}'."
                    .format(schema_identifier))
                continue

            supported_symbology_for_theme = lsu.filter_styles_by_formats(
                theme_styles_dataFrame)

            # Check if there are any supported formats
            if supported_symbology_for_theme.empty:
                log.warning("No supported formats found for theme '{}'."
                            .format(schema_identifier))
                self.ui_helpers.log_message_warning(
                    "Ingen støttede formater funnet for temaet '{}'"
                    .format(schema_identifier))
                continue

            group_layers_dataFrame = (
                lsu.apply_Gml_node_overrides(group_layers_dataFrame,
                                             schema_identifier))
            # Map layers to appropriate styles
            log.info("=== Fetch Styles for layers ===")

            group_layers_dataFrame['style_name'] = (
                group_layers_dataFrame.apply(lambda row:
                                             lsu.get_style_name(
                                                row,
                                                supported_symbology_for_theme,
                                                'qml'), axis=1))
            styled_layers_data = lu.merge_and_rename_styles_with_layers(
                group_layers_dataFrame, supported_symbology_for_theme
            )

            lu.save_layer_style_report(styled_layers_data)

            layers_with_styles = lu.filter_layers_with_styles(
                styled_layers_data)

            if layers_with_styles.empty:
                self.ui_helpers.log_message_warning(
                    "Ingen tegneregler funnet for det valgte temaet."
                )
                log.warning("No styles found for the selected theme.")
                continue
            # Count the number of layers with styles
            total_layers_with_style = len(layers_with_styles)
            total_selected_layers = len(group_layers_dataFrame.dropna(
                subset=['Layer_Name']))

            log.info("Acquired {0} of {1} selected layers"
                     .format(total_layers_with_style, total_selected_layers))
            layers_with_styles = layers_with_styles.copy()

            # Get style file string
            log.info("=== Get Style file string ===")
            layers_with_styles['Style_file_string'] = layers_with_styles.apply(
                lambda row: lsu.add_file_string_to_row(row), axis=1
            )

            # Filter out layers without style file string
            layers_with_styles = layers_with_styles[
                layers_with_styles['Style_file_string'].notnull()]

            if layers_with_styles.empty:
                self.ui_helpers.log_message_warning(
                    "Ingen tegneregler-fil ble funnet for det valgte temaet."
                )
                log.debug("No style file was fetched for the selected theme.")
                continue
            layer_styles_df = concat([layer_styles_df, layers_with_styles])
            self.ui_helpers.log_message_info(
                f"Tegneregler er hentet for '{root_filename}.")

        # Finalize and close the progress dialog
        self.ui_helpers.close_progress_bar(progress_message_bar,
                                           delay=12000)

        return layer_styles_df

    def get_gml_schemalocations(self, xml_path):
        """
        Extracts namespaces and schema locations from an XML file and
        returns them as a pandas DataFrame.

        :param xml_path: Path to the XML file.
        :type xml_path: str
        :return: DataFrame containing namespaces and schema locations.
        :rtype: pd.DataFrame
        """
        log.info("=== Extracting namespaces and schema locations ===")
        log.info(f" GML file path: '{xml_path}'")
        # Parse the XML file and get the root element
        tree = parse(xml_path)
        root = tree.getroot()

        # Extract schemaLocation attribute from the root element
        schema_location = next(
            (value for key, value in root.attrib.items()
                if key.endswith('schemaLocation')), None)

        # If schemaLocation is found, split it into a list
        if schema_location:
            schema_location_list = schema_location.split()

            # Convert the list into dictionary with alternating keys and values
            schema_dict = dict(schema_location_list[i:i + 2] for i in range(
                0,
                len(schema_location_list),
                2))

            # Convert the schema dictionary to a DataFrame
            schema_df = DataFrame(schema_dict.items(),
                                  columns=["namespace",
                                  "schemalocation"])

            # Remove known namespaces from the DataFrame
            namespace_whitelist = [
                'www.opengis.net',
                'www.w3.org',
                'www.interactive-instruments.de']
            pattern = '|'.join(namespace_whitelist)
            filtered_namespace_info = schema_df[
                ~schema_df["namespace"].str.contains(pattern)]
            log.info('Schema locations extracted successfully. {}'.format(
                filtered_namespace_info['schemalocation'].values))
            return filtered_namespace_info

        return None
