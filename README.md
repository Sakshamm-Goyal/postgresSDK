# 🐘 SourceSense - PostgreSQL Metadata Extraction App

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Atlan SDK](https://img.shields.io/badge/Atlan-SDK-green.svg)](https://github.com/atlanhq/application-sdk)

A powerful and intelligent PostgreSQL metadata extraction application built with the Atlan Application SDK. SourceSense provides comprehensive data discovery, lineage tracking, and quality profiling for PostgreSQL databases.

## 🌟 Features

### Core Metadata Extraction
- **Database Information**: Size, collation, connection limits, and active connections
- **Schema Details**: Object counts, function information, and business context
- **Table Metadata**: Comprehensive statistics, constraints, and partitioning information
- **Column Analysis**: Data types, constraints, indexes, and sequence information

### Advanced Capabilities
- **🔗 Foreign Key Lineage**: Complete relationship mapping with constraint details
- **📊 Data Quality Profiling**: Null analysis, cardinality assessment, and quality scoring
- **📈 Performance Metrics**: Row estimates, size analysis, and maintenance statistics
- **🏷️ Business Context**: Descriptions, comments, and metadata enrichment
- **🔍 Data Discovery**: Automated schema exploration and object cataloging

### Enhanced PostgreSQL Features
- **Partitioning Support**: Detection and analysis of partitioned tables
- **Sequence Management**: Auto-increment and sequence tracking
- **Index Analysis**: Comprehensive index usage and performance metrics
- **Constraint Mapping**: Primary keys, foreign keys, unique constraints, and checks
- **Data Type Intelligence**: Full PostgreSQL data type support with precision details

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- [Dapr CLI](https://docs.dapr.io/getting-started/install-dapr-cli/)
- [Temporal CLI](https://docs.temporal.io/cli)
- PostgreSQL database access
- Docker (for demo database)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Sakshamm-Goyal/postgresSDK.git
   cd postgresSDK
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Download required components:**
   ```bash
   uv run poe download-components
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL connection details
   ```

5. **Start demo database (optional):**
   ```bash
   docker-compose up postgres -d
   ```

6. **Start dependencies (in separate terminal):**
   ```bash
   uv run poe start-deps
   ```

7. **Run the application:**
   ```bash
   uv run main.py
   ```

**Access the application:**
- **Web Interface**: http://localhost:8000
- **Temporal UI**: http://localhost:8233

## 🏗️ Architecture

```mermaid
graph TD
    A[SourceSense App] --> B[PostgreSQL Client]
    A --> C[Metadata Extraction Workflow]
    A --> D[Data Quality Profiler]
    A --> E[Lineage Tracker]
    
    B --> F[PostgreSQL Database]
    C --> G[Schema Extractor]
    C --> H[Table Extractor]
    C --> I[Column Extractor]
    D --> J[Quality Metrics]
    E --> K[Foreign Key Mapper]
    
    G --> L[Atlan Transformer]
    H --> L
    I --> L
    J --> L
    K --> L
    
    L --> M[Atlan Platform]
```

## 📊 Metadata Types

### Database Level
- Database name, size, and collation
- Connection limits and active connections
- Character set and encoding information

### Schema Level
- Schema ownership and privileges
- Object counts (tables, views, functions, procedures)
- Business descriptions and context

### Table Level
- Table type and partitioning information
- Row estimates and size metrics
- Constraint and index counts
- Maintenance statistics (vacuum, analyze)

### Column Level
- Data type details with precision
- Constraint information (PK, FK, unique, check)
- Index usage and sequence information
- Data quality metrics (nulls, cardinality)

### Foreign Key Lineage
- Source and target table relationships
- Constraint definitions and rules
- Update/delete action mappings
- Relationship strength analysis

### Data Quality Metrics
- Null percentage analysis
- Cardinality assessment
- Data distribution statistics
- Quality and freshness scoring

## 🔧 Configuration

### Environment Variables

```bash
# PostgreSQL Connection
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DATABASE=your_database

# Application Settings
APP_NAME=sourcesense-postgres
TENANT_ID=your_tenant_id
CONNECTION_NAME=your_connection_name

# Optional: Advanced Settings
POSTGRES_SSLMODE=prefer
POSTGRES_CONNECT_TIMEOUT=10
```

### Connection String Format

```
postgresql+psycopg2://user:password@host:port/database?sslmode=prefer&connect_timeout=10&application_name=sourcesense-postgres
```

## 📁 Project Structure

```
sourcesense-postgres/
├── app/                    # Core application logic
│   ├── sql/               # PostgreSQL query templates
│   │   ├── EXTRACT_DATABASE.sql
│   │   ├── EXTRACT_SCHEMA.sql
│   │   ├── EXTRACT_TABLE.sql
│   │   ├── EXTRACT_COLUMN.sql
│   │   ├── EXTRACT_FOREIGN_KEYS.sql
│   │   ├── EXTRACT_DATA_QUALITY.sql
│   │   └── EXTRACT_SOURCESENSE_INSIGHTS.sql
│   ├── activities.py      # PostgreSQL extraction activities
│   ├── clients.py         # PostgreSQL client implementation
│   ├── handler.py         # Request handler
│   ├── transformer.py     # Atlan entity transformations
│   └── workflows.py       # Workflow orchestration
├── components/            # Dapr components (auto-downloaded)
├── frontend/              # Web interface
│   ├── static/           # CSS and JavaScript
│   └── templates/        # HTML templates
├── deploy/               # Deployment configurations
├── docker/               # Docker configuration
├── local/                # Local data storage
├── models/               # Data models and schemas
├── main.py               # Application entry point
├── sourcesense_demo.py   # Comprehensive demo script
├── test_queries.py       # Database testing utilities
├── pyproject.toml        # Dependencies and configuration
├── docker-compose.yml    # Docker Compose setup
└── README.md             # This file
```

## 🔄 Workflow Process

1. **Initialization**: Setup PostgreSQL client and workflow components
2. **Preflight Check**: Validate database connectivity and permissions
3. **Metadata Extraction**:
   - Extract database information and statistics
   - Discover schemas and their object counts
   - Analyze tables with comprehensive metrics
   - Profile columns with data quality insights
   - Map foreign key relationships and lineage
   - Calculate data quality scores and metrics
4. **Transformation**: Convert raw metadata into Atlan entity format
5. **Output**: Save enriched metadata to specified location

## 🧪 Demo Environment

### Docker PostgreSQL Setup

```bash
# Start PostgreSQL with sample data
docker-compose up postgres -d

# Check database status
docker-compose ps

# View logs
docker-compose logs postgres
```

### Sample Data Schema

The demo includes a comprehensive e-commerce and analytics schema with:
- **E-commerce tables**: users, products, orders, categories, addresses
- **Analytics tables**: product_views, user_events, sales_summary
- **Reporting tables**: daily_reports
- **Foreign key relationships**: Complete referential integrity
- **Sample data**: Realistic test data for demonstration

## 🚀 Advanced Features

### Data Quality Scoring

SourceSense provides intelligent data quality scoring based on:
- **Null Analysis**: Percentage of null values per column
- **Cardinality Assessment**: Uniqueness and distribution analysis
- **Freshness Metrics**: Last analyze and vacuum timestamps
- **Constraint Health**: Foreign key integrity and validation

### Lineage Tracking

Comprehensive relationship mapping including:
- **Foreign Key Chains**: Multi-level dependency tracking
- **Constraint Rules**: Update/delete action analysis
- **Relationship Strength**: Based on constraint types and rules
- **Business Context**: Descriptions and metadata enrichment

### Performance Insights

Detailed performance analysis:
- **Size Metrics**: Table, index, and total size tracking
- **Row Statistics**: Live/dead tuple analysis
- **Maintenance History**: Vacuum and analyze patterns
- **Index Usage**: Comprehensive index analysis

## 🧪 Testing

### Run Test Suite

```bash
# Test database connectivity and queries
uv run python test_queries.py

# Run comprehensive demo
uv run python sourcesense_demo.py

# Run unit tests (if available)
uv run pytest
```

### Test Results

The test suite validates:
- ✅ Database connectivity
- ✅ Schema extraction (4 schemas found)
- ✅ Table extraction (12 tables with full metadata)
- ✅ Column extraction with data quality metrics
- ✅ Foreign key lineage (6 relationships mapped)
- ✅ Data quality profiling (10 tables analyzed)
- ✅ SourceSense insights generation

## 🔧 Development

### Code Quality

```bash
# Format code
uv run black .

# Lint code
uv run flake8 .

# Type checking
uv run mypy .
```

### Local Development

```bash
# Start dependencies
uv run poe start-deps

# Run in development mode
uv run main.py --dev

# Stop dependencies
uv run poe stop-deps
```

## 📚 API Reference

### Workflow Endpoints

- `POST /workflows/v1/auth` - Test database connection
- `POST /workflows/v1/metadata` - Fetch available metadata
- `POST /workflows/v1/check` - Run preflight checks
- `POST /workflows/v1/start` - Start metadata extraction workflow

### Activities

- `fetch_databases` - Extract database information
- `fetch_schemas` - Extract schema metadata
- `fetch_tables` - Extract table metadata
- `fetch_columns` - Extract column metadata
- `fetch_foreign_keys` - Extract foreign key relationships
- `fetch_data_quality_metrics` - Extract data quality metrics
- `fetch_sourcesense_insights` - Generate unique insights

## 🎯 Use Cases

### Data Governance
- **Metadata Discovery**: Comprehensive catalog of database objects
- **Lineage Tracking**: Understand data flow and dependencies
- **Quality Assessment**: Identify data quality issues and opportunities

### Database Administration
- **Performance Monitoring**: Track table sizes and maintenance needs
- **Schema Analysis**: Understand database structure and relationships
- **Optimization Insights**: Identify unused indexes and optimization opportunities

### Business Intelligence
- **Data Understanding**: Business-friendly descriptions and context
- **Impact Analysis**: Understand downstream effects of schema changes
- **Compliance**: Track data lineage for regulatory requirements

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

### Development Guidelines

1. Follow PEP 8 style guidelines
2. Add comprehensive docstrings
3. Include unit tests for new features
4. Update documentation as needed

### Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/your-username/postgresSDK.git
cd postgresSDK

# Install dependencies
uv sync

# Run tests
uv run pytest

# Start development server
uv run poe start-deps
uv run main.py
```

## 📄 License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Check the [Atlan Documentation](https://ask.atlan.com/)
- Join our [Community Slack](https://atlan.com/slack)

## 🙏 Acknowledgments

- Built with [Atlan Application SDK](https://github.com/atlanhq/application-sdk)
- Powered by [PostgreSQL](https://www.postgresql.org/)
- Uses [SQLAlchemy](https://www.sqlalchemy.org/) for database operations
- Deployed with [Docker](https://www.docker.com/) and [Dapr](https://dapr.io/)

---

**SourceSense** - Intelligent PostgreSQL metadata extraction for the modern data stack. 🚀

*Built for the Atlan Application SDK competition - showcasing the power of comprehensive metadata extraction and data governance.*