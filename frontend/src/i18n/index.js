import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

// Import locales
import enTranslation from './locales/en';
import zhTranslation from './locales/zh';

// Get user preferred language from localStorage or browser settings
const getInitialLanguage = () => {
  const storedLanguage = localStorage.getItem('preferredLanguage');
  if (storedLanguage) {
    return storedLanguage === 'chinese' ? 'zh' : 'en';
  }
  
  // Fallback to browser language settings
  const browserLang = navigator.language || navigator.userLanguage;
  return browserLang && browserLang.toLowerCase().includes('zh') ? 'zh' : 'en';
};

i18n
  .use(initReactI18next) // Initialize react-i18next
  .init({
    resources: {
      en: {
        translation: enTranslation
      },
      zh: {
        translation: zhTranslation
      }
    },
    lng: getInitialLanguage(),
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false // Not needed for React
    }
  });

// Function to change language
export const changeLanguage = (language) => {
  const langCode = language === 'chinese' ? 'zh' : 'en';
  i18n.changeLanguage(langCode);
  // Also update HTML lang attribute
  document.documentElement.setAttribute('lang', langCode);
};

// Function to get current language
export const getCurrentLanguage = () => {
  return i18n.language === 'zh' ? 'chinese' : 'english';
};

export default i18n; 