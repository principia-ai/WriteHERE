import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  Chip,
  Divider,
  Alert,
  CircularProgress,
  Button
} from '@mui/material';
import CreateIcon from '@mui/icons-material/Create';
import SearchIcon from '@mui/icons-material/Search';
import PsychologyIcon from '@mui/icons-material/Psychology';
import io from 'socket.io-client';

// Create a singleton socket instance for the entire application
let socket;

// Function to get or create the socket instance
const getSocket = () => {
  if (!socket) {
    // Initialize socket connection - make sure this matches your backend URL
    // Using a dynamic approach that works with both development and production
    const socketUrl = process.env.REACT_APP_API_URL || 'http://localhost:5002';
    console.log('Creating new WebSocket connection to:', socketUrl);
    
    socket = io(socketUrl, {
      transports: ['polling', 'websocket'], // Try polling first, then WebSocket (more reliable initial connection)
      reconnectionAttempts: 10,
      reconnectionDelay: 500,
      timeout: 10000,
      autoConnect: true,
      query: { timestamp: Date.now() } // Prevent caching issues
    });
    
    // Set up global error handlers
    socket.on('connect_error', (err) => {
      console.error('Global socket connection error:', err);
    });
    
    socket.on('error', (err) => {
      console.error('Global socket error:', err);
    });
  }
  
  return socket;
};

const getTaskIcon = (taskType) => {
  switch (taskType) {
    case 'write':
      return <CreateIcon />;
    case 'search':
      return <SearchIcon />;
    case 'think':
      return <PsychologyIcon />;
    default:
      return <CreateIcon />;
  }
};

const getStatusColor = (status) => {
  switch (status) {
    case 'FINISH':  // Keep this for backward compatibility
      return 'success';
    case 'FINISHED':
      return 'success';
    case 'DOING':   // Keep this for backward compatibility
      return 'primary';
    case 'IN PROGRESS':
      return 'primary';
    case 'READY':
      return 'warning';
    case 'FAILED':
      return 'error';
    case 'NOT_READY':
      return 'default';
    default:
      return 'default';
  }
};

const LiveTaskList = ({ taskId, onTaskClick }) => {
  const [connected, setConnected] = useState(false);
  const [subscribed, setSubscribed] = useState(false);
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [socket, setSocket] = useState(null);

  // Process tasks hierarchically for better visualization
  const flattenTasks = (task, result = [], skipRoot = false, level = 0, parent = null) => {
    if (!task) return result;
    
    // Skip execute nodes for cleaner task list
    const isExecuteNode = task.is_execute_node || task.node_type === "EXECUTE_NODE";
    
    // Add the current task with hierarchy information
    if (!skipRoot && !isExecuteNode) {
      result.push({
        ...task,
        level, // Add level for indentation
        parent
      });
    }
    
    // Process subtasks if they exist
    if (Array.isArray(task.sub_tasks) && task.sub_tasks.length > 0) {
      // Sort the subtasks by ID
      const sortedSubTasks = [...task.sub_tasks].sort((a, b) => {
        const aId = String(a.id).split('.').pop() || '0';
        const bId = String(b.id).split('.').pop() || '0';
        return parseInt(aId) - parseInt(bId);
      });
      
      // Process each subtask with increased indentation level
      for (const subTask of sortedSubTasks) {
        flattenTasks(subTask, result, false, level + 1, task.id);
      }
    }
    
    return result;
  };

  useEffect(() => {
    // First try to get task graph data directly from API for completed tasks
    const fetchTaskGraph = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:5002/api/task-graph/${taskId}`);
        if (response.ok) {
          const data = await response.json();
          if (data.taskGraph) {
            const flatTasks = flattenTasks(data.taskGraph, [], false, 0, null);
            setTasks(flatTasks);
            setLoading(false);
            // Still connect to socket for potential additional updates
            return true;
          }
        }
        return false;
      } catch (error) {
        console.log("Error fetching task graph, will try socket connection", error);
        return false;
      }
    };

    // Try to fetch the task graph data
    fetchTaskGraph();

    // Initialize socket connection
    console.log('Initializing socket connection');
    const newSocket = getSocket();
    setSocket(newSocket);
    
    // Set up event handlers for this component instance
    if (newSocket) {
      // Add socket connection debug events
      const onConnectError = (err) => {
        console.error('Connection error:', err);
        setError(`Connection error: ${err.message}`);
        setConnected(false);
      };
      
      const onConnectTimeout = () => {
        console.error('Connection timeout');
        setError('Connection timeout - server might be unavailable');
        setConnected(false);
      };
      
      const onSocketError = (err) => {
        console.error('Socket error:', err);
        setError(`Socket error: ${err.message || 'Unknown error'}`);
      };
      
      const onConnect = () => {
        console.log('Socket connected successfully');
        setConnected(true);
        setError('');
        
        // Subscribe to task updates for this taskId
        console.log('Subscribing to task updates for:', taskId);
        newSocket.emit('subscribe_to_task', { taskId });
      };
      
      const onDisconnect = () => {
        console.log('Socket disconnected');
        setConnected(false);
        setSubscribed(false);
      };
      
      const onSubscriptionStatus = (data) => {
        console.log('Subscription status received:', data);
        if (data.taskId === taskId) {
          if (data.status === 'subscribed') {
            console.log('Successfully subscribed to task updates');
            setSubscribed(true);
            setError('');
          } else {
            console.error('Failed to subscribe:', data.message);
            setError(`Failed to subscribe to task updates: ${data.message || 'Unknown error'}`);
          }
        }
      };
      
      const onTaskUpdate = (data) => {
        console.log('Task update received:', JSON.stringify(data).slice(0, 200) + '...');
        if (data.taskId === taskId) {
          setLoading(false);
          
          if (data.taskGraph) {
            // Flatten tasks for display with hierarchy information
            const flatTasks = flattenTasks(data.taskGraph, [], false, 0, null);
            console.log(`Received update with ${flatTasks.length} tasks`);
            setTasks(flatTasks);
          }
        }
      };
      
      // Add a test handler for connection verification
      const onConnectionTest = (data) => {
        console.log('Received connection test message:', data);
        setConnected(true);
        setError('');
      };
      
      // Register all event handlers
      newSocket.on('connect_error', onConnectError);
      newSocket.on('connect_timeout', onConnectTimeout);
      newSocket.on('error', onSocketError);
      newSocket.on('connect', onConnect);
      newSocket.on('disconnect', onDisconnect);
      newSocket.on('subscription_status', onSubscriptionStatus);
      newSocket.on('task_update', onTaskUpdate);
      newSocket.on('connection_test', onConnectionTest);
      
      // If socket is already connected, subscribe immediately
      if (newSocket.connected) {
        console.log('Socket already connected, subscribing immediately');
        setConnected(true);
        newSocket.emit('subscribe_to_task', { taskId });
      } else {
        console.log('Socket not yet connected, will subscribe on connect event');
      }
      
      // Cleanup function
      return () => {
        console.log('Cleaning up socket listeners');
        newSocket.off('connect_error', onConnectError);
        newSocket.off('connect_timeout', onConnectTimeout);
        newSocket.off('error', onSocketError);
        newSocket.off('connect', onConnect);
        newSocket.off('disconnect', onDisconnect);
        newSocket.off('subscription_status', onSubscriptionStatus);
        newSocket.off('task_update', onTaskUpdate);
        newSocket.off('connection_test', onConnectionTest);
      };
    }
    
    return () => {}; // Empty cleanup if no socket
  }, [taskId]); // Only re-run if taskId changes

  if (loading) {
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 4, textAlign: 'center' }}>
        <CircularProgress size={40} sx={{ mb: 2 }} />
        <Typography variant="body1">Loading task data...</Typography>
      </Paper>
    );
  }

  if (error) {
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Typography variant="body1">
          Unable to show live task updates. You can still view the final result when generation completes.
        </Typography>
      </Paper>
    );
  }

  if (!connected) {
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Alert severity="warning" sx={{ mb: 2 }}>
          Not connected to the server
        </Alert>
        <Typography variant="body1" sx={{ mb: 2 }}>
          {error || "Trying to reconnect to see live task updates..."}
        </Typography>
        <Button 
          variant="contained" 
          color="primary"
          onClick={() => {
            console.log("Manual reconnect attempt");
            if (socket) {
              socket.disconnect();
              setTimeout(() => {
                socket.connect();
                socket.emit('subscribe_to_task', { taskId });
              }, 500);
            } else {
              const newSocket = getSocket();
              setSocket(newSocket);
            }
          }}
        >
          Try Reconnecting
        </Button>
      </Paper>
    );
  }

  if (tasks.length === 0) {
    return (
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Task Progress
        </Typography>
        <Divider sx={{ mb: 2 }} />
        <Box sx={{ textAlign: 'center', py: 3 }}>
          <Typography variant="body1" color="text.secondary">
            Waiting for tasks to start...
          </Typography>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
      <Typography variant="h6" gutterBottom>
        Task Hierarchy
      </Typography>
      <Box sx={{ mb: 2 }}>
        {tasks.length > 0 ? (
          <>
            <Chip 
              label={connected ? "Connected" : "Using saved data"} 
              color={connected ? "success" : "default"}
              size="small"
              sx={{ mr: 1 }}
            />
            {connected && (
              <Chip 
                label={subscribed ? "Receiving updates" : "Not subscribed"} 
                color={subscribed ? "success" : "warning"}
                size="small"
              />
            )}
          </>
        ) : (
          <>
            <Chip 
              label={connected ? "Connected" : "Disconnected"} 
              color={connected ? "success" : "error"}
              size="small"
              sx={{ mr: 1 }}
            />
            <Chip 
              label={subscribed ? "Receiving updates" : "Not subscribed"} 
              color={subscribed ? "success" : "warning"}
              size="small"
            />
          </>
        )}
      </Box>
      <Divider sx={{ mb: 2 }} />
      <List sx={{ width: '100%', bgcolor: 'background.paper' }}>
        {tasks.map((task, index) => (
          <React.Fragment key={task.id || index}>
            <ListItem 
              alignItems="flex-start" 
              button 
              onClick={() => onTaskClick && onTaskClick(task)}
              sx={{ 
                borderLeft: `4px solid ${
                  task.task_type === 'write' ? '#4CAF50' : 
                  task.task_type === 'think' ? '#2196F3' : 
                  task.task_type === 'search' ? '#FF9800' : 
                  '#9E9E9E'
                }`,
                mb: 1,
                pl: 2 + (task.level || 0) * 3, // Add indentation based on level
                backgroundColor: task.status === 'DOING' ? 'rgba(33, 150, 243, 0.08)' : 
                                 task.status === 'FINISH' ? 'rgba(76, 175, 80, 0.05)' : 'inherit'
              }}
            >
              <ListItemIcon sx={{ position: 'relative' }}>
                {/* Show hierarchy connector with a subtle dashed line */}
                {(task.level > 0) && (
                  <>
                    <Box
                      sx={{
                        position: 'absolute',
                        left: -24 * task.level,
                        top: '50%',
                        width: 16,
                        height: 1,
                        borderTop: '1px dashed rgba(0, 0, 0, 0.15)',
                        zIndex: 1
                      }}
                    />
                    <Box
                      sx={{
                        position: 'absolute',
                        left: -24 * task.level,
                        top: 0,
                        width: 1,
                        bottom: '50%',
                        borderLeft: '1px dashed rgba(0, 0, 0, 0.15)',
                        zIndex: 1
                      }}
                    />
                  </>
                )}
                {getTaskIcon(task.task_type)}
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1">
                      {task.id}. {task.goal}
                    </Typography>
                    <Chip 
                      label={task.status === 'FINISH' ? 'FINISHED' : 
                             task.status === 'DOING' ? 'IN PROGRESS' : 
                             task.status || 'NOT READY'} 
                      size="small" 
                      color={getStatusColor(task.status)}
                      sx={{ ml: 1 }}
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    {task.dependency && task.dependency.length > 0 && (
                      <Typography component="span" variant="body2" color="text.secondary">
                        Dependencies: {task.dependency.join(', ')}
                      </Typography>
                    )}
                  </Box>
                }
              />
            </ListItem>
            {index < tasks.length - 1 && <Divider variant="inset" component="li" />}
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
};

export default LiveTaskList;