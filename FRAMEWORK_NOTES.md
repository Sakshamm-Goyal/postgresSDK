# Atlan Apps Framework - Challenges and Patterns

## 🏗️ Framework Overview

The Atlan Apps Framework provides a powerful foundation for building metadata extraction applications. This document outlines the challenges encountered and patterns developed while building the SourceSense PostgreSQL Connector.

## 🎯 Key Framework Components

### 1. **Application SDK Structure**
```
application_sdk/
├── activities/          # Business logic activities
├── application/         # Application-specific code
├── clients/            # External service clients
├── common/             # Shared utilities
├── decorators/         # Function decorators
├── handlers/           # Request handlers
├── inputs/             # Input models
├── interceptors/       # Request/response interceptors
├── observability/      # Logging and monitoring
├── outputs/            # Output models
├── server/             # FastAPI server
├── services/           # Business services
├── transformers/       # Data transformers
└── workflows/          # Workflow definitions
```

### 2. **Core Patterns**

#### Activity Pattern
```python
@activity.defn
async def extract_table_metadata(
    self, 
    input_data: TableMetadataInput
) -> TableMetadataOutput:
    """Extract metadata for all tables in specified schemas."""
    # Business logic implementation
    pass
```

#### Handler Pattern
```python
class PostgreSQLHandler(BaseSQLHandler):
    """PostgreSQL-specific handler extending base SQL functionality."""
    
    def __init__(self):
        super().__init__()
        # PostgreSQL-specific configuration
    
    def get_metadata_sql(self) -> str:
        """Override base SQL for PostgreSQL compatibility."""
        return """
        SELECT DISTINCT
            t.table_catalog AS catalog_name,
            t.table_schema AS schema_name
        FROM information_schema.tables t
        WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY t.table_catalog, t.table_schema
        """
```

#### Workflow Pattern
```python
@workflow.defn
class PostgreSQLMetadataExtractionWorkflow:
    """Main workflow for PostgreSQL metadata extraction."""
    
    @workflow.run
    async def run(self, input_data: WorkflowInput) -> WorkflowOutput:
        """Execute the complete metadata extraction workflow."""
        # Workflow orchestration
        pass
```

## 🚧 Challenges Encountered

### 1. **Database-Specific SQL Compatibility**

#### Challenge
PostgreSQL's `information_schema` behaves differently from other databases, particularly with column aliasing and GROUP BY clauses.

#### Problem
```sql
-- This fails in PostgreSQL
SELECT 
    table_catalog AS catalog_name,
    table_schema AS schema_name
FROM information_schema.tables
GROUP BY table_catalog, table_schema
ORDER BY table_catalog, table_schema
```

#### Solution
```sql
-- PostgreSQL-compatible approach
SELECT DISTINCT
    t.table_catalog AS catalog_name,
    t.table_schema AS schema_name
FROM information_schema.tables t
WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
ORDER BY t.table_catalog, t.table_schema
```

#### Pattern
- Use `DISTINCT` instead of `GROUP BY` when possible
- Avoid column aliases in `GROUP BY` clauses
- Use subqueries for complex filtering and aliasing

### 2. **Field Name Standardization**

#### Challenge
The framework expects specific field names, but different databases return different column names.

#### Problem
```python
# Framework expects lowercase field names
expected_fields = ['catalog_name', 'schema_name']

# PostgreSQL returns uppercase
actual_fields = ['TABLE_CATALOG', 'TABLE_SCHEMA']
```

#### Solution
```python
# Standardize in SQL query
metadata_sql = """
SELECT DISTINCT
    t.table_catalog AS catalog_name,  -- Alias to expected name
    t.table_schema AS schema_name     -- Alias to expected name
FROM information_schema.tables t
WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
ORDER BY t.table_catalog, t.table_schema
"""
```

#### Pattern
- Always alias database columns to framework-expected names
- Use consistent naming conventions across all handlers
- Document field name mappings for each database type

### 3. **Error Handling and Recovery**

#### Challenge
Complex workflows with multiple activities need robust error handling and recovery mechanisms.

#### Problem
```python
# Activities can fail at any point
@activity.defn
async def extract_metadata(self, input_data):
    # What if database connection fails?
    # What if SQL query is invalid?
    # What if data transformation fails?
    pass
```

#### Solution
```python
@activity.defn
async def extract_metadata(self, input_data: MetadataInput) -> MetadataOutput:
    """Extract metadata with comprehensive error handling."""
    try:
        # Validate input
        if not input_data.database_name:
            raise ValueError("Database name is required")
        
        # Execute with retry logic
        result = await self._execute_with_retry(
            self._extract_metadata_impl,
            input_data
        )
        
        return MetadataOutput(success=True, data=result)
        
    except DatabaseConnectionError as e:
        logger.error(f"Database connection failed: {e}")
        return MetadataOutput(success=False, error=str(e))
        
    except SQLExecutionError as e:
        logger.error(f"SQL execution failed: {e}")
        return MetadataOutput(success=False, error=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return MetadataOutput(success=False, error="Internal error")
```

#### Pattern
- Use specific exception types for different error categories
- Implement retry logic for transient failures
- Return structured error responses
- Log errors with appropriate context

### 4. **Data Transformation and Serialization**

#### Challenge
Converting database metadata to framework-compatible formats while preserving all information.

#### Problem
```python
# Database returns complex nested data
raw_metadata = {
    'table_name': 'products',
    'columns': [
        {'name': 'id', 'type': 'integer', 'constraints': [...]},
        {'name': 'name', 'type': 'varchar', 'constraints': [...]}
    ],
    'indexes': [...],
    'foreign_keys': [...]
}

# Framework expects flattened structure
expected_format = {
    'table_catalog': 'sample_db',
    'table_schema': 'ecommerce',
    'table_name': 'products',
    'column_name': 'id',
    'data_type': 'integer',
    # ... flattened structure
}
```

#### Solution
```python
class MetadataTransformer:
    """Transform database metadata to framework format."""
    
    def transform_table_metadata(self, raw_data: Dict) -> List[Dict]:
        """Transform table metadata to flattened format."""
        transformed = []
        
        for table in raw_data['tables']:
            for column in table['columns']:
                transformed.append({
                    'table_catalog': raw_data['database_name'],
                    'table_schema': table['schema_name'],
                    'table_name': table['table_name'],
                    'column_name': column['name'],
                    'data_type': column['type'],
                    'is_nullable': column.get('nullable', 'YES'),
                    'column_default': column.get('default'),
                    # ... map all required fields
                })
        
        return transformed
```

#### Pattern
- Use dedicated transformer classes for data conversion
- Implement mapping functions for each metadata type
- Preserve all original data while flattening structure
- Add validation for transformed data

### 5. **Workflow Orchestration Complexity**

#### Challenge
Coordinating multiple activities with dependencies and error handling.

#### Problem
```python
@workflow.defn
class MetadataExtractionWorkflow:
    @workflow.run
    async def run(self, input_data):
        # How to handle activity failures?
        # How to manage dependencies?
        # How to provide progress updates?
        pass
```

#### Solution
```python
@workflow.defn
class PostgreSQLMetadataExtractionWorkflow:
    """Orchestrate metadata extraction with proper error handling."""
    
    @workflow.run
    async def run(self, input_data: WorkflowInput) -> WorkflowOutput:
        """Execute metadata extraction workflow."""
        try:
            # Step 1: Validate connection
            connection_result = await workflow.execute_activity(
                validate_connection,
                input_data.connection_config,
                start_to_close_timeout=timedelta(minutes=2)
            )
            
            if not connection_result.success:
                return WorkflowOutput(success=False, error="Connection validation failed")
            
            # Step 2: Extract database metadata
            db_metadata = await workflow.execute_activity(
                extract_database_metadata,
                input_data,
                start_to_close_timeout=timedelta(minutes=5)
            )
            
            # Step 3: Extract schema metadata
            schema_metadata = await workflow.execute_activity(
                extract_schema_metadata,
                input_data,
                start_to_close_timeout=timedelta(minutes=5)
            )
            
            # Step 4: Extract table metadata
            table_metadata = await workflow.execute_activity(
                extract_table_metadata,
                input_data,
                start_to_close_timeout=timedelta(minutes=10)
            )
            
            # Step 5: Extract column metadata
            column_metadata = await workflow.execute_activity(
                extract_column_metadata,
                input_data,
                start_to_close_timeout=timedelta(minutes=15)
            )
            
            # Step 6: Extract foreign keys
            fk_metadata = await workflow.execute_activity(
                extract_foreign_keys,
                input_data,
                start_to_close_timeout=timedelta(minutes=5)
            )
            
            # Step 7: Extract data quality metrics
            quality_metadata = await workflow.execute_activity(
                extract_data_quality,
                input_data,
                start_to_close_timeout=timedelta(minutes=10)
            )
            
            # Combine all metadata
            combined_metadata = {
                'database': db_metadata,
                'schemas': schema_metadata,
                'tables': table_metadata,
                'columns': column_metadata,
                'foreign_keys': fk_metadata,
                'data_quality': quality_metadata
            }
            
            return WorkflowOutput(success=True, data=combined_metadata)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return WorkflowOutput(success=False, error=str(e))
```

#### Pattern
- Use `workflow.execute_activity` for activity orchestration
- Set appropriate timeouts for each activity
- Implement proper error handling at workflow level
- Return structured results with success/failure status

### 6. **Frontend-Backend Integration**

#### Challenge
Integrating FastAPI backend with JavaScript frontend for real-time updates.

#### Problem
```javascript
// Frontend needs to:
// 1. Fetch available databases/schemas
// 2. Start workflow execution
// 3. Monitor progress
// 4. Display results

// How to handle async operations?
// How to provide real-time updates?
// How to handle errors gracefully?
```

#### Solution
```javascript
class MetadataExtractionForm {
    constructor() {
        this.workflowId = null;
        this.progressInterval = null;
    }
    
    async fetchMetadata() {
        try {
            const response = await fetch('/workflows/v1/metadata');
            const data = await response.json();
            this.populateDropdowns(data);
        } catch (error) {
            this.showError('Failed to fetch metadata: ' + error.message);
        }
    }
    
    async startWorkflow() {
        try {
            const formData = this.getFormData();
            const response = await fetch('/workflows/v1/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            this.workflowId = result.workflow_id;
            this.startProgressMonitoring();
        } catch (error) {
            this.showError('Failed to start workflow: ' + error.message);
        }
    }
    
    startProgressMonitoring() {
        this.progressInterval = setInterval(async () => {
            try {
                const response = await fetch(`/workflows/v1/status/${this.workflowId}`);
                const status = await response.json();
                
                this.updateProgress(status);
                
                if (status.completed) {
                    clearInterval(this.progressInterval);
                    this.showResults(status.result);
                }
            } catch (error) {
                this.showError('Failed to check progress: ' + error.message);
            }
        }, 1000);
    }
}
```

#### Pattern
- Use async/await for API calls
- Implement polling for progress updates
- Provide user feedback for all operations
- Handle errors gracefully with user-friendly messages

## 🎯 Best Practices Developed

### 1. **Database Handler Design**
```python
class DatabaseHandler:
    """Base class for database-specific handlers."""
    
    def __init__(self, connection_config: Dict):
        self.connection_config = connection_config
        self.connection = None
    
    async def connect(self) -> bool:
        """Establish database connection."""
        pass
    
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    def get_metadata_sql(self) -> str:
        """Return database-specific metadata SQL."""
        raise NotImplementedError
    
    async def execute_query(self, sql: str) -> List[Dict]:
        """Execute SQL query and return results."""
        pass
```

### 2. **Activity Error Handling**
```python
@activity.defn
async def robust_activity(input_data: InputType) -> OutputType:
    """Activity with comprehensive error handling."""
    try:
        # Validate input
        if not input_data.required_field:
            raise ValidationError("Required field missing")
        
        # Execute with retry
        result = await execute_with_retry(
            actual_implementation,
            input_data,
            max_retries=3,
            backoff_factor=2
        )
        
        return OutputType(success=True, data=result)
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return OutputType(success=False, error=str(e))
        
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        return OutputType(success=False, error="Database operation failed")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return OutputType(success=False, error="Internal error")
```

### 3. **Workflow Progress Tracking**
```python
@workflow.defn
class ProgressTrackingWorkflow:
    """Workflow with progress tracking."""
    
    @workflow.run
    async def run(self, input_data: WorkflowInput) -> WorkflowOutput:
        """Execute workflow with progress updates."""
        total_steps = 6
        current_step = 0
        
        # Step 1: Connection validation
        current_step += 1
        await workflow.upsert_search_attributes({
            'progress': f"Step {current_step}/{total_steps}: Validating connection"
        })
        
        connection_result = await workflow.execute_activity(
            validate_connection,
            input_data.connection_config
        )
        
        # Continue with other steps...
        
        return WorkflowOutput(success=True, data=result)
```

### 4. **Configuration Management**
```python
class ConfigManager:
    """Centralized configuration management."""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from environment and files."""
        return {
            'database': {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'name': os.getenv('DB_NAME', 'sample_db'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'password')
            },
            'workflow': {
                'timeout_minutes': int(os.getenv('WORKFLOW_TIMEOUT', 30)),
                'retry_attempts': int(os.getenv('RETRY_ATTEMPTS', 3))
            }
        }
    
    def get_database_config(self) -> Dict:
        """Get database configuration."""
        return self.config['database']
```

## 🔧 Development Patterns

### 1. **Testing Strategy**
```python
class TestMetadataExtraction:
    """Test suite for metadata extraction."""
    
    @pytest.fixture
    def mock_database(self):
        """Mock database for testing."""
        return MockDatabase()
    
    @pytest.fixture
    def sample_metadata(self):
        """Sample metadata for testing."""
        return {
            'tables': [
                {
                    'name': 'users',
                    'columns': [
                        {'name': 'id', 'type': 'integer'},
                        {'name': 'name', 'type': 'varchar'}
                    ]
                }
            ]
        }
    
    async def test_table_metadata_extraction(self, mock_database, sample_metadata):
        """Test table metadata extraction."""
        handler = PostgreSQLHandler(mock_database)
        result = await handler.extract_table_metadata(sample_metadata)
        
        assert result.success
        assert len(result.data) > 0
        assert 'table_name' in result.data[0]
```

### 2. **Logging Strategy**
```python
import structlog

logger = structlog.get_logger(__name__)

class MetadataExtractor:
    """Metadata extractor with structured logging."""
    
    async def extract_metadata(self, input_data: InputType) -> OutputType:
        """Extract metadata with detailed logging."""
        logger.info(
            "Starting metadata extraction",
            database=input_data.database_name,
            schemas=input_data.schemas
        )
        
        try:
            result = await self._extract_impl(input_data)
            
            logger.info(
                "Metadata extraction completed",
                tables_found=len(result.tables),
                columns_found=len(result.columns)
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Metadata extraction failed",
                error=str(e),
                database=input_data.database_name
            )
            raise
```

## 🎉 Conclusion

The Atlan Apps Framework provides a robust foundation for building metadata extraction applications, but requires careful attention to:

1. **Database-specific compatibility** - Each database has unique characteristics
2. **Error handling and recovery** - Complex workflows need robust error management
3. **Data transformation** - Converting between database and framework formats
4. **Frontend integration** - Real-time updates and user experience
5. **Testing and validation** - Comprehensive testing strategies

The patterns and solutions developed for the SourceSense PostgreSQL Connector can be applied to other database types and extended for more complex metadata extraction scenarios.

The framework's flexibility allows for customization while maintaining consistency across different database implementations, making it an excellent choice for enterprise metadata management solutions.
