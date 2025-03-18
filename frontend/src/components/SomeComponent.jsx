import { useTranslation } from 'react-i18next';

function SomeComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('storyGeneration.title')}</h1>
      <p>{t('storyGeneration.description')}</p>
      {/* XXX */}
    </div>
  );
}

export default SomeComponent; 