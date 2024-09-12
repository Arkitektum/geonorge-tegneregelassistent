from .util.logging_setup import logger as log
from os.path import dirname
from qgis.PyQt.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from .ui.ui_helpers import UIHelpers
from .ui.dialog_helpers import DialogHelpers
from .util.layers_utils import LayersUtils as lu
from .util.layers_utils import LayerStylesUpdater
from .util.layer_extractor import LayerExtractor
from .util.report_saver import ReportSaver
from .util.gml_processor import GMLProcessor
from pandas import DataFrame


class GeonorgeTegneregelassistent:

    def __init__(self, iface):
        """
        Initializes the plugin.

        Args:
            iface (QgisInterface): The QGIS interface object.
        """
        self.iface = iface
        self.plugin_dir = dirname(__file__)

        self.actions = []
        self.first_start = None
        self.ui_helpers = None
        self.report = None
        self.layer_extractor = None
        self.gml_layers_df_and_styles = None

    def add_actions(self):
        """
        Adds actions to QGIS toolbar and menu.
        """
        icon_path = self.plugin_dir + '/icon.png'
        icon = QIcon(icon_path)
        action = QAction(icon, 'Geonorge tegneregelassistent',
                         self.iface.mainWindow())
        action.triggered.connect(self.run)

        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu('&Geonorge', action)
        self.actions.append(action)
        return action

    def initGui(self):
        """
        Initializes the plugin GUI components.
        """
        self.add_actions()
        self.first_start = True

    def unload(self):
        """
        Unloads the plugin from QGIS.
        """
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
            self.iface.removePluginMenu('&Geonorge', action)

    def run(self):
        """
        Executes the main functionality of the plugin.
        """
        if self.first_start:
            self.first_start = False
            self.selected_layers_and_styles = None
            self.gml_layers_df = None
            self.dlg = DialogHelpers()
            self.ui_helpers = UIHelpers(self.iface)
            self.report = ReportSaver()
            self.layer_extractor = LayerExtractor(self.iface)
            log.info("=== Geonorge tegeregelassistent plugin started ===")
        else:
            # Check if the active layers are changed
            active_layers = self.iface.mapCanvas().layers()
            if (active_layers != self.layer_extractor.visible_layers):
                self.ui_helpers.message_bar_critial(
                    "Aktive lag er endret. Tegneregler ble ikke implementert. "
                    "Åpne plugin-en på nytt.")
                log.info("Active layers are changed. Plugin is reset.")
                self.reset_plugin()
                return
            self.dlg.bring_dialog_to_front()

        layer_styles_df = DataFrame()

        if self.gml_layers_df is None:
            # Get the GML layers from the project
            log.info('=== GML Layers ===')
            # self.layer_extractor = LayerExtractor(self.iface)
            self.layer_extractor.get_gml_layer_dataFrame()

            # Check if there are GML layers in the project
            if (self.layer_extractor.gml_layer_dataFrame is None):
                self.ui_helpers.message_bar_warning(
                    "Ingen GML-lag med geometry funnet i prosjektet."
                    "Vennligst legg til et GML-lag og prøv igjen.")
                log.error("No GML layers found in the project.")
                self.reset_plugin()
                return

            # Group the layers by base filenames
            grouped_layers = lu.group_layers_by_column_name(
                self.layer_extractor.gml_layer_dataFrame)

            # Populate the tree widget with the grouped layers
            self.dlg.populate_treeWidget(grouped_layers)

            # get the result of the dialog
            result = self.dlg.is_dialog_accepted()

            # close the dialog if cancel
            if not result:
                if result is None:
                    return
                log.info("User canceled the operation.")
                self.reset_plugin()
                return

            self.gml_layers_df = self.layer_extractor.gml_layer_dataFrame

            # Get the checked layers
            checked_layers = self.dlg.retrive_widget_checked_layers()
            gml_layers_dataFrame_group = (self.layer_extractor
                                          .get_group_of_selected_layers(
                                            checked_layers))

            gml_processor = GMLProcessor(self.ui_helpers)

            layer_styles_df = (
                gml_processor.process_gml_files(gml_layers_dataFrame_group))

            self.selected_layers_and_styles = layer_styles_df

        if self.selected_layers_and_styles.empty:
            self.ui_helpers.message_bar_info(
                "Ingen tegneregler funnet for de valgte lagene.")
            log.info("No styles found for the selected layers.")
            self.reset_plugin()
            return

        if self.gml_layers_df_and_styles is None or self.gml_layers_df.empty:
            gml_layers_df_and_styles = (
                lu.merge_layers_with_styles_and_gml_layers(
                    self.gml_layers_df, self.selected_layers_and_styles))
            self.gml_layers_df_and_styles = gml_layers_df_and_styles

            group_layers = lu.group_layers_by_column_name(
                self.gml_layers_df_and_styles)
            self.dlg.populate_treeWidget_and_Styles(group_layers)

        result = self.dlg.is_dialog_accepted()

        if not result:
            if result is None:
                return
            log.info("User canceled the operation.")
            self.reset_plugin()
            return

        # Check if the active layers are changed
        active_layers = self.iface.mapCanvas().layers()
        if (active_layers != self.layer_extractor.visible_layers):
            self.ui_helpers.message_bar_critial(
                "Aktive lag er endret. Tegneregler ble ikke implementert. "
                "Åpne plugin-en på nytt.")
            log.info("Active layers are changed. Plugin is reset.")
            self.reset_plugin()
            return

        # Get the user selection of layers to implement styles for
        selected_layers = self.dlg.retrive_widget_checked_layers()

        selected_layers_dataFrame = (
            self.layer_extractor.filter_selected_layers(
                selected_layers, self.selected_layers_and_styles, 'LayerName'))

        # Implement styles for the user selected layers
        layer_style_updater = LayerStylesUpdater(self.ui_helpers,
                                                 self.layer_extractor)
        update_ok = layer_style_updater.update_styles(
            selected_layers_dataFrame)

        if update_ok:
            # Show the final message
            self.ui_helpers.message_bar_success(
                "Tegnereglene er oppdatert for de valgte lagene.")
            log.info("The styles are updated for the selected layers.")
        else:
            self.ui_helpers.message_bar_critial(
                "Kunne ikke oppdatere tegnereglene for de valgte lagene.")
            log.error("Could not update the styles for the selected layers.")

        self.reset_plugin()
        log.info("=== Geonorge tegneregelassistent plugin finished ===")

    def clear_layers(self):
        """
        Resets the plugin.
        """
        self.selected_layers_and_styles = None
        self.gml_layers_df = None
        self.gml_layers_df_and_styles = None
        return

    def reset_plugin(self):
        """
        Resets the plugin.
        """
        self.clear_layers()
        self.dlg.clear_gmlTreeWidget()
        self.first_start = True
        self.dlg.close_dialog()
        log.info("Plugin is reset.")
        return
