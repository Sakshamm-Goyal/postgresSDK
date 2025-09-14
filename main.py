"""
Main entry point for the SourceSense PostgreSQL metadata extraction application.

This module initializes and runs the PostgreSQL metadata extraction application,
setting up the workflow, worker, and server components with enhanced features.
"""

import asyncio

from app.activities import PostgreSQLMetadataExtractionActivities
from app.clients import PostgreSQLClient
from app.handler import PostgreSQLHandler
from app.transformer import PostgreSQLAtlasTransformer
from app.workflows import PostgreSQLMetadataExtractionWorkflow
from application_sdk.application.metadata_extraction.sql import (
    BaseSQLMetadataExtractionApplication,
)
from application_sdk.common.error_codes import ApiError
from application_sdk.constants import APPLICATION_NAME
from application_sdk.observability.decorators.observability_decorator import (
    observability,
)
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import get_metrics
from application_sdk.observability.traces_adaptor import get_traces

logger = get_logger(__name__)
metrics = get_metrics()
traces = get_traces()


@observability(logger=logger, metrics=metrics, traces=traces)
async def main():
    try:
        # Initialize the application
        application = BaseSQLMetadataExtractionApplication(
            name=APPLICATION_NAME,
            client_class=PostgreSQLClient,
            transformer_class=PostgreSQLAtlasTransformer,
            handler_class=PostgreSQLHandler,
        )

        await application.setup_workflow(
            workflow_and_activities_classes=[
                (PostgreSQLMetadataExtractionWorkflow, PostgreSQLMetadataExtractionActivities)
            ],
        )

        # Start the worker
        await application.start_worker()

        # Setup the application server
        await application.setup_server(
            workflow_class=PostgreSQLMetadataExtractionWorkflow,
        )

        # Start the application server
        await application.start_server()

    except ApiError:
        logger.error(f"{ApiError.SERVER_START_ERROR}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
