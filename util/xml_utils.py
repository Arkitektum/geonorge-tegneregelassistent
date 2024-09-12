import pandas as pd
from xml.etree.ElementTree import parse
from .logging_setup import logger as log


def get_gml_schemalocations(xml_path):
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
        schema_df = pd.DataFrame(schema_dict.items(),
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
