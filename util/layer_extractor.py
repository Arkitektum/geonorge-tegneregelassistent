from .logging_setup import logger as log
from ..ui.ui_helpers import UIHelpers
from re import findall
from os.path import splitext, basename
from pandas import DataFrame

from .layers_utils import LayersUtils as lu


class LayerExtractor:
    def __init__(self, iface):
        self.visible_layers = iface.mapCanvas().layers()
        self.ui_helpers = UIHelpers(iface=iface)
        self.gml_layer_dataFrame = None

    def get_layers_by_name(self, layer_name):
        """
        Get the layer by name from the QGIS project instance.
        input:
            layer_name: str
        output:
            QgsVectorLayer
        """
        layers = []
        for layer in self.visible_layers:
            if layer.name() == layer_name:
                layers.append(layer)
        return layers

    def get_gml_layer_details(self, layer):
        """
        Get the details of the GML layer.
        input:
            layer: QgsVectorLayer
        output:
            dict: {
                'Gml_Node': str, # GML node name
                'Geometry': str, # Geometry type of the layer
                'FileType': str, # File extension type
                'Layer_Name': str, # Original layer name
                'File_Path': str, # File path to the layer
                'Root_Filename': str, # Base file name of the GML file
            }
        """
        # Retrieve the data source URI and layer name
        source = layer.dataProvider().dataSourceUri()
        if ".gml" not in source.lower():
            return None
        
        geometry_type = None
        root_filename = None
        gml_node_name = None
        file_type = None

        # Extract the GML node name, file path, and root filename
        layer_name = layer.name()
        file_path = source
        if '|' in source.lower():
            source_list = source.split('|')
            file_path = source_list[0]
            gml_node_name = findall(r'layername=(\w+)', source)[0]
            root_filename = splitext(basename(file_path))[0]
            gml_node_name = gml_node_name.strip()

        # Check if the layer has a geometry type attribute
        # and retrieve its name
        if hasattr(layer, 'geometryType'):
            geometry_type = layer.geometryType().name

        # Determine the file type by extracting the file extension
        file_type = splitext(file_path)[-1]

        return {
            'Gml_Node': gml_node_name,
            'Geometry': geometry_type,
            'FileType': file_type,
            'Layer_Name': layer_name,
            'File_Path': file_path,
            'Root_Filename': root_filename,
        }

    def get_gml_layer_dataFrame(self):
        """
        Extract GML layers from the QGIS project instance and return them as a
        pandas DataFrame.
        """
        gml_layers_details = []
        for layer in self.visible_layers:
            layer_details = self.get_gml_layer_details(layer)
            if layer_details is not None:
                gml_layers_details.append(layer_details)

        # Continue only if there are any GML layers in the project
        if gml_layers_details.__len__() == 0:
            return None

        layers_dataframe = DataFrame(gml_layers_details)
        layers_dataframe = layers_dataframe.iloc[::-1]

        # Exclude GML layers without geometry type
        gml_layers_df = layers_dataframe[
            (layers_dataframe['FileType'] == '.gml') &
            (layers_dataframe['Geometry'].str.lower() != "null")
        ]
        self.gml_layer_dataFrame = gml_layers_df
        return gml_layers_df

    def get_group_of_selected_layers(self, selected_layers):
        """
        Get the dataFrame group of selected layers from the QTreeWidget.
        """
        gml_selected_layers = self.filter_selected_layers(
            selected_layers, self.gml_layer_dataFrame)

        # Log the number of checked layers
        log.info('Checked layers: {}/{} - [{}]'.format(
            len(gml_selected_layers), len(self.gml_layer_dataFrame),
            ', '.join(gml_selected_layers['Layer_Name'])))

        gml_selected_layers_grouped = lu.group_layers_by_column_name(
            gml_selected_layers)

        return gml_selected_layers_grouped

    @staticmethod
    def filter_selected_layers(selected_layers, dataFrame,
                               layer_name='Layer_Name',
                               geometry='Geometry'):

        # Split the strings to get layerName and Geometry
        filter_tuples = [tuple(item.split(' - ')) for item in selected_layers]

        # Ensure the dataframe has the required columns
        if ((layer_name not in dataFrame.columns) or (geometry not in
                                                      dataFrame.columns)):
            log.error(
                "DataFrame must contain columns '{0}' and '{1}'"
                .format(layer_name, geometry))
            raise ValueError(
                "DataFrame must contain columns '{0}' and '{1}'"
                .format(layer_name, geometry))

        # Create a set of tuples to filter the dataFrame
        filter_set = set(filter_tuples)

        # Perform the filtering using a boolean mask
        filtered_layers = dataFrame[dataFrame.apply(
            lambda row: (row[layer_name], row[geometry]) in
            filter_set, axis=1)]

        return filtered_layers
