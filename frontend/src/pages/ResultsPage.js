import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Typography, 
  Box, 
  Paper, 
  Grid,
  CircularProgress,
  Alert,
  Tab,
  Tabs,
  Button,
  Divider,
  LinearProgress,
  Chip,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle
} from '@mui/material';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import LiveTaskList from '../components/LiveTaskList';
import DownloadIcon from '@mui/icons-material/Download';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { getGenerationStatus, getGenerationResult, getTaskGraph, reloadTasks, stopTask } from '../utils/api';

// Mock data for task graph - this would come from your backend in a real implementation
const mockGraphData = {
  id: '',
  goal: 'Write a report on AI writing agents',
  task_type: 'write',
  status: 'FINISH',
  sub_tasks: [
    {
      id: '0',
      goal: 'Plan the report structure',
      task_type: 'think',
      status: 'FINISH',
      sub_tasks: []
    },
    {
      id: '1',
      goal: 'Research commercial applications',
      task_type: 'search',
      status: 'FINISH',
      sub_tasks: []
    },
    {
      id: '2',
      goal: 'Analyze market trends',
      task_type: 'think',
      status: 'FINISH',
      sub_tasks: []
    },
    {
      id: '3',
      goal: 'Write introduction',
      task_type: 'write',
      status: 'FINISH',
      sub_tasks: []
    },
    {
      id: '4',
      goal: 'Write benefits section',
      task_type: 'write',
      status: 'FINISH',
      sub_tasks: []
    },
    {
      id: '5',
      goal: 'Write challenges section',
      task_type: 'write',
      status: 'FINISH',
      sub_tasks: []
    },
    {
      id: '6',
      goal: 'Write conclusion',
      task_type: 'write',
      status: 'FINISH',
      sub_tasks: []
    }
  ]
};

// Mock content for the generated report/story - would come from your backend
const mockContent = `# The Commercial Value of Long-Article Writing AI Agents

## Introduction

Long-article writing AI agents represent a significant advancement in artificial intelligence technology, offering a powerful tool for content creation that combines the efficiency of automation with increasingly sophisticated writing capabilities. These AI agents are designed to generate extended pieces of content—from blog posts and articles to reports and creative narratives—with minimal human intervention. As businesses and organizations continue to prioritize content marketing and information dissemination, the commercial potential of these tools has grown substantially.

## Market Overview

The global market for AI writing tools is experiencing rapid growth, with the long-form content segment emerging as a particularly valuable niche. According to recent market analyses, the AI content creation market is expected to reach $2.6 billion by 2026, with long-form content generation tools representing approximately 35% of this value. This growth is driven by increasing demand for content across multiple industries, from media and publishing to education and enterprise documentation.

## Key Commercial Applications

Long-article writing AI agents offer commercial value across numerous sectors:

### Content Marketing

Content marketing remains one of the primary applications for long-form AI writers. Businesses can generate blog posts, white papers, and industry analyses at scale, maintaining consistent publishing schedules without proportionally increasing their content team. This enables companies to maintain a robust content marketing strategy even with limited human resources.

### Publishing and Media

Media organizations can utilize AI writing agents to produce routine reporting, freeing human journalists to focus on investigative work, interviews, and complex storytelling. This hybrid approach allows publishers to maintain or increase output while directing human talent toward higher-value activities.

### E-commerce

Product descriptions, category pages, and buying guides represent significant content needs for e-commerce businesses. Long-form AI writers can generate detailed product content that incorporates SEO best practices while maintaining consistent brand voice across thousands of products.

### Education and Training

Educational institutions and corporate training departments can leverage AI writers to develop course materials, study guides, and instructional content. This application is particularly valuable for technical subjects where clear, structured explanation is essential.

## ROI Considerations

The commercial value of long-article writing AI agents can be assessed through several ROI factors:

1. **Labor Cost Reduction**: AI writers can reduce the cost of content production by 60-80% compared to professional human writers, particularly for routine content needs.

2. **Time Efficiency**: Content that might take a human writer several days can be generated in minutes, allowing for faster publication cycles and more responsive content strategies.

3. **Scalability**: Businesses can scale content operations without proportional increases in staff, enabling content marketing at enterprise scale even for smaller organizations.

4. **Consistency**: AI writers maintain consistent tone, style, and quality across all content, eliminating variations that can occur with multiple human writers.

## Challenges and Limitations

Despite their commercial promise, long-article writing AI agents face several challenges that impact their commercial value:

### Quality Considerations

While AI writing quality has improved dramatically, the output still requires human review and editing for high-stakes content. This creates a hybrid workflow rather than full automation, somewhat limiting cost savings.

### Originality Concerns

AI-generated content may lack truly original insights or creative approaches that human writers can provide, potentially limiting its value for thought leadership content or creative applications.

### Technical Limitations

Current AI models still struggle with factual accuracy for specialized topics, requiring subject matter expert review to prevent misinformation, which adds to the workflow cost.

## Future Commercial Potential

The commercial value of long-article writing AI agents is likely to increase as the technology evolves:

1. **Improved Specialization**: Industry and domain-specific AI writers will offer higher quality for specialized fields like legal, medical, or technical writing.

2. **Enhanced Integration**: AI writing tools integrated with content management systems, SEO tools, and analytics platforms will provide end-to-end content solutions.

3. **Multimodal Capabilities**: Future AI writers will likely incorporate image generation, video script creation, and interactive content capabilities, increasing their value proposition.

## Conclusion

Long-article writing AI agents offer substantial commercial value through cost reduction, efficiency gains, and content scalability. While they don't fully replace human writers, they represent a powerful augmentation tool that enables organizations to produce more content at lower cost. The most successful commercial applications currently involve a human-AI collaboration model, where AI handles initial drafting and humans provide editing, fact-checking, and creative direction.

As technology continues to advance, the commercial value of these tools will likely increase further, with more specialized capabilities and improved quality reducing the need for human intervention. Organizations that effectively integrate AI writing agents into their content workflows stand to gain significant competitive advantages in content production capacity, potentially transforming content from a cost center to a scalable business asset.`;

// Pass the task graph directly to the TaskList component which handles hierarchy internally

const ResultsPage = () => {
  const { id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [taskList, setTaskList] = useState([]);
  const [generationStatus, setGenerationStatus] = useState('generating');
  const [copySuccess, setCopySuccess] = useState('');
  const [progress, setProgress] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [stopConfirmOpen, setStopConfirmOpen] = useState(false);
  const [stopInProgress, setStopInProgress] = useState(false);

  // Get the generation details from location state
  const generationDetails = location.state || {
    prompt: 'Loading prompt...',
    model: 'Loading model...',
    type: 'unknown',
    status: 'unknown'
  };

  // Poll status and fetch result when ready
  useEffect(() => {
    let pollInterval;
    let pollCount = 0;
    
    const fetchStatus = async () => {
      try {
        setLoading(true);
        
        // Try to reload tasks first to ensure the task is in the backend's memory
        if (pollCount === 0) {
          try {
            await reloadTasks();
          } catch (reloadErr) {
            console.warn("Failed to reload tasks:", reloadErr);
          }
        }
        
        // Get status from backend
        const statusData = await getGenerationStatus(id);
        
        if (statusData) {
          setGenerationStatus(statusData.status);
          
          if (statusData.elapsedTime) {
            setElapsedTime(Math.round(statusData.elapsedTime));
          }
          
          // Update model information if available
          if (statusData.model && statusData.model !== 'unknown') {
            generationDetails.model = statusData.model;
          }
          
          if (statusData.searchEngine) {
            generationDetails.searchEngine = statusData.searchEngine;
          }
          
          // Update progress based on status
          if (statusData.status === 'completed') {
            setProgress(100);
            
            // Fetch the result
            const resultData = await getGenerationResult(id);
            if (resultData && resultData.result) {
              setResult(resultData.result);
              
              // Update model information from result if available
              if (resultData.model && resultData.model !== 'unknown') {
                generationDetails.model = resultData.model;
              }
              
              if (resultData.searchEngine) {
                generationDetails.searchEngine = resultData.searchEngine;
              }
              
              // Fetch the task graph data
              try {
                const graphData = await getTaskGraph(id);
                if (graphData && graphData.taskGraph) {
                  // Pass the task graph directly without flattening
                  setTaskList(graphData.taskGraph);
                } else {
                  console.warn("Task graph data not available, using mock data as fallback");
                  setTaskList(mockGraphData);
                }
              } catch (graphErr) {
                console.warn("Failed to fetch task graph:", graphErr);
                // Fallback to mock data if task graph fetch fails
                setTaskList(mockGraphData);
              }
              
              clearInterval(pollInterval);
              setLoading(false);
            }
          } else if (statusData.status === 'error') {
            setError(statusData.error || 'An error occurred during generation');
            clearInterval(pollInterval);
            setLoading(false);
          } else if (statusData.status === 'stopped') {
            setError('Task has been stopped by user request.');
            clearInterval(pollInterval);
            setLoading(false);
          } else {
            // Still processing, increment progress
            pollCount++;
            // Simple simulated progress: 10% immediately, then gradually up to 90% while waiting
            const simulatedProgress = Math.min(10 + 80 * (pollCount / 60), 90);
            setProgress(simulatedProgress);
          }
        }
      } catch (err) {
        console.error('Error polling status:', err);
        
        // If this is the first attempt and we got an error, try to load directly
        if (pollCount === 0) {
          try {
            // Try to get the result directly
            const resultData = await getGenerationResult(id);
            if (resultData && resultData.result) {
              setResult(resultData.result);
              setGenerationStatus('completed');
              setProgress(100);
              
              // Update model information from result if available
              if (resultData.model && resultData.model !== 'unknown') {
                generationDetails.model = resultData.model;
              }
              
              if (resultData.searchEngine) {
                generationDetails.searchEngine = resultData.searchEngine;
              }
              
              // Fetch the task graph data
              try {
                const graphData = await getTaskGraph(id);
                if (graphData && graphData.taskGraph) {
                  // Pass the task graph directly without flattening
                  setTaskList(graphData.taskGraph);
                } else {
                  setTaskList(mockGraphData);
                }
              } catch (graphErr) {
                setTaskList(mockGraphData);
              }
              
              clearInterval(pollInterval);
              setLoading(false);
              return;
            }
          } catch (directErr) {
            console.error('Error fetching result directly:', directErr);
          }
        }
        
        setError('Error checking generation status: ' + (err.message || 'Unknown error'));
        clearInterval(pollInterval);
        setLoading(false);
      }
    };
    
    // Initial fetch
    fetchStatus();
    
    // Set up polling every 5 seconds
    pollInterval = setInterval(fetchStatus, 5001);
    
    return () => {
      clearInterval(pollInterval);
    };
  }, [id]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleTaskClick = (task) => {
    console.log('Task clicked:', task);
    // Here you could show details about the specific task
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([result], {type: 'text/markdown'});
    element.href = URL.createObjectURL(file);
    element.download = `${id}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleCopyToClipboard = () => {
    navigator.clipboard.writeText(result).then(
      () => {
        setCopySuccess('Copied to clipboard!');
        setTimeout(() => setCopySuccess(''), 3000);
      },
      () => {
        setCopySuccess('Failed to copy');
        setTimeout(() => setCopySuccess(''), 3000);
      }
    );
  };
  
  const handleStopGeneration = () => {
    setStopInProgress(true);
    stopTask(id)
      .then(response => {
        setGenerationStatus('stopped');
        setError('Task has been stopped by user request.');
      })
      .catch(err => {
        setError(`Failed to stop task: ${err.message}`);
      })
      .finally(() => {
        setStopConfirmOpen(false);
        setStopInProgress(false);
      });
  };

  if (loading && generationStatus !== 'completed') {
    return (
      <Container maxWidth="lg" sx={{ mt: 8 }}>
        {/* Stop Confirmation Dialog */}
        <Dialog
          open={stopConfirmOpen}
          onClose={() => setStopConfirmOpen(false)}
          aria-labelledby="stop-dialog-title"
          aria-describedby="stop-dialog-description"
        >
          <DialogTitle id="stop-dialog-title">
            Confirm Stop Generation
          </DialogTitle>
          <DialogContent>
            <DialogContentText id="stop-dialog-description">
              Are you sure you want to stop this generation? This action cannot be undone, and the generation will be terminated immediately.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setStopConfirmOpen(false)} disabled={stopInProgress}>
              Cancel
            </Button>
            <Button 
              onClick={handleStopGeneration} 
              color="error" 
              autoFocus
              disabled={stopInProgress}
              startIcon={stopInProgress ? <CircularProgress size={16} /> : null}
            >
              {stopInProgress ? "Stopping..." : "Stop Generation"}
            </Button>
          </DialogActions>
        </Dialog>
        
        <Box sx={{ mb: 4 }}>
          <Typography variant="h5" sx={{ mb: 2, textAlign: 'center' }}>
            {generationStatus === 'generating' ? 'Generating content...' : 'Loading results...'}
          </Typography>
          
          <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              Generation Details
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Typography variant="body1" sx={{ mb: 2 }}>
              <strong>Prompt:</strong> {generationDetails.prompt.slice(0, 150)}{generationDetails.prompt.length > 150 ? '...' : ''}
            </Typography>
            
            <Typography variant="body1" sx={{ mb: 2 }}>
              <strong>Model:</strong> {generationDetails.model}
            </Typography>
            
            {generationDetails.searchEngine && (
              <Typography variant="body1" sx={{ mb: 2 }}>
                <strong>Search Engine:</strong> {generationDetails.searchEngine}
              </Typography>
            )}
            
            <Box sx={{ mb: 3 }}>
              <LinearProgress 
                variant="determinate" 
                value={progress} 
                sx={{ 
                  height: 8, 
                  borderRadius: 4,
                  mb: 1
                }} 
              />
              
              <Typography variant="body2" color="text.secondary" align="right">
                {progress.toFixed(2)}% complete
                {elapsedTime > 0
                  ? `· ${Math.floor(elapsedTime / 60)}:${String(elapsedTime % 60).padStart(2, '0')} elapsed`
                  : ''}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
              <Button 
                variant="contained" 
                color="error"
                onClick={() => setStopConfirmOpen(true)}
              >
                Stop Generation
              </Button>
            </Box>
            
            <Typography variant="body2" color="text.secondary">
              This may take several minutes depending on the complexity of the task.
            </Typography>
          </Paper>
          
          {/* Show live task list during generation */}
          <LiveTaskList taskId={id} onTaskClick={handleTaskClick} />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 8 }}>
        <Alert severity="error">
          {error}
        </Alert>
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Button variant="contained" onClick={() => navigate(-1)}>
            Go Back
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {generationDetails.type === 'story' ? 'Generated Story' : 'Generated Report'}
        </Typography>
        
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Generation Details
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} md={8}>
              <Typography variant="body1">
                <strong>Prompt:</strong> {generationDetails.prompt}
              </Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <Typography variant="body1">
                <strong>Model:</strong> {generationDetails.model}
              </Typography>
            </Grid>
            {generationDetails.searchEngine && (
              <Grid item xs={12} md={4}>
                <Typography variant="body1">
                  <strong>Search Engine:</strong> {generationDetails.searchEngine}
                </Typography>
              </Grid>
            )}
            <Grid item xs={12}>
              <Typography variant="body1">
                <strong>Status:</strong> {
                  generationStatus === 'completed' ? 
                  <span style={{ color: 'green' }}>Complete</span> : 
                  generationStatus === 'stopped' ?
                  <span style={{ color: 'red' }}>Stopped</span> :
                  <span style={{ color: 'orange' }}>In Progress</span>
                }
              </Typography>
            </Grid>
          </Grid>
        </Paper>
      </Box>

      <Box sx={{ mb: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={activeTab} onChange={handleTabChange} aria-label="result tabs">
            <Tab label={generationStatus === 'completed' ? "Result" : "Generating..."} />
            <Tab 
              label={
                generationStatus === 'completed' ? 
                "Task Decomposition" : 
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  Live Tasks
                  {generationStatus !== 'completed' && 
                    <Chip size="small" color="primary" label="Active" sx={{ height: 20 }} />
                  }
                </Box>
              } 
            />
          </Tabs>
        </Box>

        {activeTab === 0 && (
          <Paper elevation={3} sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2, gap: 1 }}>
              <Button 
                variant="outlined" 
                startIcon={<ContentCopyIcon />}
                onClick={handleCopyToClipboard}
              >
                Copy to Clipboard
              </Button>
              <Button 
                variant="outlined" 
                startIcon={<DownloadIcon />}
                onClick={handleDownload}
              >
                Download
              </Button>
            </Box>
            {copySuccess && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {copySuccess}
              </Alert>
            )}
            <Box className="markdown-content">
              <ReactMarkdown>
                {result}
              </ReactMarkdown>
            </Box>
          </Paper>
        )}

        {activeTab === 1 && (
          // Always use LiveTaskList for consistent display
          <LiveTaskList taskId={id} onTaskClick={handleTaskClick} />
        )}
      </Box>
    </Container>
  );
};

export default ResultsPage;