from ..util.logging_setup import logger as log
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from .tegneregelassistent_dialog_base import tegneregelassistent_dialog_base
from pandas import notna


class DialogHelpers:
    def __init__(self):
        self.dialog = tegneregelassistent_dialog_base()
        self.widget_columns_names = ["Lag", "Geometri", "Tegneregel"]

    def populate_treeWidget(self, grouped_layers):
        """
        Populate the QTreeWidget with the grouped layers.
        """

        # Clear the QTreeWidget before populating it
        self.dialog.gmlTreeWidget.clear()
        self.dialog.gmlTreeWidget.setHeaderLabels(self.widget_columns_names)

        # Iterate through each group and add to the tree widget
        for root_filename, group in grouped_layers:
            # Add the base filename as a top-level item
            root_filename_item = QTreeWidgetItem(self.dialog.gmlTreeWidget)
            root_filename_item.setText(0, root_filename)
            log.info(f'Base filename: {root_filename}')
            # Add the layers of the GML file as child items
            for _, layer in group.iterrows():
                layer_geometry = layer['Geometry']
                gml_node_geometry = (
                    f"{layer['Gml_Node']} - {layer['Geometry']}")
                log.info(f' * Layer name: {gml_node_geometry}')
                # Original layer name
                original_layer_name = (
                    f"{layer['Layer_Name']}")

                layer_item = QTreeWidgetItem(root_filename_item)
                layer_item.setText(0, original_layer_name)
                layer_item.setText(1, layer_geometry)
                layer_item.setFlags(layer_item.flags() |
                                    Qt.ItemIsUserCheckable)
                layer_item.setCheckState(0, Qt.Checked)
        # Hide the last column
        self.dialog.gmlTreeWidget.setColumnHidden(2, True)
        self.dialog.gmlTreeWidget.expandAll()
        self.dialog.gmlTreeWidget.resizeColumnToContents(0)
        self.dialog.raise_()
        self.dialog.activateWindow()

        if self.dialog.button_box:
            ok_button = self.dialog.button_box.button(
                self.dialog.button_box.Ok)
            if ok_button:
                ok_button.setText("Søk")

        self.dialog.show()
        return

    def populate_treeWidget_and_Styles(self, grouped_layers):
        """
        Populate the QTreeWidget with the grouped layers.
        """

        # Clear the QTreeWidget before populating it
        self.dialog.gmlTreeWidget.clear()
        self.dialog.gmlTreeWidget.setHeaderLabels(self.widget_columns_names)

        # Iterate through each group and add to the tree widget
        for root_filename, group in grouped_layers:
            # Add the base filename as a top-level item
            root_filename_item = QTreeWidgetItem(self.dialog.gmlTreeWidget)
            root_filename_item.setText(0, root_filename)
            # Add the layers of the GML file as child items
            for _, layer in group.iterrows():
                layer_geometry = layer['Geometry']
                # Original layer name
                original_layer_name = (
                    f"{layer['LayerName']}")
                style_name = str(layer['StyleName'])
                layer_item = QTreeWidgetItem(root_filename_item)
                layer_item.setText(0, original_layer_name)
                layer_item.setText(1, layer_geometry)
                if notna(style_name) and style_name != "nan":
                    layer_item.setCheckState(0, Qt.Checked)
                    layer_item.setText(2, str(style_name))
                    layer_item.setFlags(layer_item.flags() |
                                        Qt.ItemIsUserCheckable)
                else:
                    layer_item.setCheckState(0, Qt.Unchecked)
                    darker_gray = QColor(169, 169, 169)
                    layer_item.setForeground(0, darker_gray)
                    layer_item.setForeground(1, darker_gray)
                    layer_item.setText(2, "❌")
                    layer_item.setFlags(layer_item.flags()
                                        & ~Qt.ItemIsUserCheckable)

        self.dialog.gmlTreeWidget.setColumnHidden(2, False)
        self.dialog.gmlTreeWidget.expandAll()
        self.dialog.gmlTreeWidget.resizeColumnToContents(0)
        self.dialog.raise_()
        self.dialog.activateWindow()

        if self.dialog.button_box:
            ok_button = self.dialog.button_box.button(
                self.dialog.button_box.Ok)
            if ok_button:
                ok_button.setText("Bruk")

        self.dialog.show()
        return

    def bring_dialog_to_front(self):
        self.dialog.raise_()
        self.dialog.activateWindow()

    def is_dialog_accepted(self):
        """
        Get the result of the dialog execution.
        """

        result = self.dialog.exec_()
        # close the dialog if cancel
        if result == self.dialog.Rejected:
            self.dialog.close()
            return False

        if result == -1:
            return None

        # return if the dialog is not accepted
        if result != self.dialog.Accepted:
            return False

        return True

    def retrive_widget_checked_layers(self):
        """
        Get the names of the checked layers from the QTreeWidget.
        """
        checked_layers = []

        # Iterate over the top-level items (GML files)
        top_level_count = self.dialog.gmlTreeWidget.topLevelItemCount()
        for i in range(top_level_count):
            gml_file_item = self.dialog.gmlTreeWidget.topLevelItem(i)
            # Iterate over the child items (layers)
            child_count = gml_file_item.childCount()
            for j in range(child_count):
                layer_item = gml_file_item.child(j)
                if layer_item.checkState(0) == Qt.Checked:
                    checked_layers.append(
                        f'{layer_item.text(0)} - {layer_item.text(1)}')

        return checked_layers

    def clear_gmlTreeWidget(self):
        """
        Clear the gmlTreeWidget.
        """
        self.dialog.gmlTreeWidget.clear()

    def close_dialog(self):
        self.dialog.close()
        return
