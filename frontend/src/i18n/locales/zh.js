export default {
    common: {
      language: '语言',
      english: '英文',
      chinese: '中文',
      home: '首页',
      storyGeneration: '故事生成',
      reportGeneration: '报告生成',
      about: '关于',
      generate: '生成',
      loading: '加载中...',
      error: '错误',
      success: '成功',
      submit: '提交',
      cancel: '取消',
      save: '保存',
      delete: '删除',
      edit: '编辑',
      view: '查看',
      refresh: '刷新',
      back: '返回',
      apiSettings: 'API 设置'
    },
    header: {
    },
    storyGeneration: {
      title: '创意故事生成',
      description: '使用我们的异构递归规划框架生成创意故事。提供描述您想要创建的故事的提示，我们的系统将递归地规划并生成连贯的叙述。',
      promptLabel: '故事提示',
      promptPlaceholder: '描述您想要生成的故事...',
      modelLabel: '模型',
      modelPlaceholder: '输入或选择一个模型',
      modelHelperText: '输入任何模型名称或从建议中选择',
      languageOutputLabel: '输出语言',
      languageOutputHelperText: '选择生成故事的语言',
      outputEnglish: '英文输出',
      outputChinese: '中文输出',
      apiKeySettings: 'API 设置',
      apiKeyInfo: '您的 API 密钥存储在浏览器本地，从不发送到我们的服务器',
      openaiApiKey: 'OpenAI API 密钥',
      openaiHelperText: 'GPT 模型需要',
      claudeApiKey: 'Anthropic Claude API 密钥',
      claudeHelperText: 'Claude 模型需要',
      apiKeyPrivacyNote: '您的 API 密钥安全地存储在浏览器的本地存储中，从不发送到我们的服务器。它们仅用于从您的浏览器直接调用相应服务的 API。',
      generateStory: '生成故事',
      noPromptError: '请提供故事生成提示。',
      noOpenAIKeyError: '请在设置部分提供您的 OpenAI API 密钥。',
      noClaudeKeyError: '请在设置部分提供您的 Anthropic Claude API 密钥。',
      connectionError: '无法连接到后端服务器。请确保它在 http://localhost:5002 运行。',
      initiatingGeneration: '正在初始化故事生成...',
      generationSuccess: '故事生成成功启动！',
      examplePromptsTitle: '示例提示',
      examplePromptsSubtitle: '点击任何示例将其用作您的提示：',
      tipsTitle: '有效故事提示技巧',
      beSpecificTitle: '具体详细',
      beSpecificDescription: '提供您想要故事中的角色、背景和情节元素的具体细节。',
      defineParametersTitle: '定义参数',
      defineParametersDescription: '指定您想要的故事视角（第一人称、第三人称）、语调（幽默、严肃）和长度。',
      allowCreativityTitle: '允许创造性',
      allowCreativityDescription: '在提供指导的同时，给系统留出空间来发展增强故事的创造性元素。',
      examplePrompt1: '写一个太阳不升起的一天的故事。以第三人称的视角讲述。包括一个在太阳消失时正在户外玩耍的女孩的故事。',
      examplePrompt2: '写一个科幻故事，讲述人类在火星上的第一个殖民地面临着在这颗行星表面下的意外发现。',
      examplePrompt3: '写一个设在小海滨镇的神秘故事，每当满月时就会发生奇怪的现象。主角是一位怀疑论的记者，正在调查这些事件。',
      errors: {
        emptyPrompt: '请提供故事生成提示。',
        missingOpenAIKey: '请在设置部分提供您的 OpenAI API 密钥。',
        missingClaudeKey: '请在设置部分提供您的 Anthropic Claude API 密钥。',
        backendConnection: '无法连接到后端服务器。请确保它在 http://localhost:5002 运行。',
        generationError: '启动故事生成时出错：',
        unknown: '未知错误',
        noTaskId: '服务器未返回任务 ID'
      },
      status: {
        initiating: '正在初始化故事生成...',
        started: '故事生成成功启动！'
      }
    },
    reportGeneration: {
      title: '报告生成',
      description: '使用我们具有搜索功能的异构递归规划框架生成任何主题的综合报告。我们的系统将根据您的要求进行研究、规划并创建结构良好的报告。',
      promptLabel: '报告主题',
      promptPlaceholder: '描述您想要生成的报告...',
      modelLabel: '模型',
      modelPlaceholder: '输入或选择一个模型',
      modelHelperText: '输入任何模型名称或从建议中选择',
      enableSearchLabel: '启用搜索',
      enableSearchDescription: '允许系统搜索网络以获取最新信息',
      searchEngineLabel: '搜索引擎',
      languageOutputLabel: '输出语言',
      languageOutputHelperText: '选择生成报告的语言',
      serpapiKeyLabel: 'SerpAPI 密钥',
      serpapiHelperText: '网络搜索功能需要',
      generateReport: '生成报告',
      examplePromptsTitle: '示例主题',
      examplePromptsSubtitle: '点击任何示例将其用作您的提示：',
      tipsTitle: '有效报告提示技巧',
      defineScopeTitle: '定义范围',
      defineScopeDescription: '明确指定报告的范围和重点，确保内容满足您的特定需求。',
      indicateStructureTitle: '指明结构',
      indicateStructureDescription: '如果您对报告的结构或章节有特定要求，请在提示中提及。',
      specifyDepthTitle: '指定深度',
      specifyDepthDescription: '说明您是需要一般性概述还是需要带有详细技术信息和引用的深入分析。',
      examplePrompt1: '长文章写作AI代理的商业价值是什么？写一份详细的分析报告。',
      examplePrompt2: '撰写一份关于人工智能对医疗保健影响的综合报告，重点关注诊断、治疗计划和患者结果。',
      examplePrompt3: '为发展中国家准备一份关于可持续能源解决方案的详细报告，包括其经济可行性和环境影响。',
      errors: {
        emptyPrompt: '请提供报告生成提示。',
        missingOpenAIKey: '请在设置部分提供您的 OpenAI API 密钥。',
        missingClaudeKey: '请在设置部分提供您的 Anthropic Claude API 密钥。',
        missingSerpapiKey: '请在设置部分提供您的 SerpAPI 密钥以启用搜索功能。',
        backendConnection: '无法连接到后端服务器。请确保它在 http://localhost:5002 运行。',
        generationError: '启动报告生成时出错：',
        unknown: '未知错误',
        noTaskId: '服务器未返回任务 ID'
      },
      status: {
        initiating: '正在初始化报告生成...',
        started: '报告生成成功启动！'
      },
      searchEngines: {
        google: '谷歌',
        bing: '必应'
      }
    },
    results: {
      title: '生成结果',
      promptLabel: '原始提示：',
      modelUsed: '使用的模型：',
      languageUsed: '使用的语言：',
      generationTime: '生成时间：',
      statusLabel: '状态：',
      statusGenerating: '生成中...',
      statusCompleted: '已完成',
      statusError: '错误',
      copyToClipboard: '复制到剪贴板',
      copySuccess: '已复制到剪贴板！',
      taskGraphTitle: '任务图',
      resultTitle: '结果',
      downloadAsText: '下载为文本',
      downloadAsMarkdown: '下载为 Markdown',
      returnToGenerator: '创建另一个'
    },
    history: {
      title: '生成历史',
      empty: '未找到生成历史。',
      recentGenerations: '最近的生成',
      loadMore: '加载更多',
      storyType: '故事',
      reportType: '报告',
      deleteConfirm: '您确定要删除这个生成吗？',
      deleted: '生成已成功删除'
    }
  }; 