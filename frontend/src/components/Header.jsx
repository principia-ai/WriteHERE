import { useTranslation } from 'react-i18next';
import LanguageSwitcher from './LanguageSwitcher';

function Header() {
  const { t } = useTranslation();
  
  return (
    <AppBar position="static">
      <Toolbar>
        {/* ... existing code ... */}
        
        {/* xxx */}
        <Box sx={{ flexGrow: 0, display: 'flex', alignItems: 'center' }}>
          <LanguageSwitcher />
          {/* xxx */}
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header; 