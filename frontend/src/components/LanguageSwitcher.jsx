import React from 'react';
import { useTranslation } from 'react-i18next';
import { Button, Menu, MenuItem } from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import LanguageIcon from '@mui/icons-material/Language';

function LanguageSwitcher() {
  const { t, i18n } = useTranslation();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const open = Boolean(anchorEl);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
    handleClose();
  };

  return (
    <>
      <Button
        id="language-button"
        aria-controls={open ? 'language-menu' : undefined}
        aria-haspopup="true"
        aria-expanded={open ? 'true' : undefined}
        onClick={handleClick}
        startIcon={<LanguageIcon />}
        endIcon={<KeyboardArrowDownIcon />}
        sx={{ 
          textTransform: 'none',
          color: 'text.secondary',
          '&:hover': {
            backgroundColor: 'grey.50',
            color: 'primary.main',
          },
          fontWeight: 500,
          px: 2,
          borderRadius: 2,
        }}
      >
        {i18n.language === 'zh' ? '中文' : 'English'}
      </Button>
      <Menu
        id="language-menu"
        anchorEl={anchorEl}
        open={open}
        onClose={handleClose}
        MenuListProps={{
          'aria-labelledby': 'language-button',
        }}
        PaperProps={{
          sx: {
            mt: 1,
            borderRadius: 2,
          }
        }}
      >
        <MenuItem 
          onClick={() => changeLanguage('en')} 
          selected={i18n.language === 'en'}
          sx={{
            minWidth: 120,
            fontWeight: i18n.language === 'en' ? 600 : 400,
          }}
        >
          English
        </MenuItem>
        <MenuItem 
          onClick={() => changeLanguage('zh')} 
          selected={i18n.language === 'zh'}
          sx={{
            minWidth: 120,
            fontWeight: i18n.language === 'zh' ? 600 : 400,
          }}
        >
          中文
        </MenuItem>
      </Menu>
    </>
  );
}

export default LanguageSwitcher; 