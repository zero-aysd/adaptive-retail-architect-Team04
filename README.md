# GenAI Capstone - Adaptive Retail Architect Copilot - Tredence B4



## Overview
This project provides an AI-powered adaptive retail layout generator designed to assist architects in creating optimized store layouts based on market trends and best practices. The system leverages LangGraph agents, Azure OpenAI, and Langfuse for observability.

## API Routes

- `GET /health`  
  Health check endpoint to verify service status.

- `POST /generate_layout`  
  Main endpoint to generate retail layouts. Accepts JSON payload with parameters such as city and keywords, and returns layout data and diagram.

## Code Assets

- Python source code for LangGraph agents, data ingestion scripts, and API located in the `app/` directory.
- Jupyter notebooks for experimentation and analysis located in the `notebooks/` directory.

## Deployment Artifacts

- `Dockerfile` for containerizing the application.
- Azure deployment scripts and setup instructions are located in the `docs/` folder.

## Observability & Management

- Pre-configured Langfuse dashboard for tracing and monitoring agent performance.
- Separate Git repository for prompt versioning and management:  
  https://github.com/zero-aysd/team04-architect-copilot-prompts.git

## Documentation

- [Technical Design Document](docs/Technical_Design_Document.md)  
  Outlines the system architecture, components, and data flow.

- [User Guide](docs/User_Guide.md)  
  Simple guide for architects on using the AI Co-pilot.

- [Deployment Manual](docs/Deployment_Manual.md)  
  Step-by-step instructions for deploying the application on Azure.

- [Azure OpenAI Setup Guide](docs/Azure_OpenAI_Setup.md)  
  Detailed instructions for setting up Azure OpenAI service and permissions.

## Getting Started

1. Clone the repository --recursively.
2. Follow the Deployment Manual in the `docs/` folder to build and deploy the application.
3. Use the API endpoints to generate retail layouts.
4. Refer to the User Guide for usage details.

## Using the Streamlit UI to Interact with the ACI Instance

The `streamlitui.py` file provides a simple web interface to generate adaptive retail store layouts by interacting with the ACI backend.

### Setup

1. Configure the API endpoint in `streamlitui.py` by setting the `API_URL` variable to your ACI instance's URL, for example:

```python
API_URL = "http://<ACI_INSTANCE_IP_OR_DOMAIN>:<PORT>/generate_layout"
```

2. Ensure your ACI backend FastAPI server is running and accessible at the configured URL.

### Running the Streamlit App

Run the Streamlit app with the following command:

```bash
streamlit run streamlitui.py
```

### Using the UI

- Enter the city name in the "City" input field.
- Enter comma-separated product keywords in the "Keywords" input field.
- Click the "Generate Layout" button.

The app will send a request to the ACI backend and display the generated 2D layout image. You can also download the layout as a PNG file using the provided download button.

## Team Members
- AAYUSH SONI
- NAVNEETH IU
