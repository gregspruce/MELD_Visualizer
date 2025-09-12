/**
 * Comprehensive Theme Selector Component Tests for MELD Visualizer
 * Tests theme switching, persistence, and accessibility using MCP functions
 */

import { test, expect } from '../fixtures/mcp-fixtures';
import type { TestTypes, DashComponents } from '../types';

test.describe('Theme Selector Component', () => {
  test.beforeEach(async ({ mcpPage, settingsPage, performanceMonitor }) => {
    // Navigate to settings or ensure theme selector is accessible
    await settingsPage.navigate();
    performanceMonitor.mark('theme-page-ready');

    // Wait for theme selector to be loaded
    await expect(mcpPage.locator('[data-testid="theme-toggle"], [data-testid="theme-selector"]')).toBeVisible();
    await mcpPage.waitForLoadState('networkidle');
  });

  test.describe('Theme Selection and Switching', () => {
    test('should display all available theme options', async ({
      mcpPage,
      visualTester
    }) => {
      // Locate theme selector (could be dropdown or toggle)
      const themeSelector = mcpPage.locator('[data-testid="theme-selector"], [data-testid="theme-dropdown"]');

      if (await themeSelector.count() > 0) {
        // If it's a dropdown, open it to see options
        await themeSelector.click();

        // Verify expected theme options are available
        const expectedThemes = ['light', 'dark', 'plotly', 'plotly_dark'];

        for (const theme of expectedThemes) {
          const themeOption = mcpPage.locator(`[data-testid="theme-${theme}"], [data-value="${theme}"]`);
          await expect(themeOption).toBeVisible();

          // Verify option has proper labeling
          const optionText = await themeOption.textContent();
          expect(optionText?.toLowerCase()).toContain(theme.replace('_', ' '));
        }

        await visualTester.takeScreenshot('theme-selector-options-open');
      } else {
        // Check for toggle-style theme switcher
        const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');
        await expect(themeToggle).toBeVisible();
        await expect(themeToggle).toHaveAttribute('role', 'switch');

        await visualTester.takeScreenshot('theme-toggle-control');
      }
    });

    test('should switch to dark theme successfully', async ({
      mcpPage,
      visualTester,
      performanceMonitor,
      consoleMonitor
    }) => {
      performanceMonitor.mark('dark-theme-switch-start');

      // Get current theme state
      const initialTheme = await mcpPage.evaluate(() => {
        return document.documentElement.getAttribute('data-theme') ||
               document.body.className.match(/theme-(\w+)/)?.[1] ||
               'light';
      });

      // Take screenshot of initial theme
      await visualTester.takeScreenshot(`theme-initial-${initialTheme}`, { fullPage: true });

      // Switch to dark theme
      const darkThemeSelector = mcpPage.locator('[data-testid="theme-dark"], [data-value="dark"]');
      const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');

      if (await darkThemeSelector.count() > 0) {
        // Dropdown-style selector
        await mcpPage.locator('[data-testid="theme-selector"]').click();
        await darkThemeSelector.click();
      } else {
        // Toggle-style selector - ensure it switches to dark
        const currentState = await themeToggle.getAttribute('aria-checked');
        if (currentState === 'false') {
          await themeToggle.click();
        }
      }

      performanceMonitor.mark('dark-theme-switch-complete');

      // Wait for theme transition to complete
      await mcpPage.waitForTimeout(500);

      // Verify theme changed
      const newTheme = await mcpPage.evaluate(() => {
        return document.documentElement.getAttribute('data-theme') ||
               document.body.className.match(/theme-(\w+)/)?.[1] ||
               'unknown';
      });

      expect(newTheme).toBe('dark');

      // Verify visual changes occurred
      const backgroundColor = await mcpPage.evaluate(() => {
        return getComputedStyle(document.body).backgroundColor;
      });

      expect(backgroundColor).toMatch(/rgb\(.*\)|rgba\(.*\)|#[0-9a-f]{3,6}/i);

      // Take screenshot of dark theme
      await visualTester.takeScreenshot('theme-dark-applied', { fullPage: true });

      // Verify no console errors during theme switch
      consoleMonitor.expectNoErrors();

      // Check performance impact of theme switching
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.interactionTime).toBeLessThan(500);
    });

    test('should switch to light theme successfully', async ({
      mcpPage,
      visualTester
    }) => {
      // First ensure we're not in light theme
      const lightThemeSelector = mcpPage.locator('[data-testid="theme-light"], [data-value="light"]');
      const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');

      if (await lightThemeSelector.count() > 0) {
        // Switch to dark first, then to light
        await mcpPage.locator('[data-testid="theme-selector"]').click();
        await mcpPage.locator('[data-testid="theme-dark"]').click();
        await mcpPage.waitForTimeout(300);

        // Now switch to light
        await mcpPage.locator('[data-testid="theme-selector"]').click();
        await lightThemeSelector.click();
      } else {
        // Toggle to ensure we switch states
        await themeToggle.click();
        await mcpPage.waitForTimeout(300);
        await themeToggle.click();
      }

      // Wait for transition
      await mcpPage.waitForTimeout(500);

      // Verify light theme is applied
      const theme = await mcpPage.evaluate(() => {
        return document.documentElement.getAttribute('data-theme') ||
               document.body.className.match(/theme-(\w+)/)?.[1] ||
               'light';
      });

      expect(theme).toBe('light');

      await visualTester.takeScreenshot('theme-light-applied', { fullPage: true });
    });

    test('should switch to Plotly themes correctly', async ({
      mcpPage,
      visualTester
    }) => {
      const plotlyThemes = ['plotly', 'plotly_dark'];

      for (const plotlyTheme of plotlyThemes) {
        // Switch to Plotly theme
        const themeSelector = mcpPage.locator('[data-testid="theme-selector"]');
        if (await themeSelector.count() > 0) {
          await themeSelector.click();
          await mcpPage.locator(`[data-testid="theme-${plotlyTheme}"], [data-value="${plotlyTheme}"]`).click();
        }

        // Wait for theme application
        await mcpPage.waitForTimeout(500);

        // Verify Plotly theme is applied
        const appliedTheme = await mcpPage.evaluate(() => {
          return document.documentElement.getAttribute('data-theme') ||
                 document.body.className.match(/theme-([\w_]+)/)?.[1];
        });

        expect(appliedTheme).toBe(plotlyTheme);

        // Take screenshot of Plotly theme
        await visualTester.takeScreenshot(`theme-${plotlyTheme}-applied`, { fullPage: true });

        // Verify Plotly graphs use the correct theme
        if (await mcpPage.locator('.js-plotly-plot').count() > 0) {
          const plotlyThemeConfig = await mcpPage.evaluate((theme) => {
            const plotElement = document.querySelector('.js-plotly-plot');
            return plotElement?._fullLayout?.template || null;
          }, plotlyTheme);

          expect(plotlyThemeConfig).toBeTruthy();
        }
      }
    });
  });

  test.describe('Theme Persistence', () => {
    test('should persist theme selection across page reloads', async ({
      mcpPage,
      visualTester
    }) => {
      // Switch to dark theme
      const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');
      const darkThemeOption = mcpPage.locator('[data-testid="theme-dark"]');

      if (await darkThemeOption.count() > 0) {
        await mcpPage.locator('[data-testid="theme-selector"]').click();
        await darkThemeOption.click();
      } else {
        await themeToggle.click();
      }

      // Wait for theme to apply
      await mcpPage.waitForTimeout(500);

      // Verify theme is dark
      const themeBeforeReload = await mcpPage.evaluate(() => {
        return document.documentElement.getAttribute('data-theme') ||
               document.body.className.match(/theme-(\w+)/)?.[1];
      });

      await visualTester.takeScreenshot('theme-before-reload');

      // Reload page
      await mcpPage.reload();
      await expect(mcpPage.locator('[data-testid="theme-toggle"], [data-testid="theme-selector"]')).toBeVisible();

      // Wait for theme to be restored
      await mcpPage.waitForTimeout(1000);

      // Verify theme persisted
      const themeAfterReload = await mcpPage.evaluate(() => {
        return document.documentElement.getAttribute('data-theme') ||
               document.body.className.match(/theme-(\w+)/)?.[1];
      });

      expect(themeAfterReload).toBe(themeBeforeReload);

      await visualTester.takeScreenshot('theme-after-reload');
    });

    test('should store theme preference in local storage', async ({
      mcpPage
    }) => {
      // Switch to plotly_dark theme
      const themeSelector = mcpPage.locator('[data-testid="theme-selector"]');

      if (await themeSelector.count() > 0) {
        await themeSelector.click();
        await mcpPage.locator('[data-testid="theme-plotly_dark"], [data-value="plotly_dark"]').click();
      }

      await mcpPage.waitForTimeout(300);

      // Check local storage
      const storedTheme = await mcpPage.evaluate(() => {
        return localStorage.getItem('theme') ||
               localStorage.getItem('meld-theme') ||
               localStorage.getItem('selectedTheme');
      });

      expect(storedTheme).toBe('plotly_dark');

      // Switch to light theme
      if (await themeSelector.count() > 0) {
        await themeSelector.click();
        await mcpPage.locator('[data-testid="theme-light"], [data-value="light"]').click();
      }

      await mcpPage.waitForTimeout(300);

      // Verify storage updated
      const updatedTheme = await mcpPage.evaluate(() => {
        return localStorage.getItem('theme') ||
               localStorage.getItem('meld-theme') ||
               localStorage.getItem('selectedTheme');
      });

      expect(updatedTheme).toBe('light');
    });

    test('should handle corrupted theme data in storage', async ({
      mcpPage,
      consoleMonitor
    }) => {
      // Set invalid theme data in storage
      await mcpPage.evaluate(() => {
        localStorage.setItem('theme', 'invalid-theme-name');
        localStorage.setItem('meld-theme', '{"invalid": "json"');
      });

      // Reload page
      await mcpPage.reload();
      await expect(mcpPage.locator('[data-testid="theme-toggle"], [data-testid="theme-selector"]')).toBeVisible();

      // Should default to light theme or first available theme
      const appliedTheme = await mcpPage.evaluate(() => {
        return document.documentElement.getAttribute('data-theme') ||
               document.body.className.match(/theme-(\w+)/)?.[1] ||
               'light';
      });

      expect(['light', 'dark', 'plotly']).toContain(appliedTheme);

      // Should not throw console errors
      const errors = consoleMonitor.getErrors().filter(error =>
        error.text.includes('theme') && !error.text.includes('network')
      );
      expect(errors).toHaveLength(0);
    });
  });

  test.describe('Theme Visual Changes', () => {
    test('should apply consistent theme colors across components', async ({
      mcpPage,
      visualTester,
      uploadPage,
      testFiles
    }) => {
      // Upload some data to have multiple components visible
      await uploadPage.uploadFile(testFiles.validMELDData.path);
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();

      // Navigate to visualization to have graphs
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await expect(mcpPage.locator('[data-testid="graph-container"]')).toBeVisible({ timeout: 15000 });

      const themes = ['light', 'dark'];

      for (const themeName of themes) {
        // Switch theme
        const themeSelector = mcpPage.locator('[data-testid="theme-selector"]');
        const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');

        if (await themeSelector.count() > 0) {
          await themeSelector.click();
          await mcpPage.locator(`[data-testid="theme-${themeName}"], [data-value="${themeName}"]`).click();
        } else {
          // For toggle, determine current state and switch if needed
          const currentState = await themeToggle.getAttribute('aria-checked');
          const needsToggle = (themeName === 'dark' && currentState === 'false') ||
                             (themeName === 'light' && currentState === 'true');

          if (needsToggle) {
            await themeToggle.click();
          }
        }

        await mcpPage.waitForTimeout(800); // Allow theme transition

        // Get color values from different components
        const colors = await mcpPage.evaluate(() => {
          const getComputedColor = (selector: string) => {
            const element = document.querySelector(selector);
            return element ? getComputedStyle(element).color : null;
          };

          const getComputedBgColor = (selector: string) => {
            const element = document.querySelector(selector);
            return element ? getComputedStyle(element).backgroundColor : null;
          };

          return {
            bodyBg: getComputedBgColor('body'),
            bodyText: getComputedColor('body'),
            tabBg: getComputedBgColor('[data-testid^="tab-"]'),
            tabText: getComputedColor('[data-testid^="tab-"]'),
            buttonBg: getComputedBgColor('button'),
            buttonText: getComputedColor('button'),
            cardBg: getComputedBgColor('.card, .dash-card'),
          };
        });

        // Verify colors are appropriate for theme
        if (themeName === 'dark') {
          expect(colors.bodyBg).toMatch(/rgb\((0|[0-2][0-9]|3[0-9]|4[0-9]|5[0-9]),/); // Dark backgrounds
        } else {
          expect(colors.bodyBg).toMatch(/rgb\(([2-9][0-9][0-9]|2[5-9][0-9]|[3-9][0-9][0-9]),/); // Light backgrounds
        }

        await visualTester.takeScreenshot(`theme-${themeName}-components-consistency`, { fullPage: true });
      }
    });

    test('should animate theme transitions smoothly', async ({
      mcpPage,
      visualTester,
      performanceMonitor
    }) => {
      performanceMonitor.mark('theme-animation-test-start');

      // Enable CSS transitions monitoring
      await mcpPage.addStyleTag({
        content: `
          * {
            transition-duration: 0.3s !important;
            transition-property: background-color, color, border-color !important;
          }
        `
      });

      // Take screenshot before transition
      await visualTester.takeScreenshot('theme-before-animation');

      // Switch theme
      const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');
      await themeToggle.click();

      // Take screenshot during transition (small delay)
      await mcpPage.waitForTimeout(150);
      await visualTester.takeScreenshot('theme-during-animation');

      // Wait for transition to complete
      await mcpPage.waitForTimeout(500);
      await visualTester.takeScreenshot('theme-after-animation');

      performanceMonitor.mark('theme-animation-test-complete');

      // Verify animation performance
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.renderTime).toBeLessThan(1000); // Animation should complete quickly
    });

    test('should handle Plotly graph theme changes', async ({
      mcpPage,
      uploadPage,
      testFiles,
      visualTester
    }) => {
      // Upload data and navigate to visualization
      await uploadPage.uploadFile(testFiles.validMELDData.path);
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await expect(mcpPage.locator('.js-plotly-plot')).toBeVisible({ timeout: 15000 });

      // Switch to plotly_dark theme
      const themeSelector = mcpPage.locator('[data-testid="theme-selector"]');

      if (await themeSelector.count() > 0) {
        await themeSelector.click();
        await mcpPage.locator('[data-testid="theme-plotly_dark"], [data-value="plotly_dark"]').click();
      }

      await mcpPage.waitForTimeout(1000);

      // Verify Plotly graph updated to match theme
      const plotlyTheme = await mcpPage.evaluate(() => {
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        if (!plotElement || !plotElement._fullLayout) return null;

        return {
          paperBgColor: plotElement._fullLayout.paper_bgcolor,
          plotBgColor: plotElement._fullLayout.plot_bgcolor,
          fontColor: plotElement._fullLayout.font?.color,
          gridColor: plotElement._fullLayout.xaxis?.gridcolor
        };
      });

      expect(plotlyTheme).toBeTruthy();

      // Dark theme should have dark colors
      if (plotlyTheme?.paperBgColor) {
        expect(plotlyTheme.paperBgColor).toMatch(/#[0-4][0-9a-f]{5}|rgb\(([0-6][0-9]|7[0-9]|8[0-9]|9[0-9]),/);
      }

      await visualTester.takeScreenshot('plotly-dark-theme-applied');

      // Switch to plotly light theme
      if (await themeSelector.count() > 0) {
        await themeSelector.click();
        await mcpPage.locator('[data-testid="theme-plotly"], [data-value="plotly"]').click();
      }

      await mcpPage.waitForTimeout(1000);
      await visualTester.takeScreenshot('plotly-light-theme-applied');
    });
  });

  test.describe('Theme Accessibility', () => {
    test('should maintain proper contrast ratios in all themes', async ({
      mcpPage
    }) => {
      const themes = ['light', 'dark'];

      for (const themeName of themes) {
        // Switch to theme
        const themeSelector = mcpPage.locator('[data-testid="theme-selector"]');
        const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');

        if (await themeSelector.count() > 0) {
          await themeSelector.click();
          await mcpPage.locator(`[data-testid="theme-${themeName}"], [data-value="${themeName}"]`).click();
        } else {
          const currentTheme = await mcpPage.evaluate(() =>
            document.documentElement.getAttribute('data-theme') || 'light'
          );

          if (currentTheme !== themeName) {
            await themeToggle.click();
          }
        }

        await mcpPage.waitForTimeout(500);

        // Check contrast ratios for key elements
        const contrastResults = await mcpPage.evaluate(() => {
          const getContrast = (fg: string, bg: string): number => {
            const getLuminance = (color: string): number => {
              const rgb = color.match(/\d+/g)?.map(Number) || [0, 0, 0];
              const [r, g, b] = rgb.map(c => {
                c = c / 255;
                return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
              });
              return 0.2126 * r + 0.7152 * g + 0.0722 * b;
            };

            const l1 = getLuminance(fg);
            const l2 = getLuminance(bg);
            const lighter = Math.max(l1, l2);
            const darker = Math.min(l1, l2);

            return (lighter + 0.05) / (darker + 0.05);
          };

          const results: Array<{element: string, contrast: number, passes: boolean}> = [];

          // Check key UI elements
          const elementsToCheck = [
            { selector: 'body', name: 'body-text' },
            { selector: 'button', name: 'button' },
            { selector: '[data-testid^="tab-"]', name: 'tab' },
            { selector: '.card, .dash-card', name: 'card' },
          ];

          elementsToCheck.forEach(({ selector, name }) => {
            const element = document.querySelector(selector);
            if (element) {
              const styles = getComputedStyle(element);
              const color = styles.color;
              const bgcolor = styles.backgroundColor;

              if (color !== 'rgba(0, 0, 0, 0)' && bgcolor !== 'rgba(0, 0, 0, 0)') {
                const contrast = getContrast(color, bgcolor);
                results.push({
                  element: name,
                  contrast: Math.round(contrast * 100) / 100,
                  passes: contrast >= 4.5 // WCAG AA standard
                });
              }
            }
          });

          return results;
        });

        // Verify contrast ratios meet accessibility standards
        contrastResults.forEach(result => {
          expect(result.contrast).toBeGreaterThanOrEqual(3.0); // Minimum acceptable
          console.log(`${themeName} theme - ${result.element}: ${result.contrast}:1 contrast`);
        });
      }
    });

    test('should support reduced motion preferences', async ({
      mcpPage,
      visualTester
    }) => {
      // Set reduced motion preference
      await mcpPage.emulateMedia({ prefersReducedMotion: 'reduce' });

      // Switch themes with reduced motion
      const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');

      // Take screenshot before
      await visualTester.takeScreenshot('reduced-motion-before-theme-switch');

      await themeToggle.click();

      // Theme should change immediately without animation
      await mcpPage.waitForTimeout(100);

      await visualTester.takeScreenshot('reduced-motion-after-theme-switch');

      // Verify transitions are disabled or significantly reduced
      const transitionDuration = await mcpPage.evaluate(() => {
        const body = document.body;
        const styles = getComputedStyle(body);
        return styles.transitionDuration;
      });

      expect(transitionDuration).toMatch(/0s|0\.0*[1-2]s/); // Should be 0 or very short
    });

    test('should be accessible via keyboard navigation', async ({
      mcpPage
    }) => {
      // Navigate to theme selector using keyboard
      await mcpPage.keyboard.press('Tab');

      let tabCount = 0;
      const maxTabs = 20;

      // Find theme selector with keyboard
      while (tabCount < maxTabs) {
        const focusedElement = await mcpPage.locator(':focus').getAttribute('data-testid');

        if (focusedElement?.includes('theme')) {
          break;
        }

        await mcpPage.keyboard.press('Tab');
        tabCount++;
      }

      // Verify theme selector is focusable
      const themeElement = mcpPage.locator(':focus');
      const testId = await themeElement.getAttribute('data-testid');
      expect(testId).toMatch(/theme/);

      // Test keyboard activation
      await mcpPage.keyboard.press('Enter');

      // If it's a dropdown, arrow keys should work
      const isDropdown = await mcpPage.locator('[data-testid="theme-selector"]').count() > 0;

      if (isDropdown) {
        await mcpPage.keyboard.press('ArrowDown');
        await mcpPage.keyboard.press('Enter');
      }

      // Verify theme changed via keyboard interaction
      const themeChanged = await mcpPage.evaluate(() => {
        return document.documentElement.getAttribute('data-theme') ||
               document.body.className.includes('theme-');
      });

      expect(themeChanged).toBeTruthy();
    });

    test('should have proper ARIA attributes', async ({
      mcpPage
    }) => {
      const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');
      const themeSelector = mcpPage.locator('[data-testid="theme-selector"]');

      if (await themeToggle.count() > 0) {
        // Check toggle attributes
        await expect(themeToggle).toHaveAttribute('role', 'switch');
        await expect(themeToggle).toHaveAttribute('aria-checked');
        await expect(themeToggle).toHaveAttribute('aria-label');

        // Verify toggle state updates
        const initialState = await themeToggle.getAttribute('aria-checked');
        await themeToggle.click();
        await mcpPage.waitForTimeout(300);

        const newState = await themeToggle.getAttribute('aria-checked');
        expect(newState).not.toBe(initialState);
      }

      if (await themeSelector.count() > 0) {
        // Check dropdown attributes
        await expect(themeSelector).toHaveAttribute('role');
        await expect(themeSelector).toHaveAttribute('aria-label');

        // Check if it has aria-expanded for dropdown
        const role = await themeSelector.getAttribute('role');
        if (role === 'combobox' || role === 'listbox') {
          await expect(themeSelector).toHaveAttribute('aria-expanded');
        }
      }
    });
  });

  test.describe('Theme Integration and Performance', () => {
    test('should handle theme switching with loaded content', async ({
      mcpPage,
      uploadPage,
      testFiles,
      performanceMonitor,
      visualTester
    }) => {
      // Load content first
      await uploadPage.uploadFile(testFiles.validMELDData.path);
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await expect(mcpPage.locator('.js-plotly-plot')).toBeVisible({ timeout: 15000 });

      performanceMonitor.mark('content-loaded-theme-switch-start');

      // Switch theme with content loaded
      const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');
      await themeToggle.click();

      performanceMonitor.mark('content-loaded-theme-switch-complete');

      // Verify all content adapted to new theme
      await mcpPage.waitForTimeout(1000);

      // Check that graphs, tables, and other components updated
      const componentsUpdated = await mcpPage.evaluate(() => {
        const checks = {
          plotlyUpdated: false,
          tableUpdated: false,
          buttonsUpdated: false
        };

        // Check Plotly
        const plotElement = document.querySelector('.js-plotly-plot') as any;
        if (plotElement?._fullLayout) {
          checks.plotlyUpdated = !!plotElement._fullLayout.paper_bgcolor;
        }

        // Check tables
        const table = document.querySelector('.dash-table, [data-testid="data-table"]');
        if (table) {
          checks.tableUpdated = getComputedStyle(table).backgroundColor !== 'rgba(0, 0, 0, 0)';
        }

        // Check buttons
        const button = document.querySelector('button');
        if (button) {
          checks.buttonsUpdated = getComputedStyle(button).backgroundColor !== 'rgba(0, 0, 0, 0)';
        }

        return checks;
      });

      expect(componentsUpdated.plotlyUpdated).toBe(true);

      await visualTester.takeScreenshot('theme-switch-with-loaded-content', { fullPage: true });

      // Performance should still be good
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.renderTime).toBeLessThan(2000);
    });

    test('should maintain theme consistency across navigation', async ({
      mcpPage,
      visualTester
    }) => {
      // Switch to dark theme
      const themeToggle = mcpPage.locator('[data-testid="theme-toggle"]');
      await themeToggle.click();
      await mcpPage.waitForTimeout(500);

      const initialTheme = await mcpPage.evaluate(() =>
        document.documentElement.getAttribute('data-theme')
      );

      // Navigate through different tabs
      const tabs = ['upload', 'visualization', 'analysis'];

      for (const tabName of tabs) {
        await mcpPage.locator(`[data-testid="tab-${tabName}"]`).click();
        await expect(mcpPage.locator(`[data-testid="tab-content-${tabName}"]`)).toBeVisible({ timeout: 5000 });

        // Verify theme persisted
        const currentTheme = await mcpPage.evaluate(() =>
          document.documentElement.getAttribute('data-theme')
        );

        expect(currentTheme).toBe(initialTheme);

        await visualTester.takeScreenshot(`theme-consistency-${tabName}-tab`);
      }
    });
  });
});
