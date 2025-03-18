import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import zh from './locales/zh';
// 其他语言导入...

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      zh: zh,
      // 其他语言...
    },
    fallbackLng: 'zh',
    interpolation: {
      escapeValue: false,
    }
  });

export default i18n; 