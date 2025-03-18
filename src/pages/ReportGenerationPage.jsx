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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  InputAdornment,
  Tooltip,
  IconButton,
  Snackbar,
  FormControlLabel,
  Switch
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import InfoIcon from '@mui/icons-material/Info';
import { generateReport, pingAPI } from '../utils/api';
import HistoryPanel from '../components/HistoryPanel';
import { useTranslation } from 'react-i18next';

const ReportGenerationPage = () => {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState('');
  const [model, setModel] = useState('claude-3-5-sonnet-20241022');
  const [outputLanguage, setOutputLanguage] = useState('english');
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

  // Save API keys to localStorage when they change
  useEffect(() => {
    if (apiKeys.openai) localStorage.setItem('openai_api_key', apiKeys.openai);
    if (apiKeys.claude) localStorage.setItem('claude_api_key', apiKeys.claude);
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
        outputLanguage,
        apiKeys: {
          openai: apiKeys.openai,
          claude: apiKeys.claude
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
            outputLanguage,
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
      setError(t('reportGeneration.errors.generationError') + ' ' + (err.message || t('reportGeneration.errors.unknown')));
      console.error('Report generation error:', err);
    }
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

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>{t('reportGeneration.modelLabel')}</InputLabel>
                <Select
                  value={model}
                  label={t('reportGeneration.modelLabel')}
                  onChange={(e) => setModel(e.target.value)}
                >
                  <MenuItem value="gpt-4o">GPT-4o</MenuItem>
                  <MenuItem value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</MenuItem>
                  <MenuItem value="claude-3-7-sonnet-20250219">Claude 3.7 Sonnet (Recommended)</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>{t('reportGeneration.languageOutputLabel')}</InputLabel>
                <Select
                  value={outputLanguage}
                  label={t('reportGeneration.languageOutputLabel')}
                  onChange={(e) => setOutputLanguage(e.target.value)}
                >
                  <MenuItem value="english">{t('reportGeneration.outputEnglish')}</MenuItem>
                  <MenuItem value="chinese">{t('reportGeneration.outputChinese')}</MenuItem>
                </Select>
              </FormControl>
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
                    {t('reportGeneration.apiKeySettings')}
                    <Tooltip title={t('reportGeneration.apiKeyInfo')}>
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
                        label={t('reportGeneration.openaiApiKey')}
                        fullWidth
                        variant="outlined"
                        value={apiKeys.openai}
                        onChange={(e) => handleApiKeyChange('openai', e.target.value)}
                        type={showOpenAIKey ? 'text' : 'password'}
                        placeholder="sk-..."
                        helperText={t('reportGeneration.openaiHelperText')}
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
                        label={t('reportGeneration.claudeApiKey')}
                        fullWidth
                        variant="outlined"
                        value={apiKeys.claude}
                        onChange={(e) => handleApiKeyChange('claude', e.target.value)}
                        type={showClaudeKey ? 'text' : 'password'}
                        placeholder="sk-ant-..."
                        helperText={t('reportGeneration.claudeHelperText')}
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
                        {t('reportGeneration.apiKeyPrivacyNote')}
                      </Typography>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>

            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  size="large"
                  disabled={loading || !prompt}
                  sx={{ minWidth: 200 }}
                >
                  {loading ? <CircularProgress size={24} color="inherit" /> : t('reportGeneration.generateReport')}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default ReportGenerationPage; 