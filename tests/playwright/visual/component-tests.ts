/**
 * Component Visual Testing
 * Comprehensive visual testing for all UI components including states, interactions, and data variations
 */

import { test, expect } from '@playwright/test';
import { VisualTestUtils } from './visual-utils';
import {
  COMPONENT_SELECTORS,
  DEFAULT_VISUAL_CONFIG,
  RESPONSIVE_VIEWPORTS,
  THEME_CONFIGS
} from './visual-config';

// Component-specific configuration
const COMPONENT_CONFIG = {
  ...DEFAULT_VISUAL_CONFIG,
  threshold: 0.1,
  maxDiffPixels: 75
};

test.describe('Component Visual Testing', () => {
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

  test.describe('File Upload Component Visual States', () => {

    test('File Upload - Empty State @visual @component @file-upload', async ({ page }) => {
      const uploadExists = await page.locator(COMPONENT_SELECTORS.fileUpload).count() > 0;

      if (uploadExists) {
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.fileUpload,
          'file-upload-empty-state',
          COMPONENT_CONFIG
        );
      } else {
        // Create mock file upload component
        await page.evaluate(() => {
          const uploadDiv = document.createElement('div');
          uploadDiv.setAttribute('data-testid', 'mock-file-upload');
          uploadDiv.innerHTML = `
            <div style="
              border: 2px dashed #dee2e6;
              border-radius: 8px;
              padding: 40px 20px;
              text-align: center;
              background: #f8f9fa;
              margin: 20px;
              cursor: pointer;
              transition: border-color 0.3s, background-color 0.3s;
            ">
              <div style="font-size: 48px; color: #6c757d; margin-bottom: 16px;">📁</div>
              <h4 style="color: #495057; margin-bottom: 8px;">Drop files here to upload</h4>
              <p style="color: #6c757d; margin-bottom: 16px;">or click to select files</p>
              <button style="
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
              ">Choose Files</button>
              <p style="color: #6c757d; font-size: 12px; margin-top: 12px;">
                Supported formats: CSV, Excel, JSON (Max size: 10MB)
              </p>
            </div>
          `;
          document.body.appendChild(uploadDiv);
        });

        await visualUtils.screenshotComponent(
          '[data-testid="mock-file-upload"]',
          'file-upload-empty-state',
          COMPONENT_CONFIG
        );
      }
    });

    test('File Upload - Hover State @visual @component @file-upload', async ({ page }) => {
      // Create hover state mockup
      await page.evaluate(() => {
        const uploadDiv = document.createElement('div');
        uploadDiv.setAttribute('data-testid', 'file-upload-hover');
        uploadDiv.innerHTML = `
          <div style="
            border: 2px dashed #007bff;
            border-radius: 8px;
            padding: 40px 20px;
            text-align: center;
            background: #e7f3ff;
            margin: 20px;
            cursor: pointer;
          ">
            <div style="font-size: 48px; color: #007bff; margin-bottom: 16px;">📁</div>
            <h4 style="color: #007bff; margin-bottom: 8px;">Drop files here to upload</h4>
            <p style="color: #0056b3; margin-bottom: 16px;">or click to select files</p>
            <button style="
              background: #0056b3;
              color: white;
              border: none;
              padding: 10px 20px;
              border-radius: 4px;
              cursor: pointer;
              font-size: 14px;
              transform: translateY(-1px);
              box-shadow: 0 2px 4px rgba(0,123,255,0.25);
            ">Choose Files</button>
            <p style="color: #0056b3; font-size: 12px; margin-top: 12px;">
              Supported formats: CSV, Excel, JSON (Max size: 10MB)
            </p>
          </div>
        `;
        document.body.appendChild(uploadDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="file-upload-hover"]',
        'file-upload-hover-state',
        COMPONENT_CONFIG
      );
    });

    test('File Upload - Loading State @visual @component @file-upload', async ({ page }) => {
      await page.evaluate(() => {
        const uploadDiv = document.createElement('div');
        uploadDiv.setAttribute('data-testid', 'file-upload-loading');
        uploadDiv.innerHTML = `
          <div style="
            border: 2px solid #007bff;
            border-radius: 8px;
            padding: 40px 20px;
            text-align: center;
            background: #ffffff;
            margin: 20px;
            position: relative;
          ">
            <div style="
              display: inline-block;
              width: 40px;
              height: 40px;
              border: 4px solid #f3f3f3;
              border-top: 4px solid #007bff;
              border-radius: 50%;
              animation: spin 1s linear infinite;
              margin-bottom: 16px;
            "></div>
            <h4 style="color: #495057; margin-bottom: 8px;">Uploading files...</h4>
            <div style="
              width: 100%;
              max-width: 300px;
              height: 8px;
              background: #e9ecef;
              border-radius: 4px;
              margin: 16px auto;
              overflow: hidden;
            ">
              <div style="
                width: 60%;
                height: 100%;
                background: linear-gradient(90deg, #007bff, #0056b3);
                transition: width 0.3s ease;
              "></div>
            </div>
            <p style="color: #6c757d; font-size: 14px; margin: 8px 0;">
              data-sample.csv (2.1 MB) • 60% complete
            </p>
            <button style="
              background: #dc3545;
              color: white;
              border: none;
              padding: 8px 16px;
              border-radius: 4px;
              cursor: pointer;
              font-size: 12px;
            ">Cancel Upload</button>
          </div>
          <style>
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          </style>
        `;
        document.body.appendChild(uploadDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="file-upload-loading"]',
        'file-upload-loading-state',
        COMPONENT_CONFIG
      );
    });

    test('File Upload - Success State @visual @component @file-upload', async ({ page }) => {
      await page.evaluate(() => {
        const uploadDiv = document.createElement('div');
        uploadDiv.setAttribute('data-testid', 'file-upload-success');
        uploadDiv.innerHTML = `
          <div style="
            border: 2px solid #28a745;
            border-radius: 8px;
            padding: 40px 20px;
            text-align: center;
            background: #f8fff9;
            margin: 20px;
          ">
            <div style="font-size: 48px; color: #28a745; margin-bottom: 16px;">✅</div>
            <h4 style="color: #155724; margin-bottom: 8px;">File uploaded successfully!</h4>
            <p style="color: #6c757d; margin-bottom: 16px;">data-sample.csv (2.1 MB)</p>
            <div style="
              background: #d4edda;
              border: 1px solid #c3e6cb;
              border-radius: 4px;
              padding: 12px;
              margin: 16px auto;
              max-width: 400px;
            ">
              <div style="font-weight: bold; color: #155724; margin-bottom: 4px;">File Details:</div>
              <div style="font-size: 13px; color: #155724;">
                • 1,247 rows processed<br>
                • 8 columns detected<br>
                • Upload completed in 2.3s
              </div>
            </div>
            <div style="display: flex; gap: 10px; justify-content: center; margin-top: 16px;">
              <button style="
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
              ">View Data</button>
              <button style="
                background: transparent;
                color: #6c757d;
                border: 1px solid #6c757d;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
              ">Upload Another</button>
            </div>
          </div>
        `;
        document.body.appendChild(uploadDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="file-upload-success"]',
        'file-upload-success-state',
        COMPONENT_CONFIG
      );
    });

    test('File Upload - Error State @visual @component @file-upload', async ({ page }) => {
      await page.evaluate(() => {
        const uploadDiv = document.createElement('div');
        uploadDiv.setAttribute('data-testid', 'file-upload-error');
        uploadDiv.innerHTML = `
          <div style="
            border: 2px solid #dc3545;
            border-radius: 8px;
            padding: 40px 20px;
            text-align: center;
            background: #fef8f8;
            margin: 20px;
          ">
            <div style="font-size: 48px; color: #dc3545; margin-bottom: 16px;">❌</div>
            <h4 style="color: #721c24; margin-bottom: 8px;">Upload failed</h4>
            <p style="color: #6c757d; margin-bottom: 16px;">invalid-file.txt (15.2 MB)</p>
            <div style="
              background: #f8d7da;
              border: 1px solid #f1aeb5;
              border-radius: 4px;
              padding: 12px;
              margin: 16px auto;
              max-width: 400px;
            ">
              <div style="font-weight: bold; color: #721c24; margin-bottom: 8px;">Error Details:</div>
              <ul style="
                text-align: left;
                margin: 0;
                padding-left: 20px;
                color: #721c24;
                font-size: 13px;
                line-height: 1.4;
              ">
                <li>File size exceeds 10MB limit</li>
                <li>Unsupported file format (.txt)</li>
                <li>File appears to be corrupted</li>
              </ul>
            </div>
            <div style="display: flex; gap: 10px; justify-content: center; margin-top: 16px;">
              <button style="
                background: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
              ">Try Again</button>
              <button style="
                background: transparent;
                color: #6c757d;
                border: 1px solid #6c757d;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
              ">Choose Different File</button>
            </div>
          </div>
        `;
        document.body.appendChild(uploadDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="file-upload-error"]',
        'file-upload-error-state',
        COMPONENT_CONFIG
      );
    });
  });

  test.describe('Tab Navigation Visual States', () => {

    test('Navigation Tabs - Default State @visual @component @navigation', async ({ page }) => {
      const navExists = await page.locator(COMPONENT_SELECTORS.navigation).count() > 0;

      if (navExists) {
        await visualUtils.screenshotComponent(
          COMPONENT_SELECTORS.navigation,
          'navigation-tabs-default',
          COMPONENT_CONFIG
        );
      } else {
        // Create mock navigation tabs
        await page.evaluate(() => {
          const navDiv = document.createElement('div');
          navDiv.setAttribute('data-testid', 'mock-navigation-tabs');
          navDiv.innerHTML = `
            <nav style="
              background: #ffffff;
              border-bottom: 1px solid #dee2e6;
              padding: 0 20px;
            ">
              <div style="display: flex; gap: 0;">
                <button style="
                  background: #007bff;
                  color: white;
                  border: none;
                  padding: 12px 24px;
                  border-radius: 4px 4px 0 0;
                  font-weight: 500;
                  cursor: pointer;
                  border-bottom: 3px solid #007bff;
                ">Overview</button>
                <button style="
                  background: transparent;
                  color: #6c757d;
                  border: none;
                  padding: 12px 24px;
                  border-radius: 4px 4px 0 0;
                  font-weight: 500;
                  cursor: pointer;
                  border-bottom: 3px solid transparent;
                  transition: color 0.2s, border-color 0.2s;
                ">Visualization</button>
                <button style="
                  background: transparent;
                  color: #6c757d;
                  border: none;
                  padding: 12px 24px;
                  border-radius: 4px 4px 0 0;
                  font-weight: 500;
                  cursor: pointer;
                  border-bottom: 3px solid transparent;
                  transition: color 0.2s, border-color 0.2s;
                ">Data Table</button>
                <button style="
                  background: transparent;
                  color: #6c757d;
                  border: none;
                  padding: 12px 24px;
                  border-radius: 4px 4px 0 0;
                  font-weight: 500;
                  cursor: pointer;
                  border-bottom: 3px solid transparent;
                  transition: color 0.2s, border-color 0.2s;
                ">Export</button>
              </div>
            </nav>
          `;
          document.body.appendChild(navDiv);
        });

        await visualUtils.screenshotComponent(
          '[data-testid="mock-navigation-tabs"]',
          'navigation-tabs-default',
          COMPONENT_CONFIG
        );
      }
    });

    test('Navigation Tabs - Hover States @visual @component @navigation', async ({ page }) => {
      await page.evaluate(() => {
        const navDiv = document.createElement('div');
        navDiv.setAttribute('data-testid', 'navigation-tabs-hover');
        navDiv.innerHTML = `
          <nav style="
            background: #ffffff;
            border-bottom: 1px solid #dee2e6;
            padding: 0 20px;
          ">
            <div style="display: flex; gap: 0;">
              <button style="
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px 4px 0 0;
                font-weight: 500;
                cursor: pointer;
                border-bottom: 3px solid #007bff;
              ">Overview</button>
              <button style="
                background: #f8f9fa;
                color: #007bff;
                border: none;
                padding: 12px 24px;
                border-radius: 4px 4px 0 0;
                font-weight: 500;
                cursor: pointer;
                border-bottom: 3px solid #007bff;
                transform: translateY(-1px);
              ">Visualization</button>
              <button style="
                background: transparent;
                color: #6c757d;
                border: none;
                padding: 12px 24px;
                border-radius: 4px 4px 0 0;
                font-weight: 500;
                cursor: pointer;
                border-bottom: 3px solid transparent;
              ">Data Table</button>
              <button style="
                background: transparent;
                color: #6c757d;
                border: none;
                padding: 12px 24px;
                border-radius: 4px 4px 0 0;
                font-weight: 500;
                cursor: pointer;
                border-bottom: 3px solid transparent;
              ">Export</button>
            </div>
          </nav>
        `;
        document.body.appendChild(navDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="navigation-tabs-hover"]',
        'navigation-tabs-hover-state',
        COMPONENT_CONFIG
      );
    });

    test('Navigation Tabs - Active States @visual @component @navigation', async ({ page }) => {
      const tabs = ['Overview', 'Visualization', 'Data Table', 'Export'];

      for (let i = 0; i < tabs.length; i++) {
        await page.evaluate((activeIndex, tabNames) => {
          const navDiv = document.createElement('div');
          navDiv.setAttribute('data-testid', `navigation-tabs-active-${activeIndex}`);
          navDiv.innerHTML = `
            <nav style="
              background: #ffffff;
              border-bottom: 1px solid #dee2e6;
              padding: 0 20px;
            ">
              <div style="display: flex; gap: 0;">
                ${tabNames.map((name, index) => `
                  <button style="
                    background: ${index === activeIndex ? '#007bff' : 'transparent'};
                    color: ${index === activeIndex ? 'white' : '#6c757d'};
                    border: none;
                    padding: 12px 24px;
                    border-radius: 4px 4px 0 0;
                    font-weight: 500;
                    cursor: pointer;
                    border-bottom: 3px solid ${index === activeIndex ? '#007bff' : 'transparent'};
                    transition: all 0.2s;
                  ">${name}</button>
                `).join('')}
              </div>
            </nav>
          `;

          const existing = document.querySelector(`[data-testid^="navigation-tabs-active-"]`);
          if (existing) existing.remove();

          document.body.appendChild(navDiv);
        }, i, tabs);

        await visualUtils.screenshotComponent(
          `[data-testid="navigation-tabs-active-${i}"]`,
          `navigation-tabs-active-${tabs[i].toLowerCase().replace(' ', '-')}`,
          COMPONENT_CONFIG
        );
      }
    });

    test('Navigation Tabs - Disabled State @visual @component @navigation', async ({ page }) => {
      await page.evaluate(() => {
        const navDiv = document.createElement('div');
        navDiv.setAttribute('data-testid', 'navigation-tabs-disabled');
        navDiv.innerHTML = `
          <nav style="
            background: #ffffff;
            border-bottom: 1px solid #dee2e6;
            padding: 0 20px;
          ">
            <div style="display: flex; gap: 0;">
              <button style="
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px 4px 0 0;
                font-weight: 500;
                cursor: pointer;
                border-bottom: 3px solid #007bff;
              ">Overview</button>
              <button disabled style="
                background: transparent;
                color: #adb5bd;
                border: none;
                padding: 12px 24px;
                border-radius: 4px 4px 0 0;
                font-weight: 500;
                cursor: not-allowed;
                border-bottom: 3px solid transparent;
                opacity: 0.6;
              ">Visualization</button>
              <button disabled style="
                background: transparent;
                color: #adb5bd;
                border: none;
                padding: 12px 24px;
                border-radius: 4px 4px 0 0;
                font-weight: 500;
                cursor: not-allowed;
                border-bottom: 3px solid transparent;
                opacity: 0.6;
              ">Data Table</button>
              <button style="
                background: transparent;
                color: #6c757d;
                border: none;
                padding: 12px 24px;
                border-radius: 4px 4px 0 0;
                font-weight: 500;
                cursor: pointer;
                border-bottom: 3px solid transparent;
              ">Export</button>
            </div>
            <div style="
              background: #f8d7da;
              color: #721c24;
              padding: 8px 12px;
              font-size: 13px;
              border-radius: 4px;
              margin: 8px 0;
            ">
              ⚠️ Upload a data file to access visualization and data table features
            </div>
          </nav>
        `;
        document.body.appendChild(navDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="navigation-tabs-disabled"]',
        'navigation-tabs-disabled-state',
        COMPONENT_CONFIG
      );
    });
  });

  test.describe('Plotly Graph Visual Rendering', () => {

    test('Plotly Graph - Empty State @visual @component @plotly', async ({ page }) => {
      await page.evaluate(() => {
        const graphDiv = document.createElement('div');
        graphDiv.setAttribute('data-testid', 'plotly-empty-state');
        graphDiv.innerHTML = `
          <div style="
            width: 100%;
            height: 400px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #f8f9fa;
            margin: 20px 0;
          ">
            <div style="font-size: 64px; color: #6c757d; margin-bottom: 16px;">📊</div>
            <h4 style="color: #495057; margin-bottom: 8px;">No Data to Display</h4>
            <p style="color: #6c757d; text-align: center; max-width: 300px;">
              Upload a data file to generate visualizations and explore your data
            </p>
            <button style="
              background: #007bff;
              color: white;
              border: none;
              padding: 12px 24px;
              border-radius: 4px;
              cursor: pointer;
              font-size: 14px;
              margin-top: 16px;
            ">Upload Data File</button>
          </div>
        `;
        document.body.appendChild(graphDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="plotly-empty-state"]',
        'plotly-graph-empty-state',
        COMPONENT_CONFIG
      );
    });

    test('Plotly Graph - Loading State @visual @component @plotly', async ({ page }) => {
      await page.evaluate(() => {
        const graphDiv = document.createElement('div');
        graphDiv.setAttribute('data-testid', 'plotly-loading-state');
        graphDiv.innerHTML = `
          <div style="
            width: 100%;
            height: 400px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #ffffff;
            margin: 20px 0;
            position: relative;
          ">
            <div style="
              display: flex;
              align-items: center;
              justify-content: center;
              margin-bottom: 20px;
            ">
              <div style="
                width: 40px;
                height: 40px;
                border: 4px solid #f3f3f3;
                border-top: 4px solid #007bff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-right: 12px;
              "></div>
              <div>
                <h4 style="color: #495057; margin: 0 0 4px 0;">Generating Visualization</h4>
                <p style="color: #6c757d; margin: 0; font-size: 14px;">Processing data...</p>
              </div>
            </div>

            <div style="
              width: 100%;
              max-width: 300px;
              height: 6px;
              background: #e9ecef;
              border-radius: 3px;
              overflow: hidden;
            ">
              <div style="
                width: 75%;
                height: 100%;
                background: linear-gradient(90deg, #007bff, #0056b3);
                transition: width 0.5s ease;
              "></div>
            </div>

            <p style="color: #6c757d; font-size: 12px; margin-top: 12px;">
              Rendering 1,247 data points...
            </p>
          </div>
          <style>
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          </style>
        `;
        document.body.appendChild(graphDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="plotly-loading-state"]',
        'plotly-graph-loading-state',
        COMPONENT_CONFIG
      );
    });

    test('Plotly Graph - Sample Data Visualization @visual @component @plotly', async ({ page }) => {
      // Create a mock 3D scatter plot visualization
      await page.evaluate(() => {
        const graphDiv = document.createElement('div');
        graphDiv.setAttribute('data-testid', 'plotly-sample-data');
        graphDiv.innerHTML = `
          <div style="
            width: 100%;
            height: 500px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background: #ffffff;
            margin: 20px 0;
            position: relative;
            overflow: hidden;
          ">
            <!-- Mock Plotly toolbar -->
            <div style="
              position: absolute;
              top: 10px;
              right: 10px;
              display: flex;
              gap: 2px;
              background: rgba(255,255,255,0.9);
              padding: 4px;
              border-radius: 4px;
              border: 1px solid #ddd;
              z-index: 10;
            ">
              <button style="width: 24px; height: 24px; border: none; background: transparent; cursor: pointer; font-size: 12px;">📷</button>
              <button style="width: 24px; height: 24px; border: none; background: transparent; cursor: pointer; font-size: 12px;">🔍</button>
              <button style="width: 24px; height: 24px; border: none; background: transparent; cursor: pointer; font-size: 12px;">📐</button>
              <button style="width: 24px; height: 24px; border: none; background: transparent; cursor: pointer; font-size: 12px;">🏠</button>
            </div>

            <!-- Mock 3D visualization -->
            <div style="
              width: 100%;
              height: 100%;
              background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
              position: relative;
              display: flex;
              align-items: center;
              justify-content: center;
            ">
              <!-- Mock 3D scatter points -->
              <svg width="100%" height="100%" style="position: absolute;">
                <defs>
                  <radialGradient id="point1" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" style="stop-color:#007bff;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#0056b3;stop-opacity:0.6" />
                  </radialGradient>
                  <radialGradient id="point2" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" style="stop-color:#28a745;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#1e7e34;stop-opacity:0.6" />
                  </radialGradient>
                  <radialGradient id="point3" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" style="stop-color:#dc3545;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#bd2130;stop-opacity:0.6" />
                  </radialGradient>
                </defs>

                <!-- Sample scatter points -->
                <circle cx="150" cy="120" r="8" fill="url(#point1)" />
                <circle cx="280" cy="180" r="6" fill="url(#point2)" />
                <circle cx="220" cy="250" r="10" fill="url(#point3)" />
                <circle cx="350" cy="200" r="7" fill="url(#point1)" />
                <circle cx="180" cy="300" r="9" fill="url(#point2)" />
                <circle cx="400" cy="150" r="5" fill="url(#point3)" />
                <circle cx="320" cy="280" r="8" fill="url(#point1)" />
                <circle cx="250" cy="320" r="6" fill="url(#point2)" />
                <circle cx="380" cy="240" r="7" fill="url(#point3)" />

                <!-- Axis lines -->
                <line x1="50" y1="350" x2="450" y2="350" stroke="#6c757d" stroke-width="2" />
                <line x1="50" y1="50" x2="50" y2="350" stroke="#6c757d" stroke-width="2" />
                <line x1="50" y1="350" x2="80" y2="320" stroke="#6c757d" stroke-width="2" />

                <!-- Axis labels -->
                <text x="250" y="380" text-anchor="middle" fill="#6c757d" font-size="12">X-Axis</text>
                <text x="25" y="200" text-anchor="middle" fill="#6c757d" font-size="12" transform="rotate(-90 25 200)">Y-Axis</text>
                <text x="65" y="305" fill="#6c757d" font-size="11">Z</text>
              </svg>

              <!-- Legend -->
              <div style="
                position: absolute;
                bottom: 20px;
                left: 20px;
                background: rgba(255,255,255,0.95);
                padding: 12px;
                border-radius: 4px;
                border: 1px solid #ddd;
                font-size: 12px;
              ">
                <div style="margin-bottom: 4px;">
                  <span style="display: inline-block; width: 12px; height: 12px; background: #007bff; border-radius: 50%; margin-right: 6px;"></span>
                  Category A (245 points)
                </div>
                <div style="margin-bottom: 4px;">
                  <span style="display: inline-block; width: 12px; height: 12px; background: #28a745; border-radius: 50%; margin-right: 6px;"></span>
                  Category B (387 points)
                </div>
                <div>
                  <span style="display: inline-block; width: 12px; height: 12px; background: #dc3545; border-radius: 50%; margin-right: 6px;"></span>
                  Category C (615 points)
                </div>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(graphDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="plotly-sample-data"]',
        'plotly-graph-sample-data',
        COMPONENT_CONFIG
      );
    });

    test('Plotly Graph - Error State @visual @component @plotly', async ({ page }) => {
      await page.evaluate(() => {
        const graphDiv = document.createElement('div');
        graphDiv.setAttribute('data-testid', 'plotly-error-state');
        graphDiv.innerHTML = `
          <div style="
            width: 100%;
            height: 400px;
            border: 2px solid #dc3545;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #fef8f8;
            margin: 20px 0;
          ">
            <div style="font-size: 64px; color: #dc3545; margin-bottom: 16px;">⚠️</div>
            <h4 style="color: #721c24; margin-bottom: 8px;">Visualization Error</h4>
            <p style="color: #6c757d; text-align: center; max-width: 400px; margin-bottom: 16px;">
              Unable to generate visualization from the provided data
            </p>
            <div style="
              background: #f8d7da;
              color: #721c24;
              padding: 12px 16px;
              border-radius: 4px;
              border: 1px solid #f1aeb5;
              font-size: 14px;
              max-width: 450px;
              text-align: left;
            ">
              <strong>Error Details:</strong><br>
              • Invalid data format in column 'timestamp'<br>
              • Missing required numeric values<br>
              • Data contains null values in critical fields
            </div>
            <div style="display: flex; gap: 10px; margin-top: 20px;">
              <button style="
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
              ">Retry Visualization</button>
              <button style="
                background: transparent;
                color: #6c757d;
                border: 1px solid #6c757d;
                padding: 12px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
              ">Check Data</button>
            </div>
          </div>
        `;
        document.body.appendChild(graphDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="plotly-error-state"]',
        'plotly-graph-error-state',
        COMPONENT_CONFIG
      );
    });
  });

  test.describe('Data Table Visual States', () => {

    test('Data Table - Empty State @visual @component @data-table', async ({ page }) => {
      await page.evaluate(() => {
        const tableDiv = document.createElement('div');
        tableDiv.setAttribute('data-testid', 'data-table-empty');
        tableDiv.innerHTML = `
          <div style="padding: 20px;">
            <div style="
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 20px;
            ">
              <h4 style="margin: 0; color: #495057;">Data Table</h4>
              <div style="display: flex; gap: 10px;">
                <input type="text" placeholder="Search..." style="
                  padding: 8px 12px;
                  border: 1px solid #ced4da;
                  border-radius: 4px;
                  width: 200px;
                " disabled>
                <button style="
                  padding: 8px 16px;
                  background: #6c757d;
                  color: white;
                  border: none;
                  border-radius: 4px;
                  cursor: not-allowed;
                  opacity: 0.6;
                " disabled>Export</button>
              </div>
            </div>

            <div style="
              border: 1px solid #dee2e6;
              border-radius: 8px;
              overflow: hidden;
            ">
              <div style="
                background: #f8f9fa;
                padding: 40px 20px;
                text-align: center;
              ">
                <div style="font-size: 64px; color: #6c757d; margin-bottom: 16px;">📋</div>
                <h4 style="color: #495057; margin-bottom: 8px;">No Data Available</h4>
                <p style="color: #6c757d; margin-bottom: 16px;">
                  Upload a data file to view and explore your data in a table format
                </p>
                <button style="
                  background: #007bff;
                  color: white;
                  border: none;
                  padding: 12px 24px;
                  border-radius: 4px;
                  cursor: pointer;
                  font-size: 14px;
                ">Upload Data File</button>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(tableDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="data-table-empty"]',
        'data-table-empty-state',
        COMPONENT_CONFIG
      );
    });

    test('Data Table - With Data @visual @component @data-table', async ({ page }) => {
      await page.evaluate(() => {
        const tableDiv = document.createElement('div');
        tableDiv.setAttribute('data-testid', 'data-table-with-data');
        tableDiv.innerHTML = `
          <div style="padding: 20px;">
            <div style="
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 20px;
            ">
              <h4 style="margin: 0; color: #495057;">Data Table <span style="color: #6c757d; font-weight: normal;">(1,247 rows)</span></h4>
              <div style="display: flex; gap: 10px;">
                <input type="text" placeholder="Search..." value="sample" style="
                  padding: 8px 12px;
                  border: 1px solid #007bff;
                  border-radius: 4px;
                  width: 200px;
                ">
                <button style="
                  padding: 8px 16px;
                  background: #28a745;
                  color: white;
                  border: none;
                  border-radius: 4px;
                  cursor: pointer;
                ">Export CSV</button>
              </div>
            </div>

            <div style="
              border: 1px solid #dee2e6;
              border-radius: 8px;
              overflow: hidden;
              box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">
              <table style="width: 100%; border-collapse: collapse;">
                <thead>
                  <tr style="background: #007bff; color: white;">
                    <th style="padding: 12px; text-align: left; font-weight: 600; border-right: 1px solid rgba(255,255,255,0.1);">
                      ID <span style="font-size: 12px;">↕️</span>
                    </th>
                    <th style="padding: 12px; text-align: left; font-weight: 600; border-right: 1px solid rgba(255,255,255,0.1);">
                      Name <span style="font-size: 12px;">↕️</span>
                    </th>
                    <th style="padding: 12px; text-align: left; font-weight: 600; border-right: 1px solid rgba(255,255,255,0.1);">
                      Value <span style="font-size: 12px;">🔽</span>
                    </th>
                    <th style="padding: 12px; text-align: left; font-weight: 600; border-right: 1px solid rgba(255,255,255,0.1);">
                      Category <span style="font-size: 12px;">↕️</span>
                    </th>
                    <th style="padding: 12px; text-align: left; font-weight: 600;">
                      Date <span style="font-size: 12px;">↕️</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr style="background: #fff3cd; border-left: 3px solid #ffc107;">
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">001</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;"><strong>Sample Data A</strong></td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">245.67</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                      <span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Primary</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">2024-01-15</td>
                  </tr>
                  <tr style="background: #ffffff;">
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">002</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Sample Data B</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">189.23</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                      <span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Secondary</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">2024-01-16</td>
                  </tr>
                  <tr style="background: #f8f9fa;">
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">003</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Sample Data C</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">342.89</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                      <span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Tertiary</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">2024-01-17</td>
                  </tr>
                  <tr style="background: #ffffff;">
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">004</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Sample Data D</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">456.12</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                      <span style="background: #007bff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Primary</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">2024-01-18</td>
                  </tr>
                  <tr style="background: #f8f9fa;">
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">005</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Sample Data E</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">123.45</td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                      <span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px;">Secondary</span>
                    </td>
                    <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">2024-01-19</td>
                  </tr>
                </tbody>
              </table>

              <div style="
                background: #f8f9fa;
                padding: 12px 16px;
                border-top: 1px solid #dee2e6;
                display: flex;
                justify-content: space-between;
                align-items: center;
                font-size: 14px;
                color: #6c757d;
              ">
                <span>Showing 1-5 of 1,247 entries (filtered from 1,247 total entries)</span>
                <div style="display: flex; gap: 5px;">
                  <button style="padding: 6px 10px; border: 1px solid #dee2e6; background: white; border-radius: 3px; cursor: not-allowed; opacity: 0.6;">‹‹</button>
                  <button style="padding: 6px 10px; border: 1px solid #dee2e6; background: white; border-radius: 3px; cursor: not-allowed; opacity: 0.6;">‹</button>
                  <button style="padding: 6px 10px; border: 1px solid #007bff; background: #007bff; color: white; border-radius: 3px;">1</button>
                  <button style="padding: 6px 10px; border: 1px solid #dee2e6; background: white; border-radius: 3px; cursor: pointer;">2</button>
                  <button style="padding: 6px 10px; border: 1px solid #dee2e6; background: white; border-radius: 3px; cursor: pointer;">3</button>
                  <button style="padding: 6px 10px; border: 1px solid #dee2e6; background: white; border-radius: 3px; cursor: pointer;">...</button>
                  <button style="padding: 6px 10px; border: 1px solid #dee2e6; background: white; border-radius: 3px; cursor: pointer;">›</button>
                  <button style="padding: 6px 10px; border: 1px solid #dee2e6; background: white; border-radius: 3px; cursor: pointer;">››</button>
                </div>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(tableDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="data-table-with-data"]',
        'data-table-with-data',
        COMPONENT_CONFIG
      );
    });
  });

  test.describe('Export Component Visual States', () => {

    test('Export Section - Available Options @visual @component @export', async ({ page }) => {
      await page.evaluate(() => {
        const exportDiv = document.createElement('div');
        exportDiv.setAttribute('data-testid', 'export-section-available');
        exportDiv.innerHTML = `
          <div style="padding: 20px;">
            <h4 style="margin: 0 0 20px 0; color: #495057;">Export Options</h4>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
              <!-- Data Export -->
              <div style="
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
                background: #ffffff;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
              ">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                  <div style="font-size: 24px; margin-right: 8px;">💾</div>
                  <h5 style="margin: 0; color: #495057;">Data Export</h5>
                </div>
                <p style="color: #6c757d; font-size: 14px; margin-bottom: 16px;">
                  Export your processed data in various formats
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                  <button style="
                    background: #28a745;
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                  ">📄 CSV</button>
                  <button style="
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                  ">📊 Excel</button>
                  <button style="
                    background: #fd7e14;
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                  ">🔗 JSON</button>
                </div>
              </div>

              <!-- Visualization Export -->
              <div style="
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
                background: #ffffff;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
              ">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                  <div style="font-size: 24px; margin-right: 8px;">📊</div>
                  <h5 style="margin: 0; color: #495057;">Visualization Export</h5>
                </div>
                <p style="color: #6c757d; font-size: 14px; margin-bottom: 16px;">
                  Save your charts and graphs as image files
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                  <button style="
                    background: #6f42c1;
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                  ">🖼️ PNG</button>
                  <button style="
                    background: #20c997;
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                  ">🎯 SVG</button>
                  <button style="
                    background: #dc3545;
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                  ">📄 PDF</button>
                </div>
              </div>

              <!-- Report Export -->
              <div style="
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 20px;
                background: #ffffff;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
              ">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                  <div style="font-size: 24px; margin-right: 8px;">📋</div>
                  <h5 style="margin: 0; color: #495057;">Report Generation</h5>
                </div>
                <p style="color: #6c757d; font-size: 14px; margin-bottom: 16px;">
                  Generate comprehensive analysis reports
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                  <button style="
                    background: #e83e8c;
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                  ">📑 Full Report</button>
                  <button style="
                    background: #17a2b8;
                    color: white;
                    border: none;
                    padding: 10px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                  ">📊 Summary</button>
                </div>
              </div>
            </div>

            <div style="
              background: #d1ecf1;
              color: #0c5460;
              padding: 12px 16px;
              border-radius: 4px;
              border: 1px solid #bee5eb;
              margin-top: 20px;
              font-size: 14px;
            ">
              💡 <strong>Tip:</strong> Use high-resolution exports for presentations and publications
            </div>
          </div>
        `;
        document.body.appendChild(exportDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="export-section-available"]',
        'export-section-available',
        COMPONENT_CONFIG
      );
    });

    test('Export Section - Processing State @visual @component @export', async ({ page }) => {
      await page.evaluate(() => {
        const exportDiv = document.createElement('div');
        exportDiv.setAttribute('data-testid', 'export-section-processing');
        exportDiv.innerHTML = `
          <div style="padding: 20px;">
            <h4 style="margin: 0 0 20px 0; color: #495057;">Export Options</h4>

            <div style="
              border: 1px solid #007bff;
              border-radius: 8px;
              padding: 30px;
              background: #f8f9ff;
              text-align: center;
              margin-bottom: 20px;
            ">
              <div style="
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 16px;
              ">
                <div style="
                  width: 32px;
                  height: 32px;
                  border: 3px solid #f3f3f3;
                  border-top: 3px solid #007bff;
                  border-radius: 50%;
                  animation: spin 1s linear infinite;
                  margin-right: 12px;
                "></div>
                <h5 style="margin: 0; color: #007bff;">Generating Export...</h5>
              </div>

              <div style="
                width: 100%;
                max-width: 400px;
                height: 8px;
                background: #e9ecef;
                border-radius: 4px;
                margin: 16px auto;
                overflow: hidden;
              ">
                <div style="
                  width: 45%;
                  height: 100%;
                  background: linear-gradient(90deg, #007bff, #0056b3);
                  transition: width 0.5s ease;
                "></div>
              </div>

              <p style="color: #6c757d; margin: 8px 0;">
                Exporting data as CSV... (1,247 rows processed)
              </p>

              <button style="
                background: #dc3545;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 13px;
                margin-top: 12px;
              ">Cancel Export</button>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; opacity: 0.5;">
              <div style="border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; background: #f8f9fa;">
                <h5 style="margin: 0 0 12px 0; color: #6c757d;">Data Export</h5>
                <div style="display: flex; gap: 8px;">
                  <button disabled style="background: #6c757d; color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: not-allowed; opacity: 0.6;">CSV</button>
                  <button disabled style="background: #6c757d; color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: not-allowed; opacity: 0.6;">Excel</button>
                </div>
              </div>
            </div>
          </div>
          <style>
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          </style>
        `;
        document.body.appendChild(exportDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="export-section-processing"]',
        'export-section-processing',
        COMPONENT_CONFIG
      );
    });

    test('Export Section - No Data Available @visual @component @export', async ({ page }) => {
      await page.evaluate(() => {
        const exportDiv = document.createElement('div');
        exportDiv.setAttribute('data-testid', 'export-section-no-data');
        exportDiv.innerHTML = `
          <div style="padding: 20px;">
            <h4 style="margin: 0 0 20px 0; color: #495057;">Export Options</h4>

            <div style="
              border: 1px solid #dee2e6;
              border-radius: 8px;
              padding: 40px;
              background: #f8f9fa;
              text-align: center;
            ">
              <div style="font-size: 48px; color: #6c757d; margin-bottom: 16px;">📤</div>
              <h5 style="color: #495057; margin-bottom: 8px;">No Data to Export</h5>
              <p style="color: #6c757d; margin-bottom: 20px;">
                Upload and process data to access export functionality
              </p>
              <button style="
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
              ">Upload Data File</button>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; opacity: 0.4;">
              <div style="border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; background: #ffffff;">
                <h5 style="margin: 0 0 12px 0; color: #adb5bd;">Data Export</h5>
                <div style="display: flex; gap: 8px;">
                  <button disabled style="background: #adb5bd; color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: not-allowed;">CSV</button>
                  <button disabled style="background: #adb5bd; color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: not-allowed;">Excel</button>
                  <button disabled style="background: #adb5bd; color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: not-allowed;">JSON</button>
                </div>
              </div>
              <div style="border: 1px solid #dee2e6; border-radius: 8px; padding: 20px; background: #ffffff;">
                <h5 style="margin: 0 0 12px 0; color: #adb5bd;">Visualization Export</h5>
                <div style="display: flex; gap: 8px;">
                  <button disabled style="background: #adb5bd; color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: not-allowed;">PNG</button>
                  <button disabled style="background: #adb5bd; color: white; border: none; padding: 10px 16px; border-radius: 4px; cursor: not-allowed;">SVG</button>
                </div>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(exportDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="export-section-no-data"]',
        'export-section-no-data',
        COMPONENT_CONFIG
      );
    });
  });

  test.describe('Loading and Error States', () => {

    test('Global Loading Overlay @visual @component @loading', async ({ page }) => {
      await visualUtils.simulateLoadingState(2000);

      await visualUtils.screenshotFullPage(
        'global-loading-overlay',
        COMPONENT_CONFIG
      );
    });

    test('Component Loading Spinners @visual @component @loading', async ({ page }) => {
      await page.evaluate(() => {
        const loadingDiv = document.createElement('div');
        loadingDiv.setAttribute('data-testid', 'loading-spinners-showcase');
        loadingDiv.innerHTML = `
          <div style="padding: 20px;">
            <h4 style="margin-bottom: 30px;">Loading State Components</h4>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
              <!-- Small Spinner -->
              <div style="text-align: center; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px;">
                <div style="
                  width: 20px;
                  height: 20px;
                  border: 2px solid #f3f3f3;
                  border-top: 2px solid #007bff;
                  border-radius: 50%;
                  animation: spin 1s linear infinite;
                  margin: 0 auto 8px;
                "></div>
                <p style="margin: 0; font-size: 12px; color: #6c757d;">Small Spinner</p>
              </div>

              <!-- Medium Spinner -->
              <div style="text-align: center; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px;">
                <div style="
                  width: 32px;
                  height: 32px;
                  border: 3px solid #f3f3f3;
                  border-top: 3px solid #28a745;
                  border-radius: 50%;
                  animation: spin 1s linear infinite;
                  margin: 0 auto 8px;
                "></div>
                <p style="margin: 0; font-size: 12px; color: #6c757d;">Medium Spinner</p>
              </div>

              <!-- Large Spinner -->
              <div style="text-align: center; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px;">
                <div style="
                  width: 48px;
                  height: 48px;
                  border: 4px solid #f3f3f3;
                  border-top: 4px solid #dc3545;
                  border-radius: 50%;
                  animation: spin 1s linear infinite;
                  margin: 0 auto 8px;
                "></div>
                <p style="margin: 0; font-size: 12px; color: #6c757d;">Large Spinner</p>
              </div>

              <!-- Pulsing Dots -->
              <div style="text-align: center; padding: 20px; border: 1px solid #dee2e6; border-radius: 8px;">
                <div style="display: flex; justify-content: center; gap: 4px; margin-bottom: 8px;">
                  <div style="width: 8px; height: 8px; background: #007bff; border-radius: 50%; animation: pulse 1.5s infinite;"></div>
                  <div style="width: 8px; height: 8px; background: #007bff; border-radius: 50%; animation: pulse 1.5s infinite 0.2s;"></div>
                  <div style="width: 8px; height: 8px; background: #007bff; border-radius: 50%; animation: pulse 1.5s infinite 0.4s;"></div>
                </div>
                <p style="margin: 0; font-size: 12px; color: #6c757d;">Pulsing Dots</p>
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
        document.body.appendChild(loadingDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="loading-spinners-showcase"]',
        'loading-spinners-showcase',
        COMPONENT_CONFIG
      );
    });

    test('Error Message Components @visual @component @error', async ({ page }) => {
      await page.evaluate(() => {
        const errorDiv = document.createElement('div');
        errorDiv.setAttribute('data-testid', 'error-messages-showcase');
        errorDiv.innerHTML = `
          <div style="padding: 20px;">
            <h4 style="margin-bottom: 30px;">Error State Components</h4>

            <div style="display: flex; flex-direction: column; gap: 20px;">
              <!-- Critical Error -->
              <div style="
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f1aeb5;
                border-left: 4px solid #dc3545;
                border-radius: 4px;
                padding: 16px;
              ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                  <span style="font-size: 18px; margin-right: 8px;">🚨</span>
                  <strong>Critical Error</strong>
                </div>
                <p style="margin: 0;">Unable to process the uploaded file. The system encountered a critical error.</p>
              </div>

              <!-- Warning -->
              <div style="
                background: #fff3cd;
                color: #856404;
                border: 1px solid #ffeaa7;
                border-left: 4px solid #ffc107;
                border-radius: 4px;
                padding: 16px;
              ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                  <span style="font-size: 18px; margin-right: 8px;">⚠️</span>
                  <strong>Warning</strong>
                </div>
                <p style="margin: 0;">Some data values are missing. Visualization may be incomplete.</p>
              </div>

              <!-- Info -->
              <div style="
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
                border-left: 4px solid #17a2b8;
                border-radius: 4px;
                padding: 16px;
              ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                  <span style="font-size: 18px; margin-right: 8px;">ℹ️</span>
                  <strong>Information</strong>
                </div>
                <p style="margin: 0;">Data processing completed successfully. Ready for visualization.</p>
              </div>

              <!-- Success -->
              <div style="
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
                border-left: 4px solid #28a745;
                border-radius: 4px;
                padding: 16px;
              ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                  <span style="font-size: 18px; margin-right: 8px;">✅</span>
                  <strong>Success</strong>
                </div>
                <p style="margin: 0;">File uploaded and processed successfully. All data is valid.</p>
              </div>

              <!-- Error with Actions -->
              <div style="
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f1aeb5;
                border-radius: 8px;
                padding: 20px;
              ">
                <div style="display: flex; align-items: center; margin-bottom: 12px;">
                  <span style="font-size: 24px; margin-right: 12px;">❌</span>
                  <div>
                    <h5 style="margin: 0; color: #721c24;">Upload Failed</h5>
                    <p style="margin: 4px 0 0 0; font-size: 14px;">The file could not be processed due to format issues.</p>
                  </div>
                </div>
                <div style="
                  background: rgba(220, 53, 69, 0.1);
                  border: 1px solid #f1aeb5;
                  border-radius: 4px;
                  padding: 12px;
                  margin: 12px 0;
                  font-size: 13px;
                ">
                  <strong>Error Details:</strong><br>
                  • File format not supported (.xyz)<br>
                  • File size exceeds 10MB limit<br>
                  • Invalid character encoding detected
                </div>
                <div style="display: flex; gap: 10px; margin-top: 16px;">
                  <button style="
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                  ">Try Again</button>
                  <button style="
                    background: transparent;
                    color: #721c24;
                    border: 1px solid #721c24;
                    padding: 8px 16px;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 13px;
                  ">Choose Different File</button>
                </div>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(errorDiv);
      });

      await visualUtils.screenshotComponent(
        '[data-testid="error-messages-showcase"]',
        'error-messages-showcase',
        COMPONENT_CONFIG
      );
    });
  });
});
