import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';

// Components
import Header from './components/Header';
import Footer from './components/Footer';

// Pages
import HomePage from './pages/HomePage';
import StoryGenerationPage from './pages/StoryGenerationPage';
import ReportGenerationPage from './pages/ReportGenerationPage';
import ResultsPage from './pages/ResultsPage';
import AboutPage from './pages/AboutPage';

// Create a theme inspired by Anthropic/OpenAI/Perplexity
const theme = createTheme({
  palette: {
    primary: {
      main: '#5436DA', // Purple (similar to Anthropic/OpenAI)
      light: '#7B6EAE',
      dark: '#3E2A9F',
    },
    secondary: {
      main: '#10A37F', // Teal green (similar to OpenAI)
      light: '#34C4A9',
      dark: '#0A8C6B',
    },
    background: {
      default: '#FFFFFF',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#202123',
      secondary: '#6E6E80',
    },
    grey: {
      50: '#F7F7F8',
      100: '#ECECF1',
      200: '#D9D9E3',
      300: '#C5C5D2',
      400: '#ACACBE',
    },
  },
  typography: {
    fontFamily: '"Inter", "Söhne", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h1: {
      fontSize: '3.5rem',
      fontWeight: 700,
      letterSpacing: '-0.025em',
      lineHeight: 1.2,
    },
    h2: {
      fontSize: '2.25rem',
      fontWeight: 700,
      letterSpacing: '-0.025em',
      lineHeight: 1.3,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      letterSpacing: '-0.015em',
      lineHeight: 1.4,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
    button: {
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          padding: '10px 20px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: 'none',
          },
        },
        containedPrimary: {
          backgroundColor: '#5436DA',
          '&:hover': {
            backgroundColor: '#4A2EC2',
          },
        },
        containedSecondary: {
          backgroundColor: '#10A37F',
          '&:hover': {
            backgroundColor: '#0E9271',
          },
        },
        outlined: {
          borderWidth: '1px',
          '&:hover': {
            borderWidth: '1px',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.05), 0px 4px 8px rgba(0, 0, 0, 0.05)',
          transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0px 8px 16px rgba(0, 0, 0, 0.1)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: '0px 1px 2px rgba(0, 0, 0, 0.05)',
          backgroundColor: '#FFFFFF',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.05), 0px 4px 8px rgba(0, 0, 0, 0.05)',
        },
        elevation1: {
          boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.05), 0px 4px 8px rgba(0, 0, 0, 0.05)',
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: {
          backgroundColor: '#ECECF1',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Header />
        <main style={{ flexGrow: 1, padding: '20px' }}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/story-generation" element={<StoryGenerationPage />} />
            <Route path="/report-generation" element={<ReportGenerationPage />} />
            <Route path="/results/:id" element={<ResultsPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </ThemeProvider>
  );
}

export default App;