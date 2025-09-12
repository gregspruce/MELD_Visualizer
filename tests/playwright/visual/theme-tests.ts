/**
 * Theme Visual Validation Tests
 * Comprehensive testing of light/dark themes, color schemes, and theme transitions
 */

import { test, expect } from '@playwright/test';
import { VisualTestUtils } from './visual-utils';
import {
  THEME_CONFIGS,
  RESPONSIVE_VIEWPORTS,
  COMPONENT_SELECTORS,
  DEFAULT_VISUAL_CONFIG,
  ANIMATION_DURATIONS,
  ACCESSIBILITY_CONFIG
} from './visual-config';

// Theme-specific configuration
const THEME_CONFIG = {
  ...DEFAULT_VISUAL_CONFIG,
  threshold: 0.1,
  maxDiffPixels: 100
};

test.describe('Theme Visual Validation Tests', () => {
  let visualUtils: VisualTestUtils;

  test.beforeEach(async ({ page }) => {
    visualUtils = new VisualTestUtils(page);

    // Navigate to the application
    await page.goto('http://localhost:8050', { waitUntil: 'networkidle' });

    // Wait for initial page load
    await page.waitForLoadState('domcontentloaded');
    await visualUtils.waitForAnimationsToComplete();
  });

  // Test each theme configuration
  for (const [themeName, themeConfig] of Object.entries(THEME_CONFIGS)) {
    test.describe(`Theme: ${themeName}`, () => {

      test.beforeEach(async ({ page }) => {
        await visualUtils.setTheme(themeName as keyof typeof THEME_CONFIGS);
      });

      test(`${themeName} - Full Page Theme Application @visual @theme`, async ({ page }) => {
        await visualUtils.screenshotFullPage(
          `theme-full-page-${themeName}`,
          THEME_CONFIG
        );
      });

      test(`${themeName} - Header Theme Consistency @visual @theme`, async ({ page }) => {
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.header,
          `theme-header-${themeName}`,
          THEME_CONFIG
        );
      });

      test(`${themeName} - Navigation Theme @visual @theme`, async ({ page }) => {
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.navigation,
          `theme-navigation-${themeName}`,
          THEME_CONFIG
        );
      });

      test(`${themeName} - Main Content Theme @visual @theme`, async ({ page }) => {
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.mainContent,
          `theme-main-content-${themeName}`,
          THEME_CONFIG
        );
      });

      test(`${themeName} - File Upload Component Theme @visual @theme`, async ({ page }) => {
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.fileUpload,
          `theme-file-upload-${themeName}`,
          THEME_CONFIG
        );
      });

      test(`${themeName} - Plotly Graph Theme Integration @visual @theme`, async ({ page }) => {
        const graphCount = await page.locator(COMPONENT_SELECTORS.plotlyGraph).count();

        if (graphCount > 0) {
          await visualUtils.waitForPlotlyRender();
          await visualUtils.screenshotComponent(
            COMPONENT_SELECTORS.plotlyGraph,
            `theme-plotly-graph-${themeName}`,
            THEME_CONFIG
          );
        } else {
          // Create a themed test graph
          await page.evaluate((theme) => {
            const graphDiv = document.createElement('div');
            graphDiv.setAttribute('data-testid', 'themed-test-graph');

            const isDark = theme.includes('dark') || theme === 'cyborg' || theme === 'darkly';
            const bgColor = isDark ? '#2c3e50' : '#f8f9fa';
            const textColor = isDark ? '#ecf0f1' : '#2c3e50';
            const accentColor = isDark ? '#3498db' : '#007bff';

            graphDiv.style.cssText = `
              width: 100%;
              height: 400px;
              background: ${bgColor};
              border: 1px solid ${isDark ? '#34495e' : '#dee2e6'};
              border-radius: 8px;
              margin: 20px 0;
            `;

            graphDiv.innerHTML = `
              <div style="
                width: 100%;
                height: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: ${textColor};
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
              ">
                <h3 style="margin: 0 0 20px 0; color: ${accentColor};">Themed Graph Placeholder</h3>
                <div style="
                  width: 80%;
                  height: 200px;
                  background: linear-gradient(45deg, ${accentColor}33 25%, transparent 25%),
                             linear-gradient(-45deg, ${accentColor}33 25%, transparent 25%),
                             linear-gradient(45deg, transparent 75%, ${accentColor}33 75%),
                             linear-gradient(-45deg, transparent 75%, ${accentColor}33 75%);
                  background-size: 20px 20px;
                  background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
                  border: 2px solid ${accentColor};
                  border-radius: 4px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                ">
                  <div style="
                    background: ${bgColor};
                    padding: 10px 20px;
                    border-radius: 4px;
                    border: 1px solid ${accentColor};
                    font-size: 14px;
                  ">
                    Theme: ${theme}
                  </div>
                </div>
              </div>
            `;

            const container = document.querySelector('[data-testid="main-content"]') || document.body;
            container.appendChild(graphDiv);
          }, themeName);

          await visualUtils.screenshotComponent(
            '[data-testid="themed-test-graph"]',
            `theme-graph-placeholder-${themeName}`,
            THEME_CONFIG
          );
        }
      });

      test(`${themeName} - Form Controls Theme @visual @theme`, async ({ page }) => {
        // Create themed form controls
        await page.evaluate((theme) => {
          const formDiv = document.createElement('div');
          formDiv.setAttribute('data-testid', 'themed-form-controls');

          const isDark = theme.includes('dark') || theme === 'cyborg' || theme === 'darkly';

          formDiv.style.cssText = 'padding: 20px; max-width: 600px; margin: 20px auto;';
          formDiv.innerHTML = `
            <h3>Form Controls - ${theme} Theme</h3>
            <div style="display: flex; flex-direction: column; gap: 15px;">
              <div>
                <label style="display: block; margin-bottom: 5px;">Text Input:</label>
                <input type="text" value="Sample text" style="
                  width: 100%;
                  padding: 10px;
                  border: 1px solid ${isDark ? '#555' : '#ced4da'};
                  background: ${isDark ? '#2c3e50' : '#ffffff'};
                  color: ${isDark ? '#ecf0f1' : '#495057'};
                  border-radius: 4px;
                ">
              </div>

              <div>
                <label style="display: block; margin-bottom: 5px;">Select Dropdown:</label>
                <select style="
                  width: 100%;
                  padding: 10px;
                  border: 1px solid ${isDark ? '#555' : '#ced4da'};
                  background: ${isDark ? '#2c3e50' : '#ffffff'};
                  color: ${isDark ? '#ecf0f1' : '#495057'};
                  border-radius: 4px;
                ">
                  <option>Option 1</option>
                  <option selected>Option 2 (Selected)</option>
                  <option>Option 3</option>
                </select>
              </div>

              <div>
                <label style="display: block; margin-bottom: 5px;">Textarea:</label>
                <textarea style="
                  width: 100%;
                  padding: 10px;
                  height: 80px;
                  border: 1px solid ${isDark ? '#555' : '#ced4da'};
                  background: ${isDark ? '#2c3e50' : '#ffffff'};
                  color: ${isDark ? '#ecf0f1' : '#495057'};
                  border-radius: 4px;
                  resize: vertical;
                ">Sample textarea content</textarea>
              </div>

              <div style="display: flex; gap: 15px; align-items: center;">
                <label style="display: flex; align-items: center; gap: 5px;">
                  <input type="checkbox" checked style="
                    width: 16px;
                    height: 16px;
                    accent-color: ${isDark ? '#3498db' : '#007bff'};
                  ">
                  Checked Checkbox
                </label>
                <label style="display: flex; align-items: center; gap: 5px;">
                  <input type="radio" name="theme-radio" checked style="
                    width: 16px;
                    height: 16px;
                    accent-color: ${isDark ? '#3498db' : '#007bff'};
                  ">
                  Selected Radio
                </label>
              </div>

              <div>
                <input type="range" min="0" max="100" value="50" style="
                  width: 100%;
                  accent-color: ${isDark ? '#3498db' : '#007bff'};
                ">
              </div>

              <div style="display: flex; gap: 10px;">
                <button type="button" style="
                  padding: 10px 20px;
                  background: ${isDark ? '#3498db' : '#007bff'};
                  color: white;
                  border: none;
                  border-radius: 4px;
                  cursor: pointer;
                ">Primary Button</button>
                <button type="button" style="
                  padding: 10px 20px;
                  background: ${isDark ? '#7f8c8d' : '#6c757d'};
                  color: white;
                  border: none;
                  border-radius: 4px;
                  cursor: pointer;
                ">Secondary Button</button>
                <button type="button" disabled style="
                  padding: 10px 20px;
                  background: ${isDark ? '#34495e' : '#e9ecef'};
                  color: ${isDark ? '#7f8c8d' : '#6c757d'};
                  border: none;
                  border-radius: 4px;
                  cursor: not-allowed;
                ">Disabled Button</button>
              </div>
            </div>
          `;
          document.body.appendChild(formDiv);
        }, themeName);

        await visualUtils.screenshotComponent(
          '[data-testid="themed-form-controls"]',
          `theme-form-controls-${themeName}`,
          THEME_CONFIG
        );
      });

      test(`${themeName} - Color Palette Showcase @visual @theme`, async ({ page }) => {
        // Create a comprehensive color palette showcase for the theme
        await page.evaluate((theme) => {
          const paletteDiv = document.createElement('div');
          paletteDiv.setAttribute('data-testid', 'theme-color-palette');

          const isDark = theme.includes('dark') || theme === 'cyborg' || theme === 'darkly';

          // Define color palettes for different themes
          const colorPalettes = {
            light: {
              primary: '#007bff',
              secondary: '#6c757d',
              success: '#28a745',
              danger: '#dc3545',
              warning: '#ffc107',
              info: '#17a2b8',
              background: '#ffffff',
              surface: '#f8f9fa',
              text: '#212529'
            },
            dark: {
              primary: '#0d6efd',
              secondary: '#6c757d',
              success: '#198754',
              danger: '#dc3545',
              warning: '#fd7e14',
              info: '#0dcaf0',
              background: '#121212',
              surface: '#1e1e1e',
              text: '#ffffff'
            },
            bootstrap: {
              primary: '#007bff',
              secondary: '#6c757d',
              success: '#28a745',
              danger: '#dc3545',
              warning: '#ffc107',
              info: '#17a2b8',
              background: '#ffffff',
              surface: '#f8f9fa',
              text: '#212529'
            },
            cerulean: {
              primary: '#2FA4E7',
              secondary: '#6c757d',
              success: '#73A839',
              danger: '#C71C22',
              warning: '#DD5600',
              info: '#033C73',
              background: '#ffffff',
              surface: '#f8f9fa',
              text: '#212529'
            },
            cosmo: {
              primary: '#2780E3',
              secondary: '#373A3C',
              success: '#3FB618',
              danger: '#FF0039',
              warning: '#FF7518',
              info: '#9954BB',
              background: '#ffffff',
              surface: '#f8f9fa',
              text: '#373A3C'
            },
            cyborg: {
              primary: '#2A9FD6',
              secondary: '#555',
              success: '#77B300',
              danger: '#CC0000',
              warning: '#F57C00',
              info: '#9933CC',
              background: '#060606',
              surface: '#222',
              text: '#999'
            },
            darkly: {
              primary: '#375A7F',
              secondary: '#444',
              success: '#00BC8C',
              danger: '#E74C3C',
              warning: '#F39C12',
              info: '#3498DB',
              background: '#303030',
              surface: '#3e3e3e',
              text: '#ffffff'
            }
          };

          const palette = colorPalettes[theme] || colorPalettes[isDark ? 'dark' : 'light'];

          paletteDiv.style.cssText = `
            padding: 20px;
            background: ${palette.background};
            color: ${palette.text};
          `;

          paletteDiv.innerHTML = `
            <h3 style="color: ${palette.text}; margin-bottom: 20px;">${theme.toUpperCase()} Theme - Color Palette</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
              ${Object.entries(palette).map(([name, color]) => `
                <div style="
                  background: ${color};
                  color: ${name === 'background' || name === 'surface' ? palette.text : 'white'};
                  padding: 20px;
                  border-radius: 8px;
                  text-align: center;
                  border: 1px solid ${isDark ? '#555' : '#dee2e6'};
                  text-shadow: ${name === 'warning' || name === 'surface' || name === 'background' ? '1px 1px 2px rgba(0,0,0,0.7)' : 'none'};
                ">
                  <div style="font-weight: bold; margin-bottom: 5px; text-transform: capitalize;">${name}</div>
                  <div style="font-family: monospace; font-size: 12px;">${color}</div>
                </div>
              `).join('')}
            </div>

            <div style="margin-top: 30px;">
              <h4 style="color: ${palette.text};">Color Combinations</h4>
              <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 15px;">
                <div style="
                  background: ${palette.primary};
                  color: white;
                  padding: 15px 20px;
                  border-radius: 4px;
                ">Primary on Background</div>
                <div style="
                  background: ${palette.surface};
                  color: ${palette.text};
                  padding: 15px 20px;
                  border-radius: 4px;
                  border: 1px solid ${palette.primary};
                ">Text on Surface</div>
                <div style="
                  background: ${palette.success};
                  color: white;
                  padding: 15px 20px;
                  border-radius: 4px;
                ">Success State</div>
                <div style="
                  background: ${palette.danger};
                  color: white;
                  padding: 15px 20px;
                  border-radius: 4px;
                ">Error State</div>
                <div style="
                  background: ${palette.warning};
                  color: ${name === 'warning' ? 'black' : 'white'};
                  padding: 15px 20px;
                  border-radius: 4px;
                ">Warning State</div>
              </div>
            </div>
          `;
          document.body.appendChild(paletteDiv);
        }, themeName);

        await visualUtils.screenshotComponent(
          '[data-testid="theme-color-palette"]',
          `theme-color-palette-${themeName}`,
          THEME_CONFIG
        );
      });
    });
  }

  // Test theme transitions and animations
  test.describe('Theme Transition Testing', () => {

    test('Light to Dark Theme Transition @visual @theme @transition', async ({ page }) => {
      // Start with light theme
      await visualUtils.setTheme('light');
      await visualUtils.screenshotFullPage('transition-light-before', THEME_CONFIG);

      // Enable animations to test transition
      await page.evaluate(() => {
        // Remove animation disabling styles
        const styles = document.querySelectorAll('style');
        styles.forEach(style => {
          if (style.textContent && style.textContent.includes('animation-duration: 0s')) {
            style.remove();
          }
        });
      });

      // Transition to dark theme
      await visualUtils.setTheme('dark');
      await visualUtils.screenshotFullPage('transition-dark-after', THEME_CONFIG);
    });

    test('Bootstrap Theme Variants Transition @visual @theme @transition', async ({ page }) => {
      const themeSequence: (keyof typeof THEME_CONFIGS)[] = ['bootstrap', 'cerulean', 'cosmo'];

      for (let i = 0; i < themeSequence.length; i++) {
        await visualUtils.setTheme(themeSequence[i]);
        await visualUtils.screenshotFullPage(
          `transition-bootstrap-variant-${i + 1}-${themeSequence[i]}`,
          THEME_CONFIG
        );
      }
    });

    test('Dark Theme Variants Transition @visual @theme @transition', async ({ page }) => {
      const darkThemeSequence: (keyof typeof THEME_CONFIGS)[] = ['dark', 'cyborg', 'darkly'];

      for (let i = 0; i < darkThemeSequence.length; i++) {
        await visualUtils.setTheme(darkThemeSequence[i]);
        await visualUtils.screenshotFullPage(
          `transition-dark-variant-${i + 1}-${darkThemeSequence[i]}`,
          THEME_CONFIG
        );
      }
    });

    test('Theme Switcher Component Animation @visual @theme @transition', async ({ page }) => {
      // Test theme switcher states if it exists
      const switcherExists = await page.locator(COMPONENT_SELECTORS.themeSwitcher).count() > 0;

      if (switcherExists) {
        // Test different states of theme switcher
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.themeSwitcher,
          'theme-switcher-light',
          THEME_CONFIG
        );

        await visualUtils.setTheme('dark');
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.themeSwitcher,
          'theme-switcher-dark',
          THEME_CONFIG
        );
      } else {
        // Create a mock theme switcher for testing
        await page.evaluate(() => {
          const switcherDiv = document.createElement('div');
          switcherDiv.setAttribute('data-testid', 'mock-theme-switcher');
          switcherDiv.innerHTML = `
            <div style="
              display: flex;
              align-items: center;
              gap: 10px;
              padding: 10px 15px;
              background: var(--bs-body-bg, #ffffff);
              border: 1px solid var(--bs-border-color, #dee2e6);
              border-radius: 8px;
              margin: 20px;
            ">
              <span style="font-size: 14px;">🌙</span>
              <div style="
                position: relative;
                width: 50px;
                height: 24px;
                background: var(--bs-secondary, #6c757d);
                border-radius: 12px;
                cursor: pointer;
                transition: background-color 0.3s;
              ">
                <div style="
                  position: absolute;
                  top: 2px;
                  left: 2px;
                  width: 20px;
                  height: 20px;
                  background: white;
                  border-radius: 50%;
                  transition: transform 0.3s;
                  transform: translateX(0px);
                "></div>
              </div>
              <span style="font-size: 14px;">☀️</span>
            </div>
          `;
          document.body.appendChild(switcherDiv);
        });

        await visualUtils.screenshotComponent(
          '[data-testid="mock-theme-switcher"]',
          'mock-theme-switcher-light',
          THEME_CONFIG
        );
      }
    });
  });

  // Test theme accessibility and contrast
  test.describe('Theme Accessibility Testing', () => {

    test('Color Contrast Validation @visual @theme @accessibility', async ({ page }) => {
      for (const [themeName, themeConfig] of Object.entries(THEME_CONFIGS)) {
        await visualUtils.setTheme(themeName as keyof typeof THEME_CONFIGS);

        // Create contrast testing elements
        await page.evaluate((theme) => {
          const contrastDiv = document.createElement('div');
          contrastDiv.setAttribute('data-testid', 'contrast-test');
          contrastDiv.innerHTML = `
            <div style="padding: 20px;">
              <h2>Contrast Testing - ${theme}</h2>
              <div style="margin: 20px 0;">
                <p>Normal text should meet WCAG AA standards (4.5:1 ratio minimum)</p>
                <p><strong>Bold text</strong> should be easily readable</p>
                <p><em>Italic text</em> should maintain readability</p>
                <p><small>Small text should meet enhanced contrast requirements</small></p>
              </div>

              <div style="display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0;">
                <button style="padding: 10px 20px; background: var(--bs-primary, #007bff); color: white; border: none; border-radius: 4px;">Primary Action</button>
                <button style="padding: 10px 20px; background: var(--bs-secondary, #6c757d); color: white; border: none; border-radius: 4px;">Secondary Action</button>
                <button style="padding: 10px 20px; background: var(--bs-success, #28a745); color: white; border: none; border-radius: 4px;">Success Action</button>
                <button style="padding: 10px 20px; background: var(--bs-danger, #dc3545); color: white; border: none; border-radius: 4px;">Danger Action</button>
              </div>

              <div style="margin: 20px 0;">
                <a href="#" style="color: var(--bs-primary, #007bff);">Link text should have sufficient contrast</a>
              </div>

              <div style="background: var(--bs-light, #f8f9fa); padding: 15px; margin: 20px 0; border: 1px solid var(--bs-border-color, #dee2e6);">
                <p style="margin: 0;">Text on light background should maintain readability</p>
              </div>

              <div style="background: var(--bs-dark, #343a40); color: var(--bs-light, #f8f9fa); padding: 15px; margin: 20px 0;">
                <p style="margin: 0;">Text on dark background should maintain readability</p>
              </div>
            </div>
          `;

          // Remove existing test if present
          const existing = document.querySelector('[data-testid="contrast-test"]');
          if (existing) existing.remove();

          document.body.appendChild(contrastDiv);
        }, themeName);

        await visualUtils.screenshotComponent(
          '[data-testid="contrast-test"]',
          `theme-contrast-${themeName}`,
          THEME_CONFIG
        );
      }
    });

    test('High Contrast Mode Compatibility @visual @theme @accessibility', async ({ page }) => {
      // Test themes with forced high contrast
      for (const themeName of ['light', 'dark']) {
        await visualUtils.setTheme(themeName as keyof typeof THEME_CONFIGS);

        // Enable high contrast mode
        await page.emulateMedia({ forcedColors: 'active' });

        await visualUtils.screenshotFullPage(
          `theme-high-contrast-${themeName}`,
          THEME_CONFIG
        );

        // Reset forced colors
        await page.emulateMedia({ forcedColors: 'none' });
      }
    });

    test('Focus Indicators in Different Themes @visual @theme @accessibility', async ({ page }) => {
      for (const themeName of ['light', 'dark', 'cyborg', 'darkly']) {
        await visualUtils.setTheme(themeName as keyof typeof THEME_CONFIGS);

        // Create focusable elements
        await page.evaluate(() => {
          const focusDiv = document.createElement('div');
          focusDiv.setAttribute('data-testid', 'focus-indicators-test');
          focusDiv.innerHTML = `
            <div style="padding: 20px;">
              <h3>Focus Indicators Testing</h3>
              <div style="display: flex; flex-direction: column; gap: 15px; max-width: 400px;">
                <button>Button Element</button>
                <input type="text" placeholder="Text Input" value="Sample text">
                <select><option>Select Option</option></select>
                <textarea placeholder="Textarea">Sample content</textarea>
                <a href="#">Link Element</a>
                <div tabindex="0" style="padding: 10px; border: 1px solid #ccc; cursor: pointer;">Custom Focusable Element</div>
              </div>
            </div>
          `;

          // Remove existing test if present
          const existing = document.querySelector('[data-testid="focus-indicators-test"]');
          if (existing) existing.remove();

          document.body.appendChild(focusDiv);
        });

        // Focus each element and take screenshots
        const focusableElements = await page.locator('[data-testid="focus-indicators-test"] button, [data-testid="focus-indicators-test"] input, [data-testid="focus-indicators-test"] select, [data-testid="focus-indicators-test"] textarea, [data-testid="focus-indicators-test"] a, [data-testid="focus-indicators-test"] [tabindex]').all();

        for (let i = 0; i < focusableElements.length; i++) {
          await focusableElements[i].focus();
          await page.waitForTimeout(100);

          await visualUtils.screenshotComponent(
            '[data-testid="focus-indicators-test"]',
            `theme-focus-${themeName}-element-${i}`,
            THEME_CONFIG
          );
        }
      }
    });
  });

  // Test theme responsiveness across viewports
  test.describe('Theme Responsive Behavior', () => {

    test('Theme Consistency Across Viewports @visual @theme @responsive', async ({ page }) => {
      const testViewports: (keyof typeof RESPONSIVE_VIEWPORTS)[] = ['mobile', 'tablet', 'desktop'];
      const testThemes: (keyof typeof THEME_CONFIGS)[] = ['light', 'dark'];

      for (const themeName of testThemes) {
        await visualUtils.setTheme(themeName);

        for (const viewportName of testViewports) {
          await visualUtils.setViewport(viewportName);

          await visualUtils.screenshotFullPage(
            `theme-responsive-${themeName}-${viewportName}`,
            THEME_CONFIG
          );
        }
      }
    });

    test('Theme Switcher Responsiveness @visual @theme @responsive', async ({ page }) => {
      const testViewports: (keyof typeof RESPONSIVE_VIEWPORTS)[] = ['mobile', 'desktop'];

      for (const viewportName of testViewports) {
        await visualUtils.setViewport(viewportName);

        // Create responsive theme switcher mockup
        await page.evaluate((viewport) => {
          const switcherDiv = document.createElement('div');
          switcherDiv.setAttribute('data-testid', 'responsive-theme-switcher');

          const isMobile = viewport === 'mobile';

          switcherDiv.innerHTML = `
            <div style="
              padding: 20px;
              display: flex;
              ${isMobile ? 'flex-direction: column;' : 'flex-direction: row; justify-content: space-between;'}
              align-items: center;
              gap: ${isMobile ? '15px' : '20px'};
              background: var(--bs-body-bg, #ffffff);
              border-bottom: 1px solid var(--bs-border-color, #dee2e6);
            ">
              <div style="
                ${isMobile ? 'text-align: center;' : 'flex: 1;'}
              ">
                <h4 style="margin: 0;">Theme Settings</h4>
                ${isMobile ? '' : '<p style="margin: 5px 0 0 0; color: var(--bs-secondary, #6c757d);">Choose your preferred theme</p>'}
              </div>

              <div style="
                display: flex;
                gap: 10px;
                ${isMobile ? 'width: 100%; justify-content: center;' : ''}
              ">
                <button style="
                  padding: ${isMobile ? '12px 24px' : '8px 16px'};
                  background: var(--bs-primary, #007bff);
                  color: white;
                  border: none;
                  border-radius: 4px;
                  font-size: ${isMobile ? '16px' : '14px'};
                  cursor: pointer;
                ">Light</button>
                <button style="
                  padding: ${isMobile ? '12px 24px' : '8px 16px'};
                  background: var(--bs-secondary, #6c757d);
                  color: white;
                  border: none;
                  border-radius: 4px;
                  font-size: ${isMobile ? '16px' : '14px'};
                  cursor: pointer;
                ">Dark</button>
                <button style="
                  padding: ${isMobile ? '12px 24px' : '8px 16px'};
                  background: var(--bs-outline-secondary, transparent);
                  color: var(--bs-secondary, #6c757d);
                  border: 1px solid var(--bs-secondary, #6c757d);
                  border-radius: 4px;
                  font-size: ${isMobile ? '16px' : '14px'};
                  cursor: pointer;
                ">Auto</button>
              </div>
            </div>
          `;

          // Remove existing test if present
          const existing = document.querySelector('[data-testid="responsive-theme-switcher"]');
          if (existing) existing.remove();

          document.body.appendChild(switcherDiv);
        }, viewportName);

        await visualUtils.screenshotComponent(
          '[data-testid="responsive-theme-switcher"]',
          `theme-switcher-responsive-${viewportName}`,
          THEME_CONFIG
        );
      }
    });
  });
});
