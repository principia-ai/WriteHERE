export default {
  common: {
    language: 'Language',
    english: 'English',
    chinese: 'Chinese',
    home: 'Home',
    storyGeneration: 'Story Generation',
    reportGeneration: 'Report Generation',
    about: 'About',
    generate: 'Generate',
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    submit: 'Submit',
    cancel: 'Cancel',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    view: 'View',
    refresh: 'Refresh',
    back: 'Back',
    apiSettings: 'API Settings'
  },
  header: {
  },
  storyGeneration: {
    title: 'Story Generation',
    description: 'Generate creative stories using advanced AI models. Enter your prompt below to begin.',
    promptLabel: 'Story Prompt',
    promptPlaceholder: 'Enter your story prompt here...',
    modelLabel: 'Select Model',
    modelHelperText: 'Choose the AI model for story generation',
    languageOutputLabel: 'Output Language',
    outputEnglish: 'English',
    outputChinese: 'Chinese',
    generateStory: 'Generate Story',
    apiKeySettings: 'API Key Settings',
    apiKeyInfo: 'Configure your API keys for different AI models',
    openaiApiKey: 'OpenAI API Key',
    openaiHelperText: 'Required for GPT models',
    claudeApiKey: 'Claude API Key',
    claudeHelperText: 'Required for Claude models',
    apiKeyPrivacyNote: 'Your API keys are stored securely in your browser and never shared.',
    examplePromptsTitle: 'Example Prompts',
    examplePromptsSubtitle: 'Here are some example prompts to help you get started',
    examplePrompt1: 'Write an adventure story about a time traveler',
    examplePrompt2: 'Create a sci-fi story set in a future world',
    examplePrompt3: 'Tell a heartwarming family story',
    tipsTitle: 'Writing Tips',
    beSpecificTitle: 'Be Specific',
    beSpecificDescription: 'Provide specific scenes, characters, and plot directions',
    defineParametersTitle: 'Define Parameters',
    defineParametersDescription: 'Clarify the story background, theme, and style',
    allowCreativityTitle: 'Stay Open',
    allowCreativityDescription: 'Let AI be creative within your framework',
    errors: {
      backendConnection: 'Unable to connect to the server. Please try again later.',
      emptyPrompt: 'Please enter a story prompt.',
      missingOpenAIKey: 'OpenAI API key is required for GPT models.',
      missingClaudeKey: 'Claude API key is required for Claude models.',
      noTaskId: 'Failed to start story generation.',
      generationError: 'Error generating story:',
      unknown: 'An unknown error occurred.'
    },
    status: {
      initiating: 'Starting story generation...',
      started: 'Story generation started'
    },
    promptLanguageLabel: 'Prompt Language',
    promptLanguageHelperText: 'Choose the language for generation prompts',
    promptLanguages: {
      english: 'English Prompt',
      chinese: 'Chinese Prompt'
    }
  },
  reportGeneration: {
    title: 'Report Generation',
    description: 'Generate detailed reports using advanced AI models. Enter your prompt below to begin.',
    promptLabel: 'Report Prompt',
    promptPlaceholder: 'Enter your report prompt here...',
    modelLabel: 'Select Model',
    modelHelperText: 'Choose the AI model for report generation',
    languageOutputLabel: 'Output Language',
    languageOutputHelperText: 'Choose the language for generated content',
    outputEnglish: 'Generate in English',
    outputChinese: 'Generate in Chinese',
    generateReport: 'Generate Report',
    apiKeySettings: 'API Key Settings',
    apiKeyInfo: 'Configure your API keys for different AI models',
    openaiApiKey: 'OpenAI API Key',
    openaiHelperText: 'Required for GPT models',
    claudeApiKey: 'Claude API Key',
    claudeHelperText: 'Required for Claude models',
    serpapiKeyLabel: 'Serpapi API Key',
    serpapiHelperText: 'Required for search functionality',
    apiKeyPrivacyNote: 'Your API keys are stored securely in your browser and never shared.',
    examplePromptsTitle: 'Example Prompts',
    examplePromptsSubtitle: 'Here are some example prompts to help you get started',
    examplePrompt1: 'Analyze market trends and future prospects of an industry',
    examplePrompt2: 'Evaluate the feasibility and potential risks of a project',
    examplePrompt3: 'Summarize recent advances in a technical field',
    tipsTitle: 'Generation Tips',
    defineScopeTitle: 'Define Scope',
    defineScopeDescription: 'Specify the subject areas and key topics to be covered in the report',
    indicateStructureTitle: 'Indicate Structure',
    indicateStructureDescription: 'Outline the desired structure and section organization',
    specifyDepthTitle: 'Specify Depth',
    specifyDepthDescription: 'Determine the level of analysis and detail needed for each section',
    beSpecificTitle: 'Be Specific',
    beSpecificDescription: 'Provide specific context and requirements for more accurate reports',
    defineParametersTitle: 'Define Parameters',
    defineParametersDescription: 'Clarify the scope, depth, and key points of the report',
    allowCreativityTitle: 'Stay Open',
    allowCreativityDescription: 'Allow AI to be creative within professional frameworks',
    errors: {
      backendConnection: 'Unable to connect to the server. Please try again later.',
      emptyPrompt: 'Please enter a report prompt.',
      missingOpenAIKey: 'OpenAI API key is required for GPT models.',
      missingClaudeKey: 'Claude API key is required for Claude models.',
      missingSerpapiKey: 'Serpapi API key is required for search functionality.',
      noTaskId: 'Failed to start report generation.',
      generationError: 'Error generating report:',
      unknown: 'An unknown error occurred.'
    },
    status: {
      initiating: 'Starting report generation...',
      started: 'Report generation started'
    },
    enableSearchLabel: 'Enable Search',
    searchEngineLabel: 'Search Engine',
    searchEngineHelperText: 'Choose the search engine for information retrieval',
    enableSearchDescription: 'Use search engine to get latest information and data',
    searchEngines: {
      bing: 'Bing',
      google: 'Google',
      custom: 'Custom'
    },
    promptLanguageLabel: 'Prompt Language',
    promptLanguageHelperText: 'Choose the language for writing prompts',
    promptLanguages: {
      english: 'Write prompts in English',
      chinese: 'Write prompts in Chinese'
    }
  },
  results: {
    title: "Generation Details",
    promptLabel: "Prompt",
    modelUsed: "Model",
    searchEngineUsed: "Search Engine",
    statusLabel: "Status",
    statusCompleted: "Complete",
    statusGenerating: "In Progress",
    complete: "complete",
    secondsElapsed: "seconds elapsed",
    generationTimeEstimate: "This may take several minutes depending on the complexity of the task.",
    generatedStory: "Generated Story",
    generatedReport: "Generated Report",
    resultTitle: "Result",
    taskGraphTitle: "Task Graph",
    copyToClipboard: "Copy to Clipboard",
    downloadAsText: "Download as Text",
    downloadAsMarkdown: "Download as Markdown",
    returnToGenerator: "Generate Another"
  },
  history: {
    title: 'Generation History',
    empty: 'No generation history found.',
    recentGenerations: 'Recent Generations',
    loadMore: 'Load More',
    storyType: 'Story',
    reportType: 'Report',
    deleteConfirm: 'Are you sure you want to delete this generation?',
    deleted: 'Generation successfully deleted'
  },
  home: {
    advancedAIWriting: "Advanced AI Writing Framework",
    title: "Open Framework for Human-like Long-form Writing",
    description: "A general agent framework for long-form writing that achieves adaptive content generation through recursive task decomposition and dynamic integration of heterogeneous tasks/tools.",
    getStarted: "Get Started",
    learnMore: "Learn More",
    howItWorks: "How It Works",
    howItWorksDescription: "Heterogeneous Recursive Planning goes beyond traditional writing approaches by mimicking human cognitive processes through adaptive task decomposition.",
    retrieval: "Retrieval",
    retrievalDescription: "Dynamically searches for relevant information during the writing process, ensuring factual accuracy and comprehensive coverage of the topic.",
    reasoning: "Reasoning",
    reasoningDescription: "Applies logical analysis to plan, organize, and refine content structure, ensuring coherent and well-structured output that follows a logical flow.",
    composition: "Composition",
    compositionDescription: "Generates articulate and engaging content based on the retrieved information and reasoning, adapting to context and maintaining consistent style and tone.",
    generateContent: "Generate Content",
    generateContentDescription: "Choose the type of content you want to create and experience the power of heterogeneous recursive planning.",
    creativeStoryGeneration: "Creative Story Generation",
    craftNarratives: "Craft engaging narratives and fiction",
    storyDescription: "Generate creative narratives, fiction, and stories using our heterogeneous recursive planning approach. Perfect for creative writing, entertainment, and educational content.",
    fiction: "Fiction",
    shortStories: "Short Stories",
    creativeWriting: "Creative Writing",
    generateStory: "Generate Story",
    technicalReportGeneration: "Technical Report Generation",
    createDocuments: "Create comprehensive, fact-based documents",
    reportDescription: "Create comprehensive technical reports and documentation with accurate information retrieval and logical reasoning. Ideal for business, academic, and technical documentation.",
    research: "Research",
    analysis: "Analysis",
    documentation: "Documentation",
    generateReport: "Generate Report",
    visualizeProcess: "Visualize the Writing Process",
    visualizeDescription: "Our framework makes the writing process transparent by providing a detailed task list showing how complex writing tasks are broken down into manageable sub-tasks that integrate retrieval, reasoning, and composition.",
    step1: "Initial decomposition of the main writing task",
    step2: "Recursive planning and subtask generation",
    step3: "Dynamic integration of retrieval, reasoning, and composition",
    step4: "Content generation with coherent, high-quality output",
    readyToTransform: "Ready to transform your writing process?",
    transformDescription: "Experience the next generation of AI-assisted writing with our heterogeneous recursive planning framework.",
    tryStoryGeneration: "Try Story Generation",
    tryReportGeneration: "Try Report Generation"
  },
  about: {
    title: "About the Project",
    introduction: "Heterogeneous Recursive Planning represents a significant advancement in AI-powered content generation, enabling more adaptive and human-like writing through innovative task decomposition and planning.",
    overview: "Overview",
    overviewDescription: "Heterogeneous Recursive Planning is a general agent framework for long-form writing that achieves human-like adaptive writing through recursive task decomposition and dynamic integration of three fundamental task types: retrieval, reasoning, and composition.",
    traditionalApproach: "Unlike traditional approaches that rely on predetermined workflows and rigid thinking patterns, this framework:",
    feature1: "Eliminates workflow restrictions through a planning mechanism that interleaves recursive task decomposition and execution",
    feature2: "Facilitates heterogeneous task decomposition by integrating different task types",
    feature3: "Adapts dynamically during the writing process, similar to human writing behavior",
    evaluationResult: "Our evaluations on both fiction writing and technical report generation demonstrate that this method consistently outperforms state-of-the-art approaches across all evaluation metrics.",
    keyFeatures: "Key Features",
    recursiveTask: "Recursive task decomposition and execution",
    recursiveTaskDesc: "Breaking complex writing tasks into manageable sub-tasks",
    dynamicIntegration: "Dynamic integration of diverse task types",
    dynamicIntegrationDesc: "Seamlessly combining retrieval, reasoning, and composition",
    flexibleAdaptation: "Flexible adaptation during writing",
    flexibleAdaptationDesc: "Adjusting the plan as context evolves",
    multiDomainSupport: "Support for multiple writing domains",
    multiDomainSupportDesc: "Works for both creative fiction and technical reports",
    technicalImplementation: "Technical Implementation",
    taskGraphDesc: "The framework is built on a task graph architecture that represents writing tasks as nodes with dependencies. Each node can be one of three types:",
    compositionType: "Composition (Write)",
    compositionTypeDesc: "Creating actual content",
    retrievalType: "Retrieval (Search)",
    retrievalTypeDesc: "Gathering information",
    reasoningType: "Reasoning (Think)",
    reasoningTypeDesc: "Analyzing and planning",
    systemImplementation: "The system uses advanced language models (LLMs) like GPT-4 and Claude to execute these tasks, with a recursive planning mechanism that can decompose tasks and adapt plans dynamically.",
    researchPublication: "Research Publication",
    paperIntro: "This project is based on research described in the paper:",
    projectTeam: "Project Team"
  }
}; 