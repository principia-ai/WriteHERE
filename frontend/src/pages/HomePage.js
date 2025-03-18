import React from 'react';
import { 
  Container, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  Button, 
  Box,
  Paper,
  Chip,
  Divider,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import CreateIcon from '@mui/icons-material/Create';
import DescriptionIcon from '@mui/icons-material/Description';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SearchIcon from '@mui/icons-material/Search';
import PsychologyIcon from '@mui/icons-material/Psychology';
import EditNoteIcon from '@mui/icons-material/EditNote';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { useTranslation } from 'react-i18next';

const HomePage = () => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));
  const { t } = useTranslation();
  
  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box 
        sx={{ 
          mt: { xs: 4, md: 8 },
          mb: { xs: 6, md: 10 },
          textAlign: 'center',
          position: 'relative',
        }}
      >
        <Box 
          sx={{
            position: 'absolute',
            top: -100,
            left: -200,
            right: -200,
            bottom: -100,
            background: 'radial-gradient(circle at 50% 50%, rgba(84, 54, 218, 0.08), transparent 70%)',
            zIndex: -1,
          }}
        />
        
        <Box sx={{ maxWidth: 800, mx: 'auto' }}>
          <Chip 
            icon={<AutoAwesomeIcon />} 
            label={t('home.advancedAIWriting')}
            color="primary" 
            variant="outlined" 
            sx={{ mb: 3 }} 
          />
          <Typography 
            variant="h1" 
            component="h1" 
            gutterBottom
            sx={{ 
              fontSize: { xs: '2.5rem', md: '3.5rem' },
              letterSpacing: '-0.025em',
              backgroundImage: 'linear-gradient(to right, #5436DA, #10A37F)',
              backgroundClip: 'text',
              color: 'transparent',
              display: 'inline-block',
              mb: 2,
            }}
          >
            {t('home.title')}
          </Typography>
          <Typography 
            variant="h5" 
            color="text.secondary" 
            paragraph
            sx={{ 
              fontWeight: 400,
              mb: 4,
              maxWidth: 720,
              mx: 'auto',
              lineHeight: 1.5
            }}
          >
            {t('home.description')}
          </Typography>
          
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Button 
              component={RouterLink}
              to="/story-generation"
              variant="contained" 
              color="primary" 
              size="large"
              sx={{ 
                py: 1.5, 
                px: 4, 
                borderRadius: 3,
                fontSize: '1rem'
              }}
            >
              {t('home.getStarted')}
            </Button>
            <Button 
              component={RouterLink}
              to="/about"
              variant="outlined" 
              color="primary" 
              size="large"
              sx={{ 
                py: 1.5, 
                px: 4, 
                borderRadius: 3,
                fontSize: '1rem',
                backgroundColor: 'rgba(84, 54, 218, 0.04)',
                '&:hover': {
                  backgroundColor: 'rgba(84, 54, 218, 0.08)',
                }
              }}
            >
              {t('home.learnMore')}
            </Button>
          </Box>
        </Box>
      </Box>
      
      {/* Features Section */}
      <Box 
        sx={{ 
          mb: 10, 
          py: 6, 
          px: { xs: 2, md: 6 },
          borderRadius: 4,
          background: 'linear-gradient(145deg, rgba(84, 54, 218, 0.04), rgba(16, 163, 127, 0.04))',
        }}
      >
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography 
            variant="h2" 
            gutterBottom
            sx={{ 
              fontSize: { xs: '1.75rem', md: '2.25rem' },
              fontWeight: 700,
              color: 'text.primary'
            }}
          >
            {t('home.howItWorks')}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 700, mx: 'auto' }}>
            {t('home.howItWorksDescription')}
          </Typography>
        </Box>
        
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Box 
              sx={{ 
                p: 3, 
                borderRadius: 4, 
                height: '100%', 
                backgroundColor: 'white',
                boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.05)',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.08)',
                }
              }}
            >
              <Box 
                sx={{ 
                  display: 'inline-flex', 
                  p: 1.5, 
                  borderRadius: 2, 
                  backgroundColor: 'rgba(84, 54, 218, 0.1)', 
                  color: 'primary.main',
                  mb: 2
                }}
              >
                <SearchIcon fontSize="medium" />
              </Box>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                {t('home.retrieval')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('home.retrievalDescription')}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box 
              sx={{ 
                p: 3, 
                borderRadius: 4, 
                height: '100%', 
                backgroundColor: 'white',
                boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.05)',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.08)',
                }
              }}
            >
              <Box 
                sx={{ 
                  display: 'inline-flex', 
                  p: 1.5, 
                  borderRadius: 2, 
                  backgroundColor: 'rgba(16, 163, 127, 0.1)', 
                  color: 'secondary.main',
                  mb: 2
                }}
              >
                <PsychologyIcon fontSize="medium" />
              </Box>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                {t('home.reasoning')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('home.reasoningDescription')}
              </Typography>
            </Box>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Box 
              sx={{ 
                p: 3, 
                borderRadius: 4, 
                height: '100%', 
                backgroundColor: 'white',
                boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.05)',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-5px)',
                  boxShadow: '0px 8px 20px rgba(0, 0, 0, 0.08)',
                }
              }}
            >
              <Box 
                sx={{ 
                  display: 'inline-flex', 
                  p: 1.5, 
                  borderRadius: 2, 
                  backgroundColor: 'rgba(245, 158, 11, 0.1)', 
                  color: '#F59E0B',
                  mb: 2
                }}
              >
                <EditNoteIcon fontSize="medium" />
              </Box>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 600 }}>
                {t('home.composition')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {t('home.compositionDescription')}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Box>
      
      {/* Use Cases Section */}
      <Box sx={{ mb: 10 }}>
        <Box sx={{ textAlign: 'center', mb: 6 }}>
          <Typography 
            variant="h2" 
            gutterBottom
            sx={{ 
              fontSize: { xs: '1.75rem', md: '2.25rem' },
              fontWeight: 700,
              color: 'text.primary'
            }}
          >
            {t('home.generateContent')}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 700, mx: 'auto', mb: 4 }}>
            {t('home.generateContentDescription')}
          </Typography>
        </Box>
        
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                borderRadius: 4,
                overflow: 'hidden',
                boxShadow: '0 10px 30px rgba(0, 0, 0, 0.08)',
                transition: 'transform 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-8px)',
                }
              }}
            >
              <Box 
                sx={{ 
                  background: 'linear-gradient(135deg, #5436DA, #8667EE)',
                  p: 4,
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                <Box 
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    opacity: 0.1,
                    background: 'radial-gradient(circle at 70% 30%, white, transparent 70%)',
                  }}
                />
                <CreateIcon sx={{ fontSize: 60, color: 'white', mb: 2 }} />
                <Typography variant="h4" component="div" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>
                  {t('home.creativeStoryGeneration')}
                </Typography>
                <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                  {t('home.craftNarratives')}
                </Typography>
              </Box>
              
              <CardContent sx={{ flexGrow: 1, p: 4 }}>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  {t('home.storyDescription')}
                </Typography>
                
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                  <Chip size="small" label={t('home.fiction')} />
                  <Chip size="small" label={t('home.shortStories')} />
                  <Chip size="small" label={t('home.creativeWriting')} />
                </Box>
                
                <Button 
                  endIcon={<ArrowForwardIcon />}
                  size="large" 
                  variant="contained" 
                  color="primary" 
                  component={RouterLink}
                  to="/story-generation"
                  sx={{ 
                    borderRadius: 3,
                    py: 1.5,
                    width: '100%',
                  }}
                >
                  {t('home.generateStory')}
                </Button>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Card 
              sx={{ 
                height: '100%', 
                display: 'flex', 
                flexDirection: 'column',
                borderRadius: 4,
                overflow: 'hidden',
                boxShadow: '0 10px 30px rgba(0, 0, 0, 0.08)',
                transition: 'transform 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-8px)',
                }
              }}
            >
              <Box 
                sx={{ 
                  background: 'linear-gradient(135deg, #10A37F, #34D399)',
                  p: 4,
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                <Box 
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    opacity: 0.1,
                    background: 'radial-gradient(circle at 70% 30%, white, transparent 70%)',
                  }}
                />
                <DescriptionIcon sx={{ fontSize: 60, color: 'white', mb: 2 }} />
                <Typography variant="h4" component="div" sx={{ color: 'white', fontWeight: 700, mb: 1 }}>
                  {t('home.technicalReportGeneration')}
                </Typography>
                <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                  {t('home.createDocuments')}
                </Typography>
              </Box>
              
              <CardContent sx={{ flexGrow: 1, p: 4 }}>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  {t('home.reportDescription')}
                </Typography>
                
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                  <Chip size="small" label={t('home.research')} />
                  <Chip size="small" label={t('home.analysis')} />
                  <Chip size="small" label={t('home.documentation')} />
                </Box>
                
                <Button 
                  endIcon={<ArrowForwardIcon />}
                  size="large" 
                  variant="contained" 
                  color="secondary" 
                  component={RouterLink}
                  to="/report-generation"
                  sx={{ 
                    borderRadius: 3,
                    py: 1.5,
                    width: '100%',
                  }}
                >
                  {t('home.generateReport')}
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
      
      {/* Process Visualization */}
      <Paper 
        elevation={0} 
        sx={{ 
          p: { xs: 3, md: 5 }, 
          mb: 10, 
          borderRadius: 4, 
          backgroundColor: 'grey.50',
          border: '1px solid',
          borderColor: 'grey.100'
        }}
      >
        <Grid container spacing={4} alignItems="center">
          <Grid item xs={12} md={6}>
            <Typography 
              variant="h3" 
              gutterBottom 
              sx={{ 
                fontSize: { xs: '1.5rem', md: '2rem' },
                fontWeight: 700,
                mb: 2
              }}
            >
              {t('home.visualizeProcess')}
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              {t('home.visualizeDescription')}
            </Typography>
            <Divider sx={{ my: 3 }} />
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  borderRadius: '50%', 
                  backgroundColor: 'primary.main', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'bold'
                }}>
                  1
                </Box>
                <Typography variant="body1" fontWeight={500}>
                  {t('home.step1')}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  borderRadius: '50%', 
                  backgroundColor: 'primary.main', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'bold'
                }}>
                  2
                </Box>
                <Typography variant="body1" fontWeight={500}>
                  {t('home.step2')}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  borderRadius: '50%', 
                  backgroundColor: 'primary.main', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'bold'
                }}>
                  3
                </Box>
                <Typography variant="body1" fontWeight={500}>
                  {t('home.step3')}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Box sx={{ 
                  width: 40, 
                  height: 40, 
                  borderRadius: '50%', 
                  backgroundColor: 'primary.main', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'bold'
                }}>
                  4
                </Box>
                <Typography variant="body1" fontWeight={500}>
                  {t('home.step4')}
                </Typography>
              </Box>
            </Box>
          </Grid>
          <Grid item xs={12} md={6}>
            <Box 
              component="img"
              src="https://via.placeholder.com/600x400?text=Task+List+Visualization"
              alt="Task List Visualization"
              sx={{ 
                width: '100%',
                borderRadius: 3,
                boxShadow: '0 10px 30px rgba(0, 0, 0, 0.1)',
              }}
            />
          </Grid>
        </Grid>
      </Paper>
      
      {/* CTA Section */}
      <Box 
        sx={{ 
          mb: 10, 
          textAlign: 'center',
          p: { xs: 4, md: 8 },
          borderRadius: 4,
          background: 'linear-gradient(135deg, rgba(84, 54, 218, 0.05) 0%, rgba(84, 54, 218, 0.1) 100%)',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <Box 
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            opacity: 0.4,
            background: 'radial-gradient(circle at 70% 30%, rgba(255, 255, 255, 0.8), transparent 60%)',
          }}
        />
        
        <Box sx={{ position: 'relative', maxWidth: 800, mx: 'auto' }}>
          <Typography 
            variant="h2" 
            gutterBottom
            sx={{ 
              fontSize: { xs: '1.75rem', md: '2.5rem' },
              fontWeight: 700,
              color: 'text.primary',
              mb: 2
            }}
          >
            {t('home.readyToTransform')}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
            {t('home.transformDescription')}
          </Typography>
          
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
            <Button 
              component={RouterLink}
              to="/story-generation"
              variant="contained" 
              color="primary" 
              size="large"
              sx={{ 
                py: 1.5, 
                px: 4, 
                borderRadius: 3,
                fontSize: '1rem'
              }}
            >
              {t('home.tryStoryGeneration')}
            </Button>
            <Button 
              component={RouterLink}
              to="/report-generation"
              variant="contained" 
              color="secondary" 
              size="large"
              sx={{ 
                py: 1.5, 
                px: 4, 
                borderRadius: 3,
                fontSize: '1rem'
              }}
            >
              {t('home.tryReportGeneration')}
            </Button>
          </Box>
        </Box>
      </Box>
    </Container>
  );
};

export default HomePage;