/**
 * Type-Safe Page Objects for MELD Visualizer
 * Comprehensive page object implementations with strict typing
 */

import { Page, Locator, expect } from '@playwright/test';
import type { 
  TestTypes, 
  MELDData, 
  DashComponents, 
  PlotlyTypes,
  BasePage,
  HomePage,
  UploadPage,
  VisualizationPage,
  SettingsPage
} from '../types';

/**
 * Base page object with common functionality
 */
export abstract class BasePageObject implements BasePage {
  constructor(
    protected readonly page: Page,
    protected readonly selectors: TestTypes.PageSelectors
  ) {}

  /**
   * Navigate to page - must be implemented by subclasses
   */
  abstract goto(url?: string): Promise<void>;

  /**
   * Wait for page to be loaded - must be implemented by subclasses
   */
  abstract waitForLoad(): Promise<void>;

  /**
   * Take screenshot of current state
   */
  async screenshot(name: string): Promise<Buffer> {
    return await this.page.screenshot({ 
      fullPage: true,
      path: `screenshots/${name}.png`
    });
  }

  /**
   * Get element by test ID with type safety
   */
  getByTestId(testId: string): Locator {
    return this.page.getByTestId(testId);
  }

  /**
   * Wait for element to be visible with timeout
   */
  async waitForElement(selector: string, timeout = 10000): Promise<Locator> {
    const element = this.page.locator(selector);
    await element.waitFor({ state: 'visible', timeout });
    return element;
  }

  /**
   * Wait for network request to complete
   */
  async waitForNetworkIdle(timeout = 5000): Promise<void> {
    await this.page.waitForLoadState('networkidle', { timeout });
  }

  /**
   * Check if element exists without waiting
   */
  async elementExists(selector: string): Promise<boolean> {
    try {
      const element = this.page.locator(selector);
      await element.waitFor({ state: 'attached', timeout: 1000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get element text with null safety
   */
  async getElementText(selector: string): Promise<string> {
    const element = this.page.locator(selector);
    return await element.textContent() || '';
  }

  /**
   * Type-safe attribute getter
   */
  async getAttribute(selector: string, attribute: string): Promise<string | null> {
    const element = this.page.locator(selector);
    return await element.getAttribute(attribute);
  }

  /**
   * Safe click with retry logic
   */
  async safeClick(selector: string, options?: { timeout?: number; retries?: number }): Promise<void> {
    const { timeout = 10000, retries = 3 } = options || {};
    
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const element = this.page.locator(selector);
        await element.waitFor({ state: 'visible', timeout });
        await element.click({ timeout });
        return;
      } catch (error) {
        if (attempt === retries) {
          throw new Error(`Failed to click ${selector} after ${retries} attempts: ${error}`);
        }
        await this.page.waitForTimeout(1000 * attempt);
      }
    }
  }
}

/**
 * Home page object with type-safe navigation
 */
export class HomePageObject extends BasePageObject implements HomePage {
  readonly header: Locator;
  readonly navigation: Locator;
  readonly themeToggle: Locator;

  constructor(page: Page, selectors: TestTypes.PageSelectors) {
    super(page, selectors);
    this.header = page.locator(selectors.app.header);
    this.navigation = page.locator(selectors.tabs.container);
    this.themeToggle = page.locator(selectors.controls.themeToggle);
  }

  /**
   * Navigate to home page
   */
  async goto(): Promise<void> {
    await this.page.goto('/');
    await this.waitForLoad();
  }

  /**
   * Wait for Dash app to be fully loaded
   */
  async waitForLoad(): Promise<void> {
    // Wait for main app container
    await this.waitForElement(this.selectors.app.container, 30000);
    
    // Wait for Dash to be ready
    await this.page.waitForFunction(() => {
      return window.dash_clientside && window.Plotly;
    }, { timeout: 15000 });

    // Wait for initial loading to complete
    const loadingSelector = this.selectors.app.loading;
    if (await this.elementExists(loadingSelector)) {
      await this.page.locator(loadingSelector).waitFor({ state: 'hidden', timeout: 10000 });
    }
  }

  /**
   * Switch application theme with type safety
   */
  async switchTheme(theme: DashComponents.ThemeConfig['name']): Promise<void> {
    await this.safeClick(this.selectors.controls.themeToggle);
    
    // Wait for theme to be applied
    await this.page.waitForTimeout(1000);
    
    // Verify theme was applied
    const appliedTheme = await this.page.evaluate(() => {
      const body = document.body;
      if (body.classList.contains('dark-theme') || body.getAttribute('data-theme') === 'dark') {
        return 'dark';
      }
      return 'light';
    });

    if ((theme === 'dark' || theme === 'plotly_dark') && appliedTheme !== 'dark') {
      throw new Error(`Failed to apply dark theme. Current theme: ${appliedTheme}`);
    } else if ((theme === 'light' || theme === 'plotly') && appliedTheme !== 'light') {
      throw new Error(`Failed to apply light theme. Current theme: ${appliedTheme}`);
    }
  }

  /**
   * Navigate to specific tab with validation
   */
  async navigateToTab(tabId: string): Promise<void> {
    const tabSelector = this.selectors.tabs.tab(tabId);
    await this.safeClick(tabSelector);
    
    // Wait for tab content to be active
    await this.page.locator(this.selectors.tabs.active).waitFor({ state: 'visible' });
    
    // Verify correct tab is active
    const activeTab = await this.page.locator(`${tabSelector}.active, ${tabSelector}[aria-selected="true"]`).count();
    if (activeTab === 0) {
      throw new Error(`Tab ${tabId} is not active after navigation`);
    }
  }

  /**
   * Get current theme
   */
  async getCurrentTheme(): Promise<'light' | 'dark'> {
    return await this.page.evaluate(() => {
      const body = document.body;
      return body.classList.contains('dark-theme') || body.getAttribute('data-theme') === 'dark' 
        ? 'dark' 
        : 'light';
    });
  }

  /**
   * Check if navigation is responsive
   */
  async isNavigationResponsive(): Promise<boolean> {
    const viewport = this.page.viewportSize();
    if (!viewport) return false;
    
    return viewport.width < 768;
  }
}

/**
 * Upload page object with file handling
 */
export class UploadPageObject extends BasePageObject implements UploadPage {
  readonly dropzone: Locator;
  readonly fileInput: Locator;
  readonly uploadButton: Locator;
  readonly progressBar: Locator;
  readonly statusMessage: Locator;

  constructor(page: Page, selectors: TestTypes.PageSelectors) {
    super(page, selectors);
    this.dropzone = page.locator(selectors.upload.dropzone);
    this.fileInput = page.locator(selectors.upload.fileInput);
    this.uploadButton = page.locator(selectors.upload.button);
    this.progressBar = page.locator(selectors.upload.progress);
    this.statusMessage = page.locator(`${selectors.upload.success}, ${selectors.upload.error}`);
  }

  async goto(url?: string): Promise<void> {
    await this.page.goto(url || '/upload');
    await this.waitForLoad();
  }

  async waitForLoad(): Promise<void> {
    await this.waitForElement(this.selectors.upload.dropzone);
  }

  /**
   * Upload file with comprehensive validation
   */
  async uploadFile(file: TestTypes.TestDataFile): Promise<void> {
    // Validate file before upload
    this.validateFile(file);

    // Set up file chooser handler
    const fileChooserPromise = this.page.waitForEvent('filechooser');
    
    // Trigger file input
    if (await this.elementExists(this.selectors.upload.fileInput)) {
      await this.fileInput.click();
    } else {
      // Use dropzone if file input is hidden
      await this.dropzone.click();
    }

    // Handle file selection
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles(file.path);

    // Wait for upload to start
    await this.waitForUploadStart();
    
    // Wait for upload to complete
    await this.waitForUploadComplete();
  }

  /**
   * Wait for upload completion with timeout
   */
  async waitForUploadComplete(): Promise<void> {
    try {
      // Wait for either success or error message
      await this.statusMessage.waitFor({ state: 'visible', timeout: 30000 });
      
      // Check final status
      const status = await this.getUploadStatus();
      if (status === 'error') {
        const errorMessage = await this.getElementText(this.selectors.upload.error);
        throw new Error(`Upload failed: ${errorMessage}`);
      }
    } catch (error) {
      throw new Error(`Upload timeout or failed: ${error}`);
    }
  }

  /**
   * Get current upload status
   */
  async getUploadStatus(): Promise<'success' | 'error' | 'pending'> {
    const successExists = await this.elementExists(this.selectors.upload.success);
    const errorExists = await this.elementExists(this.selectors.upload.error);
    const progressExists = await this.elementExists(this.selectors.upload.progress);

    if (successExists) return 'success';
    if (errorExists) return 'error';
    if (progressExists) return 'pending';
    return 'pending';
  }

  /**
   * Wait for upload to start (progress bar appears)
   */
  private async waitForUploadStart(): Promise<void> {
    try {
      await this.progressBar.waitFor({ state: 'visible', timeout: 5000 });
    } catch {
      // Progress bar might not appear for small files
    }
  }

  /**
   * Validate file before upload
   */
  private validateFile(file: TestTypes.TestDataFile): void {
    if (!file.path || !file.content) {
      throw new Error('Invalid file: missing path or content');
    }

    if (file.size > 10_000_000) { // 10MB limit
      throw new Error(`File too large: ${file.size} bytes`);
    }

    const allowedTypes: TestTypes.TestFileType[] = ['csv', 'gcode', 'json'];
    if (!allowedTypes.includes(file.type)) {
      throw new Error(`Unsupported file type: ${file.type}`);
    }
  }

  /**
   * Get upload progress percentage
   */
  async getUploadProgress(): Promise<number> {
    if (!await this.elementExists(this.selectors.upload.progress)) {
      return 0;
    }

    const progress = await this.page.evaluate((selector) => {
      const element = document.querySelector(selector) as HTMLProgressElement;
      return element ? (element.value / element.max) * 100 : 0;
    }, this.selectors.upload.progress);

    return progress;
  }
}

/**
 * Visualization page object with Plotly integration
 */
export class VisualizationPageObject extends BasePageObject implements VisualizationPage {
  readonly plotlyGraph: Locator;
  readonly dataTable: Locator;
  readonly exportButton: Locator;
  readonly resetButton: Locator;
  readonly legend: Locator;

  constructor(page: Page, selectors: TestTypes.PageSelectors) {
    super(page, selectors);
    this.plotlyGraph = page.locator(selectors.graph.plotly);
    this.dataTable = page.locator(selectors.table.container);
    this.exportButton = page.locator(selectors.controls.exportButton);
    this.resetButton = page.locator(selectors.controls.resetButton);
    this.legend = page.locator(selectors.graph.legend);
  }

  async goto(url?: string): Promise<void> {
    await this.page.goto(url || '/visualization');
    await this.waitForLoad();
  }

  async waitForLoad(): Promise<void> {
    await this.waitForElement(this.selectors.graph.container);
  }

  /**
   * Wait for Plotly graph to render completely
   */
  async waitForGraphRender(): Promise<void> {
    // Wait for graph container
    await this.plotlyGraph.waitFor({ state: 'visible', timeout: 30000 });
    
    // Wait for Plotly to initialize and render
    await this.page.waitForFunction((selector) => {
      const element = document.querySelector(selector) as any;
      return element && 
             element._fullLayout && 
             element._fullData && 
             Array.isArray(element._fullData) &&
             element._fullData.length > 0;
    }, this.selectors.graph.plotly, { timeout: 15000 });

    // Wait for rendering to complete
    await this.page.waitForTimeout(1000);
  }

  /**
   * Get number of traces in the graph
   */
  async getTraceCount(): Promise<number> {
    return await this.page.evaluate((selector) => {
      const element = document.querySelector(selector) as any;
      return element && element._fullData ? element._fullData.length : 0;
    }, this.selectors.graph.plotly);
  }

  /**
   * Get data points from the visualization
   */
  async getDataPoints(): Promise<ReadonlyArray<MELDData.MELDPoint3D>> {
    const plotlyData = await this.page.evaluate((selector) => {
      const element = document.querySelector(selector) as any;
      if (!element || !element._fullData || !element._fullData[0]) {
        return [];
      }

      const trace = element._fullData[0];
      const points: MELDData.MELDPoint3D[] = [];

      if (trace.x && trace.y && trace.z) {
        for (let i = 0; i < trace.x.length; i++) {
          points.push({
            x: trace.x[i] || 0,
            y: trace.y[i] || 0,
            z: trace.z[i] || 0,
            temperature: trace.marker?.color?.[i] || 0,
            velocity: 0, // Would need to be calculated or stored separately
            timestamp: new Date().toISOString() // Would need actual timestamp
          });
        }
      }

      return points;
    }, this.selectors.graph.plotly);

    return plotlyData;
  }

  /**
   * Export visualization data
   */
  async exportData(format: 'csv' | 'json'): Promise<string> {
    // Set up download handler
    const downloadPromise = this.page.waitForEvent('download', { timeout: 10000 });
    
    // Click export button
    await this.safeClick(this.selectors.controls.exportButton);
    
    // Handle format selection if needed
    const formatSelector = `[data-format="${format}"], .export-${format}`;
    if (await this.elementExists(formatSelector)) {
      await this.safeClick(formatSelector);
    }
    
    // Wait for download
    const download = await downloadPromise;
    
    // Save and return file path
    const filePath = `downloads/${download.suggestedFilename()}`;
    await download.saveAs(filePath);
    
    return filePath;
  }

  /**
   * Reset visualization view
   */
  async resetView(): Promise<void> {
    await this.safeClick(this.selectors.controls.resetButton);
    
    // Wait for reset to complete
    await this.page.waitForTimeout(1000);
    
    // Verify reset by checking camera position
    const isReset = await this.page.evaluate((selector) => {
      const element = document.querySelector(selector) as any;
      if (!element || !element._fullLayout || !element._fullLayout.scene) {
        return false;
      }
      
      const camera = element._fullLayout.scene.camera;
      return camera && camera.eye && 
             Math.abs(camera.eye.x - 1.25) < 0.1 &&
             Math.abs(camera.eye.y - 1.25) < 0.1 &&
             Math.abs(camera.eye.z - 1.25) < 0.1;
    }, this.selectors.graph.plotly);

    if (!isReset) {
      console.warn('Graph may not have reset to default camera position');
    }
  }

  /**
   * Toggle trace visibility in legend
   */
  async toggleTrace(traceName: string): Promise<void> {
    const traceSelector = `.legend .traces .trace[data-trace-name="${traceName}"], .js-legend .traces .trace:has-text("${traceName}")`;
    
    if (await this.elementExists(traceSelector)) {
      await this.safeClick(traceSelector);
      // Wait for trace toggle to complete
      await this.page.waitForTimeout(500);
    } else {
      throw new Error(`Trace "${traceName}" not found in legend`);
    }
  }

  /**
   * Get current camera position
   */
  async getCameraPosition(): Promise<PlotlyTypes.Camera3D | null> {
    return await this.page.evaluate((selector) => {
      const element = document.querySelector(selector) as any;
      return element && element._fullLayout && element._fullLayout.scene 
        ? element._fullLayout.scene.camera 
        : null;
    }, this.selectors.graph.plotly);
  }

  /**
   * Check if graph is interactive
   */
  async isGraphInteractive(): Promise<boolean> {
    return await this.page.evaluate((selector) => {
      const element = document.querySelector(selector) as any;
      return element && element.style.pointerEvents !== 'none';
    }, this.selectors.graph.plotly);
  }
}

/**
 * Settings page object with configuration management
 */
export class SettingsPageObject extends BasePageObject implements SettingsPage {
  readonly themeSelector: Locator;
  readonly performanceOptions: Locator;
  readonly exportSettings: Locator;
  readonly resetSettings: Locator;

  constructor(page: Page, selectors: TestTypes.PageSelectors) {
    super(page, selectors);
    this.themeSelector = page.locator(`${selectors.controls.themeToggle}, .theme-selector`);
    this.performanceOptions = page.locator('.performance-settings');
    this.exportSettings = page.locator('.export-settings');
    this.resetSettings = page.locator('.reset-settings');
  }

  async goto(url?: string): Promise<void> {
    await this.page.goto(url || '/settings');
    await this.waitForLoad();
  }

  async waitForLoad(): Promise<void> {
    await this.waitForElement('.settings-container, .settings-page');
  }

  /**
   * Change application theme
   */
  async changeTheme(theme: DashComponents.ThemeConfig['name']): Promise<void> {
    // Find theme selector (could be dropdown or toggle)
    if (await this.elementExists('.theme-dropdown')) {
      await this.page.selectOption('.theme-dropdown', theme);
    } else if (await this.elementExists('.theme-selector')) {
      await this.safeClick(`.theme-option[data-theme="${theme}"]`);
    } else {
      // Fallback to theme toggle
      const currentTheme = await this.page.evaluate(() => {
        return document.body.classList.contains('dark-theme') ? 'dark' : 'light';
      });

      if ((theme.includes('dark') && currentTheme === 'light') || 
          (theme.includes('light') && currentTheme === 'dark')) {
        await this.safeClick(this.selectors.controls.themeToggle);
      }
    }

    // Wait for theme change to apply
    await this.page.waitForTimeout(1000);
  }

  /**
   * Update performance settings
   */
  async updatePerformanceSettings(settings: {
    enableAnimations?: boolean;
    maxDataPoints?: number;
    renderQuality?: 'low' | 'medium' | 'high';
  }): Promise<void> {
    if (!await this.elementExists('.performance-settings')) {
      throw new Error('Performance settings not found');
    }

    if (settings.enableAnimations !== undefined) {
      const checkbox = this.page.locator('.performance-settings .animations-toggle input');
      const isChecked = await checkbox.isChecked();
      if (isChecked !== settings.enableAnimations) {
        await checkbox.click();
      }
    }

    if (settings.maxDataPoints !== undefined) {
      await this.page.fill('.performance-settings .max-points input', settings.maxDataPoints.toString());
    }

    if (settings.renderQuality !== undefined) {
      await this.page.selectOption('.performance-settings .quality-select', settings.renderQuality);
    }

    // Save settings
    const saveButton = this.page.locator('.performance-settings .save-button');
    if (await saveButton.count() > 0) {
      await saveButton.click();
      await this.page.waitForTimeout(1000);
    }
  }

  /**
   * Reset all settings to defaults
   */
  async resetToDefaults(): Promise<void> {
    const confirmDialog = this.page.waitForEvent('dialog');
    await this.safeClick('.reset-settings');
    
    const dialog = await confirmDialog;
    await dialog.accept();
    
    // Wait for reset to complete
    await this.page.waitForTimeout(2000);
  }

  /**
   * Export current configuration
   */
  async exportConfiguration(): Promise<string> {
    const downloadPromise = this.page.waitForEvent('download');
    await this.safeClick('.export-settings');
    
    const download = await downloadPromise;
    const filePath = `downloads/config-${Date.now()}.json`;
    await download.saveAs(filePath);
    
    return filePath;
  }

  /**
   * Get current settings as object
   */
  async getCurrentSettings(): Promise<Record<string, unknown>> {
    return await this.page.evaluate(() => {
      // This would depend on how settings are stored in the app
      const settings: Record<string, unknown> = {};
      
      // Theme
      settings.theme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
      
      // Performance settings (if available)
      const animationsToggle = document.querySelector('.animations-toggle input') as HTMLInputElement;
      if (animationsToggle) {
        settings.enableAnimations = animationsToggle.checked;
      }
      
      const maxPointsInput = document.querySelector('.max-points input') as HTMLInputElement;
      if (maxPointsInput) {
        settings.maxDataPoints = parseInt(maxPointsInput.value);
      }
      
      return settings;
    });
  }
}