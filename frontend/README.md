# Heterogeneous Recursive Planning Frontend

This is the frontend application for the Heterogeneous Recursive Planning project, a general agent framework for long-form writing that achieves human-like adaptive writing through recursive task decomposition and dynamic integration of three fundamental task types: retrieval, reasoning, and composition.

## Features

- User-friendly interface for generating both creative stories and technical reports
- Visualization of the task decomposition process through interactive graphs
- Real-time monitoring of the generation progress
- Support for different language models (GPT-4, Claude)
- Integration with search capabilities for factual report generation
- Viewing and exporting generated content in markdown format

## Getting Started

### Prerequisites

- Node.js (>= 14.x)
- npm (>= 6.x)

### Installation

1. Navigate to the frontend directory
```bash
cd frontend
```

2. Install dependencies
```bash
npm install
```

3. Start the development server
```bash
PORT=3000 npm start
```

4. Open your browser and navigate to [http://localhost:3000](http://localhost:3000)

## Backend Integration

The frontend is designed to be integrated with the Heterogeneous Recursive Planning backend. To enable full functionality, you'll need to:

1. Set up the backend according to the main project's README.md
2. Configure API endpoints in the frontend to communicate with the backend
3. Ensure API keys are properly configured in the backend

## Project Structure

```
frontend/
├── public/              # Static files
├── src/                 # Source code
│   ├── components/      # Reusable UI components
│   │   ├── Footer.js    # Page footer
│   │   ├── Header.js    # Navigation header
│   │   ├── TaskGraph.js # D3-based graph visualization
│   │   └── LiveTaskList.js  # List view of tasks
│   ├── pages/           # Page components
│   │   ├── AboutPage.js             # Project information
│   │   ├── HomePage.js              # Landing page
│   │   ├── ReportGenerationPage.js  # Technical report generation
│   │   ├── ResultsPage.js           # View generation results
│   │   └── StoryGenerationPage.js   # Creative story generation
│   ├── App.js           # Main application component
│   └── index.js         # Entry point
└── package.json         # Project dependencies and scripts
```

## Technologies Used

- React - UI library
- Material UI - Component library
- React Router - Navigation
- D3.js - Graph visualization
- React Markdown - Markdown rendering

## Production Deployment

To build the application for production deployment:

```bash
npm run build
```

This will create a `build` directory with optimized production files that can be served by any static file server.

## Backend API Integration

This frontend is currently using mock data for demonstration purposes. To integrate with the actual backend:

1. Implement API calls to the backend in the appropriate components
2. Replace mock data with actual API responses
3. Add proper error handling for API failures
4. Implement authentication if needed

## Future Improvements

- User authentication system
- Saving and loading generation projects
- More advanced visualization options
- Real-time progress updates
- Collaborative writing features