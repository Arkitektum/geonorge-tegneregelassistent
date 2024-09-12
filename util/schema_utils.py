import pandas as pd
from .logging_setup import logger as log
from .config_loader import ConfigLoader
from .geonorge_apis import GeonorgeAPI
from uuid import UUID


class SchemaUtils:
    def __init__(self):
        config_loader = ConfigLoader()
        self.config = config_loader.load_resources_config()
        self.geonorge_schemas = None

    def get_schema_whitelist(self):
        """
        Returns a DataFrame of whitelisted schemas.

        :return: DataFrame containing whitelisted schemas.
        :rtype: pd.DataFrame
        """
        log.info("=== Using whitelist schemas ===")
        # Get the whitelisted schemas from the config
        schemas = self.config['schemas']

        if not schemas:
            log.debug("No schemas found in the config file.")
            return None

        # Convert the list of schemas to a DataFrame
        schema_df = pd.DataFrame(schemas)
        log.info(f"Schema whitelist applied, {len(schema_df)} schemas added.")

        return schema_df

    def fetch_geonorge_schemas(self):
        """
        Fetches schemas from Geonorge and optionally appends whitelist schemas.

        :param use_whitelist: Whether to use whitelist schemas.
        :type use_whitelist: bool
        :return: DataFrame containing combined schemas.
        :rtype: pd.DataFrame
        """
        if self.geonorge_schemas is None:
            log.info("=== Fetching schemas from Geonorge ===")

            # Fetch schemas from Geonorge
            geonorge_api = GeonorgeAPI()
            json_schemas = geonorge_api.get_schemas()

            if json_schemas is None:
                return None

            # Extract the list of schema items
            schema_items = json_schemas.get('containeditems', [])
            schema_df = pd.DataFrame(schema_items)

            # Filter the schema DataFrame to keep specific columns
            columns_to_keep = ['id', 'documentreference', 'status', 'label',
                               'seoname', 'DatasetUuid']
            schema_df_filtered = schema_df[columns_to_keep].copy()

            log.info("Have been acquired: '{}' gml schemas from geonorge"
                     .format(len(schema_df_filtered)))

            whitelist_schemas = self.get_schema_whitelist()
            if whitelist_schemas is not None:
                if schema_df_filtered is None:
                    schema_df_filtered = whitelist_schemas
                else:
                    schema_df_filtered = pd.concat(
                        [schema_df_filtered, whitelist_schemas],
                        ignore_index=True, sort=False)

            if schema_df_filtered is None:
                log.error("Failed to retrieve or generate any schemas.")
                return None

            self.geonorge_schemas = schema_df_filtered

        return self.geonorge_schemas

    def find_geonorge_schema_identifier(self, schema_locations):
        """
        Find and process the schema identifier from Geonorge
        for the given GML schemas.

        This method iterates through a list of schema locations,
        retrieves matching schemas from Geonorge, and processes them
        to extract the relevant schema identifier. If multiple schemas
        are found, it handles the case appropriately. The method also
        applies schema overrides if they are specified in the configuration.

        Args:
            schema_locations (list): List of schema locations to check.

        Returns:
            str: The relevant schema identifier if found, otherwise None.
        """
        # Fetch schemas from Geonorge
        geonorge_schemas = self.fetch_geonorge_schemas()

        matching_schemas = []

        # Iterate through schema locations to find matches
        for _, schema_location_row in schema_locations.iterrows():
            schema_location = schema_location_row['schemalocation']
            matching_schema = geonorge_schemas[
                geonorge_schemas['documentreference'].str.lower() ==
                schema_location.lower()
            ]

            if matching_schema.empty:
                schema_location_with_https_trimmed = schema_location.split(
                    '://', 1)[-1]
                matching_schema = geonorge_schemas[
                    geonorge_schemas['documentreference'].str.lower().str.endswith(
                        schema_location_with_https_trimmed.lower())
                ]
                if not matching_schema.empty:
                    log.warning(
                        "The http:// or https:// prefixes " +
                        "were ignored during the matching process " +
                        "with the Geonorge schema:{0}.".format(schema_location)
                        )

            if matching_schema.empty:
                log.warning(
                    f'Schema not found in Geonorge register: {schema_location}'
                    )
            else:
                log.info(
                    'Schema found in Geonorge register: {0} - Label: {1}'
                    .format(matching_schema['documentreference'].values[0],
                            matching_schema['label']
                            .values[0]))
                matching_schemas.append(matching_schema)

        # Check if any schemas were found
        if not matching_schemas:
            return

        # Handle case with multiple schemas found
        if len(matching_schemas) > 1:
            log.debug(
                'Multiple schemas found in Geonorge for the GML file.')
            return

        matching_schema = matching_schemas[0]
        schema_identifier = matching_schema['DatasetUuid'].values[0]

        if schema_identifier and self.is_guid(schema_identifier):
            log.info(f"DatasetUuid for Schema: {schema_identifier}")
        else:
            schema_identifier = matching_schema['label'].values[0]
            log.info("No DatasetUuid for Schema, label is used instead: {}"
                     .format(schema_identifier))

        # Apply schema overrides if any
        schema_overrides = self.config.get('schemaOverrides', [])
        if schema_overrides:
            schema_identifier = self.override_schema_identifier(
                schema_identifier, schema_overrides)
        if not schema_identifier:
            log.error("No schema identifier found for GML file {}"
                      .format(schema_location))
        return schema_identifier

    def override_schema_identifier(self, schema_label, schema_overrides):
        log.info("=== Applying schema overrides ===")
        for override in schema_overrides:
            new_schema_label = None
            if override['exactMatch']:
                if schema_label == override['sourceLabel']:
                    new_schema_label = override['targetLabel']
            else:
                if override['sourceLabel'] in schema_label:
                    new_schema_label = override['targetLabel']

            if new_schema_label:
                log.warning("Schema override applied: {0} -> {1}"
                            .format(schema_label, new_schema_label))
                return new_schema_label
        log.info("No schema override applied")
        return schema_label

    def is_guid(self, value):
        try:
            UUID(str(value))
            return True
        except ValueError:
            return False
