# SourceSense PostgreSQL Connector - Video Script

## 🎬 5-7 Minute Walkthrough Script

### Video Structure
- **Introduction** (30 seconds)
- **Application Demo** (3 minutes)
- **Technical Deep Dive** (2 minutes)
- **Challenges & Solutions** (1 minute)
- **Conclusion** (30 seconds)

---

## 📝 Detailed Script

### 🎯 Introduction (30 seconds)

**[Screen: Title slide with SourceSense logo]**

**Narrator**: "Welcome to the SourceSense PostgreSQL Connector demo. I'm going to show you a comprehensive metadata extraction application built with the Atlan Apps Framework that extracts and displays schema information, business context, lineage information, and quality metrics from PostgreSQL databases."

**[Screen: Application overview diagram]**

**Narrator**: "This application demonstrates enterprise-grade metadata extraction capabilities with a modern web interface, real-time workflow orchestration, and comprehensive data analysis."

---

### 🚀 Application Demo (3 minutes)

#### Part 1: Application Startup (30 seconds)

**[Screen: Terminal showing application startup]**

**Narrator**: "Let's start by launching the application. I'll start the PostgreSQL database, populate it with sample data, and then launch the web interface."

```bash
# Show these commands
docker-compose up -d
uv run python simple_populate.py
uv run main.py
```

**[Screen: Web interface at localhost:8000]**

**Narrator**: "The application is now running with a clean, modern web interface. You can see we have a multi-step form for metadata extraction."

#### Part 2: Database Connection (30 seconds)

**[Screen: Connection step of the form]**

**Narrator**: "First, let's test the database connection. The form is pre-configured with our PostgreSQL database settings."

**[Click "Test Connection" button]**

**Narrator**: "Perfect! The connection is successful. You can see the database details including host, port, and database name."

#### Part 3: Metadata Discovery (45 seconds)

**[Screen: Metadata step with dropdowns]**

**Narrator**: "Now let's discover the available metadata. The application has automatically detected our sample database with multiple schemas."

**[Show dropdowns populated with data]**

**Narrator**: "We have the 'sample_db' database with 'analytics' and 'ecommerce' schemas. This is a realistic e-commerce database with over 2,000 products, 500 users, and thousands of related records."

**[Demonstrate include/exclude filtering]**

**Narrator**: "I can filter which schemas to include or exclude from the extraction. For this demo, I'll include both schemas to show the full scope of metadata extraction."

#### Part 4: Workflow Execution (45 seconds)

**[Screen: Preflight checks and workflow start]**

**Narrator**: "The preflight checks validate our configuration. Now let's start the metadata extraction workflow."

**[Click "Start Workflow" button]**

**Narrator**: "The workflow is now running. You can see the real-time progress updates as different activities complete. This is powered by Temporal workflow orchestration."

**[Screen: Progress updates]**

**Narrator**: "The workflow is extracting database metadata, schema information, table details, column information, foreign keys, and data quality metrics. Each activity runs independently and can be retried if needed."

#### Part 5: Results Display (30 seconds)

**[Screen: Workflow completion and results]**

**Narrator**: "The workflow has completed successfully! Let's examine the extracted metadata to see what we've discovered."

**[Screen: Terminal showing metadata results]**

```bash
uv run python view_metadata.py
```

**Narrator**: "Here we can see comprehensive metadata including database statistics, schema information, table details with row counts and sizes, column information with data types and constraints, and foreign key relationships."

---

### 🔧 Technical Deep Dive (2 minutes)

#### Part 1: Architecture Overview (45 seconds)

**[Screen: Architecture diagram]**

**Narrator**: "Let me show you the technical architecture. The application is built on the Atlan Apps Framework with several key components:"

- **FastAPI Backend**: REST API for web interface
- **Temporal Workflows**: Orchestrates metadata extraction activities
- **PostgreSQL Handler**: Database-specific metadata extraction logic
- **Docker Infrastructure**: Containerized PostgreSQL database
- **Frontend JavaScript**: Real-time web interface

**[Screen: Code showing handler implementation]**

**Narrator**: "The PostgreSQL handler extends the base SQL handler with PostgreSQL-specific SQL queries. Notice how we handle PostgreSQL's unique information_schema behavior and field naming requirements."

#### Part 2: Key Technical Decisions (45 seconds)

**[Screen: Code showing SQL query]**

**Narrator**: "One key technical decision was handling PostgreSQL's column aliasing requirements. We use a subquery approach to ensure compatibility with the framework's expected field names."

```sql
SELECT DISTINCT
    t.table_catalog AS catalog_name,
    t.table_schema AS schema_name
FROM information_schema.tables t
WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
ORDER BY t.table_catalog, t.table_schema
```

**[Screen: Workflow code]**

**Narrator**: "The workflow orchestrates multiple activities in sequence, with proper error handling and retry logic. Each activity can fail independently without affecting the entire workflow."

**[Screen: Frontend JavaScript]**

**Narrator**: "The frontend uses modern JavaScript with async/await patterns for real-time updates and progress monitoring."

#### Part 3: Metadata Extraction Capabilities (30 seconds)

**[Screen: Metadata results breakdown]**

**Narrator**: "The application extracts comprehensive metadata including:"

- **Schema Information**: Column names, data types, constraints, indexes
- **Business Context**: Table descriptions, relationships, domain organization
- **Lineage Information**: Foreign key relationships, data dependencies
- **Quality Metrics**: Row counts, table sizes, performance statistics

**[Screen: Sample metadata output]**

**Narrator**: "This data is stored in Parquet format for efficient processing and can be easily integrated with Atlan's data catalog."

---

### 🚧 Challenges & Solutions (1 minute)

#### Part 1: Database Compatibility (30 seconds)

**[Screen: Error handling code]**

**Narrator**: "One major challenge was PostgreSQL's unique SQL syntax. Unlike other databases, PostgreSQL doesn't allow column aliases in GROUP BY clauses directly."

**[Screen: Solution code]**

**Narrator**: "We solved this by using DISTINCT with subqueries and proper field name aliasing to ensure compatibility with the Atlan Apps Framework."

#### Part 2: Frontend-Backend Integration (30 seconds)

**[Screen: API integration code]**

**Narrator**: "Another challenge was real-time frontend-backend integration. We implemented polling-based progress updates and comprehensive error handling to provide a smooth user experience."

**[Screen: Error handling in frontend]**

**Narrator**: "The frontend gracefully handles connection failures, workflow errors, and provides clear feedback to users throughout the process."

---

### 🎉 Conclusion (30 seconds)

**[Screen: Application overview]**

**Narrator**: "The SourceSense PostgreSQL Connector successfully demonstrates enterprise-grade metadata extraction capabilities. It provides comprehensive schema information, business context, lineage information, and quality metrics while maintaining a modern, user-friendly interface."

**[Screen: Key features summary]**

**Narrator**: "Key achievements include:"

- Complete metadata extraction for all required categories
- Real-world scale with 10,000+ records and complex relationships
- Modern architecture built on industry-standard frameworks
- Robust error handling and recovery mechanisms
- Production-ready deployment with Docker

**[Screen: Call to action]**

**Narrator**: "The application is ready for production use and can be easily extended to support additional database types or enhanced metadata extraction capabilities."

---

## 🎥 Visual Cues and Screen Transitions

### Screen 1: Title Slide
- SourceSense logo
- "PostgreSQL Metadata Extraction Demo"
- "Built with Atlan Apps Framework"

### Screen 2: Application Overview
- Architecture diagram
- Key components highlighted
- Data flow arrows

### Screen 3: Terminal Commands
- Clean terminal with syntax highlighting
- Commands executed one by one
- Success messages highlighted

### Screen 4: Web Interface
- Full browser window
- Form steps clearly visible
- Interactive elements highlighted

### Screen 5: Code Examples
- Syntax highlighted code
- Key sections highlighted
- Comments explaining important parts

### Screen 6: Results Display
- Terminal output with metadata
- Key statistics highlighted
- Data structure clearly shown

### Screen 7: Architecture Deep Dive
- Component diagram
- Code snippets
- Data flow visualization

### Screen 8: Challenge Solutions
- Before/after code comparison
- Error handling examples
- Solution explanations

### Screen 9: Conclusion
- Feature summary
- Key achievements
- Next steps

---

## 🎤 Speaking Notes

### Tone and Pace
- **Professional but approachable**
- **Clear and confident**
- **Moderate pace with pauses for emphasis**
- **Enthusiastic about technical achievements**

### Key Phrases to Use
- "Let me show you..."
- "Notice how..."
- "This demonstrates..."
- "The key insight here is..."
- "As you can see..."
- "This is important because..."

### Technical Terms to Explain
- **Metadata extraction**: "The process of discovering and cataloging information about data structure and content"
- **Workflow orchestration**: "Coordinating multiple tasks in a specific sequence with error handling"
- **Schema information**: "Details about database structure including tables, columns, and relationships"
- **Data lineage**: "Understanding how data flows and transforms through systems"

### Emphasis Points
- **Scale**: "10,000+ records", "2,000+ products", "complex relationships"
- **Completeness**: "All required metadata types", "comprehensive extraction"
- **Modern Architecture**: "Industry-standard frameworks", "production-ready"
- **User Experience**: "Real-time updates", "intuitive interface"

---

## 🎬 Production Tips

### Recording Setup
- **Screen resolution**: 1920x1080 minimum
- **Frame rate**: 30fps
- **Audio quality**: Clear, no background noise
- **Lighting**: Good lighting on presenter if on camera

### Screen Recording
- **Zoom level**: 100% for code, 125% for UI
- **Cursor highlighting**: Enable cursor highlighting
- **Smooth scrolling**: Use smooth scrolling for terminal
- **Clean desktop**: Remove distractions

### Post-Production
- **Intro/outro**: Add title slide and conclusion
- **Transitions**: Smooth transitions between sections
- **Captions**: Add captions for technical terms
- **Music**: Subtle background music (optional)

### Timing
- **Total length**: 5-7 minutes
- **Section timing**: Follow the script timing
- **Buffer time**: Add 30 seconds buffer for natural pauses
- **Practice**: Record multiple takes for best quality

---

## 📋 Pre-Recording Checklist

### Technical Setup
- [ ] Application running successfully
- [ ] Database populated with sample data
- [ ] Web interface accessible
- [ ] All services healthy
- [ ] Screen recording software ready
- [ ] Audio equipment tested

### Content Preparation
- [ ] Script reviewed and practiced
- [ ] Key points memorized
- [ ] Technical terms defined
- [ ] Demo flow tested
- [ ] Backup plans ready

### Environment
- [ ] Clean desktop
- [ ] Browser bookmarks cleared
- [ ] Terminal history cleared
- [ ] Notification sounds disabled
- [ ] Good lighting setup
- [ ] Quiet environment

This script provides a comprehensive guide for creating an engaging and informative video demonstration of the SourceSense PostgreSQL Connector.
