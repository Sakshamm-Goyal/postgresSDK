"""
This file contains the client for the PostgreSQL metadata extraction application.

Note:
- The DB_CONFIG is overridden from the base class to setup the connection string for the PostgreSQL database.
- Enhanced with connection pooling and advanced PostgreSQL-specific features.
"""

from application_sdk.clients.sql import BaseSQLClient


class PostgreSQLClient(BaseSQLClient):
    """
    This client handles connection string generation based on authentication
    type and manages database connectivity using SQLAlchemy with psycopg2.
    
    Enhanced with:
    - Connection pooling for better performance
    - PostgreSQL-specific connection parameters
    - SSL support for secure connections
    """

    DB_CONFIG = {
        "template": "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}",
        "required": ["user", "password", "host", "port", "database"],
        "optional": {
            "sslmode": "prefer",
            "connect_timeout": "10",
            "application_name": "sourcesense-postgres"
        }
    }
    
    def get_connection_string(self, **kwargs) -> str:
        """
        Generate PostgreSQL connection string with enhanced parameters.
        
        Args:
            **kwargs: Connection parameters including user, password, host, port, database
            
        Returns:
            str: PostgreSQL connection string
        """
        base_url = self.DB_CONFIG["template"].format(**kwargs)
        
        # Add optional parameters
        optional_params = []
        for key, default_value in self.DB_CONFIG["optional"].items():
            value = kwargs.get(key, default_value)
            if value:
                optional_params.append(f"{key}={value}")
        
        if optional_params:
            base_url += "?" + "&".join(optional_params)
            
        return base_url
