"""
This file contains the activities for the PostgreSQL metadata extraction application.

Note:
- Enhanced with PostgreSQL-specific activities for foreign key lineage and data quality profiling
- Includes advanced metadata extraction capabilities for comprehensive data governance
"""

from typing import Any, Dict, Optional, cast

from application_sdk.activities.common.models import ActivityStatistics
from application_sdk.activities.common.utils import auto_heartbeater
from application_sdk.activities.metadata_extraction.sql import (
    BaseSQLMetadataExtractionActivities,
    BaseSQLMetadataExtractionActivitiesState,
)
from application_sdk.common.utils import prepare_query
from application_sdk.observability.decorators.observability_decorator import (
    observability,
)
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces
from application_sdk.services.secretstore import SecretStore
from temporalio import activity

logger = get_logger(__name__)
activity.logger = logger
metrics = get_metrics()
traces = get_traces()


class PostgreSQLMetadataExtractionActivities(BaseSQLMetadataExtractionActivities):
    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def credential_extraction_demo_activity(
        self, workflow_args: Dict[str, Any]
    ) -> Optional[ActivityStatistics]:
        """A custom activity demostrating the use of various utilities provided by the application SDK.

        Args:
            workflow_args: The workflow arguments.

        Returns:
            Optional[ActivityStatistics]: The activity statistics.
        """

        # reference to credentials passed as user inputs are available as 'credential_guid' in workflow_args
        # in this case refer to https://github.com/atlanhq/atlan-sample-apps/blob/main/connectors/mysql/frontend/static/script.js#L740
        await SecretStore.get_credentials(workflow_args["credential_guid"])
        logger.info("credentials retrieved successfully")

        return None

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_columns(
        self, workflow_args: Dict[str, Any]
    ) -> Optional[ActivityStatistics]:
        """Fetch columns from the source database.

        Args:
            batch_input: DataFrame containing the raw column data.
            raw_output: JsonOutput instance for writing raw data.
            **kwargs: Additional keyword arguments.

        Returns:
            Optional[ActivityStatistics]: Statistics about the extracted columns, or None if extraction failed.
        """
        state = cast(
            BaseSQLMetadataExtractionActivitiesState,
            await self._get_state(workflow_args),
        )
        if not state.sql_client or not state.sql_client.engine:
            logger.error("SQL client or engine not initialized")
            raise ValueError("SQL client or engine not initialized")

        prepared_query = prepare_query(
            query=self.fetch_column_sql, workflow_args=workflow_args
        )
        statistics = await self.query_executor(
            sql_engine=state.sql_client.engine,
            sql_query=prepared_query,
            workflow_args=workflow_args,
            output_suffix="raw/column",
            typename="column",
        )

        return statistics

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_foreign_keys(
        self, workflow_args: Dict[str, Any]
    ) -> Optional[ActivityStatistics]:
        """Fetch foreign key relationships and lineage information from PostgreSQL.

        Args:
            workflow_args: The workflow arguments.

        Returns:
            Optional[ActivityStatistics]: Statistics about the extracted foreign keys, or None if extraction failed.
        """
        state = cast(
            BaseSQLMetadataExtractionActivitiesState,
            await self._get_state(workflow_args),
        )
        if not state.sql_client or not state.sql_client.engine:
            logger.error("SQL client or engine not initialized")
            raise ValueError("SQL client or engine not initialized")

        prepared_query = prepare_query(
            query=self.fetch_foreign_keys_sql, workflow_args=workflow_args
        )
        statistics = await self.query_executor(
            sql_engine=state.sql_client.engine,
            sql_query=prepared_query,
            workflow_args=workflow_args,
            output_suffix="raw/foreign_keys",
            typename="foreign_keys",
        )

        return statistics

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_data_quality_metrics(
        self, workflow_args: Dict[str, Any]
    ) -> Optional[ActivityStatistics]:
        """Fetch data quality metrics and profiling information from PostgreSQL.

        Args:
            workflow_args: The workflow arguments.

        Returns:
            Optional[ActivityStatistics]: Statistics about the extracted data quality metrics, or None if extraction failed.
        """
        state = cast(
            BaseSQLMetadataExtractionActivitiesState,
            await self._get_state(workflow_args),
        )
        if not state.sql_client or not state.sql_client.engine:
            logger.error("SQL client or engine not initialized")
            raise ValueError("SQL client or engine not initialized")

        prepared_query = prepare_query(
            query=self.fetch_data_quality_sql, workflow_args=workflow_args
        )
        statistics = await self.query_executor(
            sql_engine=state.sql_client.engine,
            sql_query=prepared_query,
            workflow_args=workflow_args,
            output_suffix="raw/data_quality",
            typename="data_quality",
        )

        return statistics

    @property
    def fetch_foreign_keys_sql(self) -> str:
        """Get the SQL query for fetching foreign key relationships."""
        from application_sdk.common.utils import read_sql_files
        from application_sdk.constants import SQL_QUERIES_PATH
        queries = read_sql_files(queries_prefix=SQL_QUERIES_PATH)
        return queries.get("EXTRACT_FOREIGN_KEYS", "")

    @property
    def fetch_data_quality_sql(self) -> str:
        """Get the SQL query for fetching data quality metrics."""
        from application_sdk.common.utils import read_sql_files
        from application_sdk.constants import SQL_QUERIES_PATH
        queries = read_sql_files(queries_prefix=SQL_QUERIES_PATH)
        return queries.get("EXTRACT_DATA_QUALITY", "")

    @observability(logger=logger, metrics=metrics, traces=traces)
    @activity.defn
    @auto_heartbeater
    async def fetch_sourcesense_insights(
        self, workflow_args: Dict[str, Any]
    ) -> Optional[ActivityStatistics]:
        """Fetch SourceSense unique insights and recommendations.

        Args:
            workflow_args: The workflow arguments.

        Returns:
            Optional[ActivityStatistics]: Statistics about the extracted insights, or None if extraction failed.
        """
        state = cast(
            BaseSQLMetadataExtractionActivitiesState,
            await self._get_state(workflow_args),
        )
        if not state.sql_client or not state.sql_client.engine:
            logger.error("SQL client or engine not initialized")
            raise ValueError("SQL client or engine not initialized")

        prepared_query = prepare_query(
            query=self.fetch_sourcesense_insights_sql, workflow_args=workflow_args
        )
        statistics = await self.query_executor(
            sql_engine=state.sql_client.engine,
            sql_query=prepared_query,
            workflow_args=workflow_args,
            output_suffix="raw/sourcesense_insights",
            typename="sourcesense_insights",
        )

        return statistics

    @property
    def fetch_sourcesense_insights_sql(self) -> str:
        """Get the SQL query for fetching SourceSense insights."""
        from application_sdk.common.utils import read_sql_files
        from application_sdk.constants import SQL_QUERIES_PATH
        queries = read_sql_files(queries_prefix=SQL_QUERIES_PATH)
        return queries.get("EXTRACT_SOURCESENSE_INSIGHTS", "")
