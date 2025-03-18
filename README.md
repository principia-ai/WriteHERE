# WriteHERE: Heterogeneous Recursive Planning based Open Writing Project

WriteHERE is an open-source, non-commercial agent framework for long-form writing that achieves human-like adaptive writing through recursive task decomposition and dynamic integration of three fundamental task types: retrieval, reasoning, and composition.

## Overview

Unlike traditional approaches that rely on predetermined workflows and rigid thinking patterns, this framework:

1. **Eliminates workflow restrictions** through a planning mechanism that interleaves recursive task decomposition and execution
2. **Facilitates heterogeneous task decomposition** by integrating different task types
3. **Adapts dynamically** during the writing process, similar to human writing behavior

Our evaluations on both fiction writing and technical report generation demonstrate that this method consistently outperforms state-of-the-art approaches across all evaluation metrics.

## Open Source Philosophy

WriteHERE is developed with these core principles:

- **Fully Open Source**: All code is freely available for use, modification, and distribution under the MIT License
- **Non-Commercial**: Developed for research and educational purposes without commercial interests
- **Full Transparency**: The entire system architecture and decision-making processes are transparent to users
- **Community-Driven**: We welcome contributions, feedback, and collaborative improvements from the community

## Getting Started

### Prerequisites

- Python 3.6+
- Node.js 14+ (for the frontend)
- API keys for:
  - OpenAI (GPT models)
  - Anthropic (Claude models)
  - SerpAPI (for search functionality in report generation)

### Quick Start

#### Standard Installation

For the easiest start, just run:

```bash
./setup_env.sh  # One-time setup of the environment
./start.sh      # Start the application
```

This will:
1. Create a clean Python virtual environment
2. Install all required dependencies
3. Start the backend server on port 5002
4. Start the frontend on port 3010
5. Open your browser at http://localhost:3010

#### For Anaconda/Miniconda Users

If you're using Anaconda and encounter dependency conflicts, use:

```bash
./run_with_anaconda.sh
```

This script will create a dedicated Anaconda environment called 'writehere' with the correct dependencies and run both servers.

#### Troubleshooting

If you encounter any issues, please check the [Troubleshooting Guide](TROUBLESHOOTING.md) for common problems and solutions.

### Manual Installation

#### Backend Setup

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install main dependencies:
```bash
pip install -v -e .
```

3. Install backend server dependencies:
```bash
pip install -r backend/requirements.txt
```

4. API Keys setup (optional - can also be done via the web UI):
```bash
# Create api_key.env file based on example
cp recursive/api_key.env.example recursive/api_key.env
# Edit the file to add your keys
nano recursive/api_key.env
```

5. Start the backend server:
```bash
cd backend
python server.py
```

#### Frontend Setup

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

2. Start the frontend development server:
```bash
npm start
```

## Features

- **Recursive Task Decomposition**: Breaks down complex writing tasks into manageable subtasks
- **Dynamic Integration**: Seamlessly combines retrieval, reasoning, and composition tasks
- **Adaptive Workflow**: Flexibly adjusts the writing process based on context and requirements
- **Versatile Applications**: Supports both creative fiction and technical report generation
- **User-Friendly Interface**: Intuitive web interface for easy interaction
- **Real-Time Visualization**: See the agent's "thinking process" as it works
- **Transparent Operation**: All agent decisions and processes are visible to users
- **Fully Customizable**: Modify prompts, parameters, and workflows to suit your needs

## Project Structure

```
.
├── backend/               # Backend Flask server
├── frontend/              # React frontend
├── recursive/             # Core engine implementation
│   ├── agent/             # Agent implementation and prompts
│   ├── executor/          # Task execution modules
│   ├── llm/               # Language model integrations
│   ├── utils/             # Utility functions and helpers
│   ├── cache.py           # Caching for improved efficiency
│   ├── engine.py          # Core planning and execution engine
│   ├── graph.py           # Task graph representation
│   ├── memory.py          # Memory management
│   ├── test_run_report.sh # Script for generating reports
│   └── test_run_story.sh  # Script for generating stories
├── test_data/             # Example data for testing
└── start.sh               # All-in-one startup script
```

## Real-time Task Visualization

The system features real-time visualization of the task execution process. As the agent works on generating content, you can see:

1. The hierarchical decomposition of tasks
2. Which tasks are currently being worked on
3. The status of each task (ready, in progress, completed)
4. The type of each task (retrieval, reasoning, composition)

This visualization gives you insight into the agent's "thinking process" and helps you understand how complex writing tasks are broken down and solved step by step.

To view the task execution in real-time, simply start a generation job and watch the task list update automatically as the agent works.


## Contributing

We welcome contributions from the community to help improve WriteHERE! Here's how you can contribute:

### Code Contributions

1. **Fork the repository** and create your feature branch from `main`
2. **Set up your development environment** following the installation instructions above
3. **Make your changes**, ensuring they follow the project's coding style and conventions
4. **Add tests** for any new functionality
5. **Ensure all tests pass** by running the test suite
6. **Submit a pull request** with a clear description of your changes and their benefits

### Bug Reports and Feature Requests

- Use the **Issues** tab to report bugs or suggest new features
- For bugs, include detailed steps to reproduce, expected behavior, and actual behavior
- For feature requests, describe the functionality you'd like to see and how it would benefit the project

### Documentation Improvements

- Help improve our documentation by fixing errors, adding examples, or clarifying instructions
- Documentation changes can be submitted through pull requests just like code changes

### Community Support

- Answer questions from other users in the Issues section
- Share your experiences and use cases with the community

### Development Guidelines

- Follow the existing code style and architecture
- Document new functions, classes, and modules
- Write clear commit messages that explain the purpose of your changes
- Keep pull requests focused on a single feature or bug fix

By contributing to WriteHERE, you agree that your contributions will be licensed under the project's MIT License.

## Citation

If you use this code in your research, please cite our paper:

```bibtex
@misc{xiong2025beyondoutlining,
      title={Beyond Outlining: Heterogeneous Recursive Planning for Adaptive Long-form Writing with Language Models}, 
      author={Ruibin Xiong and Yimeng Chen and Dmitrii Khizbullin and Jürgen Schmidhuber},
      year={2025},
      eprint={2503.08275},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2503.08275}
}
```

## License

[MIT License](LICENSE)

This project is open-source and non-commercial. You are free to use, modify, and distribute the code for research, educational, and personal purposes.