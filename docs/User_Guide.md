# User Guide for Architects: AI Co-pilot

## Introduction
The AI Co-pilot is an intelligent assistant designed to help architects generate adaptive retail layouts based on market trends and best practices. It leverages AI agents to analyze data, strategize layouts, and produce visual diagrams to support design decisions.

## Getting Started

### Accessing the AI Co-pilot
The AI Co-pilot is accessible via a REST API. Architects can send requests to generate retail layouts by specifying key parameters.

### Input Parameters
- **city** (string): The city where the retail store is located. This helps tailor the layout to local market trends.
- **keywords** (list of strings, optional): Keywords representing product categories or themes to focus on (e.g., "smartphones", "gaming laptops"). Defaults to popular categories if omitted.

### Making a Request
Send a POST request to the `/generate_layout` endpoint with a JSON body containing the input parameters.

Example request body:
```json
{
  "city": "Surat",
  "keywords": ["smartphones", "gaming laptops"]
}
```

## Understanding the Response

The response includes:

- **success**: Indicates if the layout generation was successful.
- **layout_id**: Unique identifier for the generated layout.
- **layout_data**: JSON object representing the detailed layout plan.
- **diagram_url**: URL to the generated 2D layout diagram (PNG).
- **trends_summary**: Summary of market trends influencing the layout.
- **render_time**: Time taken to generate the layout.
- **generated_at**: Timestamp of generation.
- **metadata**: Additional information.

## Interpreting the Layout and Diagram

- The layout JSON contains zones, dimensions, and compliance notes.
- The diagram visually represents the store layout with labeled zones and entrance.
- Compliance notes highlight any accessibility or best practice considerations.

## Tips for Effective Use

- Provide relevant keywords to tailor the layout to specific product focuses.
- Use the trends summary to understand market influences.
- Review compliance notes to ensure adherence to regulations.
- Use the diagram as a visual aid in presentations and planning.

## Support and Feedback

For questions or feedback, please contact the development team or refer to the project documentation.
