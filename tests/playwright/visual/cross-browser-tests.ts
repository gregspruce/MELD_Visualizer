/**
 * Cross-Browser Visual Consistency Tests
 * Ensures consistent visual appearance across different browsers and browser versions
 */

import { test, expect, devices } from '@playwright/test';
import { VisualTestUtils } from './visual-utils';
import {
  BROWSER_CONFIGS,
  RESPONSIVE_VIEWPORTS,
  COMPONENT_SELECTORS,
  STRICT_VISUAL_CONFIG
} from './visual-config';

// Test configuration for cross-browser consistency
const CROSS_BROWSER_CONFIG = {
  ...STRICT_VISUAL_CONFIG,
  threshold: 0.15, // Slightly more lenient for browser differences
  maxDiffPixels: 200 // Allow for minor rendering differences
};

// Browser-specific test suite
for (const [browserName, browserConfig] of Object.entries(BROWSER_CONFIGS)) {
  test.describe(`Cross-Browser Visual Tests - ${browserName}`, () => {
    let visualUtils: VisualTestUtils;

    test.beforeEach(async ({ page }) => {
      visualUtils = new VisualTestUtils(page);

      // Navigate to the application
      await page.goto('http://localhost:8050', { waitUntil: 'networkidle' });

      // Disable animations for consistent screenshots
      await visualUtils.disableAnimations();

      // Wait for initial page load
      await page.waitForLoadState('domcontentloaded');
      await visualUtils.waitForAnimationsToComplete();
    });

    test(`${browserName} - Full Page Layout Consistency @visual @cross-browser`, async ({ page }) => {
      // Test main page layout across browsers
      await visualUtils.screenshotFullPage(
        `cross-browser-full-page-${browserName}`,
        CROSS_BROWSER_CONFIG
      );
    });

    test(`${browserName} - Header Component Consistency @visual @cross-browser`, async ({ page }) => {
      await visualUtils.screenshotComponent(
        COMPONENT_SELECTORS.header,
        `cross-browser-header-${browserName}`,
        CROSS_BROWSER_CONFIG
      );
    });

    test(`${browserName} - Navigation Tabs Consistency @visual @cross-browser`, async ({ page }) => {
      await visualUtils.screenshotComponent(
        COMPONENT_SELECTORS.navigation,
        `cross-browser-navigation-${browserName}`,
        CROSS_BROWSER_CONFIG
      );
    });

    test(`${browserName} - File Upload Component Consistency @visual @cross-browser`, async ({ page }) => {
      await visualUtils.screenshotComponent(
        COMPONENT_SELECTORS.fileUpload,
        `cross-browser-file-upload-${browserName}`,
        CROSS_BROWSER_CONFIG
      );
    });

    test(`${browserName} - Typography and Font Rendering @visual @cross-browser`, async ({ page }) => {
      // Create a test div with various typography elements
      await page.evaluate(() => {
        const testDiv = document.createElement('div');
        testDiv.setAttribute('data-testid', 'typography-test');
        testDiv.innerHTML = `
          <h1>Heading 1 - Typography Test</h1>
          <h2>Heading 2 - Secondary Title</h2>
          <h3>Heading 3 - Tertiary Title</h3>
          <p>Regular paragraph text with <strong>bold</strong> and <em>italic</em> formatting.</p>
          <p>This is a longer paragraph to test line spacing and text flow across different browsers.
             It includes various punctuation marks: commas, periods, semicolons; exclamation points!
             And question marks? Plus numbers like 123, 456.789, and special characters like @#$%.</p>
          <ul>
            <li>Unordered list item one</li>
            <li>Unordered list item two with <code>inline code</code></li>
            <li>Unordered list item three</li>
          </ul>
          <ol>
            <li>Ordered list item one</li>
            <li>Ordered list item two</li>
          </ol>
          <blockquote>This is a blockquote for testing quote styling across browsers.</blockquote>
        `;
        testDiv.style.cssText = `
          max-width: 600px;
          margin: 20px;
          padding: 20px;
          border: 1px solid #ddd;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        `;
        document.body.appendChild(testDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="typography-test"]',
        `cross-browser-typography-${browserName}`,
        CROSS_BROWSER_CONFIG
      );
    });

    test(`${browserName} - Form Controls Consistency @visual @cross-browser`, async ({ page }) => {
      // Create comprehensive form controls test
      await page.evaluate(() => {
        const formDiv = document.createElement('div');
        formDiv.setAttribute('data-testid', 'form-controls-test');
        formDiv.innerHTML = `
          <div style="padding: 20px; max-width: 500px;">
            <h3>Form Controls Cross-Browser Test</h3>

            <div style="margin-bottom: 15px;">
              <label>Text Input:</label>
              <input type="text" value="Sample text" style="width: 100%; padding: 8px;">
            </div>

            <div style="margin-bottom: 15px;">
              <label>Password Input:</label>
              <input type="password" value="password123" style="width: 100%; padding: 8px;">
            </div>

            <div style="margin-bottom: 15px;">
              <label>Select Dropdown:</label>
              <select style="width: 100%; padding: 8px;">
                <option>Option 1</option>
                <option selected>Option 2 (Selected)</option>
                <option>Option 3</option>
              </select>
            </div>

            <div style="margin-bottom: 15px;">
              <label>Textarea:</label>
              <textarea style="width: 100%; padding: 8px; height: 80px;">Sample textarea content
Line 2 of content</textarea>
            </div>

            <div style="margin-bottom: 15px;">
              <label>
                <input type="checkbox" checked> Checked Checkbox
              </label>
            </div>

            <div style="margin-bottom: 15px;">
              <label>
                <input type="checkbox"> Unchecked Checkbox
              </label>
            </div>

            <div style="margin-bottom: 15px;">
              <label>
                <input type="radio" name="radio-test" checked> Selected Radio
              </label>
            </div>

            <div style="margin-bottom: 15px;">
              <label>
                <input type="radio" name="radio-test"> Unselected Radio
              </label>
            </div>

            <div style="margin-bottom: 15px;">
              <input type="range" min="0" max="100" value="50" style="width: 100%;">
            </div>

            <div style="margin-bottom: 15px;">
              <button type="button" style="padding: 10px 20px; margin-right: 10px;">Primary Button</button>
              <button type="button" disabled style="padding: 10px 20px;">Disabled Button</button>
            </div>
          </div>
        `;
        document.body.appendChild(formDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="form-controls-test"]',
        `cross-browser-form-controls-${browserName}`,
        CROSS_BROWSER_CONFIG
      );
    });

    test(`${browserName} - CSS Grid and Flexbox Layout @visual @cross-browser`, async ({ page }) => {
      // Test modern CSS layout techniques
      await page.evaluate(() => {
        const layoutDiv = document.createElement('div');
        layoutDiv.setAttribute('data-testid', 'layout-test');
        layoutDiv.innerHTML = `
          <div style="padding: 20px;">
            <h3>CSS Grid and Flexbox Layout Test</h3>

            <h4>CSS Grid Layout:</h4>
            <div style="
              display: grid;
              grid-template-columns: 1fr 1fr 1fr;
              gap: 10px;
              margin-bottom: 20px;
            ">
              <div style="background: #f0f0f0; padding: 20px; text-align: center;">Grid Item 1</div>
              <div style="background: #e0e0e0; padding: 20px; text-align: center;">Grid Item 2</div>
              <div style="background: #d0d0d0; padding: 20px; text-align: center;">Grid Item 3</div>
              <div style="background: #c0c0c0; padding: 20px; text-align: center; grid-column: span 2;">Spanning Item</div>
              <div style="background: #b0b0b0; padding: 20px; text-align: center;">Grid Item 6</div>
            </div>

            <h4>Flexbox Layout:</h4>
            <div style="
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 10px;
              padding: 10px;
              border: 1px solid #ccc;
            ">
              <div style="background: #ffeeee; padding: 10px;">Flex Item 1</div>
              <div style="background: #eeffee; padding: 10px; flex: 1; margin: 0 10px;">Flexible Item</div>
              <div style="background: #eeeeff; padding: 10px;">Flex Item 3</div>
            </div>

            <div style="
              display: flex;
              flex-direction: column;
              align-items: center;
              padding: 10px;
              border: 1px solid #ccc;
            ">
              <div style="background: #ffffee; padding: 10px; margin: 5px;">Column Item 1</div>
              <div style="background: #ffeeee; padding: 10px; margin: 5px;">Column Item 2</div>
              <div style="background: #eeffff; padding: 10px; margin: 5px;">Column Item 3</div>
            </div>
          </div>
        `;
        document.body.appendChild(layoutDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="layout-test"]',
        `cross-browser-layout-${browserName}`,
        CROSS_BROWSER_CONFIG
      );
    });

    test(`${browserName} - Border Radius and Box Shadow @visual @cross-browser`, async ({ page }) => {
      // Test CSS visual effects that might render differently across browsers
      await page.evaluate(() => {
        const effectsDiv = document.createElement('div');
        effectsDiv.setAttribute('data-testid', 'effects-test');
        effectsDiv.innerHTML = `
          <div style="padding: 20px;">
            <h3>CSS Effects Cross-Browser Test</h3>

            <div style="display: flex; flex-wrap: wrap; gap: 20px;">
              <div style="
                width: 100px;
                height: 100px;
                background: #007bff;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
              ">Rounded</div>

              <div style="
                width: 100px;
                height: 100px;
                background: #28a745;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
              ">Circle</div>

              <div style="
                width: 100px;
                height: 100px;
                background: #ffc107;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                display: flex;
                align-items: center;
                justify-content: center;
              ">Shadow</div>

              <div style="
                width: 100px;
                height: 100px;
                background: #dc3545;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                border-radius: 15px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
              ">Both</div>

              <div style="
                width: 100px;
                height: 100px;
                background: linear-gradient(45deg, #007bff, #28a745);
                border-radius: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
              ">Gradient</div>

              <div style="
                width: 100px;
                height: 100px;
                background: #6f42c1;
                border: 3px solid #fd7e14;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
              ">Border</div>
            </div>
          </div>
        `;
        document.body.appendChild(effectsDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="effects-test"]',
        `cross-browser-effects-${browserName}`,
        CROSS_BROWSER_CONFIG
      );
    });

    // Test responsive behavior across browsers
    for (const [viewportName, viewport] of Object.entries(RESPONSIVE_VIEWPORTS)) {
      test(`${browserName} - Responsive Layout ${viewportName} @visual @cross-browser @responsive`, async ({ page }) => {
        await visualUtils.setViewport(viewportName as keyof typeof RESPONSIVE_VIEWPORTS);

        await visualUtils.screenshotFullPage(
          `cross-browser-responsive-${browserName}-${viewportName}`,
          CROSS_BROWSER_CONFIG
        );
      });
    }
  });
}

// Cross-browser comparison tests
test.describe('Cross-Browser Comparison Tests', () => {
  test('Compare identical components across browsers @visual @cross-browser @comparison', async () => {
    // This test would run after all browser-specific tests
    // and compare the results to identify inconsistencies
    console.log('Cross-browser comparison would be performed here');

    // In a real implementation, you would:
    // 1. Load screenshots from different browsers
    // 2. Use image comparison tools to identify differences
    // 3. Generate a report showing inconsistencies
    // 4. Flag potential browser-specific issues
  });
});

// Browser-specific regression tests
test.describe('Browser-Specific Regression Tests', () => {
  test('Safari-specific font rendering issues @visual @cross-browser @safari', async ({ page, browserName }) => {
    test.skip(browserName !== 'webkit', 'Safari-specific test');

    const visualUtils = new VisualTestUtils(page);
    await page.goto('http://localhost:8050');

    // Test Safari-specific font rendering quirks
    await visualUtils.screenshotComponent(
      'body',
      'safari-font-rendering',
      { threshold: 0.1 }
    );
  });

  test('Firefox flexbox rendering edge cases @visual @cross-browser @firefox', async ({ page, browserName }) => {
    test.skip(browserName !== 'firefox', 'Firefox-specific test');

    const visualUtils = new VisualTestUtils(page);
    await page.goto('http://localhost:8050');

    // Test Firefox flexbox quirks
    if (await page.locator('.d-flex').count() > 0) {
      await visualUtils.screenshotComponent(
        '.d-flex',
        'firefox-flexbox-rendering',
        { threshold: 0.1 }
      );
    }
  });

  test('Chrome scrollbar styling @visual @cross-browser @chrome', async ({ page, browserName }) => {
    test.skip(browserName !== 'chromium', 'Chrome-specific test');

    const visualUtils = new VisualTestUtils(page);
    await page.goto('http://localhost:8050');

    // Create scrollable content to test scrollbar styling
    await page.evaluate(() => {
      const scrollDiv = document.createElement('div');
      scrollDiv.setAttribute('data-testid', 'scrollbar-test');
      scrollDiv.style.cssText = `
        width: 300px;
        height: 200px;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 10px;
      `;
      scrollDiv.innerHTML = `
        <div style="height: 500px;">
          <h4>Scrollable Content</h4>
          <p>This content is taller than the container to test scrollbar styling.</p>
          ${Array.from({ length: 20 }, (_, i) => `<p>Line ${i + 1} of scrollable content.</p>`).join('')}
        </div>
      `;
      document.body.appendChild(scrollDiv);
    });

    await visualUtils.screenshotComponent(
      '[data-testid="scrollbar-test"]',
      'chrome-scrollbar-styling',
      { threshold: 0.1 }
    );
  });
});
