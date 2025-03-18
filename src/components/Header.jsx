import React from 'react';
import { AppBar, Toolbar, Typography } from '@mui/material';
import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';

const Header = () => {
  const { t } = useTranslation();

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {t('common.home')}
        </Typography>
        
        {/* 添加语言切换器组件 */}
        <LanguageSwitcher />
      </Toolbar>
    </AppBar>
  );
};

export default Header; 