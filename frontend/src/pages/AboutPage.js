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

const AboutPage = () => {
  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          About the Project
        </Typography>
        <Typography variant="body1" paragraph>
          Heterogeneous Recursive Planning represents a significant advancement in AI-powered content generation,
          enabling more adaptive and human-like writing through innovative task decomposition and planning.
        </Typography>
      </Box>

      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <Typography variant="h4" gutterBottom>
          Overview
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Typography variant="body1" paragraph>
          Heterogeneous Recursive Planning is a general agent framework for long-form writing that achieves 
          human-like adaptive writing through recursive task decomposition and dynamic integration of three 
          fundamental task types: retrieval, reasoning, and composition.
        </Typography>
        
        <Typography variant="body1" paragraph>
          Unlike traditional approaches that rely on predetermined workflows and rigid thinking patterns, 
          this framework:
        </Typography>
        
        <Box sx={{ pl: 3, mb: 3 }}>
          <Typography variant="body1" paragraph>
            1. <strong>Eliminates workflow restrictions</strong> through a planning mechanism that interleaves recursive task decomposition and execution
          </Typography>
          <Typography variant="body1" paragraph>
            2. <strong>Facilitates heterogeneous task decomposition</strong> by integrating different task types
          </Typography>
          <Typography variant="body1" paragraph>
            3. <strong>Adapts dynamically</strong> during the writing process, similar to human writing behavior
          </Typography>
        </Box>
        
        <Typography variant="body1" paragraph>
          Our evaluations on both fiction writing and technical report generation demonstrate that this 
          method consistently outperforms state-of-the-art approaches across all evaluation metrics.
        </Typography>
      </Paper>

      <Grid container spacing={4} sx={{ mb: 6 }}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              Key Features
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box component="ul" sx={{ pl: 2 }}>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body1">
                  <strong>Recursive task decomposition and execution</strong> - Breaking complex writing tasks into manageable sub-tasks
                </Typography>
              </Box>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body1">
                  <strong>Dynamic integration of diverse task types</strong> - Seamlessly combining retrieval, reasoning, and composition
                </Typography>
              </Box>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body1">
                  <strong>Flexible adaptation during writing</strong> - Adjusting the plan as context evolves
                </Typography>
              </Box>
              <Box component="li" sx={{ mb: 1 }}>
                <Typography variant="body1">
                  <strong>Support for multiple writing domains</strong> - Works for both creative fiction and technical reports
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 4, height: '100%' }}>
            <Typography variant="h5" gutterBottom>
              Technical Implementation
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body1" paragraph>
              The framework is built on a task graph architecture that represents writing tasks as nodes with dependencies.
              Each node can be one of three types:
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Typography variant="body1">
                <strong>Composition (Write)</strong> - Creating actual content
              </Typography>
              <Typography variant="body1">
                <strong>Retrieval (Search)</strong> - Gathering information
              </Typography>
              <Typography variant="body1">
                <strong>Reasoning (Think)</strong> - Analyzing and planning
              </Typography>
            </Box>
            
            <Typography variant="body1">
              The system uses advanced language models (LLMs) like GPT-4 and Claude to execute these tasks,
              with a recursive planning mechanism that can decompose tasks and adapt plans dynamically.
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <Typography variant="h4" gutterBottom>
          Research Publication
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Typography variant="body1" paragraph>
          This project is based on research described in the paper:
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
          Project Team
        </Typography>
        <Divider sx={{ mb: 3 }} />
        <Box sx={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: 2, 
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            Ruibin Xiong
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>•</Typography>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            Yimeng Chen
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>•</Typography>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            Dmitrii Khizbullin
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>•</Typography>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            Mingchen Zhuge
          </Typography>
          <Typography variant="body1" sx={{ color: 'text.secondary' }}>•</Typography>
          <Typography variant="body1" sx={{ fontWeight: 500 }}>
            Jürgen Schmidhuber
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
};

export default AboutPage;