import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { 
  Box, 
  Paper, 
  Typography, 
  useTheme, 
  Button, 
  ButtonGroup,
  Chip,
  Tooltip,
  IconButton,
  Divider
} from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import InfoIcon from '@mui/icons-material/Info';

const TaskGraph = ({ data, onNodeClick }) => {
  const d3Container = useRef(null);
  const theme = useTheme();
  const [viewMode, setViewMode] = useState('tree'); // tree, radial, force
  const [selectedNode, setSelectedNode] = useState(null);
  
  // Define colors for different task types using theme colors
  const nodeColors = {
    write: theme.palette.secondary.main,    // Teal for composition
    think: theme.palette.primary.main,      // Purple for reasoning 
    search: '#FF9800'                       // Orange for retrieval
  };

  // Status colors
  const statusColors = {
    FINISH: theme.palette.success.main,      // Green
    DOING: theme.palette.primary.main,       // Purple
    NOT_READY: theme.palette.grey[400],      // Grey
    READY: theme.palette.warning.main,       // Orange/Yellow
    FAILED: theme.palette.error.main         // Red
  };

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    if (onNodeClick) onNodeClick(node);
  };

  const resetZoom = () => {
    if (!d3Container.current) return;
    
    d3.select(d3Container.current)
      .select('svg g')
      .transition()
      .duration(750)
      .attr('transform', `translate(${width / 2}, 80) scale(1)`);
  };

  // Set up dimensions - make these responsive
  const width = 900;
  const height = 600;
  const nodeRadius = 25;
  const nodePadding = 15;
  
  useEffect(() => {
    if (!data || !d3Container.current) return;
    
    // Clear any existing SVG
    d3.select(d3Container.current).selectAll("*").remove();

    // Create the SVG container with zoom behavior
    const svg = d3.select(d3Container.current)
      .append('svg')
      .attr('width', '100%')
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');
    
    // Add zoom functionality
    const zoom = d3.zoom()
      .scaleExtent([0.5, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });
    
    svg.call(zoom);
    
    // Create main group for the graph
    const g = svg.append('g')
      .attr('transform', `translate(${width / 2}, 80)`);
      
    // Debugging
    console.log("Graph data received:", JSON.stringify(data, null, 2).slice(0, 200) + '...');
      
    // Create a hierarchical layout with special handling for execute nodes
    let processedData;
    
    // Process the data to follow the display_plan logic
    function processNode(node) {
      if (!node) return;
      
      // Check if this is an execute node
      const isExecuteNode = node.is_execute_node || node.node_type === "EXECUTE_NODE";
      
      // Check if this node has a single execute child
      const hasSingleExecuteChild = node.sub_tasks && 
                              node.sub_tasks.length === 1 && 
                              (node.sub_tasks[0].is_execute_node || node.sub_tasks[0].node_type === "EXECUTE_NODE");
      
      // Mark node for rendering considerations
      node.isActualExecuteNode = isExecuteNode;
      
      // Unlike the TaskList, we don't want to strip out nodes from the graph
      // We just mark them for display purposes
      if (Array.isArray(node.sub_tasks) && node.sub_tasks.length > 0) {
        // Process and sort subtasks
        node.sub_tasks.sort((a, b) => {
          const aId = String(a.id).split('.').pop() || '0';
          const bId = String(b.id).split('.').pop() || '0';
          return parseInt(aId) - parseInt(bId);
        });
        
        // Process each subtask
        node.sub_tasks.forEach(processNode);
      }
    }
    
    // Process the data to ensure it has the appropriate structure for visualization
    if (!data) {
      // Create an empty root node if no data
      processedData = {
        id: "root",
        goal: "No tasks available",
        task_type: "write",
        status: "FINISH",
        sub_tasks: []
      };
    } else if (Array.isArray(data)) {
      // We have a flat task list, convert to hierarchical
      // First, create a proper root node
      const rootNode = {
        id: "0",
        goal: "Task Decomposition",
        task_type: "write",
        status: "FINISH",
        sub_tasks: []
      };
      
      // Create a map to quickly locate parent nodes
      const nodeMap = new Map();
      nodeMap.set("0", rootNode);
      
      // First pass: Add all tasks to the map
      data.forEach(task => {
        // Create a copy of the task with empty sub_tasks
        const taskNode = { ...task, sub_tasks: [] };
        nodeMap.set(String(task.id), taskNode);
      });
      
      // Second pass: Establish parent-child relationships
      data.forEach(task => {
        const taskId = String(task.id);
        const taskNode = nodeMap.get(taskId);
        
        // Skip if we somehow don't have this task
        if (!taskNode) return;
        
        // Try to determine parent ID based on task ID format (like "0.1.2")
        const idParts = taskId.split('.');
        
        if (idParts.length > 1) {
          // Remove the last segment to get parent ID
          idParts.pop();
          const parentId = idParts.join('.');
          
          // Check if parent exists in our map
          if (nodeMap.has(parentId)) {
            // Add this task as a child of its parent
            nodeMap.get(parentId).sub_tasks.push(taskNode);
          } else {
            // If parent not found, add to root
            rootNode.sub_tasks.push(taskNode);
          }
        } else {
          // Top-level task goes directly under root
          rootNode.sub_tasks.push(taskNode);
        }
      });
      
      // Use the constructed hierarchy
      processedData = rootNode;
    } else if (data.sub_tasks && data.sub_tasks.length > 0) {
      // We have a hierarchical structure already
      processedData = { ...data };
      processNode(processedData);
    } else {
      // Data exists but has no subtasks
      // Create a wrapper root node
      processedData = {
        id: "root",
        goal: data.goal || "Task Decomposition",
        task_type: data.task_type || "write",
        status: data.status || "FINISH",
        sub_tasks: [data]
      };
    }
    
    // No need to process the root node again if we're using a task list,
    // as it's already been processed in the conversion step
    
    // Create the hierarchy from the processed data
    const hierarchy = d3.hierarchy(processedData);

    // Different layout strategies based on viewMode
    let nodes;
    
    if (viewMode === 'tree') {
      // Standard tree layout (top to bottom)
      const treeLayout = d3.tree()
        .size([width - 160, height - 160])
        .nodeSize([70, 120]);
      
      nodes = treeLayout(hierarchy);
    } else if (viewMode === 'radial') {
      // Radial tree layout
      const radius = Math.min(width, height) / 2 - 80;
      const radialLayout = d3.tree()
        .size([2 * Math.PI, radius])
        .separation((a, b) => (a.parent === b.parent ? 1 : 2) / a.depth);
      
      nodes = radialLayout(hierarchy);
      
      // Convert from polar to Cartesian coordinates
      nodes.descendants().forEach(d => {
        const x = d.x;
        const y = d.y;
        d.x = y * Math.cos(x - Math.PI / 2);
        d.y = y * Math.sin(x - Math.PI / 2);
      });
    } else if (viewMode === 'force') {
      // Force-directed layout for more organic arrangement
      const simulation = d3.forceSimulation(hierarchy.descendants())
        .force('link', d3.forceLink(hierarchy.links()).id(d => d.id).distance(100))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(0, 0))
        .force('collide', d3.forceCollide(nodeRadius * 2))
        .stop();
      
      // Run the simulation
      for (let i = 0; i < 300; ++i) simulation.tick();
      
      nodes = hierarchy;
    }

    // Create links with smooth curves
    const linkGenerator = viewMode === 'radial' 
      ? d3.linkRadial()
          .angle(d => d.x)
          .radius(d => d.y)
      : d3.linkHorizontal()
          .x(d => d.x)
          .y(d => d.y);
    
    const links = g.append('g')
      .attr('class', 'links')
      .selectAll('path')
      .data(nodes.links())
      .enter()
      .append('path')
      .attr('d', viewMode === 'force' 
        ? d => {
            return `M${d.source.x},${d.source.y}
                    C${(d.source.x + d.target.x) / 2},${d.source.y}
                     ${(d.source.x + d.target.x) / 2},${d.target.y}
                     ${d.target.x},${d.target.y}`;
          }
        : linkGenerator
      )
      .attr('fill', 'none')
      .attr('stroke', theme.palette.grey[300])
      .attr('stroke-width', 2)
      .attr('opacity', 0.7);
    
    // Add dependency indicators on links
    const markers = links.append('marker')
      .attr('id', (d, i) => `arrowhead-${i}`)
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 10)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', theme.palette.grey[400]);
    
    // Create node groups
    const node = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(nodes.descendants())
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', d => `translate(${d.x},${d.y})`)
      .attr('cursor', 'pointer')
      .on('click', (event, d) => {
        event.stopPropagation();
        handleNodeClick(d.data);
        
        // Highlight the selected node
        node.selectAll('circle')
          .attr('stroke-width', n => n === d ? 4 : 2)
          .attr('stroke-opacity', n => n === d ? 1 : 0.6);
        
        // Center view on clicked node with smooth animation
        svg.transition()
          .duration(750)
          .call(zoom.transform, d3.zoomIdentity
            .translate(width / 2, height / 2)
            .scale(1.2)
            .translate(-d.x, -d.y));
      });
    
    // Add node background - slightly larger than the main circle for a halo effect
    node.append('circle')
      .attr('r', nodeRadius + 2)
      .attr('fill', 'white')
      .attr('opacity', 0.8);
    
    // Add main circle for nodes
    node.append('circle')
      .attr('r', nodeRadius)
      .attr('fill', d => {
        const taskType = d.data.task_type || '';
        return nodeColors[taskType] || theme.palette.grey[400];
      })
      .attr('opacity', 0.9)
      .attr('stroke', d => {
        const status = d.data.status || 'NOT_READY';
        return statusColors[status] || theme.palette.grey[400];
      })
      .attr('stroke-width', d => {
        // Make execute nodes have a thicker stroke
        return d.data.isActualExecuteNode ? 4 : 2;
      })
      .attr('stroke-dasharray', d => {
        // Use a dashed stroke for execute nodes
        return d.data.isActualExecuteNode ? '3,3' : 'none';
      })
      .attr('stroke-opacity', 0.8)
      .on('mouseover', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', nodeRadius + 2)
          .attr('stroke-width', 3)
          .attr('opacity', 1);
      })
      .on('mouseout', function() {
        d3.select(this)
          .transition()
          .duration(200)
          .attr('r', nodeRadius)
          .attr('stroke-width', 2)
          .attr('opacity', 0.9);
      });
    
    // Add task type icon/labels (W, T, S)
    node.append('text')
      .attr('dy', 5)
      .attr('text-anchor', 'middle')
      .attr('fill', 'white')
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text(d => {
        const taskType = d.data.task_type || '';
        return taskType.charAt(0).toUpperCase();
      });
    
    // Add goal text below nodes with better wrapping
    node.append('foreignObject')
      .attr('x', -40)
      .attr('y', nodeRadius + 5)
      .attr('width', 80)
      .attr('height', 40)
      .append('xhtml:div')
      .style('text-align', 'center')
      .style('font-size', '12px')
      .style('color', theme.palette.text.secondary)
      .style('overflow', 'hidden')
      .style('text-overflow', 'ellipsis')
      .style('display', '-webkit-box')
      .style('-webkit-line-clamp', '2')
      .style('-webkit-box-orient', 'vertical')
      .style('line-height', '1.2')
      .html(d => d.data.goal || '');
    
    // Add ID as small badge on the node
    node.append('circle')
      .attr('r', 10)
      .attr('cx', nodeRadius - 5)
      .attr('cy', -nodeRadius + 5)
      .attr('fill', 'white')
      .attr('stroke', theme.palette.grey[300])
      .attr('stroke-width', 1);
    
    node.append('text')
      .attr('x', nodeRadius - 5)
      .attr('y', -nodeRadius + 9)
      .attr('text-anchor', 'middle')
      .attr('fill', theme.palette.text.secondary)
      .attr('font-size', '10px')
      .attr('font-weight', 'bold')
      .text(d => d.data.id || '');
    
    // Add status indicator
    node.append('circle')
      .attr('r', 6)
      .attr('cx', -nodeRadius + 5)
      .attr('cy', -nodeRadius + 5)
      .attr('fill', d => {
        const status = d.data.status || 'NOT_READY';
        return statusColors[status];
      });
    
    // Add legend with improved styling
    const legend = svg.append('g')
      .attr('transform', `translate(20, 20)`)
      .attr('class', 'legend');
    
    // Background for legend
    legend.append('rect')
      .attr('width', 320)
      .attr('height', 95)
      .attr('rx', 8)
      .attr('ry', 8)
      .attr('fill', 'white')
      .attr('stroke', theme.palette.grey[200])
      .attr('stroke-width', 1)
      .attr('opacity', 0.9);
    
    // Task type legend
    const taskTypes = [
      { type: 'write', label: 'Composition' },
      { type: 'think', label: 'Reasoning' },
      { type: 'search', label: 'Retrieval' }
    ];
    
    const legendTitle = legend.append('text')
      .attr('x', 15)
      .attr('y', 25)
      .attr('fill', theme.palette.text.primary)
      .attr('font-size', '14px')
      .attr('font-weight', 'bold')
      .text('Legend');
    
    // Task type icons
    taskTypes.forEach((task, i) => {
      const g = legend.append('g')
        .attr('transform', `translate(${15 + i * 100}, 45)`);
      
      g.append('circle')
        .attr('r', 8)
        .attr('fill', nodeColors[task.type]);
      
      g.append('text')
        .attr('x', 15)
        .attr('y', 4)
        .attr('fill', theme.palette.text.secondary)
        .attr('font-size', '12px')
        .text(task.label);
    });
    
    // Status legend 
    const statuses = [
      { status: 'FINISH', label: 'Completed' },
      { status: 'DOING', label: 'In Progress' },
      { status: 'READY', label: 'Ready' }
    ];
    
    statuses.forEach((status, i) => {
      const g = legend.append('g')
        .attr('transform', `translate(${15 + i * 100}, 75)`);
      
      g.append('circle')
        .attr('r', 5)
        .attr('fill', statusColors[status.status]);
      
      g.append('text')
        .attr('x', 15)
        .attr('y', 4)
        .attr('fill', theme.palette.text.secondary)
        .attr('font-size', '12px')
        .text(status.label);
    });
    
    // Initial zoom to fit all content
    const bounds = g.node().getBBox();
    const fullWidth = bounds.width;
    const fullHeight = bounds.height;
    const midX = bounds.x + fullWidth / 2;
    const midY = bounds.y + fullHeight / 2;
    
    if (fullWidth > 0 && fullHeight > 0) {
      const scale = 0.9 / Math.max(fullWidth / width, fullHeight / height);
      const translate = [width / 2 - scale * midX, height / 2 - scale * midY];
      
      svg.call(
        zoom.transform,
        d3.zoomIdentity
          .translate(translate[0], translate[1])
          .scale(scale)
      );
    }

  }, [data, viewMode, theme, onNodeClick]);

  return (
    <Paper 
      elevation={0} 
      sx={{ 
        p: 3, 
        mb: 4,
        border: '1px solid',
        borderColor: 'grey.100',
        borderRadius: 3,
        overflow: 'hidden'
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, display: 'flex', alignItems: 'center' }}>
          Task Decomposition Graph
          <Tooltip title="This graph visualizes how the writing task is broken down recursively into subtasks">
            <IconButton size="small" sx={{ ml: 1 }}>
              <InfoIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <ButtonGroup size="small" variant="outlined" aria-label="visualization mode">
            <Button 
              onClick={() => setViewMode('tree')} 
              variant={viewMode === 'tree' ? 'contained' : 'outlined'}
            >
              Tree
            </Button>
            <Button 
              onClick={() => setViewMode('radial')} 
              variant={viewMode === 'radial' ? 'contained' : 'outlined'}
            >
              Radial
            </Button>
            <Button 
              onClick={() => setViewMode('force')} 
              variant={viewMode === 'force' ? 'contained' : 'outlined'}
            >
              Force
            </Button>
          </ButtonGroup>
          
          <ButtonGroup size="small">
            <IconButton onClick={resetZoom}>
              <RestartAltIcon fontSize="small" />
            </IconButton>
          </ButtonGroup>
        </Box>
      </Box>
      
      <Divider sx={{ mb: 2 }} />
      
      {selectedNode && (
        <Box sx={{ mb: 2, p: 2, backgroundColor: 'grey.50', borderRadius: 2 }}>
          <Typography variant="subtitle2" fontWeight={600}>
            Selected Node: {selectedNode.id}
          </Typography>
          <Typography variant="body2" sx={{ mt: 0.5 }}>
            {selectedNode.goal}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
            <Chip 
              size="small" 
              label={selectedNode.task_type || 'Unknown'} 
              color={
                selectedNode.task_type === 'write' ? 'secondary' : 
                selectedNode.task_type === 'think' ? 'primary' : 
                'default'
              }
              variant="outlined"
            />
            <Chip 
              size="small" 
              label={selectedNode.status || 'Not started'} 
              color={
                selectedNode.status === 'FINISH' ? 'success' : 
                selectedNode.status === 'DOING' ? 'primary' : 
                selectedNode.status === 'READY' ? 'warning' : 
                'default'
              }
              variant="outlined"
            />
          </Box>
        </Box>
      )}
      
      <Box 
        ref={d3Container} 
        sx={{ 
          width: '100%', 
          height: 600,
          backgroundColor: 'rgba(249, 250, 251, 0.5)',
          borderRadius: 2,
          overflow: 'hidden',
          '&:hover': {
            backgroundColor: 'rgba(249, 250, 251, 0.8)',
          }
        }}
      />
      
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="text.secondary">
          Tip: Click on nodes to see details. Drag to pan, use mouse wheel to zoom.
        </Typography>
      </Box>
    </Paper>
  );
};

export default TaskGraph;