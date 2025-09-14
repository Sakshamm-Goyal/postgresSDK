# SourceSense PostgreSQL Connector - Architecture Notes

## High-Level Design Decisions

### 1. **Atlan Apps Framework Integration**
**Decision**: Built on the Atlan Apps Framework for metadata extraction and management.

**Rationale**: 
- Provides standardized metadata extraction patterns
- Built-in support for workflow orchestration via Temporal
- Seamless integration with Atlan's data catalog
- Handles complex data lineage and relationship mapping
- Provides robust error handling and retry mechanisms

**Key Benefits**:
- **Scalability**: Framework handles distributed processing automatically
- **Reliability**: Built-in retry logic and error handling
- **Maintainability**: Standardized patterns reduce custom code
- **Integration**: Native Atlan ecosystem compatibility

### 2. **PostgreSQL-Specific Handler Implementation**
**Decision**: Created custom `PostgreSQLHandler` extending `BaseSQLHandler`.

**Rationale**:
- PostgreSQL has unique SQL syntax and metadata catalog structure
- Different information_schema behavior compared to other databases
- Specific handling needed for PostgreSQL data types and constraints
- Custom column aliasing required for framework compatibility

**Key Technical Challenges Solved**:
```python
# PostgreSQL-specific metadata SQL with proper aliasing
metadata_sql = """
SELECT DISTINCT
    t.table_catalog AS catalog_name,
    t.table_schema AS schema_name
FROM information_schema.tables t
WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
ORDER BY t.table_catalog, t.table_schema
"""
```

### 3. **Multi-Schema Architecture**
**Decision**: Organized database into logical schemas (analytics, ecommerce, reporting).

**Rationale**:
- **Separation of Concerns**: Different business domains isolated
- **Security**: Schema-level access controls
- **Maintainability**: Clear organization of related tables
- **Scalability**: Independent evolution of different domains

**Schema Structure**:
```
sample_db/
├── analytics/          # Analytics and tracking data
│   ├── product_views   # User product interactions
│   ├── user_events     # User behavior tracking
│   └── sales_summary   # Aggregated sales data
├── ecommerce/          # Core e-commerce data
│   ├── users          # User accounts
│   ├── categories     # Product categories
│   ├── products       # Product catalog
│   ├── addresses      # User addresses
│   ├── orders         # Order management
│   └── order_items    # Order line items
└── reporting/          # Business intelligence
    ├── daily_sales    # Daily sales metrics
    ├── monthly_revenue # Monthly revenue data
    └── product_performance # Product analytics
```

### 4. **Workflow Orchestration with Temporal**
**Decision**: Used Temporal for workflow management and activity coordination.

**Rationale**:
- **Reliability**: Automatic retry and failure handling
- **Observability**: Built-in workflow monitoring and debugging
- **Scalability**: Distributed execution across multiple workers
- **State Management**: Persistent workflow state across restarts

**Workflow Structure**:
```
PostgreSQLMetadataExtractionWorkflow
├── DatabaseConnectionActivity
├── SchemaDiscoveryActivity
├── TableMetadataExtractionActivity
├── ColumnMetadataExtractionActivity
├── ForeignKeyDiscoveryActivity
├── DataQualityAnalysisActivity
└── MetadataTransformationActivity
```

### 5. **Docker-Based Development Environment**
**Decision**: Containerized PostgreSQL database with Docker Compose.

**Rationale**:
- **Consistency**: Identical environment across development and production
- **Isolation**: No conflicts with local PostgreSQL installations
- **Portability**: Easy deployment and scaling
- **Version Control**: Specific PostgreSQL version management

**Container Architecture**:
```yaml
services:
  postgres-db:
    image: postgres:15
    environment:
      POSTGRES_DB: sample_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### 6. **FastAPI Web Interface**
**Decision**: Built REST API with FastAPI for user interaction.

**Rationale**:
- **Modern Framework**: Type hints, automatic validation, async support
- **Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Performance**: High-performance async request handling
- **Integration**: Easy integration with Atlan Apps Framework

**API Endpoints**:
```
GET  /workflows/v1/metadata     # Get available databases/schemas
POST /workflows/v1/start        # Start metadata extraction workflow
GET  /workflows/v1/status/{id}  # Check workflow status
GET  /workflows/v1/results/{id} # Get extraction results
```

### 7. **Frontend-Backend Separation**
**Decision**: Separate JavaScript frontend with REST API backend.

**Rationale**:
- **User Experience**: Rich, interactive web interface
- **Scalability**: Frontend and backend can scale independently
- **Maintainability**: Clear separation of concerns
- **Flexibility**: Easy to add new features or change UI

**Frontend Architecture**:
```javascript
// Multi-step form with real-time validation
class MetadataExtractionForm {
  async fetchMetadata() { /* API calls */ }
  async startWorkflow() { /* Workflow orchestration */ }
  async monitorProgress() { /* Real-time updates */ }
}
```

## Technical Challenges and Solutions

### 1. **PostgreSQL Column Alias Handling**
**Challenge**: PostgreSQL doesn't allow column aliases in GROUP BY clauses directly.

**Solution**: Used subquery approach to handle DISTINCT and aliasing:
```sql
SELECT DISTINCT
    t.table_catalog AS catalog_name,
    t.table_schema AS schema_name
FROM information_schema.tables t
WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
ORDER BY t.table_catalog, t.table_schema
```

### 2. **Field Name Mismatch Between Backend and Frontend**
**Challenge**: Backend returned `TABLE_CATALOG`/`TABLE_SCHEMA` but frontend expected `catalog_name`/`schema_name`.

**Solution**: Standardized on lowercase field names throughout the stack:
- Backend SQL: `AS catalog_name, AS schema_name`
- Frontend JavaScript: `item.catalog_name, item.schema_name`

### 3. **Foreign Key Constraint Management**
**Challenge**: Complex foreign key relationships between tables made data population difficult.

**Solution**: Implemented proper dependency order and conflict handling:
```python
# Populate in dependency order
add_users()           # No dependencies
add_categories()      # No dependencies  
add_products()        # Depends on categories
add_addresses()       # Depends on users
add_orders()          # Depends on users and addresses
add_order_items()     # Depends on orders and products
add_analytics_data()  # Depends on users and products
```

### 4. **Metadata Extraction Performance**
**Challenge**: Large databases with thousands of tables and columns.

**Solution**: 
- **Chunked Processing**: Process metadata in batches
- **Parallel Activities**: Concurrent extraction of different metadata types
- **Efficient Queries**: Optimized SQL queries with proper indexing
- **Caching**: Store intermediate results in Parquet format

### 5. **Error Handling and Recovery**
**Challenge**: Robust error handling across distributed components.

**Solution**:
- **Activity-Level Retries**: Individual activities retry on failure
- **Workflow-Level Recovery**: Resume workflows from last successful activity
- **Graceful Degradation**: Continue processing even if some metadata fails
- **Comprehensive Logging**: Detailed error tracking and debugging

## Performance Optimizations

### 1. **Database Query Optimization**
- Used `DISTINCT` to avoid duplicate metadata
- Implemented proper `WHERE` clauses to filter system schemas
- Added appropriate indexes on frequently queried columns

### 2. **Memory Management**
- Process large datasets in chunks to avoid memory issues
- Use Parquet format for efficient storage and retrieval
- Implement streaming for large result sets

### 3. **Concurrent Processing**
- Parallel execution of independent activities
- Async/await patterns for I/O operations
- Non-blocking UI updates

## Security Considerations

### 1. **Database Security**
- Connection string encryption
- Role-based access control
- Schema-level permissions

### 2. **API Security**
- Input validation and sanitization
- Rate limiting and throttling
- CORS configuration

### 3. **Data Privacy**
- No sensitive data in logs
- Secure credential management
- Data anonymization options

## Monitoring and Observability

### 1. **Workflow Monitoring**
- Temporal UI for workflow visualization
- Activity-level success/failure tracking
- Performance metrics and timing

### 2. **Application Logging**
- Structured logging with correlation IDs
- Different log levels for different environments
- Centralized log aggregation

### 3. **Health Checks**
- Database connectivity monitoring
- Service health endpoints
- Dependency status tracking

## Future Enhancements

### 1. **Advanced Metadata Extraction**
- Data lineage discovery
- Data quality metrics calculation
- Schema evolution tracking

### 2. **Performance Improvements**
- Query result caching
- Incremental metadata updates
- Parallel database connections

### 3. **User Experience**
- Real-time progress indicators
- Advanced filtering and search
- Export capabilities

### 4. **Integration Features**
- Multiple database support
- Custom transformer plugins
- API webhook notifications

## Conclusion

The SourceSense PostgreSQL Connector demonstrates a robust, scalable architecture that leverages modern technologies and frameworks to provide comprehensive metadata extraction capabilities. The design decisions prioritize maintainability, performance, and user experience while handling the complexities of PostgreSQL's metadata catalog and the distributed nature of the Atlan Apps Framework.

The architecture successfully addresses the core requirements of metadata extraction while providing a solid foundation for future enhancements and scaling to enterprise-level deployments.
