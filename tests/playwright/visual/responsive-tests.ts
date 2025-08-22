/**
 * Responsive Design Visual Tests
 * Comprehensive testing of responsive layouts across different viewports and orientations
 */

import { test, expect } from '@playwright/test';
import { VisualTestUtils } from './visual-utils';
import { 
  RESPONSIVE_VIEWPORTS, 
  COMPONENT_SELECTORS,
  DEFAULT_VISUAL_CONFIG,
  STRICT_VISUAL_CONFIG 
} from './visual-config';

// Responsive-specific configuration
const RESPONSIVE_CONFIG = {
  ...DEFAULT_VISUAL_CONFIG,
  threshold: 0.1,
  maxDiffPixels: 150
};

test.describe('Responsive Design Visual Tests', () => {
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

  // Test each viewport size individually
  for (const [viewportName, viewport] of Object.entries(RESPONSIVE_VIEWPORTS)) {
    test.describe(`Viewport: ${viewportName} (${viewport.width}x${viewport.height})`, () => {
      
      test.beforeEach(async ({ page }) => {
        await visualUtils.setViewport(viewportName as keyof typeof RESPONSIVE_VIEWPORTS);
      });

      test(`${viewportName} - Full Page Layout @visual @responsive`, async ({ page }) => {
        await visualUtils.screenshotFullPage(
          `responsive-full-page-${viewportName}`,
          RESPONSIVE_CONFIG
        );
      });

      test(`${viewportName} - Header Responsiveness @visual @responsive`, async ({ page }) => {
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.header,
          `responsive-header-${viewportName}`,
          RESPONSIVE_CONFIG
        );
      });

      test(`${viewportName} - Navigation Tabs Responsiveness @visual @responsive`, async ({ page }) => {
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.navigation,
          `responsive-navigation-${viewportName}`,
          RESPONSIVE_CONFIG
        );
      });

      test(`${viewportName} - File Upload Component Responsiveness @visual @responsive`, async ({ page }) => {
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.fileUpload,
          `responsive-file-upload-${viewportName}`,
          RESPONSIVE_CONFIG
        );
      });

      test(`${viewportName} - Main Content Area @visual @responsive`, async ({ page }) => {
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.mainContent,
          `responsive-main-content-${viewportName}`,
          RESPONSIVE_CONFIG
        );
      });

      test(`${viewportName} - Plotly Graph Responsiveness @visual @responsive`, async ({ page }) => {
        // First check if graphs are present
        const graphCount = await page.locator(COMPONENT_SELECTORS.plotlyGraph).count();
        
        if (graphCount > 0) {
          await visualUtils.waitForPlotlyRender();
          await visualUtils.screenshotComponent(
            COMPONENT_SELECTORS.plotlyGraph,
            `responsive-plotly-graph-${viewportName}`,
            RESPONSIVE_CONFIG
          );
        } else {
          // Create a test graph to verify responsive behavior
          await page.evaluate(() => {
            const graphDiv = document.createElement('div');
            graphDiv.setAttribute('data-testid', 'test-responsive-graph');
            graphDiv.style.cssText = 'width: 100%; height: 400px; border: 1px solid #ddd;';
            graphDiv.innerHTML = `
              <div style="
                width: 100%;
                height: 100%;
                background: linear-gradient(45deg, #f0f0f0 25%, transparent 25%),
                           linear-gradient(-45deg, #f0f0f0 25%, transparent 25%),
                           linear-gradient(45deg, transparent 75%, #f0f0f0 75%),
                           linear-gradient(-45deg, transparent 75%, #f0f0f0 75%);
                background-size: 20px 20px;
                background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                color: #666;
              ">
                Responsive Graph Placeholder<br>
                <small>${window.innerWidth}x${window.innerHeight}</small>
              </div>
            `;
            
            const container = document.querySelector('[data-testid="main-content"]') || document.body;
            container.appendChild(graphDiv);
          });

          await visualUtils.screenshotComponent(
            '[data-testid="test-responsive-graph"]',
            `responsive-graph-placeholder-${viewportName}`,
            RESPONSIVE_CONFIG
          );
        }
      });

      test(`${viewportName} - Data Table Responsiveness @visual @responsive`, async ({ page }) => {
        const tableCount = await page.locator(COMPONENT_SELECTORS.dataTable).count();
        
        if (tableCount > 0) {
          await visualUtils.screenshotComponent(
            COMPONENT_SELECTORS.dataTable,
            `responsive-data-table-${viewportName}`,
            RESPONSIVE_CONFIG
          );
        } else {
          // Create a responsive test table
          await page.evaluate(() => {
            const tableDiv = document.createElement('div');
            tableDiv.setAttribute('data-testid', 'test-responsive-table');
            tableDiv.style.cssText = 'width: 100%; overflow-x: auto; margin: 20px 0;';
            tableDiv.innerHTML = `
              <table style="width: 100%; border-collapse: collapse; min-width: 600px;">
                <thead>
                  <tr style="background: #f8f9fa;">
                    <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Column 1</th>
                    <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Column 2</th>
                    <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Column 3</th>
                    <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Column 4</th>
                    <th style="padding: 12px; border: 1px solid #dee2e6; text-align: left;">Column 5</th>
                  </tr>
                </thead>
                <tbody>
                  ${Array.from({ length: 5 }, (_, i) => `
                    <tr>
                      <td style="padding: 12px; border: 1px solid #dee2e6;">Row ${i + 1} Data 1</td>
                      <td style="padding: 12px; border: 1px solid #dee2e6;">Row ${i + 1} Data 2</td>
                      <td style="padding: 12px; border: 1px solid #dee2e6;">Row ${i + 1} Data 3</td>
                      <td style="padding: 12px; border: 1px solid #dee2e6;">Row ${i + 1} Data 4</td>
                      <td style="padding: 12px; border: 1px solid #dee2e6;">Row ${i + 1} Data 5</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            `;
            
            const container = document.querySelector('[data-testid="main-content"]') || document.body;
            container.appendChild(tableDiv);
          });

          await visualUtils.screenshotComponent(
            '[data-testid="test-responsive-table"]',
            `responsive-table-${viewportName}`,
            RESPONSIVE_CONFIG
          );
        }
      });
    });
  }

  // Test responsive breakpoint transitions
  test.describe('Responsive Breakpoint Transitions', () => {
    
    test('Mobile to Tablet Transition @visual @responsive @breakpoint', async ({ page }) => {
      // Test the transition between mobile and tablet layouts
      await visualUtils.setViewport('mobile');
      await visualUtils.screenshotFullPage('breakpoint-mobile-before', RESPONSIVE_CONFIG);
      
      await visualUtils.setViewport('tablet');
      await visualUtils.screenshotFullPage('breakpoint-tablet-after', RESPONSIVE_CONFIG);
    });

    test('Tablet to Desktop Transition @visual @responsive @breakpoint', async ({ page }) => {
      await visualUtils.setViewport('tablet');
      await visualUtils.screenshotFullPage('breakpoint-tablet-before', RESPONSIVE_CONFIG);
      
      await visualUtils.setViewport('desktop');
      await visualUtils.screenshotFullPage('breakpoint-desktop-after', RESPONSIVE_CONFIG);
    });

    test('Desktop to Large Desktop Transition @visual @responsive @breakpoint', async ({ page }) => {
      await visualUtils.setViewport('desktop');
      await visualUtils.screenshotFullPage('breakpoint-desktop-before', RESPONSIVE_CONFIG);
      
      await visualUtils.setViewport('desktopLarge');
      await visualUtils.screenshotFullPage('breakpoint-desktop-large-after', RESPONSIVE_CONFIG);
    });
  });

  // Test orientation changes
  test.describe('Orientation Testing', () => {
    
    test('Mobile Portrait vs Landscape @visual @responsive @orientation', async ({ page }) => {
      // Portrait
      await visualUtils.setViewport('mobile');
      await visualUtils.screenshotFullPage('orientation-mobile-portrait', RESPONSIVE_CONFIG);
      
      // Landscape
      await visualUtils.setViewport('mobileLandscape');
      await visualUtils.screenshotFullPage('orientation-mobile-landscape', RESPONSIVE_CONFIG);
    });

    test('Tablet Portrait vs Landscape @visual @responsive @orientation', async ({ page }) => {
      // Portrait
      await visualUtils.setViewport('tablet');
      await visualUtils.screenshotFullPage('orientation-tablet-portrait', RESPONSIVE_CONFIG);
      
      // Landscape
      await visualUtils.setViewport('tabletLandscape');
      await visualUtils.screenshotFullPage('orientation-tablet-landscape', RESPONSIVE_CONFIG);
    });
  });

  // Test responsive navigation behavior
  test.describe('Responsive Navigation', () => {
    
    test('Navigation Collapse on Mobile @visual @responsive @navigation', async ({ page }) => {
      await visualUtils.setViewport('mobile');
      
      // Test collapsed navigation
      await visualUtils.screenshotComponent(
        COMPONENT_SELECTORS.navigation,
        'nav-mobile-collapsed',
        RESPONSIVE_CONFIG
      );
      
      // Test expanded navigation (if hamburger menu exists)
      try {
        const hamburgerMenu = page.locator('[data-testid="hamburger-menu"], .navbar-toggler');
        if (await hamburgerMenu.count() > 0) {
          await hamburgerMenu.click();
          await visualUtils.waitForAnimationsToComplete();
          
          await visualUtils.screenshotComponent(
            COMPONENT_SELECTORS.navigation,
            'nav-mobile-expanded',
            RESPONSIVE_CONFIG
          );
        }
      } catch (error) {
        console.log('Hamburger menu not found, skipping expanded navigation test');
      }
    });

    test('Navigation Full Width on Desktop @visual @responsive @navigation', async ({ page }) => {
      await visualUtils.setViewport('desktop');
      
      await visualUtils.screenshotComponent(
        COMPONENT_SELECTORS.navigation,
        'nav-desktop-full',
        RESPONSIVE_CONFIG
      );
    });
  });

  // Test content reflow and text wrapping
  test.describe('Content Reflow Testing', () => {
    
    test('Text Wrapping at Different Viewport Sizes @visual @responsive @text', async ({ page }) => {
      // Create test content with various text lengths
      await page.evaluate(() => {
        const textDiv = document.createElement('div');
        textDiv.setAttribute('data-testid', 'text-reflow-test');
        textDiv.style.cssText = 'padding: 20px; max-width: 100%;';
        textDiv.innerHTML = `
          <h2>Responsive Text Reflow Testing</h2>
          <p>This is a paragraph with normal length text that should wrap naturally at different viewport sizes. The text should maintain good readability and proper line heights across all screen sizes.</p>
          <p>This paragraph contains a very long word: supercalifragilisticexpialidocious, which should either wrap or be handled gracefully without breaking the layout.</p>
          <p>Short text.</p>
          <p>This is another longer paragraph that contains multiple sentences to test how text flows and wraps at different viewport widths. It includes various punctuation marks, numbers like 12345, and should maintain proper spacing and alignment throughout the responsive breakpoints.</p>
          <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0;">
            <h4>Constrained Width Container</h4>
            <p>This text is inside a bordered container to test how content behaves within constrained widths at different viewport sizes.</p>
          </div>
        `;
        document.body.appendChild(textDiv);
      });

      const viewportsToTest: (keyof typeof RESPONSIVE_VIEWPORTS)[] = ['mobile', 'tablet', 'desktop'];
      
      for (const viewportName of viewportsToTest) {
        await visualUtils.setViewport(viewportName);
        await visualUtils.screenshotComponent(
          '[data-testid="text-reflow-test"]',
          `text-reflow-${viewportName}`,
          RESPONSIVE_CONFIG
        );
      }
    });

    test('Image Responsiveness @visual @responsive @images', async ({ page }) => {
      // Create responsive image test
      await page.evaluate(() => {
        const imageDiv = document.createElement('div');
        imageDiv.setAttribute('data-testid', 'image-responsive-test');
        imageDiv.style.cssText = 'padding: 20px;';
        imageDiv.innerHTML = `
          <h3>Responsive Image Testing</h3>
          
          <div style="margin-bottom: 20px;">
            <h4>Responsive Image (max-width: 100%)</h4>
            <img src="data:image/svg+xml,%3Csvg width='800' height='400' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='800' height='400' fill='%23007bff'/%3E%3Ctext x='400' y='200' text-anchor='middle' dy='0.35em' fill='white' font-size='32' font-family='Arial'%3E800x400 Responsive Image%3C/text%3E%3C/svg%3E" 
                 style="max-width: 100%; height: auto; border: 1px solid #ddd;" />
          </div>
          
          <div style="margin-bottom: 20px;">
            <h4>Fixed Width Image Container</h4>
            <div style="width: 300px; overflow: hidden; border: 1px solid #ddd;">
              <img src="data:image/svg+xml,%3Csvg width='600' height='200' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='600' height='200' fill='%23dc3545'/%3E%3Ctext x='300' y='100' text-anchor='middle' dy='0.35em' fill='white' font-size='24' font-family='Arial'%3E600x200 Fixed Container%3C/text%3E%3C/svg%3E" 
                   style="width: 100%; height: auto;" />
            </div>
          </div>
          
          <div style="display: flex; flex-wrap: wrap; gap: 10px;">
            <div style="flex: 1; min-width: 150px;">
              <img src="data:image/svg+xml,%3Csvg width='300' height='300' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='300' height='300' fill='%2328a745'/%3E%3Ctext x='150' y='150' text-anchor='middle' dy='0.35em' fill='white' font-size='16' font-family='Arial'%3EFlexible 1%3C/text%3E%3C/svg%3E" 
                   style="width: 100%; height: auto; border: 1px solid #ddd;" />
            </div>
            <div style="flex: 1; min-width: 150px;">
              <img src="data:image/svg+xml,%3Csvg width='300' height='300' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='300' height='300' fill='%23ffc107'/%3E%3Ctext x='150' y='150' text-anchor='middle' dy='0.35em' fill='black' font-size='16' font-family='Arial'%3EFlexible 2%3C/text%3E%3C/svg%3E" 
                   style="width: 100%; height: auto; border: 1px solid #ddd;" />
            </div>
          </div>
        `;
        document.body.appendChild(imageDiv);
      });

      const viewportsToTest: (keyof typeof RESPONSIVE_VIEWPORTS)[] = ['mobile', 'tablet', 'desktop'];
      
      for (const viewportName of viewportsToTest) {
        await visualUtils.setViewport(viewportName);
        await visualUtils.screenshotComponent(
          '[data-testid="image-responsive-test"]',
          `images-responsive-${viewportName}`,
          RESPONSIVE_CONFIG
        );
      }
    });
  });

  // Test responsive form layouts
  test.describe('Responsive Forms', () => {
    
    test('Form Layout Responsiveness @visual @responsive @forms', async ({ page }) => {
      await page.evaluate(() => {
        const formDiv = document.createElement('div');
        formDiv.setAttribute('data-testid', 'responsive-form-test');
        formDiv.style.cssText = 'padding: 20px; max-width: 100%;';
        formDiv.innerHTML = `
          <h3>Responsive Form Layout</h3>
          <form style="width: 100%;">
            <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 15px;">
              <div style="flex: 1; min-width: 200px;">
                <label style="display: block; margin-bottom: 5px;">First Name:</label>
                <input type="text" style="width: 100%; padding: 10px; border: 1px solid #ddd;" placeholder="Enter first name">
              </div>
              <div style="flex: 1; min-width: 200px;">
                <label style="display: block; margin-bottom: 5px;">Last Name:</label>
                <input type="text" style="width: 100%; padding: 10px; border: 1px solid #ddd;" placeholder="Enter last name">
              </div>
            </div>
            
            <div style="margin-bottom: 15px;">
              <label style="display: block; margin-bottom: 5px;">Email Address:</label>
              <input type="email" style="width: 100%; padding: 10px; border: 1px solid #ddd;" placeholder="Enter email address">
            </div>
            
            <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 15px;">
              <div style="flex: 2; min-width: 200px;">
                <label style="display: block; margin-bottom: 5px;">Address:</label>
                <input type="text" style="width: 100%; padding: 10px; border: 1px solid #ddd;" placeholder="Enter address">
              </div>
              <div style="flex: 1; min-width: 100px;">
                <label style="display: block; margin-bottom: 5px;">Zip:</label>
                <input type="text" style="width: 100%; padding: 10px; border: 1px solid #ddd;" placeholder="12345">
              </div>
            </div>
            
            <div style="margin-bottom: 15px;">
              <label style="display: block; margin-bottom: 5px;">Message:</label>
              <textarea style="width: 100%; padding: 10px; border: 1px solid #ddd; height: 100px; resize: vertical;" placeholder="Enter your message"></textarea>
            </div>
            
            <div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: flex-end;">
              <button type="button" style="padding: 10px 20px; background: #6c757d; color: white; border: none; cursor: pointer;">Cancel</button>
              <button type="submit" style="padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer;">Submit</button>
            </div>
          </form>
        `;
        document.body.appendChild(formDiv);
      });

      const viewportsToTest: (keyof typeof RESPONSIVE_VIEWPORTS)[] = ['mobile', 'tablet', 'desktop'];
      
      for (const viewportName of viewportsToTest) {
        await visualUtils.setViewport(viewportName);
        await visualUtils.screenshotComponent(
          '[data-testid="responsive-form-test"]',
          `form-responsive-${viewportName}`,
          RESPONSIVE_CONFIG
        );
      }
    });
  });

  // Edge case testing
  test.describe('Responsive Edge Cases', () => {
    
    test('Very Small Viewport Handling @visual @responsive @edge-case', async ({ page }) => {
      // Test extremely small viewport
      await page.setViewportSize({ width: 320, height: 568 });
      await visualUtils.waitForAnimationsToComplete();
      
      await visualUtils.screenshotFullPage('responsive-very-small', RESPONSIVE_CONFIG);
    });

    test('Very Large Viewport Handling @visual @responsive @edge-case', async ({ page }) => {
      // Test extremely large viewport
      await page.setViewportSize({ width: 3840, height: 2160 });
      await visualUtils.waitForAnimationsToComplete();
      
      await visualUtils.screenshotFullPage('responsive-very-large', RESPONSIVE_CONFIG);
    });

    test('Unusual Aspect Ratio @visual @responsive @edge-case', async ({ page }) => {
      // Test unusual aspect ratios
      await page.setViewportSize({ width: 1600, height: 400 }); // Very wide
      await visualUtils.waitForAnimationsToComplete();
      
      await visualUtils.screenshotFullPage('responsive-wide-aspect', RESPONSIVE_CONFIG);
      
      await page.setViewportSize({ width: 400, height: 1600 }); // Very tall
      await visualUtils.waitForAnimationsToComplete();
      
      await visualUtils.screenshotFullPage('responsive-tall-aspect', RESPONSIVE_CONFIG);
    });
  });
});