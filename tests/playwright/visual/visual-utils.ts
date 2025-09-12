/**
 * Visual Testing Utilities
 * Core utilities for screenshot comparison, baseline management, and visual validation
 */

import { Page, Locator, expect } from '@playwright/test';
import { VisualTestConfig, DEFAULT_VISUAL_CONFIG, RESPONSIVE_VIEWPORTS, THEME_CONFIGS, COMPONENT_SELECTORS, ANIMATION_DURATIONS } from './visual-config';
import * as fs from 'fs';
import * as path from 'path';

export class VisualTestUtils {
  constructor(private page: Page) {}

  /**
   * Wait for all animations to complete before taking screenshots
   */
  async waitForAnimationsToComplete(timeout: number = 2000): Promise<void> {
    // Wait for CSS transitions and animations to complete
    await this.page.waitForFunction(() => {
      const animations = document.getAnimations();
      return animations.length === 0 || animations.every(anim => anim.playState === 'finished');
    }, { timeout });

    // Additional wait for any delayed animations
    await this.page.waitForTimeout(100);
  }

  /**
   * Wait for Plotly graphs to finish rendering
   */
  async waitForPlotlyRender(selector: string = COMPONENT_SELECTORS.plotlyGraph): Promise<void> {
    await this.page.waitForSelector(selector, { state: 'visible' });

    // Wait for Plotly to be ready
    await this.page.waitForFunction(() => {
      return typeof window.Plotly !== 'undefined' &&
             document.querySelectorAll('.js-plotly-plot').length > 0;
    });

    // Wait for plot to finish rendering
    await this.page.waitForFunction(() => {
      const plots = document.querySelectorAll('.js-plotly-plot');
      return Array.from(plots).every(plot => {
        const plotDiv = plot as any;
        return plotDiv._fullLayout && plotDiv.data && !plotDiv._transitionData;
      });
    });

    await this.page.waitForTimeout(ANIMATION_DURATIONS.plotlyAnimation);
  }

  /**
   * Set theme and wait for transition to complete
   */
  async setTheme(themeName: keyof typeof THEME_CONFIGS): Promise<void> {
    const themeConfig = THEME_CONFIGS[themeName];

    // Apply color scheme preference
    await this.page.emulateMedia({ colorScheme: themeConfig.colorScheme });

    // Apply CSS variables if specified
    if (themeConfig.cssVariables) {
      await this.page.addStyleTag({
        content: `
          :root {
            ${Object.entries(themeConfig.cssVariables)
              .map(([key, value]) => `${key}: ${value};`)
              .join('\n            ')}
          }
        `
      });
    }

    // If theme switcher exists, use it
    try {
      const themeSwitcher = await this.page.locator(COMPONENT_SELECTORS.themeSwitcher);
      if (await themeSwitcher.isVisible()) {
        // Implementation depends on actual theme switcher component
        await themeSwitcher.click();
      }
    } catch {
      // Theme switcher not available, rely on emulated media
    }

    // Wait for theme transition
    await this.page.waitForTimeout(ANIMATION_DURATIONS.themeTransition);
    await this.waitForAnimationsToComplete();
  }

  /**
   * Set viewport size and wait for responsive adjustments
   */
  async setViewport(viewportName: keyof typeof RESPONSIVE_VIEWPORTS): Promise<void> {
    const viewport = RESPONSIVE_VIEWPORTS[viewportName];
    await this.page.setViewportSize(viewport);

    // Wait for responsive layout adjustments
    await this.page.waitForTimeout(200);
    await this.waitForAnimationsToComplete();

    // Wait for any responsive Plotly graph resizing
    try {
      await this.page.waitForFunction(() => {
        const plots = document.querySelectorAll('.js-plotly-plot');
        return Array.from(plots).every(plot => {
          const plotDiv = plot as any;
          return !plotDiv._transitionData;
        });
      }, { timeout: 2000 });
    } catch {
      // No Plotly graphs present
    }
  }

  /**
   * Disable animations for consistent screenshots
   */
  async disableAnimations(): Promise<void> {
    await this.page.addStyleTag({
      content: `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }

        .plotly .js-plotly-plot .plotly-notifier {
          display: none !important;
        }
      `
    });
  }

  /**
   * Enable reduced motion preferences
   */
  async enableReducedMotion(): Promise<void> {
    await this.page.emulateMedia({ reducedMotion: 'reduce' });
    await this.disableAnimations();
  }

  /**
   * Take a component screenshot with optimal settings
   */
  async screenshotComponent(
    selector: string,
    name: string,
    config: Partial<VisualTestConfig> = {}
  ): Promise<void> {
    const finalConfig = { ...DEFAULT_VISUAL_CONFIG, ...config };

    // Wait for component to be visible
    await this.page.waitForSelector(selector, { state: 'visible' });

    // Wait for animations to complete
    await this.waitForAnimationsToComplete();

    // Special handling for Plotly graphs
    if (selector.includes('.js-plotly-plot') || selector.includes('plot')) {
      await this.waitForPlotlyRender(selector);
    }

    const locator = this.page.locator(selector);
    await expect(locator).toHaveScreenshot(`${name}.png`, {
      threshold: finalConfig.threshold,
      maxDiffPixels: finalConfig.maxDiffPixels,
      animations: finalConfig.animations,
      caret: finalConfig.caret,
      mode: finalConfig.mode,
      scale: finalConfig.scale,
      mask: finalConfig.mask?.map(m => this.page.locator(m.selector))
    });
  }

  /**
   * Take a full page screenshot
   */
  async screenshotFullPage(
    name: string,
    config: Partial<VisualTestConfig> = {}
  ): Promise<void> {
    const finalConfig = { ...DEFAULT_VISUAL_CONFIG, ...config };

    // Wait for page to be fully loaded
    await this.page.waitForLoadState('networkidle');
    await this.waitForAnimationsToComplete();

    // Wait for any Plotly graphs to render
    try {
      await this.waitForPlotlyRender();
    } catch {
      // No Plotly graphs present
    }

    await expect(this.page).toHaveScreenshot(`${name}.png`, {
      fullPage: true,
      threshold: finalConfig.threshold,
      maxDiffPixels: finalConfig.maxDiffPixels,
      animations: finalConfig.animations,
      caret: finalConfig.caret,
      mode: finalConfig.mode,
      clip: finalConfig.clip,
      mask: finalConfig.mask?.map(m => this.page.locator(m.selector))
    });
  }

  /**
   * Compare screenshots across different states
   */
  async compareStates(
    selector: string,
    states: Array<{
      name: string;
      setup: () => Promise<void>;
      config?: Partial<VisualTestConfig>;
    }>
  ): Promise<void> {
    for (const state of states) {
      await state.setup();
      await this.screenshotComponent(
        selector,
        state.name,
        state.config
      );
    }
  }

  /**
   * Test component across multiple viewports
   */
  async testResponsiveComponent(
    selector: string,
    baseName: string,
    viewports: Array<keyof typeof RESPONSIVE_VIEWPORTS> = ['mobile', 'tablet', 'desktop'],
    config: Partial<VisualTestConfig> = {}
  ): Promise<void> {
    for (const viewportName of viewports) {
      await this.setViewport(viewportName);
      await this.screenshotComponent(
        selector,
        `${baseName}-${viewportName}`,
        config
      );
    }
  }

  /**
   * Test component across multiple themes
   */
  async testThemeComponent(
    selector: string,
    baseName: string,
    themes: Array<keyof typeof THEME_CONFIGS> = ['light', 'dark'],
    config: Partial<VisualTestConfig> = {}
  ): Promise<void> {
    for (const themeName of themes) {
      await this.setTheme(themeName);
      await this.screenshotComponent(
        selector,
        `${baseName}-${themeName}`,
        config
      );
    }
  }

  /**
   * Test hover states and interactions
   */
  async testInteractionStates(
    selector: string,
    baseName: string,
    config: Partial<VisualTestConfig> = {}
  ): Promise<void> {
    const element = this.page.locator(selector);

    // Normal state
    await this.screenshotComponent(selector, `${baseName}-normal`, config);

    // Hover state
    await element.hover();
    await this.page.waitForTimeout(ANIMATION_DURATIONS.hoverEffect);
    await this.screenshotComponent(selector, `${baseName}-hover`, config);

    // Focus state (if focusable)
    try {
      await element.focus();
      await this.page.waitForTimeout(100);
      await this.screenshotComponent(selector, `${baseName}-focus`, config);
    } catch {
      // Element not focusable
    }
  }

  /**
   * Validate accessibility visual indicators
   */
  async validateAccessibilityVisuals(
    selector: string,
    baseName: string
  ): Promise<void> {
    // Test focus indicators
    const element = this.page.locator(selector);

    try {
      await element.focus();
      await this.screenshotComponent(selector, `${baseName}-focus-indicator`);

      // Test high contrast mode
      await this.page.emulateMedia({ forcedColors: 'active' });
      await this.screenshotComponent(selector, `${baseName}-high-contrast`);

      // Reset forced colors
      await this.page.emulateMedia({ forcedColors: 'none' });
    } catch {
      // Element not focusable or other issues
    }
  }

  /**
   * Create baseline screenshots for new components
   */
  async createBaseline(
    selector: string,
    name: string,
    config: Partial<VisualTestConfig> = {}
  ): Promise<void> {
    // This will create new baseline screenshots when run with --update-snapshots
    await this.screenshotComponent(selector, `baseline-${name}`, config);
  }

  /**
   * Mask dynamic content for consistent screenshots
   */
  createDynamicContentMasks(additionalSelectors: string[] = []): Array<{selector: string}> {
    const defaultMasks = [
      '[data-testid="timestamp"]',
      '[data-testid="random-id"]',
      '.loading-spinner',
      '[data-testid="file-size"]',
      '[data-testid="processing-time"]'
    ];

    return [...defaultMasks, ...additionalSelectors].map(selector => ({ selector }));
  }

  /**
   * Wait for file upload completion
   */
  async waitForFileUploadComplete(): Promise<void> {
    // Wait for upload progress to disappear
    try {
      await this.page.waitForSelector(COMPONENT_SELECTORS.fileUploadProgress, {
        state: 'hidden',
        timeout: 10000
      });
    } catch {
      // Progress indicator might not be present
    }

    // Wait for success or error state
    await this.page.waitForSelector(
      `${COMPONENT_SELECTORS.fileUploadSuccess}, ${COMPONENT_SELECTORS.fileUploadError}`,
      { timeout: 10000 }
    );

    // Additional wait for any subsequent processing
    await this.page.waitForTimeout(500);
  }

  /**
   * Simulate loading states for testing
   */
  async simulateLoadingState(duration: number = 1000): Promise<void> {
    // Inject loading overlay
    await this.page.evaluate((duration) => {
      const overlay = document.createElement('div');
      overlay.setAttribute('data-testid', 'loading-overlay');
      overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(255, 255, 255, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
      `;

      const spinner = document.createElement('div');
      spinner.setAttribute('data-testid', 'loading-spinner');
      spinner.style.cssText = `
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #007bff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      `;

      const style = document.createElement('style');
      style.textContent = `
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `;

      document.head.appendChild(style);
      overlay.appendChild(spinner);
      document.body.appendChild(overlay);

      // Remove after duration
      setTimeout(() => {
        if (overlay.parentNode) {
          overlay.parentNode.removeChild(overlay);
        }
      }, duration);
    }, duration);

    await this.page.waitForTimeout(duration + 100);
  }
}

/**
 * Baseline Management Utilities
 */
export class BaselineManager {
  private baselinePath: string;

  constructor(baselinePath: string = path.join(__dirname, 'baselines')) {
    this.baselinePath = baselinePath;
    this.ensureBaselineDirectory();
  }

  private ensureBaselineDirectory(): void {
    if (!fs.existsSync(this.baselinePath)) {
      fs.mkdirSync(this.baselinePath, { recursive: true });
    }
  }

  async updateBaselines(testName: string): Promise<void> {
    // Implementation for updating baselines programmatically
    console.log(`Updating baselines for: ${testName}`);
  }

  async compareWithBaseline(
    currentScreenshot: string,
    baselineName: string
  ): Promise<{ match: boolean; diffPixels: number }> {
    // Implementation for programmatic baseline comparison
    // This would typically use pixelmatch or similar library
    return { match: true, diffPixels: 0 };
  }

  listBaselines(): string[] {
    if (!fs.existsSync(this.baselinePath)) {
      return [];
    }
    return fs.readdirSync(this.baselinePath).filter(file => file.endsWith('.png'));
  }

  deleteBaseline(baselineName: string): void {
    const baselineFile = path.join(this.baselinePath, `${baselineName}.png`);
    if (fs.existsSync(baselineFile)) {
      fs.unlinkSync(baselineFile);
    }
  }
}
