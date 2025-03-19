import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  TextField, 
  Button, 
  Box, 
  Paper, 
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Divider,
  FormControlLabel,
  Switch,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  InputAdornment,
  Tooltip,
  Autocomplete,
  Chip,
  Snackbar
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import InfoIcon from '@mui/icons-material/Info';
import { generateReport, pingAPI } from '../utils/api';
import HistoryPanel from '../components/HistoryPanel';

// Recommended model options
const commonModels = [
  { label: 'Claude 3.7 Sonnet (Recommended)', value: 'claude-3-7-sonnet-20250219' },
  { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022' },
  { label: 'GPT-4o', value: 'gpt-4o' },
];

// Example prompts for report generation
const examplePrompts = [
  "What is the commercial value of a long-article writing AI Agent? Write a detailed analysis report.",
  "Write a comprehensive report on the impact of artificial intelligence on healthcare, focusing on diagnosis, treatment planning, and patient outcomes.",
  "Prepare a detailed report on sustainable energy solutions for developing countries, including their economic viability and environmental impact."
];

const ReportGenerationPage = () => {
  const [prompt, setPrompt] = useState('');
  const [model, setModel] = useState('claude-3-5-sonnet-20241022');
  const [searchEngine, setSearchEngine] = useState('bing');
  const [enableSearch, setEnableSearch] = useState(true);
  const [apiKeys, setApiKeys] = useState({
    openai: localStorage.getItem('openai_api_key') || '',
    claude: localStorage.getItem('claude_api_key') || '',
    serpapi: localStorage.getItem('serpapi_api_key') || '',
  });
  const [showApiSection, setShowApiSection] = useState(false);
  const [showOpenAIKey, setShowOpenAIKey] = useState(false);
  const [showClaudeKey, setShowClaudeKey] = useState(false);
  const [showSerpApiKey, setShowSerpApiKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [showStatus, setShowStatus] = useState(false);
  const navigate = useNavigate();
  
  // Save API keys to localStorage when they change
  useEffect(() => {
    if (apiKeys.openai) localStorage.setItem('openai_api_key', apiKeys.openai);
    if (apiKeys.claude) localStorage.setItem('claude_api_key', apiKeys.claude);
    if (apiKeys.serpapi) localStorage.setItem('serpapi_api_key', apiKeys.serpapi);
  }, [apiKeys]);
  
  const handleApiKeyChange = (provider, value) => {
    setApiKeys(prev => ({
      ...prev,
      [provider]: value
    }));
  };

  // Check if API is available on component mount
  useEffect(() => {
    async function checkAPIConnection() {
      try {
        await pingAPI();
        // API is available, nothing to do
      } catch (err) {
        setError('Cannot connect to the backend server. Please make sure it is running at http://localhost:' + (process.env.REACT_APP_BACKEND_PORT || '5001') + '.');
      }
    }
    
    checkAPIConnection();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt) {
      setError('Please provide a prompt for report generation.');
      return;
    }
    
    // Check if the appropriate API keys are provided
    const isOpenAIModel = model.toLowerCase().includes('gpt');
    const isClaudeModel = model.toLowerCase().includes('claude');
    
    if (isOpenAIModel && !apiKeys.openai) {
      setError('Please provide your OpenAI API key in the settings section.');
      setShowApiSection(true);
      return;
    }
    
    if (isClaudeModel && !apiKeys.claude) {
      setError('Please provide your Anthropic Claude API key in the settings section.');
      setShowApiSection(true);
      return;
    }
    
    if (enableSearch && !apiKeys.serpapi) {
      setError('Please provide your SerpAPI key in the settings section to enable search functionality.');
      setShowApiSection(true);
      return;
    }
    
    // First, check if the server is reachable
    try {
      await pingAPI();
    } catch (err) {
      setError('Cannot connect to the backend server. Please make sure it is running at http://localhost:' + (process.env.REACT_APP_BACKEND_PORT || '5001') + '.');
      return;
    }
    
    setLoading(true);
    setError('');
    setStatusMessage('Initiating report generation...');
    setShowStatus(true);
    
    try {
      // Call the backend API to start report generation
      const response = await generateReport({
        prompt,
        model,
        enableSearch,
        searchEngine,
        apiKeys: {
          openai: apiKeys.openai,
          claude: apiKeys.claude,
          serpapi: apiKeys.serpapi
        }
      });
      
      // Navigate to the results page with the task ID
      if (response && response.taskId) {
        setStatusMessage('Report generation started successfully!');
        navigate(`/results/${response.taskId}`, { 
          state: { 
            taskId: response.taskId,
            prompt,
            model,
            searchEngine: enableSearch ? searchEngine : 'none',
            type: 'report',
            status: 'generating'
          } 
        });
      } else {
        throw new Error('No task ID returned from the server');
      }
    } catch (err) {
      setLoading(false);
      setStatusMessage('');
      setError('Error starting report generation: ' + (err.message || 'Unknown error'));
      console.error('Report generation error:', err);
    }
  };

  const handleExampleClick = (example) => {
    setPrompt(example);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Technical Report Generation
        </Typography>
        <Typography variant="body1" paragraph>
          Generate comprehensive technical reports using our Heterogeneous Recursive Planning framework.
          The system integrates information retrieval, logical reasoning, and content composition to 
          create well-structured and informative reports.
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}
      
      <HistoryPanel />
      
      <Snackbar
        open={showStatus}
        autoHideDuration={6000}
        onClose={() => setShowStatus(false)}
        message={statusMessage}
      />

      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                label="Report Topic"
                multiline
                rows={6}
                fullWidth
                required
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe the technical report you want to generate..."
                variant="outlined"
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <Autocomplete
                freeSolo
                options={commonModels}
                getOptionLabel={(option) => {
                  if (typeof option === 'string') {
                    return option;
                  }
                  return option.label || '';
                }}
                value={model}
                onChange={(event, newValue) => {
                  if (typeof newValue === 'string') {
                    setModel(newValue);
                  } else if (newValue && newValue.value) {
                    setModel(newValue.value);
                  } else {
                    setModel('');
                  }
                }}
                onInputChange={(event, newInputValue) => {
                  if (event && event.type === 'change') {
                    setModel(newInputValue);
                  }
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Model"
                    variant="outlined"
                    fullWidth
                    placeholder="Enter or select a model"
                    helperText="Enter any model name or select from suggestions"
                  />
                )}
                renderOption={(props, option) => (
                  <li {...props}>
                    <Box sx={{ display: 'flex', flexDirection: 'column' }}>
                      <Typography variant="body1">{option.label}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {option.value}
                      </Typography>
                    </Box>
                  </li>
                )}
                renderTags={(value, getTagProps) => 
                  value.map((option, index) => (
                    <Chip
                      label={option.label}
                      size="small"
                      {...getTagProps({ index })}
                    />
                  ))
                }
              />
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch 
                    checked={enableSearch} 
                    onChange={(e) => setEnableSearch(e.target.checked)} 
                  />
                }
                label="Enable Search"
              />
              
              <FormControl fullWidth sx={{ mt: 1 }} disabled={!enableSearch}>
                <InputLabel id="search-engine-label">Search Engine</InputLabel>
                <Select
                  labelId="search-engine-label"
                  id="search-engine-select"
                  value={searchEngine}
                  label="Search Engine"
                  onChange={(e) => setSearchEngine(e.target.value)}
                >
                  {/* <MenuItem value="google">Google</MenuItem> */}
                  <MenuItem value="bing">Bing</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4} sx={{ display: 'flex', alignItems: 'center' }}>
              <Button
                type="submit"
                variant="contained"
                color="secondary"
                size="large"
                fullWidth
                disabled={loading || !prompt}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : 'Generate Report'}
              </Button>
            </Grid>
            
            <Grid item xs={12}>
              <Accordion 
                expanded={showApiSection}
                onChange={() => setShowApiSection(!showApiSection)}
                sx={{
                  mt: 2,
                  backgroundColor: 'grey.50',
                  boxShadow: 'none',
                  '&:before': {
                    display: 'none',
                  },
                  border: '1px solid',
                  borderColor: 'grey.200',
                  borderRadius: '8px !important',
                }}
              >
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls="api-keys-content"
                  id="api-keys-header"
                  sx={{ borderRadius: 2 }}
                >
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
                    API Settings
                    <Tooltip title="Your API keys are stored locally in your browser and are never sent to our servers">
                      <IconButton size="small" sx={{ ml: 1 }}>
                        <InfoIcon fontSize="small" color="action" />
                      </IconButton>
                    </Tooltip>
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={4}>
                      <TextField
                        label="OpenAI API Key"
                        fullWidth
                        variant="outlined"
                        value={apiKeys.openai}
                        onChange={(e) => handleApiKeyChange('openai', e.target.value)}
                        type={showOpenAIKey ? 'text' : 'password'}
                        placeholder="sk-..."
                        helperText="Required for GPT models"
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                aria-label="toggle password visibility"
                                onClick={() => setShowOpenAIKey(!showOpenAIKey)}
                                edge="end"
                              >
                                {showOpenAIKey ? <VisibilityOff /> : <Visibility />}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        label="Anthropic API Key"
                        fullWidth
                        variant="outlined"
                        value={apiKeys.claude}
                        onChange={(e) => handleApiKeyChange('claude', e.target.value)}
                        type={showClaudeKey ? 'text' : 'password'}
                        placeholder="sk-ant-..."
                        helperText="Required for Claude models"
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                aria-label="toggle password visibility"
                                onClick={() => setShowClaudeKey(!showClaudeKey)}
                                edge="end"
                              >
                                {showClaudeKey ? <VisibilityOff /> : <Visibility />}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12} md={4}>
                      <TextField
                        label="SerpAPI Key"
                        fullWidth
                        variant="outlined"
                        value={apiKeys.serpapi}
                        onChange={(e) => handleApiKeyChange('serpapi', e.target.value)}
                        type={showSerpApiKey ? 'text' : 'password'}
                        placeholder="..."
                        helperText="Required for search functionality"
                        InputProps={{
                          endAdornment: (
                            <InputAdornment position="end">
                              <IconButton
                                aria-label="toggle password visibility"
                                onClick={() => setShowSerpApiKey(!showSerpApiKey)}
                                edge="end"
                              >
                                {showSerpApiKey ? <VisibilityOff /> : <Visibility />}
                              </IconButton>
                            </InputAdornment>
                          ),
                        }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary">
                        Your API keys are stored securely in your browser's local storage and are never sent to our servers.
                        They are only used to make direct API calls to the respective services from your browser.
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
        </form>
      </Paper>

      <Box sx={{ mb: 6 }}>
        <Typography variant="h5" gutterBottom>
          Example Topics
        </Typography>
        <Typography variant="body2" paragraph>
          Click on any example to use it as your prompt:
        </Typography>
        
        <Grid container spacing={3}>
          {examplePrompts.map((example, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card 
                sx={{ 
                  height: '100%', 
                  cursor: 'pointer',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-5px)',
                    boxShadow: 3
                  }
                }}
                onClick={() => handleExampleClick(example)}
              >
                <CardContent>
                  <Typography variant="body2" color="text.secondary">
                    {example.length > 200 ? example.substring(0, 200) + '...' : example}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <Typography variant="h5" gutterBottom>
          Tips for Effective Report Prompts
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" fontWeight="bold">
              Define Scope
            </Typography>
            <Typography variant="body2">
              Clearly specify the scope and focus of your report to ensure the content
              addresses your specific needs.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" fontWeight="bold">
              Indicate Structure
            </Typography>
            <Typography variant="body2">
              If you have specific requirements for the structure or sections of the report,
              mention them in your prompt.
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" fontWeight="bold">
              Specify Depth
            </Typography>
            <Typography variant="body2">
              Indicate whether you need a general overview or an in-depth analysis with
              detailed technical information and citations.
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default ReportGenerationPage;