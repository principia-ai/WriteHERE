import React, { useState, useEffect } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Button, 
  IconButton, 
  Drawer, 
  List, 
  ListItem, 
  ListItemText, 
  Box, 
  useMediaQuery, 
  useTheme,
  Container,
  Divider,
  Menu,
  MenuItem,
  AccordionSummary,
  Tooltip
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import EditNoteIcon from '@mui/icons-material/EditNote';
import LanguageIcon from '@mui/icons-material/Language';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useTranslation } from 'react-i18next';
import { changeLanguage } from '../i18n';

const Header = () => {
  const { t } = useTranslation();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [languageMenu, setLanguageMenu] = useState(null);
  const [currentLanguage, setCurrentLanguage] = useState(() => {
    return localStorage.getItem('preferredLanguage') || 'english';
  });
  
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleLanguageMenuOpen = (event) => {
    setLanguageMenu(event.currentTarget);
  };

  const handleLanguageMenuClose = () => {
    setLanguageMenu(null);
  };

  const handleLanguageChange = (language) => {
    setCurrentLanguage(language);
    localStorage.setItem('preferredLanguage', language);
    changeLanguage(language);
    handleLanguageMenuClose();
  };

  useEffect(() => {
    document.documentElement.setAttribute('lang', currentLanguage === 'chinese' ? 'zh' : 'en');
  }, [currentLanguage]);

  const menuItems = [
    { text: t('common.home'), path: '/' },
    { text: t('common.storyGeneration'), path: '/story-generation' },
    { text: t('common.reportGeneration'), path: '/report-generation' },
    { text: t('common.about'), path: '/about' }
  ];

  const drawer = (
    <Box sx={{ width: 280, padding: 2 }} role="presentation">
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box 
            sx={{ 
              display: 'flex',
              alignItems: 'center',
              mr: 1,
              position: 'relative'
            }}
          >
            <EditNoteIcon 
              sx={{ 
                color: 'primary.main',
                fontSize: 24,
                filter: 'drop-shadow(0px 1px 1px rgba(0,0,0,0.1))'
              }} 
            />
            <Box 
              sx={{
                position: 'absolute',
                right: -2,
                bottom: -2,
                width: 8,
                height: 8,
                backgroundColor: 'secondary.main',
                borderRadius: '50%',
                boxShadow: '0 0 0 1.5px white',
              }}
            />
          </Box>
          <Typography variant="h6" sx={{ 
              fontWeight: 800,
              color: 'text.primary',
              letterSpacing: '-0.01em',
              fontFamily: "'Inter', sans-serif",
              '& span': {
                color: 'secondary.main'
              }
            }}>
            Write<span>HERE</span>
          </Typography>
        </Box>
        <IconButton onClick={toggleDrawer} sx={{ color: 'text.secondary' }}>
          <CloseIcon />
        </IconButton>
      </Box>
      <Divider sx={{ mb: 2 }} />
      <List>
        {menuItems.map((item) => (
          <ListItem 
            button 
            key={item.text} 
            component={RouterLink} 
            to={item.path}
            onClick={toggleDrawer}
            sx={{
              borderRadius: 2,
              mb: 1,
              '&:hover': {
                backgroundColor: 'grey.50',
              },
            }}
          >
            <ListItemText 
              primary={item.text} 
              primaryTypographyProps={{ 
                fontWeight: 500,
                fontSize: '1rem'
              }} 
            />
          </ListItem>
        ))}
        <ListItem 
          button 
          onClick={handleLanguageMenuOpen}
          sx={{
            borderRadius: 2,
            mb: 1,
            '&:hover': {
              backgroundColor: 'grey.50',
            },
          }}
        >
          <ListItemText 
            primary={t('common.language')} 
            secondary={currentLanguage === 'english' ? 'English' : '中文'} 
            primaryTypographyProps={{ 
              fontWeight: 500,
              fontSize: '1rem'
            }} 
          />
          <LanguageIcon color="action" sx={{ ml: 1 }} />
        </ListItem>
      </List>
      <Menu
        anchorEl={languageMenu}
        open={Boolean(languageMenu)}
        onClose={handleLanguageMenuClose}
        PaperProps={{
          sx: { width: 180, maxWidth: '100%' }
        }}
      >
        <MenuItem 
          selected={currentLanguage === 'english'} 
          onClick={() => handleLanguageChange('english')}
        >
          English
        </MenuItem>
        <MenuItem 
          selected={currentLanguage === 'chinese'} 
          onClick={() => handleLanguageChange('chinese')}
        >
          中文
        </MenuItem>
      </Menu>
    </Box>
  );

  return (
    <AppBar 
      position="static" 
      elevation={0} 
      color="default" 
      sx={{ 
        borderBottom: 1, 
        borderColor: 'grey.100',
        backdropFilter: 'blur(10px)',
        backgroundColor: 'rgba(255, 255, 255, 0.8)'
      }}
    >
      <Container maxWidth="lg">
        <Toolbar sx={{ px: { xs: 0 } }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            flexGrow: 1 
          }}>
            <Box 
              sx={{ 
                display: 'flex',
                alignItems: 'center',
                mr: 1.5,
                position: 'relative'
              }}
            >
              <EditNoteIcon 
                sx={{ 
                  color: 'primary.main',
                  fontSize: 32,
                  filter: 'drop-shadow(0px 1px 2px rgba(0,0,0,0.2))'
                }} 
              />
              <Box 
                sx={{
                  position: 'absolute',
                  right: -3,
                  bottom: -3,
                  width: 12,
                  height: 12,
                  backgroundColor: 'secondary.main',
                  borderRadius: '50%',
                  boxShadow: '0 0 0 2px white',
                }}
              />
            </Box>
            <Typography 
              variant="h6" 
              component={RouterLink} 
              to="/" 
              sx={{ 
                fontWeight: 800,
                textDecoration: 'none',
                color: 'text.primary',
                letterSpacing: '-0.01em',
                fontFamily: "'Inter', sans-serif",
                '&:hover': {
                  color: 'primary.main',
                },
                '& span': {
                  color: 'secondary.main'
                }
              }}
            >
              Write<span>HERE</span>
            </Typography>
          </Box>
          
          {isMobile ? (
            <IconButton 
              edge="end" 
              aria-label="menu" 
              onClick={toggleDrawer}
              sx={{ 
                color: 'text.primary',
                '&:hover': {
                  backgroundColor: 'grey.50',
                },
              }}
            >
              <MenuIcon />
            </IconButton>
          ) : (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {menuItems.map((item) => (
                <Button 
                  key={item.text} 
                  component={RouterLink} 
                  to={item.path}
                  variant="text"
                  color="inherit"
                  sx={{ 
                    fontWeight: 500,
                    px: 2,
                    borderRadius: 2,
                    color: 'text.secondary',
                    '&:hover': {
                      backgroundColor: 'grey.50',
                      color: 'primary.main',
                    },
                  }}
                >
                  {item.text}
                </Button>
              ))}
              <IconButton 
                color="inherit"
                onClick={handleLanguageMenuOpen}
                sx={{ 
                  ml: 1,
                  color: 'text.secondary',
                  '&:hover': {
                    backgroundColor: 'grey.50',
                  },
                }}
              >
                <LanguageIcon />
              </IconButton>
            </Box>
          )}
          
          <Menu
            anchorEl={languageMenu}
            open={Boolean(languageMenu)}
            onClose={handleLanguageMenuClose}
            PaperProps={{
              sx: { width: 180, maxWidth: '100%' }
            }}
          >
            <MenuItem 
              selected={currentLanguage === 'english'} 
              onClick={() => handleLanguageChange('english')}
            >
              English
            </MenuItem>
            <MenuItem 
              selected={currentLanguage === 'chinese'} 
              onClick={() => handleLanguageChange('chinese')}
            >
              中文
            </MenuItem>
          </Menu>
          
          <Drawer
            anchor="right"
            open={drawerOpen}
            onClose={toggleDrawer}
            PaperProps={{
              sx: {
                borderTopLeftRadius: 12,
                borderBottomLeftRadius: 12,
              }
            }}
          >
            {drawer}
          </Drawer>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;