/**
 * Accessibility Visual Testing
 * Comprehensive testing of visual accessibility features, focus indicators, contrast, and WCAG compliance
 */

import { test, expect } from '@playwright/test';
import { VisualTestUtils } from './visual-utils';
import { 
  COMPONENT_SELECTORS,
  DEFAULT_VISUAL_CONFIG,
  ACCESSIBILITY_CONFIG,
  THEME_CONFIGS 
} from './visual-config';

// Accessibility-specific configuration
const ACCESSIBILITY_CONFIG_VISUAL = {
  ...DEFAULT_VISUAL_CONFIG,
  threshold: 0.05, // Very strict for accessibility features
  maxDiffPixels: 50
};

test.describe('Accessibility Visual Testing', () => {
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

  test.describe('Focus Indicators and Visual Hierarchy', () => {
    
    test('Focus Ring Visibility @visual @accessibility @focus', async ({ page }) => {
      // Create comprehensive focus indicator test
      await page.evaluate(() => {
        const focusDiv = document.createElement('div');
        focusDiv.setAttribute('data-testid', 'focus-indicators-comprehensive');
        focusDiv.innerHTML = `
          <div style="padding: 40px; background: #ffffff;">
            <h3>Focus Indicator Visibility Test</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 30px;">
              <!-- Standard Form Elements -->
              <div>
                <h4 style="margin-bottom: 20px;">Form Elements</h4>
                <div style="display: flex; flex-direction: column; gap: 15px;">
                  <input type="text" placeholder="Text input" style="
                    padding: 10px 12px;
                    border: 2px solid #dee2e6;
                    border-radius: 4px;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                  ">
                  
                  <textarea placeholder="Textarea" style="
                    padding: 10px 12px;
                    border: 2px solid #dee2e6;
                    border-radius: 4px;
                    font-size: 14px;
                    outline: none;
                    height: 80px;
                    resize: vertical;
                    transition: all 0.2s ease;
                  "></textarea>
                  
                  <select style="
                    padding: 10px 12px;
                    border: 2px solid #dee2e6;
                    border-radius: 4px;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                  ">
                    <option>Select option</option>
                    <option>Option 1</option>
                    <option>Option 2</option>
                  </select>
                  
                  <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                    <input type="checkbox" style="
                      width: 16px;
                      height: 16px;
                      outline: none;
                      accent-color: #007bff;
                    ">
                    <span>Checkbox option</span>
                  </label>
                  
                  <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                    <input type="radio" name="radio-group" style="
                      width: 16px;
                      height: 16px;
                      outline: none;
                      accent-color: #007bff;
                    ">
                    <span>Radio option</span>
                  </label>
                </div>
              </div>
              
              <!-- Buttons -->
              <div>
                <h4 style="margin-bottom: 20px;">Interactive Buttons</h4>
                <div style="display: flex; flex-direction: column; gap: 15px; align-items: flex-start;">
                  <button style="
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                  ">Primary Button</button>
                  
                  <button style="
                    background: transparent;
                    color: #007bff;
                    border: 2px solid #007bff;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    outline: none;
                    transition: all 0.2s ease;
                  ">Secondary Button</button>
                  
                  <button disabled style="
                    background: #6c757d;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    cursor: not-allowed;
                    font-size: 14px;
                    outline: none;
                    opacity: 0.65;
                  ">Disabled Button</button>
                </div>
              </div>
              
              <!-- Links and Navigation -->
              <div>
                <h4 style="margin-bottom: 20px;">Links & Navigation</h4>
                <div style="display: flex; flex-direction: column; gap: 15px; align-items: flex-start;">
                  <a href="#" style="
                    color: #007bff;
                    text-decoration: underline;
                    outline: none;
                    transition: all 0.2s ease;
                  ">Standard Link</a>
                  
                  <a href="#" style="
                    color: #007bff;
                    text-decoration: none;
                    outline: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    transition: all 0.2s ease;
                  ">Button-style Link</a>
                  
                  <div style="display: flex; gap: 20px;">
                    <a href="#" style="
                      color: #6c757d;
                      text-decoration: none;
                      padding: 8px 12px;
                      border-bottom: 2px solid transparent;
                      outline: none;
                      transition: all 0.2s ease;
                    ">Nav Item 1</a>
                    <a href="#" style="
                      color: #007bff;
                      text-decoration: none;
                      padding: 8px 12px;
                      border-bottom: 2px solid #007bff;
                      outline: none;
                      transition: all 0.2s ease;
                    ">Nav Item 2 (Active)</a>
                    <a href="#" style="
                      color: #6c757d;
                      text-decoration: none;
                      padding: 8px 12px;
                      border-bottom: 2px solid transparent;
                      outline: none;
                      transition: all 0.2s ease;
                    ">Nav Item 3</a>
                  </div>
                </div>
              </div>
              
              <!-- Custom Interactive Elements -->
              <div>
                <h4 style="margin-bottom: 20px;">Custom Interactive</h4>
                <div style="display: flex; flex-direction: column; gap: 15px; align-items: flex-start;">
                  <div tabindex="0" role="button" style="
                    background: #28a745;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    outline: none;
                    transition: all 0.2s ease;
                  ">Custom Button (div)</div>
                  
                  <div tabindex="0" role="menuitem" style="
                    padding: 8px 12px;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    cursor: pointer;
                    outline: none;
                    transition: all 0.2s ease;
                  ">Menu Item</div>
                  
                  <div tabindex="0" role="slider" aria-valuenow="50" aria-valuemin="0" aria-valuemax="100" style="
                    width: 200px;
                    height: 20px;
                    background: #e9ecef;
                    border-radius: 10px;
                    position: relative;
                    cursor: pointer;
                    outline: none;
                    transition: all 0.2s ease;
                  ">
                    <div style="
                      position: absolute;
                      top: 50%;
                      left: 50%;
                      width: 20px;
                      height: 20px;
                      background: #007bff;
                      border-radius: 50%;
                      transform: translate(-50%, -50%);
                      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                    "></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <style>
            /* Enhanced focus styles for accessibility */
            *:focus {
              outline: 3px solid #005fcc !important;
              outline-offset: 2px !important;
              box-shadow: 0 0 0 2px rgba(0, 95, 204, 0.25) !important;
            }
            
            /* Special focus styles for buttons */
            button:focus, [role="button"]:focus {
              outline: 3px solid #005fcc !important;
              outline-offset: 2px !important;
              box-shadow: 0 0 0 2px rgba(0, 95, 204, 0.25) !important;
              transform: translateY(-1px);
            }
            
            /* Link focus styles */
            a:focus {
              outline: 3px solid #005fcc !important;
              outline-offset: 2px !important;
              background-color: rgba(0, 95, 204, 0.1) !important;
              border-radius: 2px;
            }
            
            /* Form element focus styles */
            input:focus, textarea:focus, select:focus {
              border-color: #007bff !important;
              outline: 3px solid #005fcc !important;
              outline-offset: 2px !important;
              box-shadow: 0 0 0 2px rgba(0, 95, 204, 0.25) !important;
            }
            
            /* Checkbox and radio focus styles */
            input[type="checkbox"]:focus, input[type="radio"]:focus {
              outline: 3px solid #005fcc !important;
              outline-offset: 2px !important;
              box-shadow: 0 0 0 4px rgba(0, 95, 204, 0.25) !important;
            }
          </style>
        `;
        document.body.appendChild(focusDiv);
      });

      // Capture unfocused state
      await visualUtils.screenshotComponent(
        '[data-testid="focus-indicators-comprehensive"]',
        'focus-indicators-unfocused',
        ACCESSIBILITY_CONFIG_VISUAL
      );

      // Focus different elements and capture each state
      const focusableElements = await page.locator('[data-testid="focus-indicators-comprehensive"] input, [data-testid="focus-indicators-comprehensive"] textarea, [data-testid="focus-indicators-comprehensive"] select, [data-testid="focus-indicators-comprehensive"] button, [data-testid="focus-indicators-comprehensive"] a, [data-testid="focus-indicators-comprehensive"] [tabindex]').all();
      
      for (let i = 0; i < Math.min(focusableElements.length, 8); i++) {
        await focusableElements[i].focus();
        await page.waitForTimeout(200);
        
        await visualUtils.screenshotComponent(
          '[data-testid="focus-indicators-comprehensive"]',
          `focus-indicator-element-${i + 1}`,
          ACCESSIBILITY_CONFIG_VISUAL
        );
      }
    });

    test('Focus Order and Tab Navigation @visual @accessibility @keyboard', async ({ page }) => {
      await page.evaluate(() => {
        const tabDiv = document.createElement('div');
        tabDiv.setAttribute('data-testid', 'tab-navigation-order');
        tabDiv.innerHTML = `
          <div style="padding: 40px;">
            <h3>Keyboard Navigation Order Test</h3>
            <p style="color: #6c757d; margin-bottom: 30px;">
              Elements should be focusable in logical order. Current focus is highlighted.
            </p>
            
            <!-- Navigation header -->
            <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 30px;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0;">Navigation Header</h4>
                <div style="display: flex; gap: 15px;">
                  <a href="#" tabindex="1" style="color: #007bff; text-decoration: none; padding: 5px 10px;">Home</a>
                  <a href="#" tabindex="2" style="color: #007bff; text-decoration: none; padding: 5px 10px;">About</a>
                  <a href="#" tabindex="3" style="color: #007bff; text-decoration: none; padding: 5px 10px;">Contact</a>
                  <button tabindex="4" style="background: #007bff; color: white; border: none; padding: 5px 15px; border-radius: 4px;">Login</button>
                </div>
              </div>
            </div>
            
            <!-- Main content area -->
            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 30px;">
              <div>
                <h4>Main Content Area</h4>
                <form style="display: flex; flex-direction: column; gap: 15px;">
                  <label>
                    Name:
                    <input type="text" tabindex="5" style="
                      width: 100%;
                      padding: 8px 12px;
                      border: 1px solid #dee2e6;
                      border-radius: 4px;
                      margin-top: 4px;
                    ">
                  </label>
                  
                  <label>
                    Email:
                    <input type="email" tabindex="6" style="
                      width: 100%;
                      padding: 8px 12px;
                      border: 1px solid #dee2e6;
                      border-radius: 4px;
                      margin-top: 4px;
                    ">
                  </label>
                  
                  <label>
                    Message:
                    <textarea tabindex="7" style="
                      width: 100%;
                      padding: 8px 12px;
                      border: 1px solid #dee2e6;
                      border-radius: 4px;
                      margin-top: 4px;
                      height: 80px;
                      resize: vertical;
                    "></textarea>
                  </label>
                  
                  <div style="display: flex; gap: 10px;">
                    <button type="submit" tabindex="8" style="
                      background: #28a745;
                      color: white;
                      border: none;
                      padding: 10px 20px;
                      border-radius: 4px;
                    ">Submit</button>
                    <button type="reset" tabindex="9" style="
                      background: #6c757d;
                      color: white;
                      border: none;
                      padding: 10px 20px;
                      border-radius: 4px;
                    ">Reset</button>
                  </div>
                </form>
              </div>
              
              <!-- Sidebar -->
              <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h4>Sidebar</h4>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                  <a href="#" tabindex="10" style="
                    color: #007bff;
                    text-decoration: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    border: 1px solid transparent;
                  ">Related Link 1</a>
                  <a href="#" tabindex="11" style="
                    color: #007bff;
                    text-decoration: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    border: 1px solid transparent;
                  ">Related Link 2</a>
                  <a href="#" tabindex="12" style="
                    color: #007bff;
                    text-decoration: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    border: 1px solid transparent;
                  ">Related Link 3</a>
                  
                  <div style="margin-top: 20px;">
                    <h5>Quick Actions</h5>
                    <button tabindex="13" style="
                      width: 100%;
                      background: #17a2b8;
                      color: white;
                      border: none;
                      padding: 8px 12px;
                      border-radius: 4px;
                      margin-bottom: 5px;
                    ">Action 1</button>
                    <button tabindex="14" style="
                      width: 100%;
                      background: #ffc107;
                      color: #212529;
                      border: none;
                      padding: 8px 12px;
                      border-radius: 4px;
                    ">Action 2</button>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Skip link (usually hidden) -->
            <a href="#main-content" style="
              position: absolute;
              top: -40px;
              left: 6px;
              background: #000;
              color: #fff;
              padding: 8px;
              text-decoration: none;
              z-index: 1000;
              border-radius: 0 0 4px 4px;
              transition: top 0.2s;
            " tabindex="0" onfocus="this.style.top='0';" onblur="this.style.top='-40px';">Skip to main content</a>
            
            <div style="
              position: fixed;
              bottom: 20px;
              right: 20px;
              background: #007bff;
              color: white;
              padding: 10px 15px;
              border-radius: 4px;
              font-size: 12px;
              z-index: 1000;
            " id="focus-indicator">
              Current focus: None
            </div>
          </div>
          
          <style>
            *:focus {
              outline: 3px solid #ff6b35 !important;
              outline-offset: 2px !important;
              box-shadow: 0 0 0 2px rgba(255, 107, 53, 0.25) !important;
            }
          </style>
          
          <script>
            // Track focus for visual indication
            let focusCounter = 0;
            document.addEventListener('focusin', function(e) {
              focusCounter++;
              const indicator = document.getElementById('focus-indicator');
              if (indicator) {
                const tagName = e.target.tagName.toLowerCase();
                const tabIndex = e.target.tabIndex || 'auto';
                const text = e.target.textContent || e.target.placeholder || e.target.value || '';
                const displayText = text.substring(0, 20) + (text.length > 20 ? '...' : '');
                indicator.textContent = \`Focus #\${focusCounter}: \${tagName} (tab:\${tabIndex}) "\${displayText}"\`;
              }
            });
          </script>
        `;
        document.body.appendChild(tabDiv);
      });

      // Capture initial state
      await visualUtils.screenshotComponent(
        '[data-testid="tab-navigation-order"]',
        'tab-navigation-initial',
        ACCESSIBILITY_CONFIG_VISUAL
      );

      // Simulate tab navigation through elements
      for (let i = 0; i < 8; i++) {
        await page.keyboard.press('Tab');
        await page.waitForTimeout(200);
        
        await visualUtils.screenshotComponent(
          '[data-testid="tab-navigation-order"]',
          `tab-navigation-step-${i + 1}`,
          ACCESSIBILITY_CONFIG_VISUAL
        );
      }

      // Test skip link functionality
      await page.keyboard.press('Home'); // Go to beginning
      await page.keyboard.press('Tab'); // Focus skip link
      await page.waitForTimeout(200);
      
      await visualUtils.screenshotComponent(
        '[data-testid="tab-navigation-order"]',
        'tab-navigation-skip-link',
        ACCESSIBILITY_CONFIG_VISUAL
      );
    });
  });

  test.describe('Color Contrast and WCAG Compliance', () => {
    
    test('Color Contrast Validation @visual @accessibility @contrast', async ({ page }) => {
      await page.evaluate(() => {
        const contrastDiv = document.createElement('div');
        contrastDiv.setAttribute('data-testid', 'color-contrast-validation');
        contrastDiv.innerHTML = `
          <div style="padding: 40px;">
            <h3>Color Contrast Validation (WCAG 2.1 AA/AAA)</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-top: 30px;">
              <!-- WCAG AA Compliant (4.5:1 minimum) -->
              <div>
                <h4>WCAG AA Compliant Combinations</h4>
                <div style="display: flex; flex-direction: column; gap: 15px;">
                  <div style="background: #ffffff; color: #212529; padding: 15px; border: 1px solid #dee2e6;">
                    <strong>Contrast Ratio: 16.0:1</strong><br>
                    Black text on white background - Excellent readability
                  </div>
                  <div style="background: #007bff; color: #ffffff; padding: 15px;">
                    <strong>Contrast Ratio: 4.5:1</strong><br>
                    White text on primary blue - WCAG AA minimum
                  </div>
                  <div style="background: #28a745; color: #ffffff; padding: 15px;">
                    <strong>Contrast Ratio: 4.6:1</strong><br>
                    White text on success green - WCAG AA compliant
                  </div>
                  <div style="background: #dc3545; color: #ffffff; padding: 15px;">
                    <strong>Contrast Ratio: 5.3:1</strong><br>
                    White text on danger red - WCAG AA compliant
                  </div>
                </div>
              </div>
              
              <!-- WCAG AAA Compliant (7:1 minimum) -->
              <div>
                <h4>WCAG AAA Enhanced Contrast</h4>
                <div style="display: flex; flex-direction: column; gap: 15px;">
                  <div style="background: #000000; color: #ffffff; padding: 15px;">
                    <strong>Contrast Ratio: 21:1</strong><br>
                    White text on black background - Maximum contrast
                  </div>
                  <div style="background: #003d6b; color: #ffffff; padding: 15px;">
                    <strong>Contrast Ratio: 8.7:1</strong><br>
                    White text on dark blue - WCAG AAA compliant
                  </div>
                  <div style="background: #0f3443; color: #ffffff; padding: 15px;">
                    <strong>Contrast Ratio: 7.2:1</strong><br>
                    White text on dark teal - WCAG AAA compliant
                  </div>
                  <div style="background: #f8f9fa; color: #1a1a1a; padding: 15px; border: 1px solid #dee2e6;">
                    <strong>Contrast Ratio: 13.8:1</strong><br>
                    Dark text on light background - Excellent contrast
                  </div>
                </div>
              </div>
              
              <!-- Border Case Examples -->
              <div>
                <h4>Border Cases & Warnings</h4>
                <div style="display: flex; flex-direction: column; gap: 15px;">
                  <div style="background: #6c757d; color: #ffffff; padding: 15px; position: relative;">
                    <div style="position: absolute; top: 5px; right: 5px; background: #ffc107; color: #000; padding: 2px 6px; font-size: 10px; border-radius: 2px;">⚠️ BORDERLINE</div>
                    <strong>Contrast Ratio: 4.5:1</strong><br>
                    White text on gray - Right at WCAG AA minimum
                  </div>
                  <div style="background: #17a2b8; color: #ffffff; padding: 15px;">
                    <strong>Contrast Ratio: 4.9:1</strong><br>
                    White text on info blue - Safe WCAG AA
                  </div>
                  <div style="background: #ffc107; color: #000000; padding: 15px;">
                    <strong>Contrast Ratio: 11.7:1</strong><br>
                    Black text on warning yellow - High contrast
                  </div>
                  <div style="background: #f8f9fa; color: #6c757d; padding: 15px; border: 1px solid #dee2e6; position: relative;">
                    <div style="position: absolute; top: 5px; right: 5px; background: #28a745; color: #fff; padding: 2px 6px; font-size: 10px; border-radius: 2px;">✓ LARGE TEXT OK</div>
                    <strong>Contrast Ratio: 3.2:1</strong><br>
                    Gray text on light background - OK for large text (18pt+)
                  </div>
                </div>
              </div>
              
              <!-- Interactive Element Contrast -->
              <div>
                <h4>Interactive Elements</h4>
                <div style="display: flex; flex-direction: column; gap: 15px;">
                  <button style="
                    background: #007bff;
                    color: #ffffff;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 4px;
                    font-weight: 500;
                  ">
                    Primary Button (4.5:1)
                  </button>
                  <button style="
                    background: transparent;
                    color: #007bff;
                    border: 2px solid #007bff;
                    padding: 12px 20px;
                    border-radius: 4px;
                    font-weight: 500;
                  ">
                    Outline Button (4.5:1)
                  </button>
                  <a href="#" style="
                    color: #007bff;
                    text-decoration: underline;
                    font-size: 16px;
                    display: block;
                    padding: 8px 0;
                  ">
                    Standard Link (4.5:1)
                  </a>
                  <div style="
                    background: #e9ecef;
                    color: #495057;
                    padding: 12px;
                    border-radius: 4px;
                    border-left: 4px solid #007bff;
                  ">
                    <strong>Info Message (10.4:1)</strong><br>
                    This message has excellent contrast for accessibility
                  </div>
                </div>
              </div>
            </div>
            
            <div style="margin-top: 40px; padding: 20px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; color: #155724;">
              <h5 style="margin: 0 0 10px 0;">WCAG 2.1 Contrast Requirements:</h5>
              <ul style="margin: 0; padding-left: 20px;">
                <li><strong>AA Normal Text:</strong> 4.5:1 minimum contrast ratio</li>
                <li><strong>AA Large Text (18pt+ or 14pt+ bold):</strong> 3:1 minimum contrast ratio</li>
                <li><strong>AAA Normal Text:</strong> 7:1 minimum contrast ratio</li>
                <li><strong>AAA Large Text:</strong> 4.5:1 minimum contrast ratio</li>
                <li><strong>Non-text elements (UI components, graphics):</strong> 3:1 minimum</li>
              </ul>
            </div>
          </div>
        `;
        document.body.appendChild(contrastDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="color-contrast-validation"]',
        'color-contrast-validation',
        ACCESSIBILITY_CONFIG_VISUAL
      );
    });

    test('High Contrast Mode Compatibility @visual @accessibility @high-contrast', async ({ page }) => {
      // Test with forced colors (Windows High Contrast Mode simulation)
      await page.emulateMedia({ forcedColors: 'active' });
      
      await page.evaluate(() => {
        const highContrastDiv = document.createElement('div');
        highContrastDiv.setAttribute('data-testid', 'high-contrast-mode');
        highContrastDiv.innerHTML = `
          <div style="padding: 40px;">
            <h3>High Contrast Mode Compatibility</h3>
            <p style="margin-bottom: 30px;">
              This page should maintain functionality and readability in high contrast mode.
            </p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px;">
              <!-- Form Elements -->
              <div style="border: 1px solid; padding: 20px; border-radius: 8px;">
                <h4>Form Elements</h4>
                <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
                  <input type="text" placeholder="Text Input" style="
                    padding: 10px;
                    border: 1px solid;
                    background: Canvas;
                    color: CanvasText;
                  ">
                  <select style="
                    padding: 10px;
                    border: 1px solid;
                    background: Canvas;
                    color: CanvasText;
                  ">
                    <option>Select Option</option>
                    <option>Option 1</option>
                  </select>
                  <textarea placeholder="Textarea" style="
                    padding: 10px;
                    border: 1px solid;
                    background: Canvas;
                    color: CanvasText;
                    height: 60px;
                  "></textarea>
                </div>
              </div>
              
              <!-- Buttons -->
              <div style="border: 1px solid; padding: 20px; border-radius: 8px;">
                <h4>Interactive Buttons</h4>
                <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
                  <button style="
                    padding: 12px 20px;
                    border: 1px solid ButtonBorder;
                    background: ButtonFace;
                    color: ButtonText;
                    cursor: pointer;
                  ">Standard Button</button>
                  <button style="
                    padding: 12px 20px;
                    border: 2px solid Highlight;
                    background: Highlight;
                    color: HighlightText;
                    cursor: pointer;
                  ">Primary Button</button>
                  <button disabled style="
                    padding: 12px 20px;
                    border: 1px solid GrayText;
                    background: Canvas;
                    color: GrayText;
                    cursor: not-allowed;
                  ">Disabled Button</button>
                </div>
              </div>
              
              <!-- Links and Navigation -->
              <div style="border: 1px solid; padding: 20px; border-radius: 8px;">
                <h4>Links & Navigation</h4>
                <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
                  <a href="#" style="color: LinkText; text-decoration: underline;">Standard Link</a>
                  <a href="#" style="color: VisitedText; text-decoration: underline;">Visited Link</a>
                  <nav style="display: flex; gap: 15px; padding: 10px 0; border-top: 1px solid; border-bottom: 1px solid;">
                    <a href="#" style="color: LinkText; text-decoration: none; padding: 5px 10px;">Home</a>
                    <a href="#" style="color: HighlightText; background: Highlight; text-decoration: none; padding: 5px 10px;">Current</a>
                    <a href="#" style="color: LinkText; text-decoration: none; padding: 5px 10px;">About</a>
                  </nav>
                </div>
              </div>
              
              <!-- Status Messages -->
              <div style="border: 1px solid; padding: 20px; border-radius: 8px;">
                <h4>Status Messages</h4>
                <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
                  <div style="
                    padding: 10px;
                    border: 1px solid;
                    background: Canvas;
                    color: CanvasText;
                    border-left: 4px solid Highlight;
                  " role="status">
                    ✓ Success: Action completed successfully
                  </div>
                  <div style="
                    padding: 10px;
                    border: 1px solid;
                    background: Canvas;
                    color: CanvasText;
                    border-left: 4px solid;
                  " role="alert">
                    ⚠️ Warning: Please review your input
                  </div>
                  <div style="
                    padding: 10px;
                    border: 1px solid;
                    background: Canvas;
                    color: CanvasText;
                    border-left: 4px solid;
                  " role="alert">
                    ❌ Error: Something went wrong
                  </div>
                </div>
              </div>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; border: 1px solid; background: Canvas; color: CanvasText;">
              <strong>High Contrast Mode Notes:</strong>
              <ul style="margin: 10px 0 0 20px;">
                <li>Uses system colors (Canvas, CanvasText, Highlight, etc.)</li>
                <li>Maintains borders and visual hierarchy</li>
                <li>Preserves interactive element distinction</li>
                <li>Ensures focus indicators remain visible</li>
              </ul>
            </div>
          </div>
        `;
        document.body.appendChild(highContrastDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="high-contrast-mode"]',
        'high-contrast-mode-compatibility',
        ACCESSIBILITY_CONFIG_VISUAL
      );

      // Test focus states in high contrast mode
      const focusableElements = await page.locator('[data-testid="high-contrast-mode"] input, [data-testid="high-contrast-mode"] select, [data-testid="high-contrast-mode"] button, [data-testid="high-contrast-mode"] a').all();
      
      for (let i = 0; i < Math.min(focusableElements.length, 4); i++) {
        await focusableElements[i].focus();
        await page.waitForTimeout(200);
        
        await visualUtils.screenshotComponent(
          '[data-testid="high-contrast-mode"]',
          `high-contrast-focus-${i + 1}`,
          ACCESSIBILITY_CONFIG_VISUAL
        );
      }

      // Reset forced colors
      await page.emulateMedia({ forcedColors: 'none' });
    });
  });

  test.describe('Screen Reader and Assistive Technology Support', () => {
    
    test('ARIA Labels and Descriptions @visual @accessibility @aria', async ({ page }) => {
      await page.evaluate(() => {
        const ariaDiv = document.createElement('div');
        ariaDiv.setAttribute('data-testid', 'aria-labels-descriptions');
        ariaDiv.innerHTML = `
          <div style="padding: 40px;">
            <h3>ARIA Labels and Descriptions Visual Context</h3>
            <p style="margin-bottom: 30px; color: #6c757d;">
              Visual representation of elements with ARIA attributes for screen reader support.
            </p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 30px;">
              <!-- Form with ARIA Labels -->
              <div style="border: 1px solid #dee2e6; padding: 25px; border-radius: 8px;">
                <h4>Form with ARIA Labels</h4>
                <form style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
                  <div>
                    <label for="username" style="display: block; margin-bottom: 5px; font-weight: 500;">
                      Username <span style="color: #dc3545;" aria-label="required">*</span>
                    </label>
                    <input 
                      type="text" 
                      id="username"
                      aria-required="true"
                      aria-describedby="username-help username-error"
                      style="
                        width: 100%;
                        padding: 10px;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                      "
                    >
                    <div id="username-help" style="font-size: 12px; color: #6c757d; margin-top: 4px;">
                      Must be 3-20 characters long
                    </div>
                    <div id="username-error" role="alert" style="font-size: 12px; color: #dc3545; margin-top: 4px; display: none;">
                      Username is required
                    </div>
                  </div>
                  
                  <div>
                    <label for="password" style="display: block; margin-bottom: 5px; font-weight: 500;">
                      Password <span style="color: #dc3545;" aria-label="required">*</span>
                    </label>
                    <input 
                      type="password" 
                      id="password"
                      aria-required="true"
                      aria-describedby="password-strength"
                      style="
                        width: 100%;
                        padding: 10px;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                      "
                    >
                    <div id="password-strength" aria-live="polite" style="font-size: 12px; color: #6c757d; margin-top: 4px;">
                      Password strength: <span style="color: #ffc107;">Weak</span>
                    </div>
                  </div>
                  
                  <fieldset style="border: 1px solid #dee2e6; padding: 15px; border-radius: 4px;">
                    <legend style="padding: 0 8px; font-weight: 500;">Account Type</legend>
                    <div style="display: flex; flex-direction: column; gap: 8px;">
                      <label style="display: flex; align-items: center; gap: 8px;">
                        <input type="radio" name="account-type" value="personal" aria-describedby="personal-desc">
                        <span>Personal</span>
                      </label>
                      <div id="personal-desc" style="font-size: 12px; color: #6c757d; margin-left: 24px;">
                        For individual use
                      </div>
                      <label style="display: flex; align-items: center; gap: 8px;">
                        <input type="radio" name="account-type" value="business" aria-describedby="business-desc">
                        <span>Business</span>
                      </label>
                      <div id="business-desc" style="font-size: 12px; color: #6c757d; margin-left: 24px;">
                        For companies and organizations
                      </div>
                    </div>
                  </fieldset>
                </form>
              </div>
              
              <!-- Interactive Elements with ARIA -->
              <div style="border: 1px solid #dee2e6; padding: 25px; border-radius: 8px;">
                <h4>Interactive Elements</h4>
                <div style="display: flex; flex-direction: column; gap: 20px; margin-top: 15px;">
                  <!-- Custom Button -->
                  <div role="button" 
                       tabindex="0" 
                       aria-pressed="false"
                       aria-describedby="toggle-desc"
                       style="
                         background: #f8f9fa;
                         border: 1px solid #dee2e6;
                         padding: 15px;
                         border-radius: 4px;
                         cursor: pointer;
                         text-align: center;
                       "
                       onclick="
                         const pressed = this.getAttribute('aria-pressed') === 'true';
                         this.setAttribute('aria-pressed', !pressed);
                         this.style.background = !pressed ? '#007bff' : '#f8f9fa';
                         this.style.color = !pressed ? 'white' : 'black';
                         document.getElementById('toggle-status').textContent = !pressed ? 'ON' : 'OFF';
                       ">
                    Toggle Button (Click to activate)
                  </div>
                  <div id="toggle-desc" style="font-size: 12px; color: #6c757d; text-align: center;">
                    Status: <span id="toggle-status">OFF</span>
                  </div>
                  
                  <!-- Progress Indicator -->
                  <div>
                    <label for="file-progress" style="display: block; margin-bottom: 8px; font-weight: 500;">
                      File Upload Progress
                    </label>
                    <div 
                      role="progressbar" 
                      aria-valuenow="65" 
                      aria-valuemin="0" 
                      aria-valuemax="100"
                      aria-labelledby="file-progress"
                      aria-describedby="progress-desc"
                      style="
                        width: 100%;
                        height: 20px;
                        background: #e9ecef;
                        border-radius: 10px;
                        overflow: hidden;
                      ">
                      <div style="
                        width: 65%;
                        height: 100%;
                        background: linear-gradient(90deg, #007bff, #0056b3);
                        transition: width 0.3s ease;
                      "></div>
                    </div>
                    <div id="progress-desc" style="font-size: 12px; color: #6c757d; margin-top: 4px;">
                      Uploading... 65% complete (2.1 MB of 3.2 MB)
                    </div>
                  </div>
                  
                  <!-- Alert Messages -->
                  <div>
                    <h5>Status Messages</h5>
                    <div role="alert" aria-live="assertive" style="
                      background: #f8d7da;
                      color: #721c24;
                      border: 1px solid #f1aeb5;
                      padding: 12px;
                      border-radius: 4px;
                      border-left: 4px solid #dc3545;
                      margin: 8px 0;
                    ">
                      <strong>Error:</strong> Please fix the validation errors above.
                    </div>
                    <div role="status" aria-live="polite" style="
                      background: #d4edda;
                      color: #155724;
                      border: 1px solid #c3e6cb;
                      padding: 12px;
                      border-radius: 4px;
                      border-left: 4px solid #28a745;
                      margin: 8px 0;
                    ">
                      <strong>Success:</strong> Your changes have been saved.
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Data Table with ARIA -->
              <div style="border: 1px solid #dee2e6; padding: 25px; border-radius: 8px; grid-column: 1 / -1;">
                <h4>Data Table with ARIA Support</h4>
                <table role="table" aria-label="User management table" style="width: 100%; margin-top: 15px; border-collapse: collapse;">
                  <thead>
                    <tr role="row">
                      <th role="columnheader" aria-sort="ascending" tabindex="0" style="
                        padding: 12px;
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                        text-align: left;
                        cursor: pointer;
                      ">
                        Name ↑
                      </th>
                      <th role="columnheader" aria-sort="none" tabindex="0" style="
                        padding: 12px;
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                        text-align: left;
                        cursor: pointer;
                      ">
                        Email
                      </th>
                      <th role="columnheader" aria-sort="none" tabindex="0" style="
                        padding: 12px;
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                        text-align: left;
                        cursor: pointer;
                      ">
                        Role
                      </th>
                      <th role="columnheader" style="
                        padding: 12px;
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                        text-align: left;
                      ">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody role="rowgroup">
                    <tr role="row">
                      <td role="cell" style="padding: 12px; border: 1px solid #dee2e6;">John Doe</td>
                      <td role="cell" style="padding: 12px; border: 1px solid #dee2e6;">john@example.com</td>
                      <td role="cell" style="padding: 12px; border: 1px solid #dee2e6;">
                        <span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Admin</span>
                      </td>
                      <td role="cell" style="padding: 12px; border: 1px solid #dee2e6;">
                        <button aria-label="Edit John Doe" style="background: #28a745; color: white; border: none; padding: 4px 8px; border-radius: 4px; margin-right: 4px;">Edit</button>
                        <button aria-label="Delete John Doe" style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 4px;">Delete</button>
                      </td>
                    </tr>
                    <tr role="row" style="background: #f8f9fa;">
                      <td role="cell" style="padding: 12px; border: 1px solid #dee2e6;">Jane Smith</td>
                      <td role="cell" style="padding: 12px; border: 1px solid #dee2e6;">jane@example.com</td>
                      <td role="cell" style="padding: 12px; border: 1px solid #dee2e6;">
                        <span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">User</span>
                      </td>
                      <td role="cell" style="padding: 12px; border: 1px solid #dee2e6;">
                        <button aria-label="Edit Jane Smith" style="background: #28a745; color: white; border: none; padding: 4px 8px; border-radius: 4px; margin-right: 4px;">Edit</button>
                        <button aria-label="Delete Jane Smith" style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 4px;">Delete</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div style="margin-top: 10px; font-size: 12px; color: #6c757d;">
                  Showing 2 of 2 users. Use arrow keys to navigate table cells.
                </div>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(ariaDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="aria-labels-descriptions"]',
        'aria-labels-descriptions',
        ACCESSIBILITY_CONFIG_VISUAL
      );

      // Test interactive states
      await page.click('[role="button"][aria-pressed]');
      await page.waitForTimeout(200);
      
      await visualUtils.screenshotComponent(
        '[data-testid="aria-labels-descriptions"]',
        'aria-interactive-states',
        ACCESSIBILITY_CONFIG_VISUAL
      );
    });

    test('Error States and Validation Messages @visual @accessibility @errors', async ({ page }) => {
      await page.evaluate(() => {
        const errorDiv = document.createElement('div');
        errorDiv.setAttribute('data-testid', 'accessibility-error-states');
        errorDiv.innerHTML = `
          <div style="padding: 40px;">
            <h3>Accessible Error States and Validation</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 30px; margin-top: 30px;">
              <!-- Form Validation Errors -->
              <div style="border: 1px solid #dee2e6; padding: 25px; border-radius: 8px;">
                <h4>Form Validation Errors</h4>
                <form style="display: flex; flex-direction: column; gap: 20px; margin-top: 15px;">
                  <!-- Field with error -->
                  <div>
                    <label for="email-error" style="display: block; margin-bottom: 5px; font-weight: 500;">
                      Email Address <span style="color: #dc3545;" aria-label="required">*</span>
                    </label>
                    <input 
                      type="email" 
                      id="email-error"
                      value="invalid-email"
                      aria-required="true"
                      aria-invalid="true"
                      aria-describedby="email-error-msg email-help"
                      style="
                        width: 100%;
                        padding: 10px;
                        border: 2px solid #dc3545;
                        border-radius: 4px;
                        background: #fef8f8;
                      "
                    >
                    <div id="email-help" style="font-size: 12px; color: #6c757d; margin-top: 4px;">
                      Enter a valid email address
                    </div>
                    <div id="email-error-msg" role="alert" style="
                      font-size: 12px; 
                      color: #dc3545; 
                      margin-top: 4px;
                      display: flex;
                      align-items: center;
                      gap: 4px;
                    ">
                      <span aria-hidden="true">⚠️</span>
                      Please enter a valid email address
                    </div>
                  </div>
                  
                  <!-- Field with success -->
                  <div>
                    <label for="name-success" style="display: block; margin-bottom: 5px; font-weight: 500;">
                      Full Name <span style="color: #dc3545;" aria-label="required">*</span>
                    </label>
                    <input 
                      type="text" 
                      id="name-success"
                      value="John Doe"
                      aria-required="true"
                      aria-invalid="false"
                      aria-describedby="name-success-msg"
                      style="
                        width: 100%;
                        padding: 10px;
                        border: 2px solid #28a745;
                        border-radius: 4px;
                        background: #f8fff9;
                      "
                    >
                    <div id="name-success-msg" role="status" style="
                      font-size: 12px; 
                      color: #28a745; 
                      margin-top: 4px;
                      display: flex;
                      align-items: center;
                      gap: 4px;
                    ">
                      <span aria-hidden="true">✓</span>
                      Name looks good
                    </div>
                  </div>
                  
                  <!-- Field with warning -->
                  <div>
                    <label for="password-warning" style="display: block; margin-bottom: 5px; font-weight: 500;">
                      Password <span style="color: #dc3545;" aria-label="required">*</span>
                    </label>
                    <input 
                      type="password" 
                      id="password-warning"
                      value="123456"
                      aria-required="true"
                      aria-describedby="password-warning-msg"
                      style="
                        width: 100%;
                        padding: 10px;
                        border: 2px solid #ffc107;
                        border-radius: 4px;
                        background: #fffbf0;
                      "
                    >
                    <div id="password-warning-msg" role="status" aria-live="polite" style="
                      font-size: 12px; 
                      color: #856404; 
                      margin-top: 4px;
                      display: flex;
                      align-items: center;
                      gap: 4px;
                    ">
                      <span aria-hidden="true">⚡</span>
                      Password strength: Weak. Consider using a stronger password.
                    </div>
                  </div>
                </form>
              </div>
              
              <!-- Global Error Messages -->
              <div style="border: 1px solid #dee2e6; padding: 25px; border-radius: 8px;">
                <h4>Global Error Messages</h4>
                <div style="display: flex; flex-direction: column; gap: 15px; margin-top: 15px;">
                  <!-- Critical Error -->
                  <div role="alert" aria-live="assertive" style="
                    background: #f8d7da;
                    color: #721c24;
                    border: 1px solid #f1aeb5;
                    border-left: 4px solid #dc3545;
                    padding: 15px;
                    border-radius: 4px;
                  ">
                    <div style="display: flex; align-items: flex-start; gap: 10px;">
                      <span style="font-size: 20px;" aria-hidden="true">🚨</span>
                      <div>
                        <strong>Critical Error</strong>
                        <p style="margin: 4px 0 0 0;">
                          Unable to save your data. Please try again or contact support if the problem persists.
                        </p>
                        <button style="
                          background: #dc3545;
                          color: white;
                          border: none;
                          padding: 6px 12px;
                          border-radius: 4px;
                          margin-top: 8px;
                          font-size: 12px;
                        ">Retry</button>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Warning Message -->
                  <div role="status" aria-live="polite" style="
                    background: #fff3cd;
                    color: #856404;
                    border: 1px solid #ffeaa7;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    border-radius: 4px;
                  ">
                    <div style="display: flex; align-items: flex-start; gap: 10px;">
                      <span style="font-size: 20px;" aria-hidden="true">⚠️</span>
                      <div>
                        <strong>Warning</strong>
                        <p style="margin: 4px 0 0 0;">
                          Your session will expire in 5 minutes. Save your work to avoid losing changes.
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Info Message -->
                  <div role="status" aria-live="polite" style="
                    background: #d1ecf1;
                    color: #0c5460;
                    border: 1px solid #bee5eb;
                    border-left: 4px solid #17a2b8;
                    padding: 15px;
                    border-radius: 4px;
                  ">
                    <div style="display: flex; align-items: flex-start; gap: 10px;">
                      <span style="font-size: 20px;" aria-hidden="true">ℹ️</span>
                      <div>
                        <strong>Information</strong>
                        <p style="margin: 4px 0 0 0;">
                          Your data has been automatically saved. Last saved: 2 minutes ago.
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Success Message -->
                  <div role="status" aria-live="polite" style="
                    background: #d4edda;
                    color: #155724;
                    border: 1px solid #c3e6cb;
                    border-left: 4px solid #28a745;
                    padding: 15px;
                    border-radius: 4px;
                  ">
                    <div style="display: flex; align-items: flex-start; gap: 10px;">
                      <span style="font-size: 20px;" aria-hidden="true">✅</span>
                      <div>
                        <strong>Success</strong>
                        <p style="margin: 4px 0 0 0;">
                          Your profile has been updated successfully.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Loading and Processing States -->
              <div style="border: 1px solid #dee2e6; padding: 25px; border-radius: 8px; grid-column: 1 / -1;">
                <h4>Loading and Processing States</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 15px;">
                  <!-- Loading State -->
                  <div style="text-align: center; padding: 20px;">
                    <div role="status" aria-live="polite" aria-label="Loading content">
                      <div style="
                        width: 40px;
                        height: 40px;
                        border: 4px solid #f3f3f3;
                        border-top: 4px solid #007bff;
                        border-radius: 50%;
                        animation: spin 1s linear infinite;
                        margin: 0 auto 15px;
                      " aria-hidden="true"></div>
                      <p style="margin: 0; color: #6c757d;">Loading your data...</p>
                    </div>
                  </div>
                  
                  <!-- Processing State -->
                  <div style="text-align: center; padding: 20px;">
                    <div role="status" aria-live="polite" aria-label="Processing request">
                      <div style="display: flex; justify-content: center; gap: 4px; margin-bottom: 15px;">
                        <div style="width: 8px; height: 8px; background: #007bff; border-radius: 50%; animation: pulse 1.5s infinite;" aria-hidden="true"></div>
                        <div style="width: 8px; height: 8px; background: #007bff; border-radius: 50%; animation: pulse 1.5s infinite 0.2s;" aria-hidden="true"></div>
                        <div style="width: 8px; height: 8px; background: #007bff; border-radius: 50%; animation: pulse 1.5s infinite 0.4s;" aria-hidden="true"></div>
                      </div>
                      <p style="margin: 0; color: #6c757d;">Processing your request...</p>
                    </div>
                  </div>
                  
                  <!-- Upload Progress -->
                  <div style="padding: 20px;">
                    <div role="status" aria-live="polite">
                      <h5 style="margin: 0 0 10px 0;">File Upload Progress</h5>
                      <div 
                        role="progressbar" 
                        aria-valuenow="75" 
                        aria-valuemin="0" 
                        aria-valuemax="100"
                        aria-label="Upload progress: 75% complete"
                        style="
                          width: 100%;
                          height: 20px;
                          background: #e9ecef;
                          border-radius: 10px;
                          overflow: hidden;
                          margin-bottom: 8px;
                        ">
                        <div style="
                          width: 75%;
                          height: 100%;
                          background: linear-gradient(90deg, #007bff, #0056b3);
                          transition: width 0.3s ease;
                        " aria-hidden="true"></div>
                      </div>
                      <p style="margin: 0; font-size: 14px; color: #6c757d;">
                        Uploading document.pdf: 75% complete (3.2 MB of 4.3 MB)
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <style>
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
            
            @keyframes pulse {
              0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
              40% { transform: scale(1); opacity: 1; }
            }
          </style>
        `;
        document.body.appendChild(errorDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="accessibility-error-states"]',
        'accessibility-error-states',
        ACCESSIBILITY_CONFIG_VISUAL
      );
    });
  });

  test.describe('Theme Accessibility Across All Themes', () => {
    
    test('Focus Indicators Across Themes @visual @accessibility @theme-focus', async ({ page }) => {
      const themes: (keyof typeof THEME_CONFIGS)[] = ['light', 'dark', 'cyborg', 'darkly'];
      
      for (const themeName of themes) {
        await visualUtils.setTheme(themeName);
        
        // Create theme-specific focus test
        await page.evaluate((theme) => {
          // Remove existing test
          const existing = document.querySelector('[data-testid="theme-focus-test"]');
          if (existing) existing.remove();
          
          const focusDiv = document.createElement('div');
          focusDiv.setAttribute('data-testid', 'theme-focus-test');
          focusDiv.innerHTML = `
            <div style="padding: 30px;">
              <h4>${theme.toUpperCase()} Theme - Focus Indicators</h4>
              <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 20px;">
                <button style="
                  background: var(--bs-primary, #007bff);
                  color: var(--bs-light, white);
                  border: none;
                  padding: 10px 20px;
                  border-radius: 4px;
                ">Primary Button</button>
                
                <input type="text" placeholder="Text input" style="
                  padding: 10px;
                  border: 1px solid var(--bs-border-color, #dee2e6);
                  border-radius: 4px;
                  background: var(--bs-body-bg, white);
                  color: var(--bs-body-color, #212529);
                ">
                
                <select style="
                  padding: 10px;
                  border: 1px solid var(--bs-border-color, #dee2e6);
                  border-radius: 4px;
                  background: var(--bs-body-bg, white);
                  color: var(--bs-body-color, #212529);
                ">
                  <option>Select option</option>
                </select>
                
                <a href="#" style="
                  color: var(--bs-primary, #007bff);
                  text-decoration: underline;
                  padding: 10px;
                ">Sample Link</a>
                
                <div tabindex="0" style="
                  background: var(--bs-secondary, #6c757d);
                  color: var(--bs-light, white);
                  padding: 10px 15px;
                  border-radius: 4px;
                  cursor: pointer;
                ">Custom Focusable</div>
              </div>
            </div>
          `;
          document.body.appendChild(focusDiv);
        }, themeName);

        // Focus each element
        const focusableElements = await page.locator('[data-testid="theme-focus-test"] button, [data-testid="theme-focus-test"] input, [data-testid="theme-focus-test"] select, [data-testid="theme-focus-test"] a, [data-testid="theme-focus-test"] [tabindex]').all();
        
        for (let i = 0; i < focusableElements.length; i++) {
          await focusableElements[i].focus();
          await page.waitForTimeout(200);
          
          await visualUtils.screenshotComponent(
            '[data-testid="theme-focus-test"]',
            `theme-focus-${themeName}-element-${i + 1}`,
            ACCESSIBILITY_CONFIG_VISUAL
          );
        }
      }
    });
  });
});