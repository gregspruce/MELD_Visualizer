/**
 * Visual Regression Testing Configuration
 * Comprehensive configuration for visual testing across browsers, themes, and viewports
 */

export interface VisualTestConfig {
  // Screenshot comparison settings
  threshold: number;
  maxDiffPixels: number;
  pixelRatio: number;
  
  // Animation and timing
  animations: 'disabled' | 'allow';
  caret: 'hide' | 'initial';
  mode: 'light' | 'dark' | 'forced-colors' | 'no-preference';
  
  // Viewport settings
  scale: 'css' | 'device';
  
  // Masking and clipping
  mask?: Array<{selector: string}>;
  clip?: {x: number, y: number, width: number, height: number};
}

export const DEFAULT_VISUAL_CONFIG: VisualTestConfig = {
  threshold: 0.2,
  maxDiffPixels: 100,
  pixelRatio: 1,
  animations: 'disabled',
  caret: 'hide',
  mode: 'light',
  scale: 'css'
};

export const STRICT_VISUAL_CONFIG: VisualTestConfig = {
  threshold: 0.1,
  maxDiffPixels: 50,
  pixelRatio: 1,
  animations: 'disabled',
  caret: 'hide',
  mode: 'light',
  scale: 'css'
};

export const RESPONSIVE_VIEWPORTS = {
  mobile: { width: 375, height: 667 },
  mobileLandscape: { width: 667, height: 375 },
  tablet: { width: 768, height: 1024 },
  tabletLandscape: { width: 1024, height: 768 },
  desktop: { width: 1280, height: 720 },
  desktopLarge: { width: 1920, height: 1080 },
  desktopXL: { width: 2560, height: 1440 }
} as const;

export const BROWSER_CONFIGS = {
  chromium: {
    name: 'chromium',
    use: {
      ...DEFAULT_VISUAL_CONFIG,
      channel: 'chrome'
    }
  },
  firefox: {
    name: 'firefox',
    use: {
      ...DEFAULT_VISUAL_CONFIG
    }
  },
  webkit: {
    name: 'webkit',
    use: {
      ...DEFAULT_VISUAL_CONFIG
    }
  }
} as const;

export const THEME_CONFIGS = {
  light: {
    colorScheme: 'light' as const,
    mode: 'light' as const,
    cssVariables: {
      '--bs-primary': '#007bff',
      '--bs-body-bg': '#ffffff',
      '--bs-body-color': '#212529'
    }
  },
  dark: {
    colorScheme: 'dark' as const,
    mode: 'dark' as const,
    cssVariables: {
      '--bs-primary': '#0d6efd',
      '--bs-body-bg': '#121212',
      '--bs-body-color': '#ffffff'
    }
  },
  bootstrap: {
    colorScheme: 'light' as const,
    mode: 'light' as const,
    theme: 'BOOTSTRAP'
  },
  cerulean: {
    colorScheme: 'light' as const,
    mode: 'light' as const,
    theme: 'CERULEAN'
  },
  cosmo: {
    colorScheme: 'light' as const,
    mode: 'light' as const,
    theme: 'COSMO'
  },
  cyborg: {
    colorScheme: 'dark' as const,
    mode: 'dark' as const,
    theme: 'CYBORG'
  },
  darkly: {
    colorScheme: 'dark' as const,
    mode: 'dark' as const,
    theme: 'DARKLY'
  }
} as const;

export const COMPONENT_SELECTORS = {
  // Main layout components
  header: '[data-testid="app-header"]',
  navigation: '[data-testid="navigation-tabs"]',
  mainContent: '[data-testid="main-content"]',
  footer: '[data-testid="app-footer"]',
  
  // File upload components
  fileUpload: '[data-testid="file-upload"]',
  fileUploadDropzone: '[data-testid="file-upload-dropzone"]',
  fileUploadProgress: '[data-testid="file-upload-progress"]',
  fileUploadError: '[data-testid="file-upload-error"]',
  fileUploadSuccess: '[data-testid="file-upload-success"]',
  
  // Tab components
  tabContent: '[data-testid="tab-content"]',
  tabOverview: '[data-testid="tab-overview"]',
  tabVisualization: '[data-testid="tab-visualization"]',
  tabDataTable: '[data-testid="tab-data-table"]',
  tabExport: '[data-testid="tab-export"]',
  
  // Plotly graphs
  plotlyGraph: '.js-plotly-plot',
  scatter3dPlot: '[data-testid="scatter-3d-plot"]',
  volumePlot: '[data-testid="volume-plot"]',
  
  // Data table components
  dataTable: '[data-testid="data-table"]',
  dataTablePagination: '[data-testid="data-table-pagination"]',
  dataTableSearch: '[data-testid="data-table-search"]',
  
  // Export components
  exportSection: '[data-testid="export-section"]',
  exportButtons: '[data-testid="export-buttons"]',
  exportProgress: '[data-testid="export-progress"]',
  
  // Theme switcher
  themeSwitcher: '[data-testid="theme-switcher"]',
  themeToggle: '[data-testid="theme-toggle"]',
  
  // Loading states
  loadingSpinner: '[data-testid="loading-spinner"]',
  loadingOverlay: '[data-testid="loading-overlay"]',
  
  // Error states
  errorMessage: '[data-testid="error-message"]',
  errorBoundary: '[data-testid="error-boundary"]'
} as const;

export const ANIMATION_DURATIONS = {
  themeTransition: 300,
  tabTransition: 200,
  hoverEffect: 150,
  loadingSpinner: 1000,
  plotlyAnimation: 500
} as const;

export const ACCESSIBILITY_CONFIG = {
  contrastRatio: {
    normal: 4.5,
    large: 3.0,
    enhanced: 7.0
  },
  focusIndicator: {
    minWidth: 2,
    color: '#005fcc',
    style: 'solid'
  },
  reducedMotion: {
    prefersReducedMotion: 'reduce'
  }
} as const;

export const PERFORMANCE_THRESHOLDS = {
  // Layout shift thresholds
  cumulativeLayoutShift: 0.1,
  
  // Paint timing thresholds (ms)
  firstContentfulPaint: 1500,
  largestContentfulPaint: 2500,
  
  // Interaction timing (ms)
  firstInputDelay: 100,
  
  // Resource loading (ms)
  cssLoadTime: 500,
  imageLoadTime: 1000
} as const;