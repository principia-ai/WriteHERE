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

const HomePage = () => {
  const theme = useTheme();
  const isSmallScreen = useMediaQuery(theme.breakpoints.down('md'));
  
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
            label="Advanced AI Writing Framework" 
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
            Open Framework for Human-like Long-form Writing
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
            A general agent framework for long-form writing that achieves adaptive content generation
            through recursive task decomposition and dynamic integration of heterogeneous tasks/tools.
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
              Get Started
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
              Learn More
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
            How It Works
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 700, mx: 'auto' }}>
            Heterogeneous Recursive Planning goes beyond traditional writing approaches by mimicking
            human cognitive processes through adaptive task decomposition.
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
                Retrieval
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Dynamically searches for relevant information during the writing process,
                ensuring factual accuracy and comprehensive coverage of the topic.
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
                Reasoning
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Applies logical analysis to plan, organize, and refine content structure,
                ensuring coherent and well-structured output that follows a logical flow.
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
                Composition
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Generates articulate and engaging content based on the retrieved information
                and reasoning, adapting to context and maintaining consistent style and tone.
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
            Generate Content
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 700, mx: 'auto', mb: 4 }}>
            Choose the type of content you want to create and experience the power of heterogeneous recursive planning.
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
                  Creative Story Generation
                </Typography>
                <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                  Craft engaging narratives and fiction
                </Typography>
              </Box>
              
              <CardContent sx={{ flexGrow: 1, p: 4 }}>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  Generate creative narratives, fiction, and stories using our heterogeneous 
                  recursive planning approach. Perfect for creative writing, entertainment, 
                  and educational content.
                </Typography>
                
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                  <Chip size="small" label="Fiction" />
                  <Chip size="small" label="Short Stories" />
                  <Chip size="small" label="Creative Writing" />
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
                  Generate Story
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
                  Technical Report Generation
                </Typography>
                <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                  Create comprehensive, fact-based documents
                </Typography>
              </Box>
              
              <CardContent sx={{ flexGrow: 1, p: 4 }}>
                <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                  Create comprehensive technical reports and documentation with accurate information 
                  retrieval and logical reasoning. Ideal for business, academic, and technical documentation.
                </Typography>
                
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 3 }}>
                  <Chip size="small" label="Research" />
                  <Chip size="small" label="Analysis" />
                  <Chip size="small" label="Documentation" />
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
                  Generate Report
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
        <Box sx={{ maxWidth: 800, mx: 'auto' }}>
          <Typography 
            variant="h3" 
            gutterBottom 
            sx={{ 
              fontSize: { xs: '1.5rem', md: '2rem' },
              fontWeight: 700,
              mb: 3,
              textAlign: 'center'
            }}
          >
            Visualize the Writing Process
          </Typography>
          <Typography variant="body1" color="text.secondary" paragraph sx={{ mb: 4, textAlign: 'center' }}>
            Our framework makes the writing process transparent by showing how complex writing tasks are broken down into manageable sub-tasks that integrate retrieval, reasoning, and composition.
          </Typography>
          
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
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
                  fontWeight: 'bold',
                  flexShrink: 0
                }}>
                  1
                </Box>
                <Typography variant="body1">
                  <strong>Initial decomposition</strong> of writing task
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
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
                  fontWeight: 'bold',
                  flexShrink: 0
                }}>
                  2
                </Box>
                <Typography variant="body1">
                  <strong>Recursive planning</strong> of subtasks
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
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
                  fontWeight: 'bold',
                  flexShrink: 0
                }}>
                  3
                </Box>
                <Typography variant="body1">
                  <strong>Dynamic integration</strong> of components
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={12} md={6}>
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
                  fontWeight: 'bold',
                  flexShrink: 0
                }}>
                  4
                </Box>
                <Typography variant="body1">
                  <strong>Content generation</strong> with quality
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>
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
            Ready to transform your writing process?
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
            Experience the next generation of AI-assisted writing with our heterogeneous recursive planning framework.
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
              Try Story Generation
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
              Try Report Generation
            </Button>
          </Box>
        </Box>
      </Box>
    </Container>
  );
};

export default HomePage;