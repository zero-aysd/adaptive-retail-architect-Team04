# Technical Design Document

## System Overview
The AI Co-pilot system is designed to generate adaptive retail layouts powered by AI agents. It leverages a modular architecture with multiple specialized agents collaborating to analyze market trends, strategize layouts, and generate visual diagrams.

## Main Components

### FastAPI Backend
- Provides REST API endpoints for layout generation.
- Handles secret management via Azure Key Vault.
- Integrates Langfuse for observability and tracing.
- Implements CORS middleware for cross-origin requests.

### Agents
- **Market Analyst**: Analyzes market trends based on city and keywords.
- **Layout Strategist**: Designs retail layouts using market trends and best practices.
- **Draftsman**: Generates 2D layout diagrams as PNG images.

### Graph Orchestration
- Uses a state graph to orchestrate agent execution flow:
  1. Market Analyst node
  2. Layout Strategist node
  3. Draftsman node
- Each node logs detailed information and updates the shared state.

### Prompt Management
- Prompts are stored as YAML files and loaded dynamically.
- Supports multiple prompt variants.

### Models
- Pydantic models define request and response schemas for API.
- Layout plans and reviews are strongly typed.

## Data Flow and Interactions
1. Client sends a layout generation request with city and keywords.
2. Market Analyst agent resolves geographic data and fetches market trends.
3. Layout Strategist agent uses trends and retrieved context to draft a layout plan.
4. Reviewer sub-node evaluates compliance and best practice scores.
5. Draftsman agent generates a visual diagram from the final layout plan.
6. API returns layout data, diagram URL, trends summary, and metadata.

## API Endpoints
- `GET /health`: Health check endpoint.
- `POST /generate_layout`: Accepts layout requests and returns generated layout data and diagram.

## Observability and Management
- Langfuse dashboard is pre-configured to trace agent performance and API calls.
- Prompt versioning and management are handled in a separate Git repository.

## Deployment
- Containerized using Docker.
- Secrets managed via Azure Key Vault.
- Deployment scripts and instructions provided for Azure Container Registry and Azure Container Instances.

## Prompt Repository Reference
The prompt templates used by the AI Co-pilot are maintained in a separate Git repository for versioning and management:

https://github.com/zero-aysd/team04-architect-copilot-prompts.git
