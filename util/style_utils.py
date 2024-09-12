import re
from .api_call_manager import ApiCallManager as acm
from .logging_setup import logger as log
from pandas import DataFrame
from .config_loader import ConfigLoader
from .geonorge_apis import GeonorgeAPI


class LayerStylesUpdater:

    @staticmethod
    def get_styles_for_theme(theme):
        """Fetch and return styles for the specified theme."""
        log.info("=== Get styles for theme ===")
        geonorge_api = GeonorgeAPI()
        json_styles = geonorge_api.get_styles_for_theme(theme)

        if not json_styles:
            log.debug("No styles data retrieved from Geonorge for theme "
                      f"'{theme}'.")
            return DataFrame()
        stiles_file = json_styles.get('Files')
        if not stiles_file:
            log.error(f"Empty style data for theme '{theme}'. "
                      "Theme exists but has no styles.")
            return DataFrame()
        styles_df = DataFrame(stiles_file)

        columns = ['Uuid', 'Name', 'OwnerDataset', 'Format', 'DatasetName',
                   'Status', 'Theme', 'FileUrl', 'DetailsUrl']
        styles_df = styles_df[columns]
        styles_df.rename(columns={'Name': 'StyleName'}, inplace=True)
        log.info("Successfully retrieved styles for theme '{}'. ({}) "
                 "styles where found".format(theme, len(styles_df)))
        return styles_df

    @staticmethod
    def filter_styles_by_formats(theme_styles_df):
        """Filter styles by supported formats."""
        log.info("=== Filter styles by supported formats ===")
        supported_formats = ['sld', 'qml']
        styles_formats = theme_styles_df.get('Format')

        if styles_formats is None:
            log.error("No formats found for the theme.")
            return DataFrame()

        supported_formats_df = theme_styles_df[
            theme_styles_df['Format'].isin(supported_formats)]

        if supported_formats_df.empty:
            log.warning("No supported formats found for the theme.")
            return DataFrame()
        else:
            log.info("Found {} supported formats for the theme."
                     .format(len(supported_formats_df)))
        return supported_formats_df

    @staticmethod
    def apply_Gml_node_overrides(layers_df, theme):
        """Apply GML node overrides based on theme."""
        config_loader = ConfigLoader()
        resources = config_loader.load_resources_config()
        node_overrides = resources.get(
            'schemaNodeOverrides', {}).get(theme, [])

        if node_overrides:
            log.info("=== Applying GML node overrides ===")
            layers_df['mapped_style_name'] = layers_df['Gml_Node'].apply(
                lambda x:
                LayerStylesUpdater.override_gml_node_name(x, node_overrides))
        return layers_df

    @staticmethod
    def get_style_name(row, styles_df, style_format):

        """Determine the appropriate style name
           based on GML node and geometry."""
        gml_geometry_type = row['Geometry'].lower()
        gml_node_name = row['Gml_Node']
        mapped_style_name = row.get('mapped_style_name')
        name_to_find = None
        if mapped_style_name:
            name_to_find = mapped_style_name
        else:
            name_to_find = gml_node_name

        name_to_find = name_to_find.lower()

        style_names = [
            style['StyleName'] for _, style in styles_df.iterrows()
            if re.search(rf'(?i)(\b{name_to_find}\b)', style['StyleName'])
        ]

        style_count = len(style_names)

        style_name = None
        if style_count == 1:
            style_name = style_names[0]
        elif style_count > 1:
            style_names_fileter_by_geometry = (
                LayerStylesUpdater.filter_styles_by_geometry(
                    style_names, gml_geometry_type))

            if len(style_names_fileter_by_geometry) == 1:
                style_name = style_names_fileter_by_geometry[0]
            elif style_names_fileter_by_geometry:
                style_name = LayerStylesUpdater.filter_style_by_format(
                    style_names_fileter_by_geometry, styles_df, style_format)

        if style_name:
            log.info(
                "OK - '{0}' - ({1}) Style: '{2}'".format(name_to_find,
                                                         gml_geometry_type,
                                                         style_name))
        else:
            log.info("None - '{0}' - ({1}) Style: '{2}'"
                     .format(name_to_find, gml_geometry_type, style_name))
        return style_name

    @staticmethod
    def filter_styles_by_geometry(style_names, gml_geometry_type):
        """Filter styles based on geometry type and format."""
        appropriate_styles = []
        temp_styles = []
        for style_name in style_names:
            is_valid_style_for_geometry = (
                LayerStylesUpdater.is_appropriate_style_for_geometry(
                    style_name, gml_geometry_type))

            if is_valid_style_for_geometry:
                appropriate_styles.append(style_name)
                break

            if is_valid_style_for_geometry is None:
                temp_styles.append(style_name)
                continue

        if not appropriate_styles:
            appropriate_styles = temp_styles

        return appropriate_styles

    @staticmethod
    def add_file_string_to_row(row):
        """Fetch and return the file string from the file URL."""
        if row['Format'] in ['sld', 'qml']:
            api_call_new = acm()
            style_url = row['FileUrl']

            # Avoid 301 responses for https resources referenced with http
            style_url_with_https = style_url.replace('http://', 'https://')
            if style_url_with_https != style_url:
                log.warning(
                    'http:// was replaced with https:// for ' + style_url)

            api_call_new.get(style_url_with_https)
            xml_response = api_call_new.get_response_data()
            if xml_response:
                log.info(
                    "Successfully retrieved '{}' style for layer '{}'"
                    .format(row['Format'], row['LayerName']))
                xml_string = str(xml_response, 'utf-8')
                return xml_string
            else:
                log.error(
                    "Failed to retrieve the style for layer '{}'"
                    .format(row['LayerName']))
        return None

    @staticmethod
    def filter_style_by_format(style_names, styles_df, style_format):
        """Filter and return style names by the specified format."""
        df = (styles_df[styles_df['StyleName'].isin(style_names) &
                        (styles_df['Format'] == style_format)])
        return df['StyleName'].values[0] if not df.empty else None

    @staticmethod
    def override_gml_node_name(gml_node_name, node_overrides):
        """Override GML node name based on configuration."""
        for override in node_overrides:
            if (override['exactMatch'] and
                gml_node_name == override['sourceNode']) or (
                    not override['exactMatch'] and
                    override['sourceNode'] in gml_node_name):

                log.warning(
                    "GML node override applied: {0} -> {1}"
                    .format(gml_node_name, override['styleName']))
                return override['styleName']
        return None

    @staticmethod
    def is_appropriate_style_for_geometry(style_name, gml_geometry_type):
        """Check if a style is appropriate for a given geometry type."""
        gml_geometry_type = gml_geometry_type.lower()
        style_name = style_name.lower()

        # Define keyword lists for each geometry type
        polygon_list = ['område', 'sone']
        point_list = ['punkt']
        line_list = ['linje']

        if gml_geometry_type == 'point':
            exclude_list = polygon_list + line_list
            return LayerStylesUpdater.check_style_appropriateness(
                style_name, point_list, exclude_list)

        elif gml_geometry_type == 'polygon':
            exclude_list = point_list + line_list
            return LayerStylesUpdater.check_style_appropriateness(
                style_name, polygon_list, exclude_list)

        elif gml_geometry_type == 'line':
            exclude_list = point_list
            return LayerStylesUpdater.check_style_appropriateness(
                style_name, line_list, exclude_list)

        return None

    @staticmethod
    def check_style_appropriateness(style_name, include_list, exclude_list):
        """Check if a style name is appropriate based on
        include and exclude lists."""
        is_included = any(keyword in style_name for keyword in include_list)
        is_excluded = any(keyword in style_name for keyword in exclude_list)

        if is_included and not is_excluded:
            return True
        elif is_excluded:
            return False
        return None
