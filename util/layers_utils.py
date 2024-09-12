from .report_saver import ReportSaver
from pandas import merge
from .logging_setup import logger as log
from tempfile import mkstemp
from os import fdopen, remove


class LayersUtils:

    @staticmethod
    def group_layers_by_column_name(gml_layer_dataFrame,
                                    column_name='Root_Filename'):
        """
        Group the GML layers by their base file names.
        input:
            gml_layer_dataFrame: DataFrame containing GML layer details.
            column_name: str, default='Root_Filename'
        output:
            DataFrameGroupBy
        """
        if gml_layer_dataFrame is None:
            return None

        # Group the layers by the base file name
        grouped_layers = gml_layer_dataFrame.groupby(column_name)

        return grouped_layers

    @staticmethod
    def merge_and_rename_styles_with_layers(theme_layers_dataframe,
                                            supported_symbology_for_theme):
        """
        Merge and rename the styles with the layers.
        input:
            theme_layers_dataframe: DataFrame containing theme layers.
            supported_symboly_for_theme: DataFrame containing supported styles.
        output:
            DataFrame
        """
        # Merge layer_styles with group on LayerName
        merged_group_layer_styles = merge(theme_layers_dataframe,
                                          supported_symbology_for_theme,
                                          how='outer', right_on='StyleName',
                                          left_on='style_name')

        # Filter relevant columns
        relevant_columns = ['Gml_Node', 'Geometry', 'Layer_Name',
                            'StyleName', 'Format', 'DatasetName',
                            'Status', 'FileUrl']
        filtered_dataset = merged_group_layer_styles[relevant_columns]

        # Rename columns
        new_column_names = ['GmlNode', 'Geometry', 'LayerName',
                            'StyleName', 'Format', 'DatasetName',
                            'Status', 'FileUrl']

        filtered_dataset.columns = new_column_names

        return filtered_dataset

    @staticmethod
    def merge_layers_with_styles_and_gml_layers(gml_layers_dataframe_grouped,
                                                layers_with_styles_dataframe):
        """
        Merge layers with styles and GML layers.
        input:
            gml_layers_dataframe_grouped: DataFrameGroupBy containing
            GML layers.
            layers_with_styles_dataframe: DataFrame containing layers
            with styles.
        output:
            DataFrame
        """
        # Merge layers with styles and GML layers
        merged_layers_with_styles = merge(
            layers_with_styles_dataframe, gml_layers_dataframe_grouped,
            how='outer', left_on=['LayerName', 'Geometry'],
            right_on=['Layer_Name', 'Geometry'])

        relevant_columns = ['Geometry', 'Format', 'Style_file_string',
                            'Layer_Name', 'StyleName', 'Root_Filename',
                            'GmlNode']
        filtered_dataset = merged_layers_with_styles[relevant_columns].copy()
        filtered_dataset.rename(columns={'Layer_Name': 'LayerName'},
                                inplace=True)
        return filtered_dataset

    @staticmethod
    def filter_layers_with_styles(theme_layers_dataframe):
        """
        Filter layers with styles.
        input:
            theme_layers_dataframe: DataFrame containing theme layers.
        output:
            DataFrame
        """
        # Filter layers without styles
        layers_with_styles = theme_layers_dataframe.loc[
            (theme_layers_dataframe['GmlNode'].notnull()) &
            (theme_layers_dataframe['StyleName'].notnull())]
        return layers_with_styles

    @staticmethod
    def save_layer_style_report(layers_with_styles):
        """
        Save a sorted report for layers with their associated styles.

        This function sorts the given DataFrame of layers and their styles
        by GML
        node, geometry type, and style name, then saves the sorted data as a
        CSV report.

        Args:
            layers_with_styles (DataFrame): A DataFrame containing layers with
            styles and all styles for the theme.
        """
        # Sort layers and styles before saving the report
        sorted_layers = layers_with_styles.sort_values(
                ['GmlNode', 'Geometry', 'StyleName'], inplace=False)
        report_saver = ReportSaver()
        report_saver.save_report_as_csv(sorted_layers)


class LayerStylesUpdater:
    def __init__(self, ui_helpers, layer_extractor):
        self.layer_extractor = layer_extractor
        self.ui_helpers = ui_helpers

    def update_styles(self, layer_styles_df):

        try:
            layers_count = len(layer_styles_df)
            progress_message_bar, progress_bar = (
                self.ui_helpers.show_progress_bar(
                    layers_count, "Updating styles for '{}' layers"
                    .format(layers_count))
            )
            current_step = 0

            # Iterate through each row in the layer_styles_df
            for _, style_rule in layer_styles_df.iterrows():
                # Get the layer name
                layer_name = style_rule['LayerName']

                # Update the progress bar and message
                progress_bar.setValue(current_step)
                current_step += 1
                progress_message_bar.setText(
                        "Oppdaterer tegneregler for lag '{0}' ({1}/{2})"
                        .format(layer_name, current_step, layers_count))
                log.info("Updating styles for layer '{0}' - Geometry: {1} "
                         " - ({2}/{3})"
                         .format(layer_name, style_rule['GmlNode'],
                                 current_step, layers_count))

                layers = self.layer_extractor.get_layers_by_name(
                    layer_name)

                if layers.__len__() > 0:
                    for layer in layers:
                        style_updated = self.apply_style_to_layer(layer,
                                                                  style_rule)
                        if style_updated:
                            layer.triggerRepaint()
                else:
                    log.error("Can't find the layer with name: '{}'"
                              .format(layer_name))
            # Finalize and close the progress message bar with a delay
            self.ui_helpers.close_progress_bar(progress_message_bar)
            return True
        except Exception as e:
            log.error("Failed to update layer styles: {0}".format(e))
            return False

    def apply_style_to_layer(self, layer, style_rule):
        """Update the layer style based on the given style rule."""
        style_updated = False

        if not hasattr(layer, 'geometryType'):
            log.debug("Layer '{0}' has no geometry type.".format(layer.name()))
            return style_updated

        layer_geometry_type = layer.geometryType().name

        if (layer_geometry_type and (style_rule['Geometry'].lower()
                                     != layer_geometry_type.lower())):
            return style_updated

        file_string = style_rule['Style_file_string']
        fd, path = mkstemp(suffix=style_rule['Format'])
        layer_name = style_rule['LayerName']
        style_name = style_rule['StyleName']
        try:
            with fdopen(fd, 'w') as tmp:
                tmp.write(file_string)
            if style_rule['Format'] == 'sld':
                updated = layer.loadSldStyle(path)
            elif style_rule['Format'] == 'qml':
                updated = layer.loadNamedStyle(path)

            layer.triggerRepaint()

            if updated:
                log.info(
                    "Update Successful: Layer '{0}' style '{1}' was updated."
                    .format(layer_name, style_name))
                style_updated = True
            else:
                log.debug(
                    "Update Failed: Could not update Layer '{0}' style '{1}'."
                    .format(layer_name, style_name))
        except Exception as e:
            log.error(
                "Update layer '{0}' style '{1}: {2}'.".format(
                    layer_name, style_name, e))
        finally:
            remove(path)
            return style_updated
