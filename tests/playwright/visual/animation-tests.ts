/**
 * Animation and Transition Visual Tests
 * Comprehensive testing of animations, transitions, and interactive feedback
 */

import { test, expect } from '@playwright/test';
import { VisualTestUtils } from './visual-utils';
import {
  COMPONENT_SELECTORS,
  DEFAULT_VISUAL_CONFIG,
  ANIMATION_DURATIONS,
  RESPONSIVE_VIEWPORTS
} from './visual-config';

// Animation-specific configuration
const ANIMATION_CONFIG = {
  ...DEFAULT_VISUAL_CONFIG,
  threshold: 0.15, // More lenient for animations
  maxDiffPixels: 200,
  animations: 'allow' as const // Allow animations for testing
};

const STATIC_CONFIG = {
  ...DEFAULT_VISUAL_CONFIG,
  threshold: 0.1,
  maxDiffPixels: 100,
  animations: 'disabled' as const
};

test.describe('Animation and Transition Visual Tests', () => {
  let visualUtils: VisualTestUtils;

  test.beforeEach(async ({ page }) => {
    visualUtils = new VisualTestUtils(page);

    // Navigate to the application
    await page.goto('http://localhost:8050', { waitUntil: 'networkidle' });

    // Wait for initial page load
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(500);
  });

  test.describe('Theme Transition Animations', () => {

    test('Theme Transition Animation Sequence @visual @animation @theme', async ({ page }) => {
      // Enable animations for this test
      await page.evaluate(() => {
        // Remove any animation-disabling styles
        const styles = document.querySelectorAll('style');
        styles.forEach(style => {
          if (style.textContent && style.textContent.includes('animation-duration: 0s')) {
            style.remove();
          }
        });
      });

      // Create animated theme switcher
      await page.evaluate(() => {
        const switcherDiv = document.createElement('div');
        switcherDiv.setAttribute('data-testid', 'animated-theme-switcher');
        switcherDiv.innerHTML = `
          <div id="theme-container" style="
            padding: 40px;
            background: var(--bg-color, #ffffff);
            color: var(--text-color, #212529);
            border-radius: 12px;
            margin: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            --bg-color: #ffffff;
            --text-color: #212529;
            --primary-color: #007bff;
            --border-color: #dee2e6;
          ">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
              <h3 style="margin: 0; transition: color 0.3s ease;">Theme Transition Demo</h3>
              <div style="
                position: relative;
                width: 60px;
                height: 30px;
                background: var(--border-color);
                border-radius: 15px;
                cursor: pointer;
                transition: background-color 0.3s ease;
                border: 2px solid var(--border-color);
              " id="theme-toggle">
                <div style="
                  position: absolute;
                  top: 2px;
                  left: 2px;
                  width: 22px;
                  height: 22px;
                  background: var(--primary-color);
                  border-radius: 50%;
                  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                " id="toggle-knob"></div>
              </div>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
              <div style="
                background: var(--primary-color);
                color: white;
                padding: 20px;
                border-radius: 8px;
                transition: all 0.3s ease;
                transform: translateY(0);
              ">
                <h4 style="margin: 0 0 8px 0;">Primary Card</h4>
                <p style="margin: 0; opacity: 0.9;">This card demonstrates color transitions</p>
              </div>
              <div style="
                background: transparent;
                color: var(--text-color);
                padding: 20px;
                border: 2px solid var(--border-color);
                border-radius: 8px;
                transition: all 0.3s ease;
              ">
                <h4 style="margin: 0 0 8px 0;">Secondary Card</h4>
                <p style="margin: 0;">Border and text color transitions</p>
              </div>
            </div>

            <div style="margin-top: 30px;">
              <div style="
                width: 100%;
                height: 8px;
                background: var(--border-color);
                border-radius: 4px;
                overflow: hidden;
                transition: background-color 0.3s ease;
              ">
                <div style="
                  width: 70%;
                  height: 100%;
                  background: var(--primary-color);
                  transition: background-color 0.3s ease;
                "></div>
              </div>
              <p style="
                margin: 8px 0 0 0;
                font-size: 14px;
                color: var(--text-color);
                transition: color 0.3s ease;
              ">Progress indicator with theme colors</p>
            </div>
          </div>

          <script>
            let isDark = false;
            const toggle = document.getElementById('theme-toggle');
            const container = document.getElementById('theme-container');
            const knob = document.getElementById('toggle-knob');

            toggle.addEventListener('click', function() {
              isDark = !isDark;

              if (isDark) {
                container.style.setProperty('--bg-color', '#1a1a1a');
                container.style.setProperty('--text-color', '#ffffff');
                container.style.setProperty('--primary-color', '#0d6efd');
                container.style.setProperty('--border-color', '#404040');
                knob.style.transform = 'translateX(28px)';
              } else {
                container.style.setProperty('--bg-color', '#ffffff');
                container.style.setProperty('--text-color', '#212529');
                container.style.setProperty('--primary-color', '#007bff');
                container.style.setProperty('--border-color', '#dee2e6');
                knob.style.transform = 'translateX(0px)';
              }
            });
          </script>
        `;
        document.body.appendChild(switcherDiv);
      });

      // Capture before state
      await visualUtils.screenshotComponent(
        '[data-testid="animated-theme-switcher"]',
        'theme-transition-light-state',
        STATIC_CONFIG
      );

      // Trigger transition
      await page.click('#theme-toggle');

      // Capture mid-transition (if possible)
      await page.waitForTimeout(150); // Half of transition duration
      await visualUtils.screenshotComponent(
        '[data-testid="animated-theme-switcher"]',
        'theme-transition-mid-state',
        ANIMATION_CONFIG
      );

      // Wait for transition to complete
      await page.waitForTimeout(ANIMATION_DURATIONS.themeTransition);

      // Capture after state
      await visualUtils.screenshotComponent(
        '[data-testid="animated-theme-switcher"]',
        'theme-transition-dark-state',
        STATIC_CONFIG
      );
    });

    test('Smooth Color Transition Effects @visual @animation @theme', async ({ page }) => {
      await page.evaluate(() => {
        const colorDiv = document.createElement('div');
        colorDiv.setAttribute('data-testid', 'smooth-color-transitions');
        colorDiv.innerHTML = `
          <div style="padding: 20px;">
            <h4>Smooth Color Transition Effects</h4>

            <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 20px;">
              <button class="transition-btn" style="
                background: #007bff;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                transition: all 0.3s ease;
                transform: translateY(0);
                box-shadow: 0 2px 4px rgba(0, 123, 255, 0.3);
              " onmouseover="
                this.style.background='#0056b3';
                this.style.transform='translateY(-2px)';
                this.style.boxShadow='0 4px 8px rgba(0, 86, 179, 0.4)';
              " onmouseout="
                this.style.background='#007bff';
                this.style.transform='translateY(0)';
                this.style.boxShadow='0 2px 4px rgba(0, 123, 255, 0.3)';
              ">Hover Effect</button>

              <div class="color-morph" style="
                width: 120px;
                height: 60px;
                background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
                border-radius: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.4s ease;
                animation: colorShift 3s infinite;
              ">Morphing</div>

              <div style="
                width: 100px;
                height: 100px;
                border-radius: 50%;
                background: conic-gradient(from 0deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57, #ff9ff3, #ff6b6b);
                animation: rotate 4s linear infinite;
                display: flex;
                align-items: center;
                justify-content: center;
              ">
                <div style="
                  width: 80px;
                  height: 80px;
                  background: white;
                  border-radius: 50%;
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  font-size: 12px;
                  font-weight: bold;
                  color: #333;
                ">Spinning</div>
              </div>
            </div>

            <div style="margin-top: 40px;">
              <h5>Gradient Transitions</h5>
              <div style="
                width: 100%;
                height: 60px;
                background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                border-radius: 8px;
                animation: gradientShift 4s ease-in-out infinite;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
              ">Animated Gradient Background</div>
            </div>
          </div>

          <style>
            @keyframes colorShift {
              0% { background: linear-gradient(45deg, #ff6b6b, #4ecdc4); }
              25% { background: linear-gradient(45deg, #4ecdc4, #45b7d1); }
              50% { background: linear-gradient(45deg, #45b7d1, #96ceb4); }
              75% { background: linear-gradient(45deg, #96ceb4, #feca57); }
              100% { background: linear-gradient(45deg, #feca57, #ff6b6b); }
            }

            @keyframes rotate {
              from { transform: rotate(0deg); }
              to { transform: rotate(360deg); }
            }

            @keyframes gradientShift {
              0% { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); }
              25% { background: linear-gradient(90deg, #f093fb 0%, #f5576c 100%); }
              50% { background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); }
              75% { background: linear-gradient(90deg, #43e97b 0%, #38f9d7 100%); }
              100% { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); }
            }

            .color-morph:hover {
              transform: scale(1.1);
              filter: brightness(1.1);
            }
          </style>
        `;
        document.body.appendChild(colorDiv);
      });

      // Wait for animations to start
      await page.waitForTimeout(500);

      // Capture at different animation phases
      await visualUtils.screenshotComponent(
        '[data-testid="smooth-color-transitions"]',
        'color-transitions-phase-1',
        ANIMATION_CONFIG
      );

      await page.waitForTimeout(1000);
      await visualUtils.screenshotComponent(
        '[data-testid="smooth-color-transitions"]',
        'color-transitions-phase-2',
        ANIMATION_CONFIG
      );

      await page.waitForTimeout(1000);
      await visualUtils.screenshotComponent(
        '[data-testid="smooth-color-transitions"]',
        'color-transitions-phase-3',
        ANIMATION_CONFIG
      );
    });
  });

  test.describe('Loading Animation Consistency', () => {

    test('Loading Spinners Animation States @visual @animation @loading', async ({ page }) => {
      await page.evaluate(() => {
        const loadingDiv = document.createElement('div');
        loadingDiv.setAttribute('data-testid', 'loading-animations');
        loadingDiv.innerHTML = `
          <div style="padding: 40px;">
            <h4>Loading Animation States</h4>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 30px; margin-top: 30px;">
              <!-- Classic Spinner -->
              <div style="text-align: center;">
                <div style="
                  width: 50px;
                  height: 50px;
                  border: 5px solid #f3f3f3;
                  border-top: 5px solid #007bff;
                  border-radius: 50%;
                  animation: spin 1s linear infinite;
                  margin: 0 auto 15px;
                "></div>
                <h6>Classic Spinner</h6>
                <p style="font-size: 12px; color: #666;">1s linear infinite</p>
              </div>

              <!-- Pulsing Circle -->
              <div style="text-align: center;">
                <div style="
                  width: 50px;
                  height: 50px;
                  background: #28a745;
                  border-radius: 50%;
                  animation: pulse 1.5s ease-in-out infinite;
                  margin: 0 auto 15px;
                "></div>
                <h6>Pulsing Circle</h6>
                <p style="font-size: 12px; color: #666;">1.5s ease-in-out infinite</p>
              </div>

              <!-- Bouncing Dots -->
              <div style="text-align: center;">
                <div style="display: flex; justify-content: center; gap: 8px; margin: 0 auto 15px; width: 70px;">
                  <div style="width: 12px; height: 12px; background: #dc3545; border-radius: 50%; animation: bounce 1.4s ease-in-out infinite both; animation-delay: -0.32s;"></div>
                  <div style="width: 12px; height: 12px; background: #dc3545; border-radius: 50%; animation: bounce 1.4s ease-in-out infinite both; animation-delay: -0.16s;"></div>
                  <div style="width: 12px; height: 12px; background: #dc3545; border-radius: 50%; animation: bounce 1.4s ease-in-out infinite both;"></div>
                </div>
                <h6>Bouncing Dots</h6>
                <p style="font-size: 12px; color: #666;">1.4s staggered bounce</p>
              </div>

              <!-- Growing Bars -->
              <div style="text-align: center;">
                <div style="display: flex; justify-content: center; align-items: flex-end; gap: 4px; height: 50px; margin-bottom: 15px;">
                  <div style="width: 6px; background: #ffc107; animation: grow 1.2s ease-in-out infinite; animation-delay: 0s;"></div>
                  <div style="width: 6px; background: #ffc107; animation: grow 1.2s ease-in-out infinite; animation-delay: 0.1s;"></div>
                  <div style="width: 6px; background: #ffc107; animation: grow 1.2s ease-in-out infinite; animation-delay: 0.2s;"></div>
                  <div style="width: 6px; background: #ffc107; animation: grow 1.2s ease-in-out infinite; animation-delay: 0.3s;"></div>
                  <div style="width: 6px; background: #ffc107; animation: grow 1.2s ease-in-out infinite; animation-delay: 0.4s;"></div>
                </div>
                <h6>Growing Bars</h6>
                <p style="font-size: 12px; color: #666;">1.2s staggered growth</p>
              </div>

              <!-- Rotating Squares -->
              <div style="text-align: center;">
                <div style="
                  width: 50px;
                  height: 50px;
                  background: #6f42c1;
                  margin: 0 auto 15px;
                  animation: rotateSquare 2s infinite ease-in-out;
                "></div>
                <h6>Rotating Square</h6>
                <p style="font-size: 12px; color: #666;">2s ease-in-out infinite</p>
              </div>

              <!-- Wave Effect -->
              <div style="text-align: center;">
                <div style="display: flex; justify-content: center; align-items: center; height: 50px; margin-bottom: 15px;">
                  <div style="
                    width: 40px;
                    height: 40px;
                    border: 3px solid #17a2b8;
                    border-radius: 50%;
                    border-top-color: transparent;
                    animation: wave 1.5s linear infinite;
                  "></div>
                </div>
                <h6>Wave Spinner</h6>
                <p style="font-size: 12px; color: #666;">1.5s linear wave</p>
              </div>
            </div>
          </div>

          <style>
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }

            @keyframes pulse {
              0%, 100% { transform: scale(0.5); opacity: 1; }
              50% { transform: scale(1.2); opacity: 0.7; }
            }

            @keyframes bounce {
              0%, 80%, 100% { transform: scale(0); }
              40% { transform: scale(1); }
            }

            @keyframes grow {
              0%, 40%, 100% { height: 10px; }
              20% { height: 50px; }
            }

            @keyframes rotateSquare {
              0% { transform: perspective(120px) rotateX(0deg) rotateY(0deg); }
              50% { transform: perspective(120px) rotateX(-180.1deg) rotateY(0deg); }
              100% { transform: perspective(120px) rotateX(-180deg) rotateY(-179.9deg); }
            }

            @keyframes wave {
              0% { transform: rotate(0deg); border-width: 3px; }
              50% { transform: rotate(180deg); border-width: 1px; }
              100% { transform: rotate(360deg); border-width: 3px; }
            }
          </style>
        `;
        document.body.appendChild(loadingDiv);
      });

      // Capture different animation phases
      for (let i = 0; i < 4; i++) {
        await page.waitForTimeout(500);
        await visualUtils.screenshotComponent(
          '[data-testid="loading-animations"]',
          `loading-animations-phase-${i + 1}`,
          ANIMATION_CONFIG
        );
      }
    });

    test('Progress Bar Animations @visual @animation @loading', async ({ page }) => {
      await page.evaluate(() => {
        const progressDiv = document.createElement('div');
        progressDiv.setAttribute('data-testid', 'progress-animations');
        progressDiv.innerHTML = `
          <div style="padding: 40px;">
            <h4>Progress Bar Animations</h4>

            <div style="display: flex; flex-direction: column; gap: 30px; margin-top: 30px;">
              <!-- Linear Progress -->
              <div>
                <h6>Linear Progress (Determinate)</h6>
                <div style="
                  width: 100%;
                  height: 8px;
                  background: #e9ecef;
                  border-radius: 4px;
                  overflow: hidden;
                  margin: 10px 0;
                ">
                  <div style="
                    height: 100%;
                    background: #007bff;
                    width: 0%;
                    animation: progressFill 3s ease-out forwards;
                    border-radius: 4px;
                  "></div>
                </div>
                <p style="font-size: 12px; color: #666;">Fills over 3 seconds</p>
              </div>

              <!-- Indeterminate Progress -->
              <div>
                <h6>Indeterminate Progress</h6>
                <div style="
                  width: 100%;
                  height: 8px;
                  background: #e9ecef;
                  border-radius: 4px;
                  overflow: hidden;
                  margin: 10px 0;
                  position: relative;
                ">
                  <div style="
                    position: absolute;
                    height: 100%;
                    width: 30%;
                    background: linear-gradient(90deg, transparent, #28a745, transparent);
                    animation: indeterminateProgress 2s ease-in-out infinite;
                    border-radius: 4px;
                  "></div>
                </div>
                <p style="font-size: 12px; color: #666;">Continuous sliding animation</p>
              </div>

              <!-- Striped Progress -->
              <div>
                <h6>Striped Animated Progress</h6>
                <div style="
                  width: 100%;
                  height: 20px;
                  background: #e9ecef;
                  border-radius: 10px;
                  overflow: hidden;
                  margin: 10px 0;
                ">
                  <div style="
                    height: 100%;
                    width: 65%;
                    background: repeating-linear-gradient(
                      45deg,
                      #dc3545,
                      #dc3545 10px,
                      #c82333 10px,
                      #c82333 20px
                    );
                    animation: moveStripes 1s linear infinite;
                    border-radius: 10px;
                    transition: width 0.6s ease;
                  "></div>
                </div>
                <p style="font-size: 12px; color: #666;">Animated diagonal stripes</p>
              </div>

              <!-- Circular Progress -->
              <div>
                <h6>Circular Progress</h6>
                <div style="display: flex; gap: 30px; align-items: center;">
                  <div style="
                    width: 80px;
                    height: 80px;
                    border-radius: 50%;
                    background: conic-gradient(#007bff 270deg, #e9ecef 270deg);
                    position: relative;
                    animation: circularProgress 4s ease-in-out forwards;
                  ">
                    <div style="
                      position: absolute;
                      top: 10px;
                      left: 10px;
                      right: 10px;
                      bottom: 10px;
                      background: white;
                      border-radius: 50%;
                      display: flex;
                      align-items: center;
                      justify-content: center;
                      font-size: 12px;
                      font-weight: bold;
                      color: #007bff;
                    ">75%</div>
                  </div>

                  <div style="
                    width: 60px;
                    height: 60px;
                    border: 6px solid #e9ecef;
                    border-top: 6px solid #ffc107;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                  "></div>
                </div>
                <p style="font-size: 12px; color: #666;">Determinate and spinning variants</p>
              </div>

              <!-- Multi-step Progress -->
              <div>
                <h6>Multi-step Progress</h6>
                <div style="display: flex; align-items: center; gap: 10px; margin: 20px 0;">
                  <div style="
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    background: #28a745;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    font-weight: bold;
                    position: relative;
                  ">1
                    <div style="
                      position: absolute;
                      top: 50%;
                      left: 100%;
                      width: 60px;
                      height: 3px;
                      background: #28a745;
                      transform: translateY(-50%);
                    "></div>
                  </div>

                  <div style="
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    background: #007bff;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    font-weight: bold;
                    position: relative;
                    animation: pulse 1.5s ease-in-out infinite;
                  ">2
                    <div style="
                      position: absolute;
                      top: 50%;
                      left: 100%;
                      width: 60px;
                      height: 3px;
                      background: #e9ecef;
                      transform: translateY(-50%);
                    "></div>
                  </div>

                  <div style="
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    background: #e9ecef;
                    color: #6c757d;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    font-weight: bold;
                  ">3</div>
                </div>
                <p style="font-size: 12px; color: #666;">Step 2 of 3 - Current step pulsing</p>
              </div>
            </div>
          </div>

          <style>
            @keyframes progressFill {
              from { width: 0%; }
              to { width: 75%; }
            }

            @keyframes indeterminateProgress {
              0% { left: -30%; }
              100% { left: 100%; }
            }

            @keyframes moveStripes {
              0% { background-position: 0 0; }
              100% { background-position: 40px 0; }
            }

            @keyframes circularProgress {
              from { background: conic-gradient(#007bff 0deg, #e9ecef 0deg); }
              to { background: conic-gradient(#007bff 270deg, #e9ecef 270deg); }
            }
          </style>
        `;
        document.body.appendChild(progressDiv);
      });

      // Capture progress animations at different stages
      await page.waitForTimeout(500);
      await visualUtils.screenshotComponent(
        '[data-testid="progress-animations"]',
        'progress-animations-start',
        ANIMATION_CONFIG
      );

      await page.waitForTimeout(1500);
      await visualUtils.screenshotComponent(
        '[data-testid="progress-animations"]',
        'progress-animations-middle',
        ANIMATION_CONFIG
      );

      await page.waitForTimeout(2000);
      await visualUtils.screenshotComponent(
        '[data-testid="progress-animations"]',
        'progress-animations-end',
        ANIMATION_CONFIG
      );
    });
  });

  test.describe('Interactive Feedback Animations', () => {

    test('Button Hover and Click Animations @visual @animation @interaction', async ({ page }) => {
      await page.evaluate(() => {
        const buttonDiv = document.createElement('div');
        buttonDiv.setAttribute('data-testid', 'button-animations');
        buttonDiv.innerHTML = `
          <div style="padding: 40px;">
            <h4>Interactive Button Animations</h4>

            <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-top: 30px;">
              <!-- Hover Scale -->
              <button style="
                background: #007bff;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
                transform: scale(1);
              " onmouseover="
                this.style.transform='scale(1.05)';
                this.style.boxShadow='0 4px 8px rgba(0, 123, 255, 0.3)';
              " onmouseout="
                this.style.transform='scale(1)';
                this.style.boxShadow='none';
              " onmousedown="
                this.style.transform='scale(0.95)';
              " onmouseup="
                this.style.transform='scale(1.05)';
              ">Hover Scale</button>

              <!-- Slide Up -->
              <button style="
                background: #28a745;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: transform 0.2s ease;
                transform: translateY(0);
              " onmouseover="
                this.style.transform='translateY(-3px)';
                this.style.boxShadow='0 6px 12px rgba(40, 167, 69, 0.3)';
              " onmouseout="
                this.style.transform='translateY(0)';
                this.style.boxShadow='none';
              ">Slide Up</button>

              <!-- Ripple Effect -->
              <button style="
                background: #dc3545;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                position: relative;
                overflow: hidden;
                transition: background-color 0.3s ease;
              " onclick="
                const ripple = document.createElement('span');
                ripple.style.cssText = \`
                  position: absolute;
                  border-radius: 50%;
                  background: rgba(255, 255, 255, 0.6);
                  transform: scale(0);
                  animation: ripple 0.6s linear;
                  pointer-events: none;
                \`;
                const rect = this.getBoundingClientRect();
                const size = Math.max(rect.width, rect.height);
                ripple.style.width = ripple.style.height = size + 'px';
                ripple.style.left = (event.clientX - rect.left - size/2) + 'px';
                ripple.style.top = (event.clientY - rect.top - size/2) + 'px';
                this.appendChild(ripple);
                setTimeout(() => ripple.remove(), 600);
              ">Ripple Click</button>

              <!-- Bounce -->
              <button style="
                background: #ffc107;
                color: #212529;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
              " onmouseover="
                this.style.animation='bounce 0.6s ease-in-out';
              " onanimationend="
                this.style.animation='';
              ">Bounce Hover</button>

              <!-- Glow Effect -->
              <button style="
                background: #6f42c1;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: box-shadow 0.3s ease;
                position: relative;
              " onmouseover="
                this.style.boxShadow='0 0 20px #6f42c1';
              " onmouseout="
                this.style.boxShadow='none';
              ">Glow Effect</button>

              <!-- Rotate -->
              <button style="
                background: #17a2b8;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: transform 0.3s ease;
              " onmouseover="
                this.style.transform='rotateY(180deg)';
              " onmouseout="
                this.style.transform='rotateY(0deg)';
              ">Flip Rotate</button>
            </div>

            <div style="margin-top: 40px;">
              <h5>Loading States</h5>
              <div style="display: flex; gap: 20px; margin-top: 20px;">
                <button style="
                  background: #007bff;
                  color: white;
                  border: none;
                  padding: 12px 24px;
                  border-radius: 6px;
                  cursor: not-allowed;
                  font-size: 14px;
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  opacity: 0.7;
                " disabled>
                  <div style="
                    width: 16px;
                    height: 16px;
                    border: 2px solid transparent;
                    border-top: 2px solid currentColor;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                  "></div>
                  Loading...
                </button>

                <button style="
                  background: #28a745;
                  color: white;
                  border: none;
                  padding: 12px 24px;
                  border-radius: 6px;
                  cursor: pointer;
                  font-size: 14px;
                  display: flex;
                  align-items: center;
                  gap: 8px;
                  animation: successPulse 2s ease-in-out infinite;
                ">
                  ✓ Success
                </button>
              </div>
            </div>
          </div>

          <style>
            @keyframes ripple {
              to { transform: scale(4); opacity: 0; }
            }

            @keyframes bounce {
              0%, 100% { transform: translateY(0); }
              50% { transform: translateY(-10px); }
            }

            @keyframes successPulse {
              0%, 100% { box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
              70% { box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
            }
          </style>
        `;
        document.body.appendChild(buttonDiv);
      });

      // Capture default state
      await visualUtils.screenshotComponent(
        '[data-testid="button-animations"]',
        'button-animations-default',
        STATIC_CONFIG
      );

      // Test hover states by adding hover classes via JavaScript
      await page.evaluate(() => {
        const buttons = document.querySelectorAll('[data-testid="button-animations"] button');
        buttons.forEach((button, index) => {
          if (index < 3) { // Apply hover to first few buttons
            button.dispatchEvent(new MouseEvent('mouseover'));
          }
        });
      });

      await page.waitForTimeout(300);
      await visualUtils.screenshotComponent(
        '[data-testid="button-animations"]',
        'button-animations-hover-states',
        ANIMATION_CONFIG
      );
    });

    test('Form Input Focus Animations @visual @animation @interaction', async ({ page }) => {
      await page.evaluate(() => {
        const formDiv = document.createElement('div');
        formDiv.setAttribute('data-testid', 'form-input-animations');
        formDiv.innerHTML = `
          <div style="padding: 40px;">
            <h4>Form Input Focus Animations</h4>

            <div style="display: flex; flex-direction: column; gap: 30px; margin-top: 30px; max-width: 400px;">
              <!-- Floating Label -->
              <div style="position: relative;">
                <input type="text" id="floating-input" style="
                  width: 100%;
                  padding: 16px 12px 8px 12px;
                  border: 2px solid #e9ecef;
                  border-radius: 6px;
                  font-size: 16px;
                  outline: none;
                  transition: border-color 0.3s ease;
                  background: white;
                " onfocus="
                  this.style.borderColor='#007bff';
                  this.nextElementSibling.style.transform='translateY(-20px) scale(0.8)';
                  this.nextElementSibling.style.color='#007bff';
                " onblur="
                  if(!this.value) {
                    this.nextElementSibling.style.transform='translateY(0) scale(1)';
                    this.nextElementSibling.style.color='#6c757d';
                  }
                  this.style.borderColor='#e9ecef';
                ">
                <label for="floating-input" style="
                  position: absolute;
                  left: 12px;
                  top: 50%;
                  transform: translateY(-50%);
                  color: #6c757d;
                  font-size: 16px;
                  transition: all 0.3s ease;
                  pointer-events: none;
                  background: white;
                  padding: 0 4px;
                ">Floating Label Input</label>
              </div>

              <!-- Underline Animation -->
              <div style="position: relative;">
                <input type="text" style="
                  width: 100%;
                  padding: 12px 0;
                  border: none;
                  border-bottom: 2px solid #e9ecef;
                  font-size: 16px;
                  outline: none;
                  background: transparent;
                  transition: border-color 0.3s ease;
                " onfocus="
                  this.style.borderBottomColor='#28a745';
                  this.nextElementSibling.style.width='100%';
                " onblur="
                  this.style.borderBottomColor='#e9ecef';
                  this.nextElementSibling.style.width='0%';
                ">
                <div style="
                  position: absolute;
                  bottom: 0;
                  left: 50%;
                  transform: translateX(-50%);
                  width: 0%;
                  height: 2px;
                  background: #28a745;
                  transition: width 0.3s ease;
                "></div>
                <label style="
                  position: absolute;
                  left: 0;
                  top: -20px;
                  color: #6c757d;
                  font-size: 14px;
                ">Underline Animation</label>
              </div>

              <!-- Glow Focus -->
              <input type="text" placeholder="Glow Focus Effect" style="
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e9ecef;
                border-radius: 25px;
                font-size: 16px;
                outline: none;
                transition: all 0.3s ease;
              " onfocus="
                this.style.borderColor='#dc3545';
                this.style.boxShadow='0 0 15px rgba(220, 53, 69, 0.3)';
                this.style.transform='scale(1.02)';
              " onblur="
                this.style.borderColor='#e9ecef';
                this.style.boxShadow='none';
                this.style.transform='scale(1)';
              ">

              <!-- Slide In Label -->
              <div style="position: relative; overflow: hidden;">
                <input type="text" style="
                  width: 100%;
                  padding: 16px 12px;
                  border: 2px solid #e9ecef;
                  border-radius: 6px;
                  font-size: 16px;
                  outline: none;
                  transition: border-color 0.3s ease;
                " onfocus="
                  this.style.borderColor='#ffc107';
                  this.nextElementSibling.style.transform='translateX(0)';
                " onblur="
                  this.style.borderColor='#e9ecef';
                  this.nextElementSibling.style.transform='translateX(-100%)';
                ">
                <div style="
                  position: absolute;
                  top: 0;
                  left: 0;
                  right: 0;
                  height: 4px;
                  background: linear-gradient(90deg, #ffc107, #fd7e14);
                  transform: translateX(-100%);
                  transition: transform 0.3s ease;
                "></div>
                <label style="
                  position: absolute;
                  left: 12px;
                  top: -10px;
                  color: #6c757d;
                  font-size: 12px;
                  background: white;
                  padding: 0 4px;
                ">Slide In Effect</label>
              </div>

              <!-- Search Input with Icon -->
              <div style="position: relative;">
                <input type="search" placeholder="Search with animation..." style="
                  width: 100%;
                  padding: 12px 16px 12px 45px;
                  border: 2px solid #e9ecef;
                  border-radius: 25px;
                  font-size: 16px;
                  outline: none;
                  transition: all 0.3s ease;
                " onfocus="
                  this.style.borderColor='#17a2b8';
                  this.style.paddingLeft='50px';
                  this.previousElementSibling.style.color='#17a2b8';
                  this.previousElementSibling.style.transform='scale(1.1)';
                " onblur="
                  this.style.borderColor='#e9ecef';
                  this.style.paddingLeft='45px';
                  this.previousElementSibling.style.color='#6c757d';
                  this.previousElementSibling.style.transform='scale(1)';
                ">
                <div style="
                  position: absolute;
                  left: 15px;
                  top: 50%;
                  transform: translateY(-50%);
                  color: #6c757d;
                  font-size: 18px;
                  transition: all 0.3s ease;
                  pointer-events: none;
                ">🔍</div>
              </div>
            </div>
          </div>
        `;
        document.body.appendChild(formDiv);
      });

      // Capture default state
      await visualUtils.screenshotComponent(
        '[data-testid="form-input-animations"]',
        'form-input-animations-default',
        STATIC_CONFIG
      );

      // Focus first input to show floating label animation
      await page.focus('#floating-input');
      await page.waitForTimeout(400);

      await visualUtils.screenshotComponent(
        '[data-testid="form-input-animations"]',
        'form-input-animations-focused',
        ANIMATION_CONFIG
      );

      // Test multiple inputs focused
      const inputs = await page.locator('[data-testid="form-input-animations"] input').all();
      for (let i = 0; i < Math.min(inputs.length, 3); i++) {
        await inputs[i].focus();
        await page.waitForTimeout(100);
      }

      await page.waitForTimeout(300);
      await visualUtils.screenshotComponent(
        '[data-testid="form-input-animations"]',
        'form-input-animations-multiple-focused',
        ANIMATION_CONFIG
      );
    });
  });

  test.describe('Plotly Graph Interaction Animations', () => {

    test('Plotly Graph Animation States @visual @animation @plotly', async ({ page }) => {
      await page.evaluate(() => {
        const plotlyDiv = document.createElement('div');
        plotlyDiv.setAttribute('data-testid', 'plotly-animation-states');
        plotlyDiv.innerHTML = `
          <div style="padding: 20px;">
            <h4>Plotly Graph Animation States</h4>

            <!-- Mock animated graph container -->
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
              <!-- Mock toolbar -->
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
                animation: fadeIn 0.5s ease-in-out;
              ">
                <button style="width: 24px; height: 24px; border: none; background: transparent; cursor: pointer; transition: background-color 0.2s;">📷</button>
                <button style="width: 24px; height: 24px; border: none; background: transparent; cursor: pointer; transition: background-color 0.2s;">🔍</button>
                <button style="width: 24px; height: 24px; border: none; background: transparent; cursor: pointer; transition: background-color 0.2s;">📐</button>
              </div>

              <!-- Animated data points -->
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

                <!-- Animated scatter points -->
                <circle cx="150" cy="120" r="0" fill="url(#point1)" style="animation: growPoint 1s ease-out 0.2s forwards;">
                  <animate attributeName="r" values="0;8;6;8" dur="2s" repeatCount="indefinite" begin="1s"/>
                </circle>
                <circle cx="280" cy="180" r="0" fill="url(#point2)" style="animation: growPoint 1s ease-out 0.4s forwards;">
                  <animate attributeName="r" values="0;6;4;6" dur="2.5s" repeatCount="indefinite" begin="1.2s"/>
                </circle>
                <circle cx="220" cy="250" r="0" fill="url(#point3)" style="animation: growPoint 1s ease-out 0.6s forwards;">
                  <animate attributeName="r" values="0;10;8;10" dur="1.8s" repeatCount="indefinite" begin="1.4s"/>
                </circle>
                <circle cx="350" cy="200" r="0" fill="url(#point1)" style="animation: growPoint 1s ease-out 0.8s forwards;">
                  <animate attributeName="r" values="0;7;5;7" dur="2.2s" repeatCount="indefinite" begin="1.6s"/>
                </circle>
                <circle cx="180" cy="300" r="0" fill="url(#point2)" style="animation: growPoint 1s ease-out 1.0s forwards;">
                  <animate attributeName="r" values="0;9;7;9" dur="2.3s" repeatCount="indefinite" begin="1.8s"/>
                </circle>

                <!-- Animated connecting lines -->
                <path d="M 150,120 Q 215,150 280,180" stroke="#007bff" stroke-width="2" fill="none" opacity="0.6" style="
                  stroke-dasharray: 200;
                  stroke-dashoffset: 200;
                  animation: drawLine 2s ease-in-out 1.5s forwards;
                "/>
                <path d="M 280,180 Q 250,215 220,250" stroke="#28a745" stroke-width="2" fill="none" opacity="0.6" style="
                  stroke-dasharray: 100;
                  stroke-dashoffset: 100;
                  animation: drawLine 1.5s ease-in-out 2s forwards;
                "/>

                <!-- Axis lines with animation -->
                <line x1="50" y1="50" x2="50" y2="450" stroke="#6c757d" stroke-width="2" style="
                  stroke-dasharray: 400;
                  stroke-dashoffset: 400;
                  animation: drawLine 1s ease-in-out 0.5s forwards;
                "/>
                <line x1="50" y1="450" x2="550" y2="450" stroke="#6c757d" stroke-width="2" style="
                  stroke-dasharray: 500;
                  stroke-dashoffset: 500;
                  animation: drawLine 1s ease-in-out 0.7s forwards;
                "/>

                <!-- Axis labels -->
                <text x="300" y="480" text-anchor="middle" fill="#6c757d" font-size="14" style="animation: fadeIn 1s ease-in-out 2s forwards; opacity: 0;">X-Axis</text>
                <text x="25" y="250" text-anchor="middle" fill="#6c757d" font-size="14" transform="rotate(-90 25 250)" style="animation: fadeIn 1s ease-in-out 2s forwards; opacity: 0;">Y-Axis</text>
              </svg>

              <!-- Animated legend -->
              <div style="
                position: absolute;
                bottom: 20px;
                left: 20px;
                background: rgba(255,255,255,0.95);
                padding: 15px;
                border-radius: 6px;
                border: 1px solid #ddd;
                font-size: 12px;
                opacity: 0;
                animation: slideInUp 0.8s ease-out 2.5s forwards;
                transform: translateY(20px);
              ">
                <div style="margin-bottom: 6px; display: flex; align-items: center;">
                  <div style="width: 12px; height: 12px; background: #007bff; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite;"></div>
                  <span>Category A</span>
                </div>
                <div style="margin-bottom: 6px; display: flex; align-items: center;">
                  <div style="width: 12px; height: 12px; background: #28a745; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite 0.3s;"></div>
                  <span>Category B</span>
                </div>
                <div style="display: flex; align-items: center;">
                  <div style="width: 12px; height: 12px; background: #dc3545; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite 0.6s;"></div>
                  <span>Category C</span>
                </div>
              </div>

              <!-- Loading overlay that fades out -->
              <div style="
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                animation: fadeOut 0.5s ease-in-out 1s forwards;
                z-index: 5;
              ">
                <div style="text-align: center;">
                  <div style="
                    width: 40px;
                    height: 40px;
                    border: 4px solid #f3f3f3;
                    border-top: 4px solid #007bff;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 16px;
                  "></div>
                  <p style="color: #6c757d; margin: 0;">Rendering visualization...</p>
                </div>
              </div>
            </div>
          </div>

          <style>
            @keyframes fadeIn {
              from { opacity: 0; }
              to { opacity: 1; }
            }

            @keyframes fadeOut {
              from { opacity: 1; }
              to { opacity: 0; }
            }

            @keyframes growPoint {
              from { r: 0; }
              to { r: 8; }
            }

            @keyframes drawLine {
              from { stroke-dashoffset: 200; }
              to { stroke-dashoffset: 0; }
            }

            @keyframes slideInUp {
              from { opacity: 0; transform: translateY(20px); }
              to { opacity: 1; transform: translateY(0); }
            }

            @keyframes pulse {
              0%, 100% { transform: scale(1); }
              50% { transform: scale(1.1); }
            }
          </style>
        `;
        document.body.appendChild(plotlyDiv);
      });

      // Capture different phases of the animation
      await page.waitForTimeout(500);
      await visualUtils.screenshotComponent(
        '[data-testid="plotly-animation-states"]',
        'plotly-animation-loading',
        ANIMATION_CONFIG
      );

      await page.waitForTimeout(1500);
      await visualUtils.screenshotComponent(
        '[data-testid="plotly-animation-states"]',
        'plotly-animation-drawing',
        ANIMATION_CONFIG
      );

      await page.waitForTimeout(2000);
      await visualUtils.screenshotComponent(
        '[data-testid="plotly-animation-states"]',
        'plotly-animation-complete',
        ANIMATION_CONFIG
      );
    });
  });

  test.describe('Reduced Motion Testing', () => {

    test('Reduced Motion Compliance @visual @animation @accessibility', async ({ page }) => {
      // Enable reduced motion preference
      await visualUtils.enableReducedMotion();

      await page.evaluate(() => {
        const motionDiv = document.createElement('div');
        motionDiv.setAttribute('data-testid', 'reduced-motion-test');
        motionDiv.innerHTML = `
          <div style="padding: 40px;">
            <h4>Reduced Motion Compliance Test</h4>

            <div style="display: flex; flex-direction: column; gap: 30px; margin-top: 30px;">
              <!-- Elements that should respect reduced motion -->
              <div>
                <h6>Transitions (should be instant with reduced motion)</h6>
                <button style="
                  background: #007bff;
                  color: white;
                  border: none;
                  padding: 12px 24px;
                  border-radius: 6px;
                  cursor: pointer;
                  font-size: 14px;
                  transition: background-color 0.3s ease, transform 0.3s ease;
                " onmouseover="
                  this.style.backgroundColor='#0056b3';
                  this.style.transform='translateY(-2px)';
                " onmouseout="
                  this.style.backgroundColor='#007bff';
                  this.style.transform='translateY(0)';
                ">Hover Transition</button>
              </div>

              <div>
                <h6>Animations (should be disabled with reduced motion)</h6>
                <div style="
                  width: 60px;
                  height: 60px;
                  background: #28a745;
                  border-radius: 50%;
                  animation: pulse 2s ease-in-out infinite;
                "></div>
              </div>

              <div>
                <h6>Loading Spinners (functional animations - allowed)</h6>
                <div style="
                  width: 40px;
                  height: 40px;
                  border: 4px solid #f3f3f3;
                  border-top: 4px solid #dc3545;
                  border-radius: 50%;
                  animation: spin 1s linear infinite;
                "></div>
              </div>

              <div>
                <h6>Parallax/Auto-playing (should be disabled)</h6>
                <div style="
                  width: 100%;
                  height: 100px;
                  background: linear-gradient(45deg, #667eea, #764ba2);
                  border-radius: 8px;
                  position: relative;
                  overflow: hidden;
                ">
                  <div style="
                    position: absolute;
                    width: 120%;
                    height: 120%;
                    background: repeating-linear-gradient(
                      45deg,
                      rgba(255,255,255,0.1),
                      rgba(255,255,255,0.1) 10px,
                      transparent 10px,
                      transparent 20px
                    );
                    animation: movePattern 3s linear infinite;
                  "></div>
                  <div style="
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    color: white;
                    font-weight: bold;
                  ">Auto-scrolling Pattern</div>
                </div>
              </div>
            </div>

            <div style="
              margin-top: 30px;
              padding: 15px;
              background: #d1ecf1;
              border: 1px solid #bee5eb;
              border-radius: 4px;
              color: #0c5460;
              font-size: 14px;
            ">
              <strong>Note:</strong> With reduced motion enabled, decorative animations should be disabled while functional animations (like loading indicators) remain active for usability.
            </div>
          </div>

          <style>
            /* Respect user's motion preferences */
            @media (prefers-reduced-motion: reduce) {
              *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
              }

              /* Keep essential animations for functionality */
              [data-essential-animation] {
                animation-duration: revert !important;
                animation-iteration-count: revert !important;
              }
            }

            @keyframes movePattern {
              from { transform: translate(-10%, -10%); }
              to { transform: translate(10%, 10%); }
            }
          </style>
        `;
        document.body.appendChild(motionDiv);
      });

      await page.waitForTimeout(500);
      await visualUtils.screenshotComponent(
        '[data-testid="reduced-motion-test"]',
        'reduced-motion-compliance',
        STATIC_CONFIG
      );

      // Test hover state with reduced motion
      await page.hover('[data-testid="reduced-motion-test"] button');
      await page.waitForTimeout(100); // Should be instant with reduced motion

      await visualUtils.screenshotComponent(
        '[data-testid="reduced-motion-test"]',
        'reduced-motion-hover-state',
        STATIC_CONFIG
      );
    });
  });

  test.describe('Animation Performance Testing', () => {

    test('Animation Performance Impact @visual @animation @performance', async ({ page }) => {
      // Create multiple animated elements to test performance
      await page.evaluate(() => {
        const perfDiv = document.createElement('div');
        perfDiv.setAttribute('data-testid', 'animation-performance-test');
        perfDiv.innerHTML = `
          <div style="padding: 20px;">
            <h4>Animation Performance Test</h4>
            <p style="font-size: 14px; color: #6c757d;">Multiple animated elements to test rendering performance</p>

            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 15px; margin-top: 20px;">
              ${Array.from({ length: 20 }, (_, i) => `
                <div style="
                  width: 60px;
                  height: 60px;
                  background: hsl(${i * 18}, 70%, 60%);
                  border-radius: 50%;
                  animation: complexAnimation ${1 + (i % 3) * 0.5}s ease-in-out infinite;
                  animation-delay: ${i * 0.1}s;
                  transform-origin: center;
                "></div>
              `).join('')}
            </div>

            <div style="margin-top: 40px;">
              <h6>Complex Synchronized Animations</h6>
              <div style="display: flex; justify-content: center; align-items: end; gap: 4px; height: 100px; margin: 20px 0;">
                ${Array.from({ length: 12 }, (_, i) => `
                  <div style="
                    width: 12px;
                    background: linear-gradient(to top, #007bff, #00d4ff);
                    animation: waveHeight ${1.5 + (i % 3) * 0.2}s ease-in-out infinite;
                    animation-delay: ${i * 0.1}s;
                    border-radius: 6px 6px 0 0;
                  "></div>
                `).join('')}
              </div>
            </div>

            <div style="margin-top: 30px; padding: 12px; background: #f8f9fa; border-radius: 4px; font-size: 12px; color: #6c757d;">
              Performance Note: This test includes 32 simultaneously animated elements to evaluate smooth rendering capabilities.
            </div>
          </div>

          <style>
            @keyframes complexAnimation {
              0% { transform: scale(1) rotate(0deg); }
              25% { transform: scale(1.2) rotate(90deg); }
              50% { transform: scale(0.8) rotate(180deg); }
              75% { transform: scale(1.1) rotate(270deg); }
              100% { transform: scale(1) rotate(360deg); }
            }

            @keyframes waveHeight {
              0%, 100% { height: 20px; }
              50% { height: 80px; }
            }
          </style>
        `;
        document.body.appendChild(perfDiv);
      });

      // Capture performance test at different phases
      await page.waitForTimeout(300);
      await visualUtils.screenshotComponent(
        '[data-testid="animation-performance-test"]',
        'animation-performance-phase-1',
        ANIMATION_CONFIG
      );

      await page.waitForTimeout(800);
      await visualUtils.screenshotComponent(
        '[data-testid="animation-performance-test"]',
        'animation-performance-phase-2',
        ANIMATION_CONFIG
      );

      await page.waitForTimeout(1200);
      await visualUtils.screenshotComponent(
        '[data-testid="animation-performance-test"]',
        'animation-performance-phase-3',
        ANIMATION_CONFIG
      );
    });
  });
});
