import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Paper, Grid, FormControl, InputLabel, Select, MenuItem, Typography, Button, CircularProgress } from '@mui/material';
import { Autocomplete } from '@mui/material';
import { generateStory } from '../services/storyGenerationService';
import { useNavigate } from 'react-router-dom';

const StoryGenerationPage = () => {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState('');
  const [model, setModel] = useState('gpt-4o');
  const [promptLanguage, setPromptLanguage] = useState('english');
  const [outputLanguage, setOutputLanguage] = useState('english');
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // ... existing validation code ...
    
    try {
      // Call the backend API to start story generation
      const response = await generateStory({
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
        setStatusMessage(t('storyGeneration.status.started'));
        navigate(`/results/${response.taskId}`, { 
          state: { 
            taskId: response.taskId,
            prompt,
            model,
            outputLanguage,
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
      setError(t('storyGeneration.errors.generationError') + ' ' + (err.message || t('storyGeneration.errors.unknown')));
      console.error('Story generation error:', err);
    }
  };

  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              {/* ... existing prompt TextField ... */}
            </Grid>

            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>{t('storyGeneration.promptLanguageLabel')}</InputLabel>
                <Select
                  value={promptLanguage}
                  label={t('storyGeneration.promptLanguageLabel')}
                  onChange={(e) => setPromptLanguage(e.target.value)}
                >
                  <MenuItem value="english">{t('storyGeneration.promptLanguages.english')}</MenuItem>
                  <MenuItem value="chinese">{t('storyGeneration.promptLanguages.chinese')}</MenuItem>
                </Select>
                <Typography variant="caption" color="textSecondary">
                  {t('storyGeneration.promptLanguageHelperText')}
                </Typography>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4}>
              <Autocomplete
                // ... existing model selection Autocomplete ...
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>{t('storyGeneration.languageOutputLabel')}</InputLabel>
                <Select
                  value={outputLanguage}
                  label={t('storyGeneration.languageOutputLabel')}
                  onChange={(e) => setOutputLanguage(e.target.value)}
                >
                  <MenuItem value="english">{t('storyGeneration.outputEnglish')}</MenuItem>
                  <MenuItem value="chinese">{t('storyGeneration.outputChinese')}</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={4} sx={{ display: 'flex', alignItems: 'center' }}>
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
          </Grid>
        </form>
      </Paper>
    </Container>
  );
};

export default StoryGenerationPage; 