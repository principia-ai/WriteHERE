import React from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Grid,
  Divider,
  Link
} from '@mui/material';
import { useTranslation } from 'react-i18next';

const AboutPage = () => {
  const { t } = useTranslation();

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          {t('about.title')}
        </Typography>
        <Typography variant="body1" paragraph>
          {t('about.introduction')}
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <Typography variant="h4" gutterBottom>
          {t('about.overview')}
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Typography variant="body1" paragraph>
          {t('about.overviewDescription')}
        </Typography>
        
        <Typography variant="body1" paragraph>
          {t('about.traditionalApproach')}
        </Typography>
        
        <Box sx={{ pl: 3, mb: 3 }}>
          <Typography variant="body1" paragraph>
            1. <strong>{t('about.feature1')}</strong>
          </Typography>
          <Typography variant="body1" paragraph>
            2. <strong>{t('about.feature2')}</strong>
          </Typography>
          <Typography variant="body1" paragraph>
            3. <strong>{t('about.feature3')}</strong>
          </Typography>
        </Box>
        
        <Typography variant="body1" paragraph>
          {t('about.evaluationResult')}
        </Typography>
      </Paper>

      <Grid container spacing={4} sx={{ mb: 6 }}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              {t('about.keyFeatures')}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box component="ul" sx={{ pl: 2 }}>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body1">
                  <strong>{t('about.recursiveTask')}</strong> - {t('about.recursiveTaskDesc')}
                </Typography>
              </Box>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body1">
                  <strong>{t('about.dynamicIntegration')}</strong> - {t('about.dynamicIntegrationDesc')}
                </Typography>
              </Box>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body1">
                  <strong>{t('about.flexibleAdaptation')}</strong> - {t('about.flexibleAdaptationDesc')}
                </Typography>
              </Box>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body1">
                  <strong>{t('about.multiDomainSupport')}</strong> - {t('about.multiDomainSupportDesc')}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              {t('about.technicalImplementation')}
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body1" paragraph>
              {t('about.taskGraphDesc')}
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body1">
                <strong>{t('about.compositionType')}</strong> - {t('about.compositionTypeDesc')}
              </Typography>
              <Typography variant="body1">
                <strong>{t('about.retrievalType')}</strong> - {t('about.retrievalTypeDesc')}
              </Typography>
              <Typography variant="body1">
                <strong>{t('about.reasoningType')}</strong> - {t('about.reasoningTypeDesc')}
              </Typography>
            </Box>
            
            <Typography variant="body1">
              {t('about.systemImplementation')}
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <Typography variant="h4" gutterBottom>
          {t('about.researchPublication')}
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Typography variant="body1" paragraph>
          {t('about.paperIntro')}
        </Typography>
        
        <Box sx={{ p: 3, backgroundColor: '#f5f5f5', borderRadius: 2, mb: 3 }}>
          <Typography variant="body1" fontFamily="monospace">
            @misc&#123;xiong2025beyondoutlining,
            <br />
            &nbsp;&nbsp;title=&#123;Beyond Outlining: Heterogeneous Recursive Planning for Adaptive Long-form Writing with Language Models&#125;, 
            <br />
            &nbsp;&nbsp;author=&#123;Ruibin Xiong and Yimeng Chen and Dmitrii Khizbullin and Jürgen Schmidhuber&#125;,
            <br />
            &nbsp;&nbsp;year=&#123;2025&#125;,
            <br />
            &nbsp;&nbsp;eprint=&#123;2503.08275&#125;,
            <br />
            &nbsp;&nbsp;archivePrefix=&#123;arXiv&#125;,
            <br />
            &nbsp;&nbsp;primaryClass=&#123;cs.AI&#125;,
            <br />
            &nbsp;&nbsp;url=&#123;https://arxiv.org/abs/2503.08275&#125;
            <br />
            &#125;
          </Typography>
        </Box>
        
        <Typography variant="body1">
          For more detailed information, you can read the full paper at{' '}
          <Link href="https://arxiv.org/abs/2503.08275" target="_blank" rel="noopener">
            https://arxiv.org/abs/2503.08275
          </Link>
        </Typography>
      </Paper>

      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <Typography variant="h4" gutterBottom>
          {t('about.projectTeam')}
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Grid container spacing={3}>
          <Grid item xs={12} md={3}>
            <Typography variant="body1">
              <strong>Ruibin Xiong</strong>
            </Typography>
          </Grid>
          <Grid item xs={12} md={3}>
            <Typography variant="body1">
              <strong>Yimeng Chen</strong>
            </Typography>
          </Grid>
          <Grid item xs={12} md={3}>
            <Typography variant="body1">
              <strong>Dmitrii Khizbullin</strong>
            </Typography>
          </Grid>
          <Grid item xs={12} md={3}>
            <Typography variant="body1">
              <strong>Jürgen Schmidhuber</strong>
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default AboutPage;