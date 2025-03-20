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
  Tooltip
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import CreateIcon from '@mui/icons-material/Create';
import EditNoteIcon from '@mui/icons-material/EditNote';
import LanguageIcon from '@mui/icons-material/Language';
import { useTranslation } from 'react-i18next';
import i18n from '../utils/i18n';

const Header = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [anchorElLang, setAnchorElLang] = useState(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { t } = useTranslation();

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleLanguageMenuOpen = (event) => {
    setAnchorElLang(event.currentTarget);
  };

  const handleLanguageMenuClose = () => {
    setAnchorElLang(null);
  };

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('language', lng);
    handleLanguageMenuClose();
  };

  const menuItems = [
    { text: t('header.home'), path: '/' },
    { text: t('header.storyGeneration'), path: '/story-generation' },
    { text: t('header.reportGeneration'), path: '/report-generation' },
    { text: t('header.about'), path: '/about' }
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
      </List>
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
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Tooltip title={t('common.selectLanguage')}>
                <IconButton
                  color="inherit"
                  onClick={handleLanguageMenuOpen}
                  sx={{ mr: 1 }}
                >
                  <LanguageIcon />
                </IconButton>
              </Tooltip>
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
            </Box>
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
              <Tooltip title={t('common.selectLanguage')}>
                <IconButton
                  color="inherit"
                  onClick={handleLanguageMenuOpen}
                  sx={{ ml: 1 }}
                >
                  <LanguageIcon />
                </IconButton>
              </Tooltip>
            </Box>
          )}
          
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

          {/* Language Menu */}
          <Menu
            anchorEl={anchorElLang}
            open={Boolean(anchorElLang)}
            onClose={handleLanguageMenuClose}
            sx={{ mt: 1 }}
          >
            <MenuItem onClick={() => changeLanguage('en')}>
              <Typography variant="body2">{t('common.english')}</Typography>
            </MenuItem>
            <MenuItem onClick={() => changeLanguage('zh')}>
              <Typography variant="body2">{t('common.chinese')}</Typography>
            </MenuItem>
          </Menu>
        </Toolbar>
      </Container>
    </AppBar>
  );
};

export default Header;