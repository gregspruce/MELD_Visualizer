/**
 * CSS Validation and Performance Assessment Tests
 * Comprehensive testing of CSS properties, layout consistency, and performance impact
 */

import { test, expect } from '@playwright/test';
import { VisualTestUtils } from './visual-utils';
import {
  COMPONENT_SELECTORS,
  DEFAULT_VISUAL_CONFIG,
  PERFORMANCE_THRESHOLDS,
  RESPONSIVE_VIEWPORTS
} from './visual-config';

// CSS validation specific configuration
const CSS_VALIDATION_CONFIG = {
  ...DEFAULT_VISUAL_CONFIG,
  threshold: 0.05, // Very strict for CSS consistency
  maxDiffPixels: 25
};

test.describe('CSS Validation and Performance Tests', () => {
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

  test.describe('CSS Grid and Flexbox Validation', () => {

    test('CSS Grid Layout Consistency @visual @css @grid', async ({ page }) => {
      await page.evaluate(() => {
        const gridDiv = document.createElement('div');
        gridDiv.setAttribute('data-testid', 'css-grid-validation');
        gridDiv.innerHTML = `
          <div style="padding: 40px;">
            <h3>CSS Grid Layout Validation</h3>

            <!-- Basic Grid Layout -->
            <div style="margin-bottom: 40px;">
              <h4>Basic Grid (3 columns, auto rows)</h4>
              <div style="
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 20px;
                border: 2px solid #007bff;
                padding: 20px;
                border-radius: 8px;
              ">
                <div style="background: #e3f2fd; padding: 15px; border-radius: 4px; text-align: center;">Item 1</div>
                <div style="background: #f3e5f5; padding: 15px; border-radius: 4px; text-align: center;">Item 2</div>
                <div style="background: #e8f5e8; padding: 15px; border-radius: 4px; text-align: center;">Item 3</div>
                <div style="background: #fff3e0; padding: 15px; border-radius: 4px; text-align: center;">Item 4</div>
                <div style="background: #fce4ec; padding: 15px; border-radius: 4px; text-align: center;">Item 5</div>
                <div style="background: #e0f2f1; padding: 15px; border-radius: 4px; text-align: center;">Item 6</div>
              </div>
            </div>

            <!-- Complex Grid Layout -->
            <div style="margin-bottom: 40px;">
              <h4>Complex Grid (Named lines, spanning)</h4>
              <div style="
                display: grid;
                grid-template-columns: [sidebar-start] 200px [sidebar-end main-start] 1fr [main-end];
                grid-template-rows: [header-start] 60px [header-end content-start] 1fr [content-end footer-start] 40px [footer-end];
                gap: 20px;
                height: 300px;
                border: 2px solid #28a745;
                padding: 20px;
                border-radius: 8px;
              ">
                <div style="
                  grid-column: sidebar-start / main-end;
                  grid-row: header-start / header-end;
                  background: #007bff;
                  color: white;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  border-radius: 4px;
                ">Header (spans full width)</div>

                <div style="
                  grid-column: sidebar-start / sidebar-end;
                  grid-row: content-start / footer-start;
                  background: #6c757d;
                  color: white;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  border-radius: 4px;
                ">Sidebar</div>

                <div style="
                  grid-column: main-start / main-end;
                  grid-row: content-start / content-end;
                  background: #f8f9fa;
                  border: 1px solid #dee2e6;
                  padding: 20px;
                  border-radius: 4px;
                  overflow: auto;
                ">
                  <h5>Main Content Area</h5>
                  <p>This is the main content area that takes up the remaining space. It demonstrates proper grid layout with named grid lines and area spanning.</p>
                  <ul>
                    <li>Grid item with complex positioning</li>
                    <li>Responsive behavior maintained</li>
                    <li>Proper spacing and alignment</li>
                  </ul>
                </div>

                <div style="
                  grid-column: sidebar-start / main-end;
                  grid-row: footer-start / footer-end;
                  background: #dc3545;
                  color: white;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  border-radius: 4px;
                ">Footer (spans full width)</div>
              </div>
            </div>

            <!-- Auto-fit and minmax -->
            <div style="margin-bottom: 40px;">
              <h4>Auto-fit with minmax (responsive cards)</h4>
              <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                border: 2px solid #ffc107;
                padding: 20px;
                border-radius: 8px;
              ">
                <div style="
                  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  color: white;
                  padding: 20px;
                  border-radius: 8px;
                  text-align: center;
                ">
                  <h5 style="margin: 0 0 10px 0;">Card 1</h5>
                  <p style="margin: 0; opacity: 0.9;">Responsive card using auto-fit</p>
                </div>
                <div style="
                  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                  color: white;
                  padding: 20px;
                  border-radius: 8px;
                  text-align: center;
                ">
                  <h5 style="margin: 0 0 10px 0;">Card 2</h5>
                  <p style="margin: 0; opacity: 0.9;">Automatically adjusts size</p>
                </div>
                <div style="
                  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                  color: white;
                  padding: 20px;
                  border-radius: 8px;
                  text-align: center;
                ">
                  <h5 style="margin: 0 0 10px 0;">Card 3</h5>
                  <p style="margin: 0; opacity: 0.9;">Maintains minimum width</p>
                </div>
                <div style="
                  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
                  color: white;
                  padding: 20px;
                  border-radius: 8px;
                  text-align: center;
                ">
                  <h5 style="margin: 0 0 10px 0;">Card 4</h5>
                  <p style="margin: 0; opacity: 0.9;">Expands to fill space</p>
                </div>
              </div>
            </div>

            <!-- Grid alignment -->
            <div>
              <h4>Grid Alignment Properties</h4>
              <div style="
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                grid-template-rows: repeat(3, 100px);
                gap: 10px;
                border: 2px solid #17a2b8;
                padding: 20px;
                border-radius: 8px;
              ">
                <div style="
                  background: #e3f2fd;
                  border: 2px solid #2196f3;
                  display: flex;
                  align-items: start;
                  justify-content: start;
                  padding: 10px;
                  border-radius: 4px;
                ">
                  <span style="background: #2196f3; color: white; padding: 4px 8px; border-radius: 2px; font-size: 12px;">Start Start</span>
                </div>
                <div style="
                  background: #f3e5f5;
                  border: 2px solid #9c27b0;
                  display: flex;
                  align-items: start;
                  justify-content: center;
                  padding: 10px;
                  border-radius: 4px;
                ">
                  <span style="background: #9c27b0; color: white; padding: 4px 8px; border-radius: 2px; font-size: 12px;">Start Center</span>
                </div>
                <div style="
                  background: #e8f5e8;
                  border: 2px solid #4caf50;
                  display: flex;
                  align-items: start;
                  justify-content: end;
                  padding: 10px;
                  border-radius: 4px;
                ">
                  <span style="background: #4caf50; color: white; padding: 4px 8px; border-radius: 2px; font-size: 12px;">Start End</span>
                </div>
                <div style="
                  background: #fff3e0;
                  border: 2px solid #ff9800;
                  display: flex;
                  align-items: center;
                  justify-content: start;
                  padding: 10px;
                  border-radius: 4px;
                ">
                  <span style="background: #ff9800; color: white; padding: 4px 8px; border-radius: 2px; font-size: 12px;">Center Start</span>
                </div>
                <div style="
                  background: #fce4ec;
                  border: 2px solid #e91e63;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  padding: 10px;
                  border-radius: 4px;
                ">
                  <span style="background: #e91e63; color: white; padding: 4px 8px; border-radius: 2px; font-size: 12px;">Center Center</span>
                </div>
                <div style="
                  background: #e0f2f1;
                  border: 2px solid #009688;
                  display: flex;
                  align-items: center;
                  justify-content: end;
                  padding: 10px;
                  border-radius: 4px;
                ">
                  <span style="background: #009688; color: white; padding: 4px 8px; border-radius: 2px; font-size: 12px;">Center End</span>
                </div>
                <div style="
                  background: #efebe9;
                  border: 2px solid #795548;
                  display: flex;
                  align-items: end;
                  justify-content: start;
                  padding: 10px;
                  border-radius: 4px;
                ">
                  <span style="background: #795548; color: white; padding: 4px 8px; border-radius: 2px; font-size: 12px;">End Start</span>
                </div>
                <div style="
                  background: #f3e5f5;
                  border: 2px solid #673ab7;
                  display: flex;
                  align-items: end;
                  justify-content: center;
                  padding: 10px;
                  border-radius: 4px;
                ">
                  <span style="background: #673ab7; color: white; padding: 4px 8px; border-radius: 2px; font-size: 12px;">End Center</span>
                </div>
                <div style="
                  background: #e8eaf6;
                  border: 2px solid #3f51b5;
                  display: flex;
                  align-items: end;
                  justify-content: end;
                  padding: 10px;
                  border-radius: 4px;
                ">
                  <span style="background: #3f51b5; color: white; padding: 4px 8px; border-radius: 2px; font-size: 12px;">End End</span>
                </div>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(gridDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="css-grid-validation"]',
        'css-grid-layout-validation',
        CSS_VALIDATION_CONFIG
      );
    });

    test('Flexbox Layout Consistency @visual @css @flexbox', async ({ page }) => {
      await page.evaluate(() => {
        const flexDiv = document.createElement('div');
        flexDiv.setAttribute('data-testid', 'css-flexbox-validation');
        flexDiv.innerHTML = `
          <div style="padding: 40px;">
            <h3>CSS Flexbox Layout Validation</h3>

            <!-- Basic Flex Container -->
            <div style="margin-bottom: 40px;">
              <h4>Basic Flexbox (row direction)</h4>
              <div style="
                display: flex;
                gap: 15px;
                border: 2px solid #007bff;
                padding: 20px;
                border-radius: 8px;
              ">
                <div style="background: #e3f2fd; padding: 15px; border-radius: 4px;">Item 1</div>
                <div style="background: #f3e5f5; padding: 15px; border-radius: 4px; flex: 1;">Item 2 (flex: 1)</div>
                <div style="background: #e8f5e8; padding: 15px; border-radius: 4px;">Item 3</div>
              </div>
            </div>

            <!-- Flex Direction Variations -->
            <div style="margin-bottom: 40px;">
              <h4>Flex Direction Variations</h4>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                  <h5>Row (default)</h5>
                  <div style="
                    display: flex;
                    flex-direction: row;
                    gap: 10px;
                    border: 1px solid #28a745;
                    padding: 15px;
                    border-radius: 4px;
                    min-height: 80px;
                  ">
                    <div style="background: #d4edda; padding: 10px; border-radius: 4px;">1</div>
                    <div style="background: #d1ecf1; padding: 10px; border-radius: 4px;">2</div>
                    <div style="background: #fff3cd; padding: 10px; border-radius: 4px;">3</div>
                  </div>
                </div>
                <div>
                  <h5>Row Reverse</h5>
                  <div style="
                    display: flex;
                    flex-direction: row-reverse;
                    gap: 10px;
                    border: 1px solid #28a745;
                    padding: 15px;
                    border-radius: 4px;
                    min-height: 80px;
                  ">
                    <div style="background: #d4edda; padding: 10px; border-radius: 4px;">1</div>
                    <div style="background: #d1ecf1; padding: 10px; border-radius: 4px;">2</div>
                    <div style="background: #fff3cd; padding: 10px; border-radius: 4px;">3</div>
                  </div>
                </div>
                <div>
                  <h5>Column</h5>
                  <div style="
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                    border: 1px solid #28a745;
                    padding: 15px;
                    border-radius: 4px;
                    min-height: 120px;
                  ">
                    <div style="background: #d4edda; padding: 10px; border-radius: 4px;">1</div>
                    <div style="background: #d1ecf1; padding: 10px; border-radius: 4px;">2</div>
                    <div style="background: #fff3cd; padding: 10px; border-radius: 4px;">3</div>
                  </div>
                </div>
                <div>
                  <h5>Column Reverse</h5>
                  <div style="
                    display: flex;
                    flex-direction: column-reverse;
                    gap: 10px;
                    border: 1px solid #28a745;
                    padding: 15px;
                    border-radius: 4px;
                    min-height: 120px;
                  ">
                    <div style="background: #d4edda; padding: 10px; border-radius: 4px;">1</div>
                    <div style="background: #d1ecf1; padding: 10px; border-radius: 4px;">2</div>
                    <div style="background: #fff3cd; padding: 10px; border-radius: 4px;">3</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Justify Content Options -->
            <div style="margin-bottom: 40px;">
              <h4>Justify Content (main axis alignment)</h4>
              <div style="display: flex; flex-direction: column; gap: 15px;">
                <div>
                  <h6>flex-start (default)</h6>
                  <div style="
                    display: flex;
                    justify-content: flex-start;
                    border: 1px solid #ffc107;
                    padding: 10px;
                    border-radius: 4px;
                    min-height: 60px;
                    background: #fffbf0;
                  ">
                    <div style="background: #ffc107; color: #212529; padding: 8px 12px; border-radius: 4px; margin-right: 5px;">A</div>
                    <div style="background: #fd7e14; color: white; padding: 8px 12px; border-radius: 4px; margin-right: 5px;">B</div>
                    <div style="background: #dc3545; color: white; padding: 8px 12px; border-radius: 4px;">C</div>
                  </div>
                </div>
                <div>
                  <h6>center</h6>
                  <div style="
                    display: flex;
                    justify-content: center;
                    border: 1px solid #ffc107;
                    padding: 10px;
                    border-radius: 4px;
                    min-height: 60px;
                    background: #fffbf0;
                  ">
                    <div style="background: #ffc107; color: #212529; padding: 8px 12px; border-radius: 4px; margin-right: 5px;">A</div>
                    <div style="background: #fd7e14; color: white; padding: 8px 12px; border-radius: 4px; margin-right: 5px;">B</div>
                    <div style="background: #dc3545; color: white; padding: 8px 12px; border-radius: 4px;">C</div>
                  </div>
                </div>
                <div>
                  <h6>space-between</h6>
                  <div style="
                    display: flex;
                    justify-content: space-between;
                    border: 1px solid #ffc107;
                    padding: 10px;
                    border-radius: 4px;
                    min-height: 60px;
                    background: #fffbf0;
                  ">
                    <div style="background: #ffc107; color: #212529; padding: 8px 12px; border-radius: 4px;">A</div>
                    <div style="background: #fd7e14; color: white; padding: 8px 12px; border-radius: 4px;">B</div>
                    <div style="background: #dc3545; color: white; padding: 8px 12px; border-radius: 4px;">C</div>
                  </div>
                </div>
                <div>
                  <h6>space-around</h6>
                  <div style="
                    display: flex;
                    justify-content: space-around;
                    border: 1px solid #ffc107;
                    padding: 10px;
                    border-radius: 4px;
                    min-height: 60px;
                    background: #fffbf0;
                  ">
                    <div style="background: #ffc107; color: #212529; padding: 8px 12px; border-radius: 4px;">A</div>
                    <div style="background: #fd7e14; color: white; padding: 8px 12px; border-radius: 4px;">B</div>
                    <div style="background: #dc3545; color: white; padding: 8px 12px; border-radius: 4px;">C</div>
                  </div>
                </div>
                <div>
                  <h6>space-evenly</h6>
                  <div style="
                    display: flex;
                    justify-content: space-evenly;
                    border: 1px solid #ffc107;
                    padding: 10px;
                    border-radius: 4px;
                    min-height: 60px;
                    background: #fffbf0;
                  ">
                    <div style="background: #ffc107; color: #212529; padding: 8px 12px; border-radius: 4px;">A</div>
                    <div style="background: #fd7e14; color: white; padding: 8px 12px; border-radius: 4px;">B</div>
                    <div style="background: #dc3545; color: white; padding: 8px 12px; border-radius: 4px;">C</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Align Items Options -->
            <div style="margin-bottom: 40px;">
              <h4>Align Items (cross axis alignment)</h4>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                  <h6>flex-start</h6>
                  <div style="
                    display: flex;
                    align-items: flex-start;
                    border: 1px solid #17a2b8;
                    padding: 15px;
                    border-radius: 4px;
                    height: 120px;
                    background: #e7f6fd;
                  ">
                    <div style="background: #17a2b8; color: white; padding: 10px; border-radius: 4px; margin-right: 10px;">Short</div>
                    <div style="background: #20c997; color: white; padding: 20px 10px; border-radius: 4px; margin-right: 10px;">Medium<br>Height</div>
                    <div style="background: #6f42c1; color: white; padding: 30px 10px; border-radius: 4px;">Tall<br>Content<br>Here</div>
                  </div>
                </div>
                <div>
                  <h6>center</h6>
                  <div style="
                    display: flex;
                    align-items: center;
                    border: 1px solid #17a2b8;
                    padding: 15px;
                    border-radius: 4px;
                    height: 120px;
                    background: #e7f6fd;
                  ">
                    <div style="background: #17a2b8; color: white; padding: 10px; border-radius: 4px; margin-right: 10px;">Short</div>
                    <div style="background: #20c997; color: white; padding: 20px 10px; border-radius: 4px; margin-right: 10px;">Medium<br>Height</div>
                    <div style="background: #6f42c1; color: white; padding: 30px 10px; border-radius: 4px;">Tall<br>Content<br>Here</div>
                  </div>
                </div>
                <div>
                  <h6>flex-end</h6>
                  <div style="
                    display: flex;
                    align-items: flex-end;
                    border: 1px solid #17a2b8;
                    padding: 15px;
                    border-radius: 4px;
                    height: 120px;
                    background: #e7f6fd;
                  ">
                    <div style="background: #17a2b8; color: white; padding: 10px; border-radius: 4px; margin-right: 10px;">Short</div>
                    <div style="background: #20c997; color: white; padding: 20px 10px; border-radius: 4px; margin-right: 10px;">Medium<br>Height</div>
                    <div style="background: #6f42c1; color: white; padding: 30px 10px; border-radius: 4px;">Tall<br>Content<br>Here</div>
                  </div>
                </div>
                <div>
                  <h6>stretch (default)</h6>
                  <div style="
                    display: flex;
                    align-items: stretch;
                    border: 1px solid #17a2b8;
                    padding: 15px;
                    border-radius: 4px;
                    height: 120px;
                    background: #e7f6fd;
                  ">
                    <div style="background: #17a2b8; color: white; padding: 10px; border-radius: 4px; margin-right: 10px; display: flex; align-items: center;">Short</div>
                    <div style="background: #20c997; color: white; padding: 10px; border-radius: 4px; margin-right: 10px; display: flex; align-items: center;">Medium</div>
                    <div style="background: #6f42c1; color: white; padding: 10px; border-radius: 4px; display: flex; align-items: center;">Stretched</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Flex Wrap -->
            <div>
              <h4>Flex Wrap Behavior</h4>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                  <h6>nowrap (default)</h6>
                  <div style="
                    display: flex;
                    flex-wrap: nowrap;
                    border: 1px solid #dc3545;
                    padding: 15px;
                    border-radius: 4px;
                    background: #fef5f5;
                    overflow: auto;
                  ">
                    <div style="background: #dc3545; color: white; padding: 10px; border-radius: 4px; margin-right: 10px; min-width: 100px;">Item 1</div>
                    <div style="background: #fd7e14; color: white; padding: 10px; border-radius: 4px; margin-right: 10px; min-width: 100px;">Item 2</div>
                    <div style="background: #ffc107; color: #212529; padding: 10px; border-radius: 4px; margin-right: 10px; min-width: 100px;">Item 3</div>
                    <div style="background: #28a745; color: white; padding: 10px; border-radius: 4px; margin-right: 10px; min-width: 100px;">Item 4</div>
                    <div style="background: #17a2b8; color: white; padding: 10px; border-radius: 4px; min-width: 100px;">Item 5</div>
                  </div>
                </div>
                <div>
                  <h6>wrap</h6>
                  <div style="
                    display: flex;
                    flex-wrap: wrap;
                    border: 1px solid #dc3545;
                    padding: 15px;
                    border-radius: 4px;
                    background: #fef5f5;
                  ">
                    <div style="background: #dc3545; color: white; padding: 10px; border-radius: 4px; margin-right: 10px; margin-bottom: 10px; min-width: 100px;">Item 1</div>
                    <div style="background: #fd7e14; color: white; padding: 10px; border-radius: 4px; margin-right: 10px; margin-bottom: 10px; min-width: 100px;">Item 2</div>
                    <div style="background: #ffc107; color: #212529; padding: 10px; border-radius: 4px; margin-right: 10px; margin-bottom: 10px; min-width: 100px;">Item 3</div>
                    <div style="background: #28a745; color: white; padding: 10px; border-radius: 4px; margin-right: 10px; margin-bottom: 10px; min-width: 100px;">Item 4</div>
                    <div style="background: #17a2b8; color: white; padding: 10px; border-radius: 4px; margin-bottom: 10px; min-width: 100px;">Item 5</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(flexDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="css-flexbox-validation"]',
        'css-flexbox-layout-validation',
        CSS_VALIDATION_CONFIG
      );
    });
  });

  test.describe('Typography and Font Rendering', () => {

    test('Font Stack and Typography Consistency @visual @css @typography', async ({ page }) => {
      await page.evaluate(() => {
        const typoDiv = document.createElement('div');
        typoDiv.setAttribute('data-testid', 'typography-consistency');
        typoDiv.innerHTML = `
          <div style="padding: 40px;">
            <h3>Typography and Font Rendering Consistency</h3>

            <!-- Font Stack Testing -->
            <div style="margin-bottom: 40px;">
              <h4>System Font Stacks</h4>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                <div>
                  <h5>System UI Font Stack</h5>
                  <div style="
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
                    border: 1px solid #dee2e6;
                    padding: 20px;
                    border-radius: 8px;
                    background: #f8f9fa;
                  ">
                    <p style="margin: 0 0 10px 0; font-size: 16px; font-weight: 400;">
                      The quick brown fox jumps over the lazy dog. 0123456789
                    </p>
                    <p style="margin: 0 0 10px 0; font-size: 16px; font-weight: 600;">
                      <strong>Bold:</strong> The quick brown fox jumps over the lazy dog.
                    </p>
                    <p style="margin: 0 0 10px 0; font-size: 16px; font-style: italic;">
                      <em>Italic:</em> The quick brown fox jumps over the lazy dog.
                    </p>
                    <p style="margin: 0; font-size: 14px; color: #6c757d;">
                      Font Family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto'...
                    </p>
                  </div>
                </div>

                <div>
                  <h5>Monospace Font Stack</h5>
                  <div style="
                    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
                    border: 1px solid #dee2e6;
                    padding: 20px;
                    border-radius: 8px;
                    background: #f8f9fa;
                  ">
                    <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: 400;">
                      The quick brown fox jumps over the lazy dog. 0123456789
                    </p>
                    <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: 600;">
                      <strong>Bold:</strong> function example() { return true; }
                    </p>
                    <p style="margin: 0 0 10px 0; font-size: 14px;">
                      Code Example: <code style="background: #e9ecef; padding: 2px 4px; border-radius: 2px;">console.log('Hello, World!');</code>
                    </p>
                    <p style="margin: 0; font-size: 12px; color: #6c757d;">
                      Font Family: 'SFMono-Regular', Consolas, 'Liberation Mono'...
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Typography Scale -->
            <div style="margin-bottom: 40px;">
              <h4>Typography Scale and Hierarchy</h4>
              <div style="border: 1px solid #007bff; padding: 30px; border-radius: 8px; background: #ffffff;">
                <h1 style="margin: 0 0 16px 0; font-size: 2.5rem; font-weight: 600; line-height: 1.2; color: #212529;">
                  Heading 1 (h1) - 2.5rem / 40px
                </h1>
                <h2 style="margin: 0 0 14px 0; font-size: 2rem; font-weight: 600; line-height: 1.25; color: #212529;">
                  Heading 2 (h2) - 2rem / 32px
                </h2>
                <h3 style="margin: 0 0 12px 0; font-size: 1.75rem; font-weight: 600; line-height: 1.3; color: #212529;">
                  Heading 3 (h3) - 1.75rem / 28px
                </h3>
                <h4 style="margin: 0 0 10px 0; font-size: 1.5rem; font-weight: 600; line-height: 1.35; color: #212529;">
                  Heading 4 (h4) - 1.5rem / 24px
                </h4>
                <h5 style="margin: 0 0 8px 0; font-size: 1.25rem; font-weight: 600; line-height: 1.4; color: #212529;">
                  Heading 5 (h5) - 1.25rem / 20px
                </h5>
                <h6 style="margin: 0 0 16px 0; font-size: 1rem; font-weight: 600; line-height: 1.45; color: #212529;">
                  Heading 6 (h6) - 1rem / 16px
                </h6>

                <p style="margin: 0 0 16px 0; font-size: 1rem; line-height: 1.5; color: #212529;">
                  <strong>Body text (normal):</strong> This is the standard body text used throughout the application. It should be highly readable and maintain good contrast ratios. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                </p>

                <p style="margin: 0 0 16px 0; font-size: 1.125rem; line-height: 1.5; color: #212529;">
                  <strong>Large body text:</strong> This slightly larger text is used for introductory paragraphs or important content that needs emphasis. It maintains readability while drawing attention.
                </p>

                <p style="margin: 0 0 16px 0; font-size: 0.875rem; line-height: 1.4; color: #6c757d;">
                  <strong>Small text:</strong> This smaller text is used for captions, footnotes, and supplementary information. It should still maintain readability while being clearly secondary to the main content.
                </p>

                <p style="margin: 0; font-size: 0.75rem; line-height: 1.3; color: #6c757d;">
                  <strong>Extra small text:</strong> Used for metadata, timestamps, and fine print. This is the minimum readable size for the application.
                </p>
              </div>
            </div>

            <!-- Text Formatting and Styling -->
            <div style="margin-bottom: 40px;">
              <h4>Text Formatting and Styling</h4>
              <div style="border: 1px solid #28a745; padding: 25px; border-radius: 8px; background: #f8fff9;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 30px;">
                  <div>
                    <h5>Text Emphasis</h5>
                    <p style="margin-bottom: 15px;">
                      This paragraph contains <strong>bold text</strong>, <em>italic text</em>,
                      <u>underlined text</u>, and <mark style="background: #fff3cd; padding: 2px 4px;">highlighted text</mark>.
                    </p>
                    <p style="margin-bottom: 15px;">
                      <small>This is small text</small> and this is
                      <span style="font-size: 1.125rem;">slightly larger text</span> for comparison.
                    </p>
                    <p style="margin-bottom: 15px;">
                      Text can be <span style="text-decoration: line-through;">struck through</span>,
                      <sup>superscript</sup>, or <sub>subscript</sub>.
                    </p>
                  </div>

                  <div>
                    <h5>Code and Technical Text</h5>
                    <p style="margin-bottom: 15px;">
                      Inline code: <code style="
                        background: #f8f9fa;
                        color: #e83e8c;
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: 'SFMono-Regular', Consolas, monospace;
                        font-size: 0.875em;
                      ">console.log('Hello');</code>
                    </p>
                    <pre style="
                      background: #f8f9fa;
                      color: #212529;
                      padding: 15px;
                      border-radius: 4px;
                      border: 1px solid #e9ecef;
                      font-family: 'SFMono-Regular', Consolas, monospace;
                      font-size: 0.875rem;
                      line-height: 1.4;
                      overflow-x: auto;
                      margin: 15px 0;
                    ">function example() {
  return {
    message: 'Hello, World!',
    timestamp: new Date()
  };
}</pre>
                    <p style="margin: 0;">
                      Variable name: <var style="font-style: italic; color: #6f42c1;">userName</var><br>
                      Keyboard input: <kbd style="
                        background: #212529;
                        color: #fff;
                        padding: 2px 4px;
                        border-radius: 3px;
                        font-family: monospace;
                        font-size: 0.875em;
                      ">Ctrl+C</kbd>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Link Styles and States -->
            <div>
              <h4>Link Styles and States</h4>
              <div style="border: 1px solid #ffc107; padding: 25px; border-radius: 8px; background: #fffbf0;">
                <div style="display: flex; flex-wrap: wrap; gap: 30px; align-items: start;">
                  <div>
                    <h5>Standard Links</h5>
                    <p style="margin-bottom: 10px;">
                      <a href="#" style="color: #007bff; text-decoration: underline;">Default link</a>
                    </p>
                    <p style="margin-bottom: 10px;">
                      <a href="#" style="color: #6f42c1; text-decoration: underline;">Visited link (simulated)</a>
                    </p>
                    <p style="margin-bottom: 10px;">
                      <a href="#" style="color: #007bff; text-decoration: none; background: #e7f3ff; padding: 4px 8px; border-radius: 4px;">Link with background</a>
                    </p>
                    <p style="margin: 0;">
                      <a href="#" style="color: #28a745; text-decoration: none; border-bottom: 2px solid #28a745;">Link with border</a>
                    </p>
                  </div>

                  <div>
                    <h5>Button-style Links</h5>
                    <p style="margin-bottom: 10px;">
                      <a href="#" style="
                        display: inline-block;
                        background: #007bff;
                        color: white;
                        text-decoration: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: 500;
                      ">Primary Link Button</a>
                    </p>
                    <p style="margin-bottom: 10px;">
                      <a href="#" style="
                        display: inline-block;
                        background: transparent;
                        color: #007bff;
                        text-decoration: none;
                        padding: 8px 16px;
                        border: 1px solid #007bff;
                        border-radius: 4px;
                        font-weight: 500;
                      ">Secondary Link Button</a>
                    </p>
                    <p style="margin: 0;">
                      <a href="#" style="
                        display: inline-block;
                        background: #f8f9fa;
                        color: #6c757d;
                        text-decoration: none;
                        padding: 8px 16px;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        font-weight: 500;
                        cursor: not-allowed;
                        opacity: 0.6;
                      ">Disabled Link Button</a>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(typoDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="typography-consistency"]',
        'typography-font-consistency',
        CSS_VALIDATION_CONFIG
      );
    });

    test('Line Height and Text Spacing @visual @css @spacing', async ({ page }) => {
      await page.evaluate(() => {
        const spacingDiv = document.createElement('div');
        spacingDiv.setAttribute('data-testid', 'text-spacing-validation');
        spacingDiv.innerHTML = `
          <div style="padding: 40px;">
            <h3>Line Height and Text Spacing Validation</h3>

            <!-- Line Height Variations -->
            <div style="margin-bottom: 40px;">
              <h4>Line Height Variations</h4>
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
                <div style="border: 1px solid #007bff; padding: 20px; border-radius: 8px;">
                  <h5>line-height: 1.2 (Tight)</h5>
                  <p style="line-height: 1.2; margin: 0; background: #e7f3ff; padding: 10px; border-radius: 4px;">
                    This paragraph has a tight line height of 1.2. Notice how the lines are closer together, which can be useful for headings but may reduce readability for body text. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                  </p>
                </div>

                <div style="border: 1px solid #28a745; padding: 20px; border-radius: 8px;">
                  <h5>line-height: 1.5 (Standard)</h5>
                  <p style="line-height: 1.5; margin: 0; background: #e8f5e8; padding: 10px; border-radius: 4px;">
                    This paragraph has the standard line height of 1.5, which is generally recommended for body text as it provides good readability and comfortable reading experience. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                  </p>
                </div>

                <div style="border: 1px solid #ffc107; padding: 20px; border-radius: 8px;">
                  <h5>line-height: 1.8 (Loose)</h5>
                  <p style="line-height: 1.8; margin: 0; background: #fffbf0; padding: 10px; border-radius: 4px;">
                    This paragraph has a loose line height of 1.8. While this provides excellent readability and accessibility, it may consume more vertical space. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
                  </p>
                </div>
              </div>
            </div>

            <!-- Paragraph Spacing -->
            <div style="margin-bottom: 40px;">
              <h4>Paragraph and Element Spacing</h4>
              <div style="border: 1px solid #17a2b8; padding: 25px; border-radius: 8px; background: #e7f6fd;">
                <h5 style="margin-top: 0; margin-bottom: 16px;">Heading with Standard Spacing</h5>
                <p style="margin-bottom: 16px; line-height: 1.5;">
                  This is the first paragraph with standard bottom margin. It demonstrates proper spacing between paragraphs to maintain readability and visual hierarchy. The margin-bottom creates clear separation.
                </p>
                <p style="margin-bottom: 16px; line-height: 1.5;">
                  This is the second paragraph, showing consistent spacing. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                </p>
                <ul style="margin-bottom: 16px; line-height: 1.5; padding-left: 20px;">
                  <li style="margin-bottom: 8px;">List item with proper spacing</li>
                  <li style="margin-bottom: 8px;">Another list item with consistent spacing</li>
                  <li style="margin-bottom: 0;">Final list item (no bottom margin)</li>
                </ul>
                <p style="margin-bottom: 0; line-height: 1.5;">
                  Final paragraph with no bottom margin to prevent extra space at container end.
                </p>
              </div>
            </div>

            <!-- Letter and Word Spacing -->
            <div style="margin-bottom: 40px;">
              <h4>Letter and Word Spacing</h4>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px;">
                <div style="border: 1px solid #dc3545; padding: 20px; border-radius: 8px;">
                  <h5>Letter Spacing Variations</h5>
                  <div style="display: flex; flex-direction: column; gap: 15px;">
                    <p style="letter-spacing: -0.5px; margin: 0; background: #fef5f5; padding: 10px; border-radius: 4px;">
                      <strong>Tight (-0.5px):</strong> Condensed letter spacing
                    </p>
                    <p style="letter-spacing: 0; margin: 0; background: #fef5f5; padding: 10px; border-radius: 4px;">
                      <strong>Normal (0):</strong> Standard letter spacing
                    </p>
                    <p style="letter-spacing: 0.5px; margin: 0; background: #fef5f5; padding: 10px; border-radius: 4px;">
                      <strong>Loose (0.5px):</strong> Expanded letter spacing
                    </p>
                    <p style="letter-spacing: 2px; margin: 0; background: #fef5f5; padding: 10px; border-radius: 4px; text-transform: uppercase; font-size: 0.875rem;">
                      <strong>Wide (2px):</strong> S P A C E D   O U T
                    </p>
                  </div>
                </div>

                <div style="border: 1px solid #6f42c1; padding: 20px; border-radius: 8px;">
                  <h5>Word Spacing Variations</h5>
                  <div style="display: flex; flex-direction: column; gap: 15px;">
                    <p style="word-spacing: -2px; margin: 0; background: #f8f7ff; padding: 10px; border-radius: 4px;">
                      <strong>Tight (-2px):</strong> Words are closer together in this example
                    </p>
                    <p style="word-spacing: 0; margin: 0; background: #f8f7ff; padding: 10px; border-radius: 4px;">
                      <strong>Normal (0):</strong> Standard word spacing for comfortable reading
                    </p>
                    <p style="word-spacing: 3px; margin: 0; background: #f8f7ff; padding: 10px; border-radius: 4px;">
                      <strong>Loose (3px):</strong> Words have more space between them
                    </p>
                    <p style="word-spacing: 8px; margin: 0; background: #f8f7ff; padding: 10px; border-radius: 4px;">
                      <strong>Wide (8px):</strong> Very spaced out words for emphasis
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Text Alignment -->
            <div>
              <h4>Text Alignment and Justification</h4>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px;">
                <div style="border: 1px solid #fd7e14; padding: 20px; border-radius: 8px;">
                  <h5 style="text-align: left; margin-top: 0;">Left Aligned (Default)</h5>
                  <p style="text-align: left; margin-bottom: 15px; line-height: 1.5; background: #fff4e6; padding: 10px; border-radius: 4px;">
                    This paragraph is left-aligned, which is the default and most common alignment for reading. It provides a consistent left edge that guides the eye from line to line.
                  </p>

                  <h5 style="text-align: center;">Center Aligned</h5>
                  <p style="text-align: center; margin-bottom: 15px; line-height: 1.5; background: #fff4e6; padding: 10px; border-radius: 4px;">
                    This paragraph is center-aligned, which is often used for headings, poetry, or short announcements but can be harder to read for longer text.
                  </p>

                  <h5 style="text-align: right;">Right Aligned</h5>
                  <p style="text-align: right; margin-bottom: 0; line-height: 1.5; background: #fff4e6; padding: 10px; border-radius: 4px;">
                    This paragraph is right-aligned, which is uncommon in English but might be used for specific design purposes or in languages that read right-to-left.
                  </p>
                </div>

                <div style="border: 1px solid #20c997; padding: 20px; border-radius: 8px;">
                  <h5 style="margin-top: 0;">Justified Text</h5>
                  <p style="text-align: justify; margin-bottom: 15px; line-height: 1.6; background: #e6fdf5; padding: 15px; border-radius: 4px;">
                    This paragraph is justified, meaning the text is aligned to both the left and right margins. The spacing between words is adjusted to achieve this alignment. While this can create a clean, formal appearance, it may sometimes result in irregular word spacing that can affect readability, especially in narrow columns or with certain fonts.
                  </p>

                  <h5>Text with Hyphenation</h5>
                  <p style="
                    text-align: justify;
                    margin-bottom: 0;
                    line-height: 1.6;
                    background: #e6fdf5;
                    padding: 15px;
                    border-radius: 4px;
                    hyphens: auto;
                    -webkit-hyphens: auto;
                    -ms-hyphens: auto;
                  ">
                    This paragraph demonstrates automatic hyphenation in justified text. Words that would otherwise create large gaps are hyphen-ated at appropriate syllable breaks, resulting in more even word spacing and better overall text appearance.
                  </p>
                </div>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(spacingDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="text-spacing-validation"]',
        'text-spacing-validation',
        CSS_VALIDATION_CONFIG
      );
    });
  });

  test.describe('CSS Performance and Layout Metrics', () => {

    test('Layout Stability and CLS Assessment @visual @css @performance', async ({ page }) => {
      // Monitor layout shifts during page interactions
      await page.evaluate(() => {
        // Create performance monitoring test
        const perfDiv = document.createElement('div');
        perfDiv.setAttribute('data-testid', 'layout-stability-test');
        perfDiv.innerHTML = `
          <div style="padding: 40px;">
            <h3>Layout Stability Assessment</h3>
            <p style="color: #6c757d; margin-bottom: 30px;">
              This test evaluates layout stability and measures cumulative layout shift (CLS)
            </p>

            <!-- Stable Layout Section -->
            <div style="margin-bottom: 40px;">
              <h4>Stable Layout (Good)</h4>
              <div style="border: 2px solid #28a745; border-radius: 8px; padding: 20px; background: #f8fff9;">
                <div style="display: grid; grid-template-columns: 200px 1fr; gap: 20px; align-items: start;">
                  <div style="background: #e8f5e8; padding: 15px; border-radius: 4px; min-height: 150px;">
                    <h5 style="margin: 0 0 10px 0;">Fixed Sidebar</h5>
                    <p style="margin: 0; font-size: 14px; line-height: 1.4;">
                      This sidebar has fixed dimensions and won't cause layout shifts when content loads.
                    </p>
                  </div>
                  <div style="background: #ffffff; border: 1px solid #c3e6cb; padding: 20px; border-radius: 4px;">
                    <h5 style="margin: 0 0 15px 0;">Stable Content Area</h5>
                    <div style="height: 100px; background: #d4edda; border-radius: 4px; margin-bottom: 15px; display: flex; align-items: center; justify-content: center;">
                      Reserved Space for Image/Content
                    </div>
                    <p style="margin: 0; line-height: 1.5;">
                      Content has reserved space and proper dimensions to prevent layout shifts during loading.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Dynamic Loading Section -->
            <div style="margin-bottom: 40px;">
              <h4>Dynamic Content Loading</h4>
              <div id="dynamic-content" style="border: 2px solid #ffc107; border-radius: 8px; padding: 20px; background: #fffbf0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                  <h5 style="margin: 0;">Loading Content Test</h5>
                  <button onclick="loadDynamicContent()" style="
                    background: #ffc107;
                    border: none;
                    color: #212529;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-weight: 500;
                  ">Load Content</button>
                </div>
                <div id="content-placeholder" style="
                  min-height: 100px;
                  background: #fff8e1;
                  border: 2px dashed #ffb300;
                  border-radius: 4px;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  color: #bf8900;
                ">
                  Click "Load Content" to test dynamic loading
                </div>
              </div>
            </div>

            <!-- Responsive Image Section -->
            <div style="margin-bottom: 40px;">
              <h4>Image Loading Behavior</h4>
              <div style="border: 2px solid #17a2b8; border-radius: 8px; padding: 20px; background: #e7f6fd;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                  <div>
                    <h6>With Aspect Ratio Preservation</h6>
                    <div style="
                      width: 100%;
                      aspect-ratio: 16/9;
                      background: linear-gradient(45deg, #17a2b8, #20c997);
                      border-radius: 4px;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      color: white;
                      font-weight: 500;
                      margin-bottom: 10px;
                    ">
                      Image Placeholder (16:9)
                    </div>
                    <p style="margin: 0; font-size: 12px; color: #0c5460;">
                      Uses aspect-ratio property to prevent layout shift
                    </p>
                  </div>
                  <div>
                    <h6>With Fixed Dimensions</h6>
                    <div style="
                      width: 100%;
                      height: 150px;
                      background: linear-gradient(135deg, #6f42c1, #e83e8c);
                      border-radius: 4px;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      color: white;
                      font-weight: 500;
                      margin-bottom: 10px;
                    ">
                      Fixed Height Image
                    </div>
                    <p style="margin: 0; font-size: 12px; color: #0c5460;">
                      Uses fixed height to maintain layout stability
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Performance Metrics Display -->
            <div>
              <h4>Layout Performance Metrics</h4>
              <div style="border: 2px solid #dc3545; border-radius: 8px; padding: 20px; background: #fef5f5;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                  <div style="background: #ffffff; border: 1px solid #f1aeb5; padding: 15px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #dc3545; margin-bottom: 5px;" id="cls-score">0.000</div>
                    <div style="font-size: 12px; color: #721c24; font-weight: 500;">Cumulative Layout Shift</div>
                    <div style="font-size: 10px; color: #6c757d; margin-top: 2px;">< 0.1 Good, < 0.25 Needs Improvement</div>
                  </div>
                  <div style="background: #ffffff; border: 1px solid #f1aeb5; padding: 15px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #dc3545; margin-bottom: 5px;" id="lcp-score">0ms</div>
                    <div style="font-size: 12px; color: #721c24; font-weight: 500;">Largest Contentful Paint</div>
                    <div style="font-size: 10px; color: #6c757d; margin-top: 2px;">< 2.5s Good, < 4s Needs Improvement</div>
                  </div>
                  <div style="background: #ffffff; border: 1px solid #f1aeb5; padding: 15px; border-radius: 4px; text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #dc3545; margin-bottom: 5px;" id="fcp-score">0ms</div>
                    <div style="font-size: 12px; color: #721c24; font-weight: 500;">First Contentful Paint</div>
                    <div style="font-size: 10px; color: #6c757d; margin-top: 2px;">< 1.8s Good, < 3s Needs Improvement</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <script>
            // Layout shift monitoring
            let clsScore = 0;

            // Performance observer for CLS
            if ('LayoutShift' in window) {
              new PerformanceObserver(function(entries) {
                for (const entry of entries.getEntries()) {
                  if (!entry.hadRecentInput) {
                    clsScore += entry.value;
                    document.getElementById('cls-score').textContent = clsScore.toFixed(3);
                  }
                }
              }).observe({type: 'layout-shift', buffered: true});
            }

            // Performance observer for paint metrics
            new PerformanceObserver(function(entries) {
              for (const entry of entries.getEntries()) {
                if (entry.name === 'first-contentful-paint') {
                  document.getElementById('fcp-score').textContent = Math.round(entry.startTime) + 'ms';
                }
                if (entry.name === 'largest-contentful-paint') {
                  document.getElementById('lcp-score').textContent = Math.round(entry.startTime) + 'ms';
                }
              }
            }).observe({type: 'paint', buffered: true});

            // Dynamic content loading function
            function loadDynamicContent() {
              const placeholder = document.getElementById('content-placeholder');
              placeholder.innerHTML = \`
                <div style="width: 100%; padding: 20px;">
                  <h6 style="margin: 0 0 10px 0; color: #bf8900;">Content Loaded Successfully!</h6>
                  <p style="margin: 0 0 15px 0; line-height: 1.4; color: #856404;">
                    This content was loaded dynamically but maintained the reserved space to prevent layout shift.
                  </p>
                  <div style="display: flex; gap: 10px;">
                    <div style="flex: 1; background: #fff3cd; padding: 10px; border-radius: 4px; font-size: 14px;">Item 1</div>
                    <div style="flex: 1; background: #fff3cd; padding: 10px; border-radius: 4px; font-size: 14px;">Item 2</div>
                    <div style="flex: 1; background: #fff3cd; padding: 10px; border-radius: 4px; font-size: 14px;">Item 3</div>
                  </div>
                </div>
              \`;
            }
          </script>
        `;
        document.body.appendChild(perfDiv);
      });

      // Take initial screenshot
      await visualUtils.screenshotComponent(
        '[data-testid="layout-stability-test"]',
        'layout-stability-initial',
        CSS_VALIDATION_CONFIG
      );

      // Trigger dynamic content loading
      await page.click('button');
      await page.waitForTimeout(500);

      // Take screenshot after dynamic loading
      await visualUtils.screenshotComponent(
        '[data-testid="layout-stability-test"]',
        'layout-stability-after-loading',
        CSS_VALIDATION_CONFIG
      );
    });

    test('CSS Custom Properties and Variables @visual @css @variables', async ({ page }) => {
      await page.evaluate(() => {
        const variablesDiv = document.createElement('div');
        variablesDiv.setAttribute('data-testid', 'css-variables-test');
        variablesDiv.innerHTML = `
          <div style="
            padding: 40px;
            --primary-color: #007bff;
            --secondary-color: #6c757d;
            --success-color: #28a745;
            --danger-color: #dc3545;
            --warning-color: #ffc107;
            --info-color: #17a2b8;

            --primary-rgb: 0, 123, 255;
            --secondary-rgb: 108, 117, 125;

            --font-size-sm: 0.875rem;
            --font-size-base: 1rem;
            --font-size-lg: 1.125rem;
            --font-size-xl: 1.25rem;

            --spacing-xs: 0.25rem;
            --spacing-sm: 0.5rem;
            --spacing-md: 1rem;
            --spacing-lg: 1.5rem;
            --spacing-xl: 3rem;

            --border-radius-sm: 0.25rem;
            --border-radius: 0.5rem;
            --border-radius-lg: 0.75rem;

            --shadow-sm: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
            --shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
            --shadow-lg: 0 1rem 3rem rgba(0, 0, 0, 0.175);
          ">
            <h3>CSS Custom Properties and Variables</h3>

            <!-- Color Variables -->
            <div style="margin-bottom: var(--spacing-xl);">
              <h4>Color System Variables</h4>
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: var(--spacing-md);">
                <div style="
                  background: var(--primary-color);
                  color: white;
                  padding: var(--spacing-lg);
                  border-radius: var(--border-radius);
                  text-align: center;
                  box-shadow: var(--shadow-sm);
                ">
                  <strong>Primary</strong><br>
                  <small>var(--primary-color)</small>
                </div>
                <div style="
                  background: var(--secondary-color);
                  color: white;
                  padding: var(--spacing-lg);
                  border-radius: var(--border-radius);
                  text-align: center;
                  box-shadow: var(--shadow-sm);
                ">
                  <strong>Secondary</strong><br>
                  <small>var(--secondary-color)</small>
                </div>
                <div style="
                  background: var(--success-color);
                  color: white;
                  padding: var(--spacing-lg);
                  border-radius: var(--border-radius);
                  text-align: center;
                  box-shadow: var(--shadow-sm);
                ">
                  <strong>Success</strong><br>
                  <small>var(--success-color)</small>
                </div>
                <div style="
                  background: var(--danger-color);
                  color: white;
                  padding: var(--spacing-lg);
                  border-radius: var(--border-radius);
                  text-align: center;
                  box-shadow: var(--shadow-sm);
                ">
                  <strong>Danger</strong><br>
                  <small>var(--danger-color)</small>
                </div>
                <div style="
                  background: var(--warning-color);
                  color: #212529;
                  padding: var(--spacing-lg);
                  border-radius: var(--border-radius);
                  text-align: center;
                  box-shadow: var(--shadow-sm);
                ">
                  <strong>Warning</strong><br>
                  <small>var(--warning-color)</small>
                </div>
                <div style="
                  background: var(--info-color);
                  color: white;
                  padding: var(--spacing-lg);
                  border-radius: var(--border-radius);
                  text-align: center;
                  box-shadow: var(--shadow-sm);
                ">
                  <strong>Info</strong><br>
                  <small>var(--info-color)</small>
                </div>
              </div>
            </div>

            <!-- Alpha/Opacity Variables -->
            <div style="margin-bottom: var(--spacing-xl);">
              <h4>Color with Alpha Variables</h4>
              <div style="display: flex; flex-wrap: wrap; gap: var(--spacing-md);">
                <div style="
                  background: rgba(var(--primary-rgb), 0.1);
                  color: var(--primary-color);
                  padding: var(--spacing-md);
                  border-radius: var(--border-radius);
                  border: 1px solid rgba(var(--primary-rgb), 0.3);
                ">
                  <strong>Primary 10%</strong><br>
                  <small>rgba(var(--primary-rgb), 0.1)</small>
                </div>
                <div style="
                  background: rgba(var(--primary-rgb), 0.25);
                  color: var(--primary-color);
                  padding: var(--spacing-md);
                  border-radius: var(--border-radius);
                  border: 1px solid rgba(var(--primary-rgb), 0.5);
                ">
                  <strong>Primary 25%</strong><br>
                  <small>rgba(var(--primary-rgb), 0.25)</small>
                </div>
                <div style="
                  background: rgba(var(--primary-rgb), 0.5);
                  color: white;
                  padding: var(--spacing-md);
                  border-radius: var(--border-radius);
                ">
                  <strong>Primary 50%</strong><br>
                  <small>rgba(var(--primary-rgb), 0.5)</small>
                </div>
                <div style="
                  background: rgba(var(--primary-rgb), 0.75);
                  color: white;
                  padding: var(--spacing-md);
                  border-radius: var(--border-radius);
                ">
                  <strong>Primary 75%</strong><br>
                  <small>rgba(var(--primary-rgb), 0.75)</small>
                </div>
              </div>
            </div>

            <!-- Typography Variables -->
            <div style="margin-bottom: var(--spacing-xl);">
              <h4>Typography Variables</h4>
              <div style="
                border: 1px solid rgba(var(--secondary-rgb), 0.3);
                border-radius: var(--border-radius-lg);
                padding: var(--spacing-lg);
                background: rgba(var(--secondary-rgb), 0.05);
              ">
                <p style="font-size: var(--font-size-xl); margin-bottom: var(--spacing-sm);">
                  <strong>Extra Large Text</strong> - var(--font-size-xl)
                </p>
                <p style="font-size: var(--font-size-lg); margin-bottom: var(--spacing-sm);">
                  <strong>Large Text</strong> - var(--font-size-lg)
                </p>
                <p style="font-size: var(--font-size-base); margin-bottom: var(--spacing-sm);">
                  <strong>Base Text</strong> - var(--font-size-base)
                </p>
                <p style="font-size: var(--font-size-sm); margin-bottom: 0;">
                  <strong>Small Text</strong> - var(--font-size-sm)
                </p>
              </div>
            </div>

            <!-- Spacing Variables -->
            <div style="margin-bottom: var(--spacing-xl);">
              <h4>Spacing Scale Variables</h4>
              <div style="display: flex; flex-direction: column; gap: var(--spacing-xs);">
                <div style="display: flex; align-items: center; gap: var(--spacing-md);">
                  <div style="
                    width: var(--spacing-xs);
                    height: 40px;
                    background: var(--primary-color);
                    border-radius: var(--border-radius-sm);
                  "></div>
                  <span><strong>XS (0.25rem)</strong> - var(--spacing-xs)</span>
                </div>
                <div style="display: flex; align-items: center; gap: var(--spacing-md);">
                  <div style="
                    width: var(--spacing-sm);
                    height: 40px;
                    background: var(--success-color);
                    border-radius: var(--border-radius-sm);
                  "></div>
                  <span><strong>SM (0.5rem)</strong> - var(--spacing-sm)</span>
                </div>
                <div style="display: flex; align-items: center; gap: var(--spacing-md);">
                  <div style="
                    width: var(--spacing-md);
                    height: 40px;
                    background: var(--warning-color);
                    border-radius: var(--border-radius-sm);
                  "></div>
                  <span><strong>MD (1rem)</strong> - var(--spacing-md)</span>
                </div>
                <div style="display: flex; align-items: center; gap: var(--spacing-md);">
                  <div style="
                    width: var(--spacing-lg);
                    height: 40px;
                    background: var(--info-color);
                    border-radius: var(--border-radius-sm);
                  "></div>
                  <span><strong>LG (1.5rem)</strong> - var(--spacing-lg)</span>
                </div>
                <div style="display: flex; align-items: center; gap: var(--spacing-md);">
                  <div style="
                    width: var(--spacing-xl);
                    height: 40px;
                    background: var(--danger-color);
                    border-radius: var(--border-radius-sm);
                  "></div>
                  <span><strong>XL (3rem)</strong> - var(--spacing-xl)</span>
                </div>
              </div>
            </div>

            <!-- Shadow and Border Radius Variables -->
            <div>
              <h4>Shadow and Border Radius Variables</h4>
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: var(--spacing-lg);">
                <div style="
                  background: white;
                  padding: var(--spacing-lg);
                  border-radius: var(--border-radius-sm);
                  box-shadow: var(--shadow-sm);
                  border: 1px solid rgba(var(--secondary-rgb), 0.1);
                ">
                  <h6 style="margin: 0 0 var(--spacing-sm) 0;">Small Shadow</h6>
                  <p style="margin: 0; font-size: var(--font-size-sm); color: var(--secondary-color);">
                    box-shadow: var(--shadow-sm)<br>
                    border-radius: var(--border-radius-sm)
                  </p>
                </div>
                <div style="
                  background: white;
                  padding: var(--spacing-lg);
                  border-radius: var(--border-radius);
                  box-shadow: var(--shadow);
                ">
                  <h6 style="margin: 0 0 var(--spacing-sm) 0;">Medium Shadow</h6>
                  <p style="margin: 0; font-size: var(--font-size-sm); color: var(--secondary-color);">
                    box-shadow: var(--shadow)<br>
                    border-radius: var(--border-radius)
                  </p>
                </div>
                <div style="
                  background: white;
                  padding: var(--spacing-lg);
                  border-radius: var(--border-radius-lg);
                  box-shadow: var(--shadow-lg);
                ">
                  <h6 style="margin: 0 0 var(--spacing-sm) 0;">Large Shadow</h6>
                  <p style="margin: 0; font-size: var(--font-size-sm); color: var(--secondary-color);">
                    box-shadow: var(--shadow-lg)<br>
                    border-radius: var(--border-radius-lg)
                  </p>
                </div>
              </div>
            </div>

            <!-- Theme Switcher Demo -->
            <div style="margin-top: var(--spacing-xl); text-align: center;">
              <button onclick="toggleTheme()" style="
                background: var(--primary-color);
                color: white;
                border: none;
                padding: var(--spacing-md) var(--spacing-lg);
                border-radius: var(--border-radius);
                font-size: var(--font-size-base);
                font-weight: 500;
                cursor: pointer;
                box-shadow: var(--shadow-sm);
                transition: all 0.2s ease;
              " onmouseover="this.style.boxShadow='var(--shadow)'" onmouseout="this.style.boxShadow='var(--shadow-sm)'">
                Toggle Dark Theme (CSS Variables)
              </button>
            </div>
          </div>

          <script>
            let isDarkTheme = false;

            function toggleTheme() {
              const container = document.querySelector('[data-testid="css-variables-test"] > div');

              if (!isDarkTheme) {
                // Apply dark theme variables
                container.style.setProperty('--primary-color', '#0d6efd');
                container.style.setProperty('--secondary-color', '#6c757d');
                container.style.setProperty('--success-color', '#198754');
                container.style.setProperty('--danger-color', '#dc3545');
                container.style.setProperty('--warning-color', '#fd7e14');
                container.style.setProperty('--info-color', '#0dcaf0');
                container.style.setProperty('--primary-rgb', '13, 110, 253');
                container.style.background = '#1a1a1a';
                container.style.color = '#ffffff';
                isDarkTheme = true;
              } else {
                // Reset to light theme variables
                container.style.setProperty('--primary-color', '#007bff');
                container.style.setProperty('--secondary-color', '#6c757d');
                container.style.setProperty('--success-color', '#28a745');
                container.style.setProperty('--danger-color', '#dc3545');
                container.style.setProperty('--warning-color', '#ffc107');
                container.style.setProperty('--info-color', '#17a2b8');
                container.style.setProperty('--primary-rgb', '0, 123, 255');
                container.style.background = '';
                container.style.color = '';
                isDarkTheme = false;
              }
            }
          </script>
        `;
        document.body.appendChild(variablesDiv);
      });

      // Capture initial light theme state
      await visualUtils.screenshotComponent(
        '[data-testid="css-variables-test"]',
        'css-variables-light-theme',
        CSS_VALIDATION_CONFIG
      );

      // Toggle to dark theme and capture
      await page.click('button');
      await page.waitForTimeout(300);

      await visualUtils.screenshotComponent(
        '[data-testid="css-variables-test"]',
        'css-variables-dark-theme',
        CSS_VALIDATION_CONFIG
      );
    });
  });
});
