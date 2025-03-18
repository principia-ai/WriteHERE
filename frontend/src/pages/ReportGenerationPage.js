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
  Snackbar,
  FormHelperText
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import InfoIcon from '@mui/icons-material/Info';
import { generateReport, pingAPI } from '../utils/api';
import HistoryPanel from '../components/HistoryPanel';
import { useTranslation } from 'react-i18next';
import { getCurrentLanguage } from '../i18n';

// Recommended model options
const commonModels = [
  { label: 'GPT-4o', value: 'gpt-4o' },
  { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022' },
  { label: 'Claude 3.7 Sonnet (Recommended)', value: 'claude-3-7-sonnet-20250219' },
];

const ReportGenerationPage = () => {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState('');
  const [model, setModel] = useState('claude-3-5-sonnet-20241022');
  const [searchEngine, setSearchEngine] = useState('bing');
  const [enableSearch, setEnableSearch] = useState(true);
  const [outputLanguage, setOutputLanguage] = useState(() => {
    return localStorage.getItem('outputLanguage') || (localStorage.getItem('preferredLanguage') || 'english');
  });
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
  
  // Get example prompts from translations
  const examplePrompts = [
    t('reportGeneration.examplePrompt1'),
    t('reportGeneration.examplePrompt2'),
    t('reportGeneration.examplePrompt3')
  ];
  
  // Save output language preference to localStorage
  useEffect(() => {
    localStorage.setItem('outputLanguage', outputLanguage);
  }, [outputLanguage]);
  
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
        setError(t('reportGeneration.errors.backendConnection'));
      }
    }
    
    checkAPIConnection();
  }, [t]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt) {
      setError(t('reportGeneration.errors.emptyPrompt'));
      return;
    }
    
    // Check if the appropriate API keys are provided
    const isOpenAIModel = model.toLowerCase().includes('gpt');
    const isClaudeModel = model.toLowerCase().includes('claude');
    
    if (isOpenAIModel && !apiKeys.openai) {
      setError(t('reportGeneration.errors.missingOpenAIKey'));
      setShowApiSection(true);
      return;
    }
    
    if (isClaudeModel && !apiKeys.claude) {
      setError(t('reportGeneration.errors.missingClaudeKey'));
      setShowApiSection(true);
      return;
    }
    
    if (enableSearch && !apiKeys.serpapi) {
      setError(t('reportGeneration.errors.missingSerpapiKey'));
      setShowApiSection(true);
      return;
    }
    
    // First, check if the server is reachable
    try {
      await pingAPI();
    } catch (err) {
      setError(t('reportGeneration.errors.backendConnection'));
      return;
    }
    
    setLoading(true);
    setError('');
    setStatusMessage(t('reportGeneration.status.initiating'));
    setShowStatus(true);
    
    try {
      // Call the backend API to start report generation
      const response = await generateReport({
        prompt,
        model,
        enableSearch,
        searchEngine,
        language: outputLanguage,
        apiKeys: {
          openai: apiKeys.openai,
          claude: apiKeys.claude,
          serpapi: apiKeys.serpapi
        }
      });
      
      // Navigate to the results page with the task ID
      if (response && response.taskId) {
        setStatusMessage(t('reportGeneration.status.started'));
        navigate(`/results/${response.taskId}`, { 
          state: { 
            taskId: response.taskId,
            prompt,
            model,
            language: outputLanguage,
            searchEngine: enableSearch ? searchEngine : 'none',
            type: 'report',
            status: 'generating'
          } 
        });
      } else {
        throw new Error(t('reportGeneration.errors.noTaskId'));
      }
    } catch (err) {
      setLoading(false);
      setStatusMessage('');
      setError(t('reportGeneration.errors.generationError') + (err.message || t('reportGeneration.errors.unknown')));
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
          {t('reportGeneration.title')}
        </Typography>
        <Typography variant="body1" paragraph>
          {t('reportGeneration.description')}
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
                label={t('reportGeneration.promptLabel')}
                multiline
                rows={6}
                fullWidth
                required
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder={t('reportGeneration.promptPlaceholder')}
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
                    label={t('reportGeneration.modelLabel')}
                    variant="outlined"
                    fullWidth
                    placeholder={t('reportGeneration.modelPlaceholder')}
                    helperText={t('reportGeneration.modelHelperText')}
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
                label={t('reportGeneration.enableSearchLabel')}
              />
              
              <FormControl fullWidth sx={{ mt: 1 }} disabled={!enableSearch}>
                <InputLabel id="search-engine-label">{t('reportGeneration.searchEngineLabel')}</InputLabel>
                <Select
                  labelId="search-engine-label"
                  id="search-engine-select"
                  value={searchEngine}
                  label={t('reportGeneration.searchEngineLabel')}
                  onChange={(e) => setSearchEngine(e.target.value)}
                >
                  {/* <MenuItem value="google">{t('reportGeneration.searchEngines.google')}</MenuItem> */}
                  <MenuItem value="bing">{t('reportGeneration.searchEngines.bing')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
                <InputLabel id="output-language-label">{t('reportGeneration.languageOutputLabel')}</InputLabel>
                <Select
                  labelId="output-language-label"
                  id="output-language-select"
                  value={outputLanguage}
                  onChange={(e) => setOutputLanguage(e.target.value)}
                  label={t('reportGeneration.languageOutputLabel')}
                >
                  <MenuItem value="english">{t('storyGeneration.outputEnglish')}</MenuItem>
                  <MenuItem value="chinese">{t('storyGeneration.outputChinese')}</MenuItem>
                </Select>
                <FormHelperText>{t('reportGeneration.languageOutputHelperText')}</FormHelperText>
              </FormControl>

              <Button
                type="submit"
                variant="contained"
                color="secondary"
                size="large"
                fullWidth
                disabled={loading || !prompt}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : t('reportGeneration.generateReport')}
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
                    {t('common.apiSettings')}
                    <Tooltip title={t('storyGeneration.apiKeyInfo')}>
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
                        label={t('storyGeneration.openaiApiKey')}
                        fullWidth
                        variant="outlined"
                        value={apiKeys.openai}
                        onChange={(e) => handleApiKeyChange('openai', e.target.value)}
                        type={showOpenAIKey ? 'text' : 'password'}
                        placeholder="sk-..."
                        helperText={t('storyGeneration.openaiHelperText')}
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
                        label={t('storyGeneration.claudeApiKey')}
                        fullWidth
                        variant="outlined"
                        value={apiKeys.claude}
                        onChange={(e) => handleApiKeyChange('claude', e.target.value)}
                        type={showClaudeKey ? 'text' : 'password'}
                        placeholder="sk-ant-..."
                        helperText={t('storyGeneration.claudeHelperText')}
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
                        label={t('reportGeneration.serpapiKeyLabel')}
                        fullWidth
                        variant="outlined"
                        value={apiKeys.serpapi}
                        onChange={(e) => handleApiKeyChange('serpapi', e.target.value)}
                        type={showSerpApiKey ? 'text' : 'password'}
                        placeholder="..."
                        helperText={t('reportGeneration.serpapiHelperText')}
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
                        {t('storyGeneration.apiKeyPrivacyNote')}
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
          {t('reportGeneration.examplePromptsTitle')}
        </Typography>
        <Typography variant="body2" paragraph>
          {t('reportGeneration.examplePromptsSubtitle')}
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
          {t('reportGeneration.tipsTitle')}
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" fontWeight="bold">
              {t('reportGeneration.defineScopeTitle')}
            </Typography>
            <Typography variant="body2">
              {t('reportGeneration.defineScopeDescription')}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" fontWeight="bold">
              {t('reportGeneration.indicateStructureTitle')}
            </Typography>
            <Typography variant="body2">
              {t('reportGeneration.indicateStructureDescription')}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" fontWeight="bold">
              {t('reportGeneration.specifyDepthTitle')}
            </Typography>
            <Typography variant="body2">
              {t('reportGeneration.specifyDepthDescription')}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default ReportGenerationPage;