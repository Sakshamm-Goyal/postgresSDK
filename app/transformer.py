"""
This file contains the transformer for the PostgreSQL metadata extraction application.
The transformer is responsible for transforming the raw metadata into the Atlan Type.

Enhanced with:
- PostgreSQL-specific entity transformations
- Foreign key lineage support
- Data quality metrics integration
- Advanced business context mapping

Read More: ./models/README.md
"""

from typing import Any, Dict, Optional, Type

from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.transformers.atlas import AtlasTransformer
from application_sdk.transformers.common.utils import build_atlas_qualified_name

logger = get_logger(__name__)


class PostgreSQLDatabase:
    """Represents a PostgreSQL database entity in Atlan.

    This class handles the transformation of PostgreSQL database metadata into Atlan entity format.
    Enhanced with size information, connection metrics, and business context.
    """

    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Transform PostgreSQL database metadata into Atlan entity attributes.

        Args:
            obj: Dictionary containing the raw PostgreSQL database metadata.

        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes and custom attributes.
        """
        attributes = {
            "name": obj.get("database_name", ""),
            "qualifiedName": build_atlas_qualified_name(
                obj.get("connection_qualified_name", ""), obj.get("database_name", "")
            ),
            "connectionQualifiedName": obj.get("connection_qualified_name", ""),
        }
        
        custom_attributes = {
            "database_size": obj.get("database_size", ""),
            "collation": obj.get("collation", ""),
            "character_type": obj.get("character_type", ""),
            "connection_limit": obj.get("connection_limit_display", ""),
            "allows_connections": obj.get("allows_connections", True),
            "is_template": obj.get("is_template", False),
            "size_bytes": obj.get("size_bytes", 0),
            "active_connections": obj.get("active_connections", 0),
        }
        
        return {
            "attributes": attributes,
            "custom_attributes": custom_attributes,
        }


class PostgreSQLSchema:
    """Represents a PostgreSQL schema entity in Atlan.

    This class handles the transformation of PostgreSQL schema metadata into Atlan entity format.
    Enhanced with object counts, function information, and business context.
    """

    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Transform PostgreSQL schema metadata into Atlan entity attributes.

        Args:
            obj: Dictionary containing the raw PostgreSQL schema metadata.

        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes and custom attributes.
        """
        attributes = {
            "name": obj.get("schema_name", ""),
            "qualifiedName": build_atlas_qualified_name(
                obj.get("connection_qualified_name", ""),
                obj.get("default_character_set_catalog", ""),
                obj.get("schema_name", ""),
            ),
            "connectionQualifiedName": obj.get("connection_qualified_name", ""),
            "databaseName": obj.get("default_character_set_catalog", ""),
            "tableCount": obj.get("table_count", 0),
            "viewCount": obj.get("view_count", 0),
        }
        
        custom_attributes = {
            "schema_owner": obj.get("schema_owner", ""),
            "default_character_set_name": obj.get("default_character_set_name", ""),
            "sql_path": obj.get("sql_path", ""),
            "materialized_view_count": obj.get("materialized_view_count", 0),
            "foreign_table_count": obj.get("foreign_table_count", 0),
            "total_objects": obj.get("total_objects", 0),
            "function_count": obj.get("function_count", 0),
            "aggregate_count": obj.get("aggregate_count", 0),
            "window_count": obj.get("window_count", 0),
            "procedure_count": obj.get("procedure_count", 0),
            "description": obj.get("description", ""),
            "schema_qualified_name": obj.get("schema_qualified_name", ""),
        }
        
        return {
            "attributes": attributes,
            "custom_attributes": custom_attributes,
        }


class PostgreSQLTable:
    """Represents a PostgreSQL table entity in Atlan.

    This class handles the transformation of PostgreSQL table metadata into Atlan entity format.
    Enhanced with comprehensive statistics, constraints, and data quality metrics.
    """

    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Transform PostgreSQL table metadata into Atlan entity attributes.

        Args:
            obj: Dictionary containing the raw PostgreSQL table metadata.

        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes and custom attributes.
        """
        attributes = {
            "name": obj.get("table_name", ""),
            "schemaName": obj.get("table_schema", ""),
            "databaseName": obj.get("table_catalog", ""),
            "qualifiedName": build_atlas_qualified_name(
                obj.get("connection_qualified_name", ""),
                obj.get("table_catalog", ""),
                obj.get("table_schema", ""),
                obj.get("table_name", ""),
            ),
            "connectionQualifiedName": obj.get("connection_qualified_name", ""),
        }
        
        custom_attributes = {
            "table_type": obj.get("table_type", ""),
            "estimated_row_count": obj.get("estimated_row_count", 0),
            "dead_row_count": obj.get("dead_row_count", 0),
            "total_inserts": obj.get("total_inserts", 0),
            "total_updates": obj.get("total_updates", 0),
            "total_deletes": obj.get("total_deletes", 0),
            "last_vacuum": obj.get("last_vacuum", ""),
            "last_analyze": obj.get("last_analyze", ""),
            "vacuum_count": obj.get("vacuum_count", 0),
            "analyze_count": obj.get("analyze_count", 0),
            "total_size": obj.get("total_size", ""),
            "total_size_bytes": obj.get("total_size_bytes", 0),
            "table_size": obj.get("table_size", ""),
            "table_size_bytes": obj.get("table_size_bytes", 0),
            "indexes_size": obj.get("indexes_size", ""),
            "indexes_size_bytes": obj.get("indexes_size_bytes", 0),
            "constraint_count": obj.get("constraint_count", 0),
            "primary_key_count": obj.get("primary_key_count", 0),
            "foreign_key_count": obj.get("foreign_key_count", 0),
            "unique_constraint_count": obj.get("unique_constraint_count", 0),
            "check_constraint_count": obj.get("check_constraint_count", 0),
            "index_count": obj.get("index_count", 0),
            "unique_index_count": obj.get("unique_index_count", 0),
            "primary_index_count": obj.get("primary_index_count", 0),
            "description": obj.get("description", ""),
            "is_partitioned": obj.get("is_partitioned", False),
            "partition_strategy": obj.get("partition_strategy", ""),
            "partition_column_count": obj.get("partition_column_count", 0),
        }
        
        return {
            "attributes": attributes,
            "custom_attributes": custom_attributes,
        }


class PostgreSQLColumn:
    """Represents a PostgreSQL column entity in Atlan.

    This class handles the transformation of PostgreSQL column metadata into Atlan entity format.
    Enhanced with comprehensive data type information, constraints, and data quality metrics.
    """

    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Transform PostgreSQL column metadata into Atlan entity attributes.

        Args:
            obj: Dictionary containing the raw PostgreSQL column metadata.

        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes and custom attributes.
        """
        attributes = {
            "name": obj.get("column_name", ""),
            "qualifiedName": build_atlas_qualified_name(
                obj.get("connection_qualified_name", ""),
                obj.get("table_catalog", ""),
                obj.get("table_schema", ""),
                obj.get("table_name", ""),
                obj.get("column_name", ""),
            ),
            "connectionQualifiedName": obj.get("connection_qualified_name", ""),
            "tableName": obj.get("table_name", ""),
            "schemaName": obj.get("table_schema", ""),
            "databaseName": obj.get("table_catalog", ""),
            "isNullable": obj.get("is_nullable", "NO") == "YES",
            "dataType": obj.get("data_type", ""),
            "order": obj.get("ordinal_position", 1),
        }

        custom_attributes = {
            "column_default": obj.get("column_default", ""),
            "character_maximum_length": obj.get("character_maximum_length", 0),
            "character_octet_length": obj.get("character_octet_length", 0),
            "numeric_precision": obj.get("numeric_precision", 0),
            "numeric_precision_radix": obj.get("numeric_precision_radix", 0),
            "numeric_scale": obj.get("numeric_scale", 0),
            "datetime_precision": obj.get("datetime_precision", 0),
            "interval_type": obj.get("interval_type", ""),
            "interval_precision": obj.get("interval_precision", 0),
            "character_set_name": obj.get("character_set_name", ""),
            "collation_name": obj.get("collation_name", ""),
            "domain_name": obj.get("domain_name", ""),
            "udt_name": obj.get("udt_name", ""),
            "is_identity": obj.get("is_identity", "NO") == "YES",
            "identity_generation": obj.get("identity_generation", ""),
            "identity_start": obj.get("identity_start", 0),
            "identity_increment": obj.get("identity_increment", 0),
            "identity_maximum": obj.get("identity_maximum", 0),
            "identity_minimum": obj.get("identity_minimum", 0),
            "identity_cycle": obj.get("identity_cycle", "NO") == "YES",
            "is_generated": obj.get("is_generated", "NO") == "YES",
            "generation_expression": obj.get("generation_expression", ""),
            "is_updatable": obj.get("is_updatable", "NO") == "YES",
            # Data quality metrics
            "distinct_value_count": obj.get("distinct_value_count", 0),
            "estimated_distinct_values": obj.get("estimated_distinct_values", 0),
            "null_fraction": obj.get("null_fraction", 0),
            "average_width": obj.get("average_width", 0),
            "correlation": obj.get("correlation", 0),
            "most_common_values": obj.get("most_common_values", []),
            "most_common_frequencies": obj.get("most_common_frequencies", []),
            "histogram_bounds": obj.get("histogram_bounds", []),
            # Constraint information
            "constraint_name": obj.get("constraint_name", ""),
            "constraint_type": obj.get("constraint_type", ""),
            "foreign_table_schema": obj.get("foreign_table_schema", ""),
            "foreign_table_name": obj.get("foreign_table_name", ""),
            "foreign_column_name": obj.get("foreign_column_name", ""),
            "foreign_key_update_rule": obj.get("foreign_key_update_rule", ""),
            "foreign_key_delete_rule": obj.get("foreign_key_delete_rule", ""),
            # Index information
            "index_count": obj.get("index_count", 0),
            "unique_index_count": obj.get("unique_index_count", 0),
            "primary_index_count": obj.get("primary_index_count", 0),
            "index_names": obj.get("index_names", ""),
            # Sequence information
            "sequence_name": obj.get("sequence_name", ""),
            "sequence_last_value": obj.get("sequence_last_value", 0),
            "sequence_start_value": obj.get("sequence_start_value", 0),
            "sequence_increment": obj.get("sequence_increment", 0),
            "sequence_max_value": obj.get("sequence_max_value", 0),
            "sequence_min_value": obj.get("sequence_min_value", 0),
            "sequence_is_cycled": obj.get("sequence_is_cycled", False),
            # Business context
            "description": obj.get("description", ""),
            "full_data_type": obj.get("full_data_type", ""),
            "auto_increment_type": obj.get("auto_increment_type", "NONE"),
        }

        return {
            "attributes": attributes,
            "custom_attributes": custom_attributes,
        }


class PostgreSQLForeignKey:
    """Represents a PostgreSQL foreign key relationship entity in Atlan.

    This class handles the transformation of foreign key metadata into Atlan entity format.
    Enhanced with lineage information and relationship metadata.
    """

    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Transform PostgreSQL foreign key metadata into Atlan entity attributes.

        Args:
            obj: Dictionary containing the raw PostgreSQL foreign key metadata.

        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes and custom attributes.
        """
        attributes = {
            "name": obj.get("constraint_name", ""),
            "qualifiedName": build_atlas_qualified_name(
                obj.get("connection_qualified_name", ""),
                obj.get("source_schema", ""),
                obj.get("source_table", ""),
                obj.get("source_column", ""),
                obj.get("constraint_name", ""),
            ),
            "connectionQualifiedName": obj.get("connection_qualified_name", ""),
            "sourceQualifiedName": obj.get("source_qualified_name", ""),
            "targetQualifiedName": obj.get("target_qualified_name", ""),
        }
        
        custom_attributes = {
            "source_schema": obj.get("source_schema", ""),
            "source_table": obj.get("source_table", ""),
            "source_column": obj.get("source_column", ""),
            "target_schema": obj.get("target_schema", ""),
            "target_table": obj.get("target_table", ""),
            "target_column": obj.get("target_column", ""),
            "constraint_name": obj.get("constraint_name", ""),
            "update_rule": obj.get("update_rule", ""),
            "delete_rule": obj.get("delete_rule", ""),
            "is_deferrable": obj.get("is_deferrable", False),
            "initially_deferred": obj.get("initially_deferred", False),
            "constraint_definition": obj.get("constraint_definition", ""),
            "is_validated": obj.get("is_validated", True),
            "is_no_inherit": obj.get("is_no_inherit", False),
            "source_description": obj.get("source_description", ""),
            "target_description": obj.get("target_description", ""),
            "constraint_description": obj.get("constraint_description", ""),
            "update_action": obj.get("update_action", ""),
            "delete_action": obj.get("delete_action", ""),
            "relationship_strength": obj.get("relationship_strength", ""),
        }
        
        return {
            "attributes": attributes,
            "custom_attributes": custom_attributes,
        }


class PostgreSQLDataQuality:
    """Represents a PostgreSQL data quality metrics entity in Atlan.

    This class handles the transformation of data quality metrics into Atlan entity format.
    Enhanced with comprehensive quality analysis and profiling information.
    """

    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """Transform PostgreSQL data quality metrics into Atlan entity attributes.

        Args:
            obj: Dictionary containing the raw PostgreSQL data quality metrics.

        Returns:
            Dict[str, Any]: Dictionary containing the transformed attributes and custom attributes.
        """
        attributes = {
            "name": f"{obj.get('schemaname', '')}.{obj.get('tablename', '')}_quality",
            "qualifiedName": build_atlas_qualified_name(
                obj.get("connection_qualified_name", ""),
                obj.get("schemaname", ""),
                obj.get("tablename", ""),
                "data_quality",
            ),
            "connectionQualifiedName": obj.get("connection_qualified_name", ""),
            "schemaName": obj.get("schemaname", ""),
            "tableName": obj.get("tablename", ""),
        }
        
        custom_attributes = {
            "live_tuples": obj.get("live_tuples", 0),
            "dead_tuples": obj.get("dead_tuples", 0),
            "total_inserts": obj.get("total_inserts", 0),
            "total_updates": obj.get("total_updates", 0),
            "total_deletes": obj.get("total_deletes", 0),
            "last_vacuum": obj.get("last_vacuum", ""),
            "last_autovacuum": obj.get("last_autovacuum", ""),
            "last_analyze": obj.get("last_analyze", ""),
            "last_autoanalyze": obj.get("last_autoanalyze", ""),
            "vacuum_count": obj.get("vacuum_count", 0),
            "autovacuum_count": obj.get("autovacuum_count", 0),
            "analyze_count": obj.get("analyze_count", 0),
            "autoanalyze_count": obj.get("autoanalyze_count", 0),
            "hours_since_last_analyze": obj.get("hours_since_last_analyze", 0),
            "hours_since_last_vacuum": obj.get("hours_since_last_vacuum", 0),
            "change_ratio": obj.get("change_ratio", 0),
            "dead_tuple_status": obj.get("dead_tuple_status", ""),
            "total_size_bytes": obj.get("total_size_bytes", 0),
            "table_size_bytes": obj.get("table_size_bytes", 0),
            "indexes_size_bytes": obj.get("indexes_size_bytes", 0),
            "toast_size_bytes": obj.get("toast_size_bytes", 0),
            "total_columns": obj.get("total_columns", 0),
            "high_null_columns": obj.get("high_null_columns", 0),
            "medium_null_columns": obj.get("medium_null_columns", 0),
            "low_null_columns": obj.get("low_null_columns", 0),
            "no_null_columns": obj.get("no_null_columns", 0),
            "constant_columns": obj.get("constant_columns", 0),
            "low_cardinality_columns": obj.get("low_cardinality_columns", 0),
            "medium_cardinality_columns": obj.get("medium_cardinality_columns", 0),
            "high_cardinality_columns": obj.get("high_cardinality_columns", 0),
            "quality_score": obj.get("quality_score", 0),
            "freshness_score": obj.get("freshness_score", 0),
        }

        return {
            "attributes": attributes,
            "custom_attributes": custom_attributes,
        }


class PostgreSQLAtlasTransformer(AtlasTransformer):
    def __init__(self, connector_name: str, tenant_id: str, **kwargs: Any):
        super().__init__(connector_name, tenant_id, **kwargs)

        # PostgreSQL entity definitions
        self.entity_class_definitions["DATABASE"] = PostgreSQLDatabase
        self.entity_class_definitions["SCHEMA"] = PostgreSQLSchema
        self.entity_class_definitions["TABLE"] = PostgreSQLTable
        self.entity_class_definitions["COLUMN"] = PostgreSQLColumn
        self.entity_class_definitions["FOREIGN_KEY"] = PostgreSQLForeignKey
        self.entity_class_definitions["DATA_QUALITY"] = PostgreSQLDataQuality

    def transform_row(
        self,
        typename: str,
        data: Dict[str, Any],
        workflow_id: str,
        workflow_run_id: str,
        entity_class_definitions: Dict[str, Type[Any]] | None = None,
        **kwargs: Any,
    ) -> Optional[Dict[str, Any]]:
        """Transform metadata into an Atlas entity.

        This method transforms the provided metadata into an Atlas entity based on
        the specified type. It also enriches the entity with workflow metadata.

        Args:
            typename (str): Type of the entity to create.
            data (Dict[str, Any]): Metadata to transform.
            workflow_id (str): ID of the workflow.
            workflow_run_id (str): ID of the workflow run.
            entity_class_definitions (Dict[str, Type[Any]], optional): Custom entity
                class definitions. Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            Optional[Dict[str, Any]]: The transformed entity as a dictionary, or None
                if transformation fails.

        Raises:
            Exception: If there's an error during entity deserialization.
        """
        typename = typename.upper()
        self.entity_class_definitions = (
            entity_class_definitions or self.entity_class_definitions
        )

        connection_qualified_name = kwargs.get("connection_qualified_name", None)
        connection_name = kwargs.get("connection_name", None)

        data.update(
            {
                "connection_qualified_name": connection_qualified_name,
                "connection_name": connection_name,
            }
        )

        creator = self.entity_class_definitions.get(typename)
        if creator:
            try:
                entity_attributes = creator.get_attributes(data)
                # enrich the entity with workflow metadata
                enriched_data = self._enrich_entity_with_metadata(
                    workflow_id, workflow_run_id, data
                )

                entity_attributes["attributes"].update(enriched_data["attributes"])
                entity_attributes["custom_attributes"].update(
                    enriched_data["custom_attributes"]
                )

                entity = {
                    "typeName": typename,
                    "attributes": entity_attributes["attributes"],
                    "customAttributes": entity_attributes["custom_attributes"],
                    "status": "ACTIVE",
                }

                return entity
            except Exception as e:
                logger.error(
                    "Error transforming {} entity: {}",
                    typename,
                    str(e),
                    extra={"data": data},
                )
                return None
        else:
            logger.error(f"Unknown typename: {typename}")
            return None
