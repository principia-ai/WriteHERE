import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Paper, Grid, FormControl, InputLabel, Select, MenuItem, Typography, FormControlLabel, Switch, Button, CircularProgress, Box } from '@mui/material';
import { Autocomplete } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { generateReport } from '../services/reportService';

const ReportGenerationPage = () => {
  const { t, i18n } = useTranslation();
  const [prompt, setPrompt] = useState('');
  const [model, setModel] = useState('gpt-4o');
  const [promptLanguage, setPromptLanguage] = useState('english');
  const [outputLanguage, setOutputLanguage] = useState('english');
  const [enableSearch, setEnableSearch] = useState(false);
  const [searchEngine, setSearchEngine] = useState('bing');
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLanguageChange = (event) => {
    const newLang = event.target.value;
    i18n.changeLanguage(newLang);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // ... existing validation code ...
    
    try {
      // Call the backend API to start report generation
      const response = await generateReport({
        prompt,
        model,
        promptLanguage,
        outputLanguage,
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
        setStatusMessage(t('reportGeneration.status.started'));
        navigate(`/results/${response.taskId}`, { 
          state: { 
            taskId: response.taskId,
            prompt,
            model,
            promptLanguage,
            outputLanguage,
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
      setError(t('reportGeneration.errors.generationError') + ' ' + (err.message || t('reportGeneration.errors.unknown')));
      console.error('Report generation error:', err);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <FormControl sx={{ minWidth: 120 }}>
          <Select
            value={i18n.language}
            onChange={handleLanguageChange}
            variant="outlined"
            size="small"
            sx={{ '& .MuiSelect-select': { py: 1 } }}
          >
            <MenuItem value="en">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <img src="/flags/us.svg" alt="English" style={{ width: 20, height: 15 }} />
                {t('common.english')}
              </Box>
            </MenuItem>
            <MenuItem value="zh">
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <img src="/flags/cn.svg" alt="Chinese" style={{ width: 20, height: 15 }} />
                {t('common.chinese')}
              </Box>
            </MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label={t('reportGeneration.promptLabel')}
                placeholder={t('reportGeneration.promptPlaceholder')}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                required
                error={!prompt && error}
                helperText={!prompt && error ? t('reportGeneration.errors.emptyPrompt') : ''}
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                {t('common.language')}
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>{t('reportGeneration.languageOutputLabel')}</InputLabel>
                    <Select
                      value={outputLanguage}
                      label={t('reportGeneration.languageOutputLabel')}
                      onChange={(e) => setOutputLanguage(e.target.value)}
                    >
                      <MenuItem value="english">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <img src="/flags/us.svg" alt="English" style={{ width: 20, height: 15 }} />
                          {t('reportGeneration.outputEnglish')}
                        </Box>
                      </MenuItem>
                      <MenuItem value="chinese">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <img src="/flags/cn.svg" alt="Chinese" style={{ width: 20, height: 15 }} />
                          {t('reportGeneration.outputChinese')}
                        </Box>
                      </MenuItem>
                    </Select>
                    <Typography variant="caption" color="textSecondary">
                      {t('reportGeneration.languageOutputHelperText')}
                    </Typography>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>{t('reportGeneration.promptLanguageLabel')}</InputLabel>
                    <Select
                      value={promptLanguage}
                      label={t('reportGeneration.promptLanguageLabel')}
                      onChange={(e) => setPromptLanguage(e.target.value)}
                    >
                      <MenuItem value="english">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <img src="/flags/us.svg" alt="English" style={{ width: 20, height: 15 }} />
                          {t('reportGeneration.promptLanguages.english')}
                        </Box>
                      </MenuItem>
                      <MenuItem value="chinese">
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <img src="/flags/cn.svg" alt="Chinese" style={{ width: 20, height: 15 }} />
                          {t('reportGeneration.promptLanguages.chinese')}
                        </Box>
                      </MenuItem>
                    </Select>
                    <Typography variant="caption" color="textSecondary">
                      {t('reportGeneration.promptLanguageHelperText')}
                    </Typography>
                  </FormControl>
                </Grid>
              </Grid>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                {t('reportGeneration.apiKeySettings')}
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>{t('reportGeneration.modelLabel')}</InputLabel>
                    <Select
                      value={model}
                      label={t('reportGeneration.modelLabel')}
                      onChange={(e) => setModel(e.target.value)}
                    >
                      <MenuItem value="gpt-4o">GPT-4</MenuItem>
                      <MenuItem value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</MenuItem>
                    </Select>
                    <Typography variant="caption" color="textSecondary">
                      {t('reportGeneration.modelHelperText')}
                    </Typography>
                  </FormControl>
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={enableSearch}
                          onChange={(e) => setEnableSearch(e.target.checked)}
                          name="enableSearch"
                        />
                      }
                      label={t('reportGeneration.enableSearchLabel')}
                    />
                    {enableSearch && (
                      <>
                        <Select
                          value={searchEngine}
                          onChange={(e) => setSearchEngine(e.target.value)}
                          sx={{ mt: 2 }}
                        >
                          <MenuItem value="bing">{t('reportGeneration.searchEngines.bing')}</MenuItem>
                          <MenuItem value="google">{t('reportGeneration.searchEngines.google')}</MenuItem>
                          <MenuItem value="custom">{t('reportGeneration.searchEngines.custom')}</MenuItem>
                        </Select>
                        <Typography variant="caption" color="textSecondary">
                          {t('reportGeneration.searchEngineHelperText')}
                        </Typography>
                      </>
                    )}
                  </FormControl>
                </Grid>
              </Grid>
            </Grid>

            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                size="large"
                fullWidth
                disabled={loading || !prompt}
                sx={{ mt: 2 }}
              >
                {loading ? <CircularProgress size={24} color="inherit" /> : t('reportGeneration.generateReport')}
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default ReportGenerationPage;

 