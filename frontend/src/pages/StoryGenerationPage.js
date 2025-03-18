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
import { generateStory, pingAPI } from '../utils/api';
import HistoryPanel from '../components/HistoryPanel';
import { useTranslation } from 'react-i18next';
import { getCurrentLanguage } from '../i18n';

// Recommended model options
const commonModels = [
  { label: 'GPT-4o', value: 'gpt-4o' },
  { label: 'Claude 3.5 Sonnet', value: 'claude-3-5-sonnet-20241022' },
  { label: 'Claude 3.7 Sonnet (Recommended)', value: 'claude-3-7-sonnet-20250219' },
];

// Example prompts for story generation
// These will be replaced by translated versions in the component

const StoryGenerationPage = () => {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState('');
  const [model, setModel] = useState('gpt-4o');
  const [language, setLanguage] = useState(() => {
    return localStorage.getItem('preferredLanguage') || 'english';
  });
  const [outputLanguage, setOutputLanguage] = useState(() => {
    return localStorage.getItem('outputLanguage') || language;
  });
  const [apiKeys, setApiKeys] = useState({
    openai: localStorage.getItem('openai_api_key') || '',
    claude: localStorage.getItem('claude_api_key') || '',
  });
  const [showApiSection, setShowApiSection] = useState(false);
  const [showOpenAIKey, setShowOpenAIKey] = useState(false);
  const [showClaudeKey, setShowClaudeKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [showStatus, setShowStatus] = useState(false);
  const navigate = useNavigate();

  // Get example prompts from translations
  const examplePrompts = [
    t('storyGeneration.examplePrompt1'),
    t('storyGeneration.examplePrompt2'),
    t('storyGeneration.examplePrompt3')
  ];
  
  // Save API keys to localStorage when they change
  useEffect(() => {
    if (apiKeys.openai) localStorage.setItem('openai_api_key', apiKeys.openai);
    if (apiKeys.claude) localStorage.setItem('claude_api_key', apiKeys.claude);
  }, [apiKeys]);

  // Update language when preferredLanguage changes in localStorage
  useEffect(() => {
    const handleStorageChange = () => {
      setLanguage(localStorage.getItem('preferredLanguage') || 'english');
    };

    window.addEventListener('storage', handleStorageChange);
    
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  // Update output language when interface language changes
  useEffect(() => {
    if (!localStorage.getItem('outputLanguage')) {
      setOutputLanguage(language);
    }
  }, [language]);

  // Save output language preference to localStorage
  useEffect(() => {
    localStorage.setItem('outputLanguage', outputLanguage);
  }, [outputLanguage]);

  // Check if API is available on component mount
  useEffect(() => {
    async function checkAPIConnection() {
      try {
        await pingAPI();
        // API is available, nothing to do
      } catch (err) {
        setError(t('storyGeneration.errors.backendConnection'));
      }
    }
    
    checkAPIConnection();
  }, [t]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt) {
      setError(t('storyGeneration.errors.emptyPrompt'));
      return;
    }
    
    // Check if the appropriate API key is provided
    const isOpenAIModel = model.toLowerCase().includes('gpt');
    const isClaudeModel = model.toLowerCase().includes('claude');
    
    if (isOpenAIModel && !apiKeys.openai) {
      setError(t('storyGeneration.errors.missingOpenAIKey'));
      setShowApiSection(true);
      return;
    }
    
    if (isClaudeModel && !apiKeys.claude) {
      setError(t('storyGeneration.errors.missingClaudeKey'));
      setShowApiSection(true);
      return;
    }
    
    // First, check if the server is reachable
    try {
      await pingAPI();
    } catch (err) {
      setError(t('storyGeneration.errors.backendConnection'));
      return;
    }
    
    setLoading(true);
    setError('');
    setStatusMessage(t('storyGeneration.status.initiating'));
    setShowStatus(true);
    
    try {
      // Call the backend API to start story generation
      const response = await generateStory({
        prompt,
        model,
        language: outputLanguage,
        apiKeys: {
          openai: apiKeys.openai,
          claude: apiKeys.claude
        }
      });
      
      // Navigate to the results page with the task ID
      if (response && response.taskId) {
        setStatusMessage(t('storyGeneration.status.started'));
        navigate(`/results/${response.taskId}`, { 
          state: { 
            taskId: response.taskId,
            prompt,
            model,
            language: outputLanguage,
            type: 'story',
            status: 'generating'
          } 
        });
      } else {
        throw new Error(t('storyGeneration.errors.noTaskId'));
      }
    } catch (err) {
      setLoading(false);
      setStatusMessage('');
      setError(t('storyGeneration.errors.generationError') + (err.message || t('storyGeneration.errors.unknown')));
      console.error('Story generation error:', err);
    }
  };
  
  const handleApiKeyChange = (provider, value) => {
    setApiKeys(prev => ({
      ...prev,
      [provider]: value
    }));
  };

  const handleExampleClick = (example) => {
    setPrompt(example);
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          {t('storyGeneration.title')}
        </Typography>
        <Typography variant="body1" paragraph>
          {t('storyGeneration.description')}
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
                label={t('storyGeneration.promptLabel')}
                multiline
                rows={6}
                fullWidth
                required
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder={t('storyGeneration.promptPlaceholder')}
                variant="outlined"
              />
            </Grid>

            <Grid item xs={12} md={6}>
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
                    label={t('storyGeneration.modelLabel')}
                    variant="outlined"
                    fullWidth
                    placeholder={t('storyGeneration.modelPlaceholder')}
                    helperText={t('storyGeneration.modelHelperText')}
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

            <Grid item xs={12} md={6}>
              <FormControl fullWidth variant="outlined" sx={{ mb: 2 }}>
                <InputLabel id="output-language-label">{t('storyGeneration.languageOutputLabel')}</InputLabel>
                <Select
                  labelId="output-language-label"
                  id="output-language-select"
                  value={outputLanguage}
                  onChange={(e) => setOutputLanguage(e.target.value)}
                  label={t('storyGeneration.languageOutputLabel')}
                >
                  <MenuItem value="english">{t('storyGeneration.outputEnglish')}</MenuItem>
                  <MenuItem value="chinese">{t('storyGeneration.outputChinese')}</MenuItem>
                </Select>
                <FormHelperText>{t('storyGeneration.languageOutputHelperText')}</FormHelperText>
              </FormControl>

              <Button
                type="submit"
                variant="contained"
                color="primary"
                size="large"
                fullWidth
                disabled={loading || !prompt}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : t('storyGeneration.generateStory')}
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
                    {t('storyGeneration.apiKeySettings')}
                    <Tooltip title={t('storyGeneration.apiKeyInfo')}>
                      <IconButton size="small" sx={{ ml: 1 }}>
                        <InfoIcon fontSize="small" color="action" />
                      </IconButton>
                    </Tooltip>
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
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
                    <Grid item xs={12} md={6}>
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
          {t('storyGeneration.examplePromptsTitle')}
        </Typography>
        <Typography variant="body2" paragraph>
          {t('storyGeneration.examplePromptsSubtitle')}
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
          {t('storyGeneration.tipsTitle')}
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" fontWeight="bold">
              {t('storyGeneration.beSpecificTitle')}
            </Typography>
            <Typography variant="body2">
              {t('storyGeneration.beSpecificDescription')}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" fontWeight="bold">
              {t('storyGeneration.defineParametersTitle')}
            </Typography>
            <Typography variant="body2">
              {t('storyGeneration.defineParametersDescription')}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="subtitle1" fontWeight="bold">
              {t('storyGeneration.allowCreativityTitle')}
            </Typography>
            <Typography variant="body2">
              {t('storyGeneration.allowCreativityDescription')}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default StoryGenerationPage;