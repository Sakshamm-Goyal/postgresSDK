# SourceSense PostgreSQL Connector - Demo Instructions

## 🎯 Demo Overview

This demo showcases a comprehensive PostgreSQL metadata extraction application built with the Atlan Apps Framework. The application extracts and displays:

- **Schema Information**: Column names, data types, constraints
- **Business Context**: Table/column descriptions, relationships
- **Lineage Information**: Data relationships and dependencies
- **Quality Metrics**: Row counts, indexes, performance statistics

## 📋 Prerequisites

### Required Software
- Docker and Docker Compose
- Python 3.11+ with `uv` package manager
- Git
- Modern web browser (Chrome, Firefox, Safari, Edge)

### System Requirements
- 4GB+ RAM
- 2GB+ free disk space
- Internet connection for initial setup

## 🚀 Quick Start Demo

### Step 1: Clone and Setup
```bash
# Clone the repository
git clone https://github.com/Sakshamm-Goyal/postgresSDK.git
cd postgresSDK

# Install dependencies
uv sync --all-extras --all-groups
```

### Step 2: Start Infrastructure
```bash
# Start PostgreSQL database
docker-compose up -d

# Verify database is running
docker ps
# Should show: sourcesense-postgres container running on port 5432
```

### Step 3: Populate Sample Data
```bash
# Add 10,000+ records for impressive demo
uv run python simple_populate.py

# Verify data was added
uv run python view_metadata.py
```

### Step 4: Start the Application
```bash
# Start Dapr and Temporal (in separate terminals)
uv run poe start-deps

# Start the application
uv run main.py
```

### Step 5: Access the Web Interface
1. Open browser to: `http://localhost:8000`
2. You should see the SourceSense metadata extraction interface

## 🎬 Detailed Demo Walkthrough

### Phase 1: Database Setup and Data Population (2 minutes)

#### 1.1 Database Initialization
```bash
# Start PostgreSQL with sample schema
docker-compose up -d

# Check database status
docker exec sourcesense-postgres psql -U postgres -d sample_db -c "\dt"
```

**What to Show**:
- Empty database initially
- Docker container running successfully
- Database connection established

#### 1.2 Sample Data Population
```bash
# Run the population script
uv run python simple_populate.py
```

**What to Show**:
- 500+ users created
- 50+ categories created  
- 2,000+ products created
- 1,000+ addresses created
- 1,500+ orders created
- 3,000+ order items created
- 5,000+ analytics records created

**Key Points**:
- Realistic e-commerce data structure
- Foreign key relationships maintained
- Multiple schemas (analytics, ecommerce)
- Substantial data volume for impressive demo

### Phase 2: Application Startup (1 minute)

#### 2.1 Start Dependencies
```bash
# Terminal 1: Start Dapr and Temporal
uv run poe start-deps
```

**What to Show**:
- Dapr sidecar starting
- Temporal server starting
- Redis cache initializing
- All services healthy

#### 2.2 Start Application
```bash
# Terminal 2: Start the application
uv run main.py
```

**What to Show**:
- FastAPI server starting on port 8000
- Database connection established
- Workflow activities registered
- Application ready for requests

### Phase 3: Web Interface Demo (3 minutes)

#### 3.1 Access the Interface
1. Open `http://localhost:8000` in browser
2. Show the multi-step form interface

**What to Show**:
- Clean, modern web interface
- Multi-step form with progress indicator
- Real-time validation and feedback

#### 3.2 Database Selection
1. Click "Test Connection" button
2. Show connection success message
3. Navigate to "Connection" step

**What to Show**:
- Connection parameters pre-filled
- Database connection test successful
- Connection details displayed

#### 3.3 Metadata Discovery
1. Navigate to "Metadata" step
2. Show database/schema dropdowns populated
3. Demonstrate include/exclude filtering

**What to Show**:
- `sample_db` database detected
- `analytics` and `ecommerce` schemas available
- Schema filtering options
- Real-time dropdown population

#### 3.4 Workflow Execution
1. Select schemas to include/exclude
2. Click "Start Workflow" button
3. Show workflow progress

**What to Show**:
- Workflow ID generated
- Real-time progress updates
- Activity completion status
- Success confirmation

### Phase 4: Results Analysis (2 minutes)

#### 4.1 View Extracted Metadata
```bash
# Show the extracted metadata
uv run python view_metadata.py
```

**What to Show**:
- Database metadata (size, connections, etc.)
- Schema metadata (table counts, descriptions)
- Table metadata (row counts, sizes, constraints)
- Column metadata (data types, constraints, indexes)
- Foreign key relationships
- Data quality metrics

#### 4.2 Demonstrate Key Features

**Schema Information**:
- Column names and data types
- Primary and foreign key constraints
- Index information
- Table descriptions and comments

**Business Context**:
- Table relationships and dependencies
- Data lineage information
- Business domain organization (analytics, ecommerce)

**Quality Metrics**:
- Row counts and table sizes
- Index usage statistics
- Constraint information
- Performance metrics

## 🎯 Key Demo Points

### 1. **Comprehensive Metadata Extraction**
- **Schema Information**: All column details, data types, constraints
- **Business Context**: Table descriptions, relationships, domain organization
- **Lineage Information**: Foreign key relationships, data dependencies
- **Quality Metrics**: Row counts, sizes, performance statistics

### 2. **Real-World Data Scale**
- 2,000+ products across 50+ categories
- 500+ users with addresses and orders
- 3,000+ order items with relationships
- 5,000+ analytics events and views
- Multiple schemas with complex relationships

### 3. **Modern Architecture**
- Atlan Apps Framework integration
- Temporal workflow orchestration
- Docker containerization
- FastAPI REST API
- Real-time web interface

### 4. **User Experience**
- Intuitive multi-step form
- Real-time validation and feedback
- Progress tracking and monitoring
- Clean, modern interface

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart if needed
docker-compose restart
```

#### Application Won't Start
```bash
# Check if port 8000 is available
lsof -i :8000

# Kill existing process if needed
pkill -f "uv run main.py"
```

#### Metadata Dropdowns Empty
```bash
# Check database connection
docker exec sourcesense-postgres psql -U postgres -d sample_db -c "\dt"

# Restart application
uv run main.py
```

#### Workflow Fails
```bash
# Check Temporal UI
open http://localhost:8233

# Check Dapr status
dapr list
```

### Debug Commands

#### Check Database Status
```bash
# List all tables
docker exec sourcesense-postgres psql -U postgres -d sample_db -c "\dt"

# Check specific schema
docker exec sourcesense-postgres psql -U postgres -d sample_db -c "\dt analytics.*"

# Count records
docker exec sourcesense-postgres psql -U postgres -d sample_db -c "SELECT COUNT(*) FROM ecommerce.products;"
```

#### Check Application Logs
```bash
# View application logs
uv run main.py 2>&1 | tee app.log

# Check Dapr logs
dapr logs --app-id sourcesense-postgres
```

#### Check Workflow Status
```bash
# List workflows
temporal workflow list

# Check specific workflow
temporal workflow show <workflow-id>
```

## 📊 Demo Data Overview

### Database Statistics
- **Total Tables**: 12+ tables across 3 schemas
- **Total Records**: 10,000+ records
- **Database Size**: ~8.5 MB
- **Schemas**: analytics, ecommerce, reporting

### Sample Data Breakdown
- **Users**: 500+ customer accounts
- **Products**: 2,000+ products across 50+ categories
- **Orders**: 1,500+ orders with 3,000+ line items
- **Analytics**: 5,000+ product views and user events
- **Addresses**: 1,000+ shipping/billing addresses

### Schema Organization
- **analytics**: User behavior and product analytics
- **ecommerce**: Core business data (users, products, orders)
- **reporting**: Aggregated business intelligence data

## 🎉 Demo Conclusion

This demo successfully showcases:

1. **Complete Metadata Extraction**: All required metadata types extracted and displayed
2. **Real-World Scale**: Substantial data volume with complex relationships
3. **Modern Architecture**: Built on industry-standard frameworks and tools
4. **User Experience**: Intuitive interface with real-time feedback
5. **Production Ready**: Robust error handling and monitoring

The SourceSense PostgreSQL Connector demonstrates enterprise-grade metadata extraction capabilities while maintaining ease of use and comprehensive feature coverage.

## 📞 Support

For questions or issues during the demo:
- Check the troubleshooting section above
- Review application logs for error details
- Ensure all prerequisites are met
- Verify database connectivity and data population

The application is designed to be self-contained and should work out-of-the-box with the provided setup instructions.
