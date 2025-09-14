"""
This file contains the workflow definition for the PostgreSQL metadata extraction application.

Note:
- Enhanced with PostgreSQL-specific activities for foreign key lineage and data quality profiling
- Includes comprehensive metadata extraction workflow for data governance
"""

import asyncio
from datetime import timedelta
from typing import Any, Callable, Dict, List

from app.activities import PostgreSQLMetadataExtractionActivities
from application_sdk.observability.decorators.observability_decorator import (
    observability,
)
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces
from application_sdk.workflows.metadata_extraction.sql import (
    BaseSQLMetadataExtractionWorkflow,
)
from temporalio import workflow
from temporalio.common import RetryPolicy

logger = get_logger(__name__)
workflow.logger = logger
metrics = get_metrics()
traces = get_traces()


@workflow.defn
class PostgreSQLMetadataExtractionWorkflow(BaseSQLMetadataExtractionWorkflow):
    @observability(logger=logger, metrics=metrics, traces=traces)
    @workflow.run
    async def run(self, workflow_config: Dict[str, Any]):
        """
        Run the workflow.

        :param workflow_args: The workflow arguments.
        """
        activities_instance = PostgreSQLMetadataExtractionActivities()

        workflow_args: Dict[str, Any] = await workflow.execute_activity_method(
            activities_instance.get_workflow_args,
            workflow_config,
            start_to_close_timeout=timedelta(seconds=10),
        )

        retry_policy = RetryPolicy(
            maximum_attempts=6,
            backoff_coefficient=2,
        )

        await workflow.execute_activity_method(
            activities_instance.preflight_check,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=self.default_start_to_close_timeout,
            heartbeat_timeout=self.default_heartbeat_timeout,
        )

        await workflow.execute_activity_method(
            activities_instance.credential_extraction_demo_activity,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=self.default_start_to_close_timeout,
            heartbeat_timeout=self.default_heartbeat_timeout,
        )

        fetch_and_transforms = [
            self.fetch_and_transform(
                activities_instance.fetch_databases,
                workflow_args,
                retry_policy,
            ),
            self.fetch_and_transform(
                activities_instance.fetch_schemas,
                workflow_args,
                retry_policy,
            ),
            self.fetch_and_transform(
                activities_instance.fetch_tables,
                workflow_args,
                retry_policy,
            ),
            self.fetch_and_transform(
                activities_instance.fetch_columns,
                workflow_args,
                retry_policy,
            ),
            self.fetch_and_transform(
                activities_instance.fetch_foreign_keys,
                workflow_args,
                retry_policy,
            ),
            self.fetch_and_transform(
                activities_instance.fetch_data_quality_metrics,
                workflow_args,
                retry_policy,
            ),

        ]
        await asyncio.gather(*fetch_and_transforms)

    @staticmethod
    def get_activities(
        activities: PostgreSQLMetadataExtractionActivities,
    ) -> List[Callable[..., Any]]:
        """Get the list of activities for the workflow.

        Args:
            activities: The activities instance containing the workflow activities.

        Returns:
            List[Callable[..., Any]]: A list of activity methods that can be executed by the workflow.
        """
        return [
            activities.get_workflow_args,
            activities.preflight_check,
            activities.fetch_databases,
            activities.fetch_schemas,
            activities.fetch_tables,
            activities.fetch_columns,
            activities.fetch_foreign_keys,
            activities.fetch_data_quality_metrics,
            activities.credential_extraction_demo_activity,
            activities.transform_data,
        ]
