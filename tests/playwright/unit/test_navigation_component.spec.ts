/**
 * Comprehensive Tab Navigation Component Tests for MELD Visualizer
 * Tests tab switching, state persistence, and keyboard navigation using MCP functions
 */

import { test, expect } from '../fixtures/mcp-fixtures';
import type { TestTypes } from '../types';

test.describe('Tab Navigation Component', () => {
  test.beforeEach(async ({ mcpPage, homePage, performanceMonitor }) => {
    // Navigate to home page and ensure tabs are loaded
    await homePage.navigate();
    performanceMonitor.mark('navigation-page-ready');

    // Wait for tab navigation to be fully loaded
    await expect(mcpPage.locator('[data-testid="tabs"]')).toBeVisible();
    await mcpPage.waitForLoadState('networkidle');
  });

  test.describe('Basic Tab Navigation', () => {
    test('should display all main navigation tabs', async ({
      mcpPage,
      visualTester
    }) => {
      // Verify all expected tabs are present
      const expectedTabs = ['upload', 'visualization', 'analysis', 'settings'];

      for (const tabId of expectedTabs) {
        const tab = mcpPage.locator(`[data-testid="tab-${tabId}"]`);
        await expect(tab).toBeVisible();
        await expect(tab).toBeEnabled();

        // Verify tab has proper attributes
        await expect(tab).toHaveAttribute('role', 'tab');
        await expect(tab).toHaveAttribute('aria-controls');
      }

      // Take screenshot of initial tab state
      await visualTester.takeScreenshot('tabs-initial-state', { fullPage: true });
    });

    test('should switch between tabs correctly', async ({
      mcpPage,
      performanceMonitor,
      visualTester,
      consoleMonitor
    }) => {
      // Test switching to each tab
      const tabs = ['upload', 'visualization', 'analysis', 'settings'];

      for (const tabId of tabs) {
        performanceMonitor.mark(`tab-${tabId}-switch-start`);

        const tabElement = mcpPage.locator(`[data-testid="tab-${tabId}"]`);

        // Click tab
        await tabElement.click();

        // Wait for tab content to load
        await expect(mcpPage.locator(`[data-testid="tab-content-${tabId}"]`)).toBeVisible({ timeout: 5000 });

        // Verify tab is marked as active
        await expect(tabElement).toHaveClass(/active|selected/);
        await expect(tabElement).toHaveAttribute('aria-selected', 'true');

        // Verify other tabs are not active
        const otherTabs = tabs.filter(id => id !== tabId);
        for (const otherId of otherTabs) {
          await expect(mcpPage.locator(`[data-testid="tab-${otherId}"]`)).not.toHaveClass(/active|selected/);
          await expect(mcpPage.locator(`[data-testid="tab-${otherId}"]`)).toHaveAttribute('aria-selected', 'false');
        }

        performanceMonitor.mark(`tab-${tabId}-switch-complete`);

        // Take screenshot of each tab
        await visualTester.takeScreenshot(`tab-${tabId}-active`);
      }

      // Verify no console errors during navigation
      consoleMonitor.expectNoErrors();
    });

    test('should load tab content dynamically', async ({
      mcpPage,
      performanceMonitor
    }) => {
      // Switch to visualization tab
      await mcpPage.locator('[data-testid="tab-visualization"]').click();

      performanceMonitor.mark('visualization-content-load-start');

      // Verify visualization content loads
      await expect(mcpPage.locator('[data-testid="graph-container"]')).toBeVisible({ timeout: 10000 });

      performanceMonitor.mark('visualization-content-load-complete');

      // Switch to analysis tab
      await mcpPage.locator('[data-testid="tab-analysis"]').click();

      // Verify analysis content loads
      await expect(mcpPage.locator('[data-testid="analysis-panel"]')).toBeVisible({ timeout: 5000 });

      // Check performance of tab switching
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.interactionTime).toBeLessThan(500); // Should be responsive
    });
  });

  test.describe('Tab State Persistence', () => {
    test('should remember active tab across page reloads', async ({
      mcpPage,
      visualTester
    }) => {
      // Switch to analysis tab
      await mcpPage.locator('[data-testid="tab-analysis"]').click();
      await expect(mcpPage.locator('[data-testid="tab-content-analysis"]')).toBeVisible();

      // Take screenshot before reload
      await visualTester.takeScreenshot('before-reload-analysis-active');

      // Reload page
      await mcpPage.reload();
      await expect(mcpPage.locator('[data-testid="tabs"]')).toBeVisible();

      // Verify analysis tab is still active
      await expect(mcpPage.locator('[data-testid="tab-analysis"]')).toHaveClass(/active|selected/);
      await expect(mcpPage.locator('[data-testid="tab-content-analysis"]')).toBeVisible();

      // Take screenshot after reload
      await visualTester.takeScreenshot('after-reload-analysis-active');
    });

    test('should persist tab state in local storage', async ({
      mcpPage
    }) => {
      // Switch to settings tab
      await mcpPage.locator('[data-testid="tab-settings"]').click();
      await expect(mcpPage.locator('[data-testid="tab-content-settings"]')).toBeVisible();

      // Check local storage for tab state
      const storedTab = await mcpPage.evaluate(() => {
        return localStorage.getItem('activeTab') || localStorage.getItem('meld-active-tab');
      });

      expect(storedTab).toBe('settings');

      // Switch to upload tab
      await mcpPage.locator('[data-testid="tab-upload"]').click();
      await expect(mcpPage.locator('[data-testid="tab-content-upload"]')).toBeVisible();

      // Verify local storage updated
      const updatedTab = await mcpPage.evaluate(() => {
        return localStorage.getItem('activeTab') || localStorage.getItem('meld-active-tab');
      });

      expect(updatedTab).toBe('upload');
    });

    test('should handle tab state restoration with invalid values', async ({
      mcpPage
    }) => {
      // Set invalid tab state in local storage
      await mcpPage.evaluate(() => {
        localStorage.setItem('activeTab', 'invalid-tab');
      });

      // Reload page
      await mcpPage.reload();
      await expect(mcpPage.locator('[data-testid="tabs"]')).toBeVisible();

      // Should default to first tab (upload) when invalid state found
      await expect(mcpPage.locator('[data-testid="tab-upload"]')).toHaveClass(/active|selected/);
      await expect(mcpPage.locator('[data-testid="tab-content-upload"]')).toBeVisible();
    });
  });

  test.describe('Keyboard Navigation', () => {
    test('should support arrow key navigation between tabs', async ({
      mcpPage,
      visualTester
    }) => {
      // Focus on first tab
      await mcpPage.locator('[data-testid="tab-upload"]').focus();
      await expect(mcpPage.locator('[data-testid="tab-upload"]')).toBeFocused();

      // Take screenshot of initial focus
      await visualTester.takeScreenshot('tab-keyboard-initial-focus');

      // Navigate with right arrow
      await mcpPage.keyboard.press('ArrowRight');
      await expect(mcpPage.locator('[data-testid="tab-visualization"]')).toBeFocused();

      // Navigate with right arrow again
      await mcpPage.keyboard.press('ArrowRight');
      await expect(mcpPage.locator('[data-testid="tab-analysis"]')).toBeFocused();

      // Navigate with left arrow
      await mcpPage.keyboard.press('ArrowLeft');
      await expect(mcpPage.locator('[data-testid="tab-visualization"]')).toBeFocused();

      // Test wrapping - go to last tab and press right
      await mcpPage.locator('[data-testid="tab-settings"]').focus();
      await mcpPage.keyboard.press('ArrowRight');
      await expect(mcpPage.locator('[data-testid="tab-upload"]')).toBeFocused();

      // Test reverse wrapping - go to first tab and press left
      await mcpPage.keyboard.press('ArrowLeft');
      await expect(mcpPage.locator('[data-testid="tab-settings"]')).toBeFocused();

      await visualTester.takeScreenshot('tab-keyboard-navigation-complete');
    });

    test('should activate tabs with Enter and Space keys', async ({
      mcpPage,
      performanceMonitor
    }) => {
      performanceMonitor.mark('keyboard-activation-test-start');

      // Focus on visualization tab
      await mcpPage.locator('[data-testid="tab-visualization"]').focus();
      await expect(mcpPage.locator('[data-testid="tab-visualization"]')).toBeFocused();

      // Activate with Enter key
      await mcpPage.keyboard.press('Enter');
      await expect(mcpPage.locator('[data-testid="tab-visualization"]')).toHaveClass(/active|selected/);
      await expect(mcpPage.locator('[data-testid="tab-content-visualization"]')).toBeVisible();

      // Focus on analysis tab
      await mcpPage.locator('[data-testid="tab-analysis"]').focus();

      // Activate with Space key
      await mcpPage.keyboard.press('Space');
      await expect(mcpPage.locator('[data-testid="tab-analysis"]')).toHaveClass(/active|selected/);
      await expect(mcpPage.locator('[data-testid="tab-content-analysis"]')).toBeVisible();

      performanceMonitor.mark('keyboard-activation-test-complete');

      // Verify keyboard activation is responsive
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.interactionTime).toBeLessThan(200);
    });

    test('should support Tab key for sequential navigation', async ({
      mcpPage
    }) => {
      // Start from beginning of page
      await mcpPage.keyboard.press('Home');

      // Tab to navigation area
      let tabPresses = 0;
      const maxTabs = 20; // Safety limit

      while (tabPresses < maxTabs) {
        await mcpPage.keyboard.press('Tab');
        tabPresses++;

        const focusedElement = await mcpPage.locator(':focus').getAttribute('data-testid');
        if (focusedElement?.startsWith('tab-')) {
          break;
        }
      }

      // Verify we reached a tab element
      const focusedTab = await mcpPage.locator(':focus').getAttribute('data-testid');
      expect(focusedTab).toMatch(/^tab-/);

      // Continue tabbing through all tabs
      const tabElements = await mcpPage.locator('[data-testid^="tab-"]').count();

      for (let i = 1; i < tabElements; i++) {
        await mcpPage.keyboard.press('Tab');
        const currentFocus = await mcpPage.locator(':focus').getAttribute('data-testid');
        expect(currentFocus).toMatch(/^tab-/);
      }
    });
  });

  test.describe('Tab Content Loading', () => {
    test('should show loading states when switching tabs', async ({
      mcpPage,
      visualTester,
      performanceMonitor
    }) => {
      performanceMonitor.mark('tab-loading-test-start');

      // Switch to visualization tab (typically has longer loading time)
      await mcpPage.locator('[data-testid="tab-visualization"]').click();

      // Verify loading indicator appears quickly
      const loadingIndicator = mcpPage.locator('[data-testid="tab-loading"], [data-testid="graph-loading"]');
      await expect(loadingIndicator).toBeVisible({ timeout: 1000 });

      // Take screenshot of loading state
      await visualTester.takeScreenshot('tab-content-loading');

      // Wait for content to fully load
      await expect(mcpPage.locator('[data-testid="graph-container"]')).toBeVisible({ timeout: 15000 });

      // Verify loading indicator is hidden
      await expect(loadingIndicator).not.toBeVisible();

      performanceMonitor.mark('tab-loading-test-complete');

      // Take screenshot of loaded state
      await visualTester.takeScreenshot('tab-content-loaded');
    });

    test('should handle loading errors gracefully', async ({
      mcpPage,
      networkMocker,
      consoleMonitor
    }) => {
      // Mock network error for tab content
      await networkMocker.mockApiError('/_dash-update-component', 500);

      // Switch to visualization tab
      await mcpPage.locator('[data-testid="tab-visualization"]').click();

      // Verify error handling
      await expect(mcpPage.locator('[data-testid="tab-error"], [data-testid="content-error"]')).toBeVisible({ timeout: 10000 });

      // Verify error message is informative
      const errorMessage = mcpPage.locator('[data-testid="tab-error"], [data-testid="content-error"]');
      await expect(errorMessage).toContainText(/error|failed|load/i);

      // Verify retry option is available
      await expect(mcpPage.locator('[data-testid="retry-button"]')).toBeVisible();

      // Ensure errors are handled gracefully (no console errors)
      const errors = consoleMonitor.getErrors().filter(error =>
        !error.text.includes('500') && !error.text.includes('network')
      );
      expect(errors).toHaveLength(0);
    });

    test('should cache tab content after initial load', async ({
      mcpPage,
      uploadPage,
      testFiles,
      performanceMonitor
    }) => {
      // Upload data first to have content to cache
      await uploadPage.uploadFile(testFiles.validMELDData.path);
      await expect(mcpPage.locator('[data-testid="upload-success"]')).toBeVisible();

      // Switch to visualization tab (initial load)
      performanceMonitor.mark('first-viz-load-start');
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await expect(mcpPage.locator('[data-testid="graph-container"]')).toBeVisible();
      performanceMonitor.mark('first-viz-load-complete');

      // Switch away and back
      await mcpPage.locator('[data-testid="tab-analysis"]').click();
      await expect(mcpPage.locator('[data-testid="tab-content-analysis"]')).toBeVisible();

      // Switch back to visualization (should be cached)
      performanceMonitor.mark('cached-viz-load-start');
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await expect(mcpPage.locator('[data-testid="graph-container"]')).toBeVisible({ timeout: 2000 });
      performanceMonitor.mark('cached-viz-load-complete');

      // Cached load should be significantly faster
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.interactionTime).toBeLessThan(500);
    });
  });

  test.describe('Tab Accessibility', () => {
    test('should have proper ARIA attributes', async ({
      mcpPage
    }) => {
      // Check tablist role
      const tabContainer = mcpPage.locator('[data-testid="tabs"]');
      await expect(tabContainer).toHaveAttribute('role', 'tablist');

      // Check individual tab attributes
      const tabs = mcpPage.locator('[data-testid^="tab-"]');
      const tabCount = await tabs.count();

      for (let i = 0; i < tabCount; i++) {
        const tab = tabs.nth(i);

        // Check required attributes
        await expect(tab).toHaveAttribute('role', 'tab');
        await expect(tab).toHaveAttribute('aria-controls');
        await expect(tab).toHaveAttribute('aria-selected');
        await expect(tab).toHaveAttribute('tabindex');

        // Check aria-label or text content exists
        const hasLabel = await tab.getAttribute('aria-label');
        const hasText = await tab.textContent();
        expect(hasLabel || hasText).toBeTruthy();
      }

      // Check tab panels
      const panels = mcpPage.locator('[data-testid^="tab-content-"]');
      const panelCount = await panels.count();

      for (let i = 0; i < panelCount; i++) {
        const panel = panels.nth(i);
        await expect(panel).toHaveAttribute('role', 'tabpanel');
        await expect(panel).toHaveAttribute('aria-labelledby');
      }
    });

    test('should support screen reader navigation', async ({
      mcpPage
    }) => {
      // Check tab announcements
      const activeTab = mcpPage.locator('[data-testid="tab-upload"][aria-selected="true"]');
      await expect(activeTab).toBeVisible();

      // Verify tab has accessible name
      const tabName = await activeTab.textContent();
      expect(tabName?.trim()).toBeTruthy();

      // Switch tab and verify announcements
      await mcpPage.locator('[data-testid="tab-visualization"]').click();

      // Check that aria-selected updates correctly
      await expect(mcpPage.locator('[data-testid="tab-upload"]')).toHaveAttribute('aria-selected', 'false');
      await expect(mcpPage.locator('[data-testid="tab-visualization"]')).toHaveAttribute('aria-selected', 'true');

      // Verify corresponding panel is properly labeled
      const activePanel = mcpPage.locator('[data-testid="tab-content-visualization"]');
      const panelLabel = await activePanel.getAttribute('aria-labelledby');
      const associatedTab = await mcpPage.locator(`[id="${panelLabel}"]`);
      await expect(associatedTab).toBeVisible();
    });

    test('should handle focus management correctly', async ({
      mcpPage
    }) => {
      // Initial focus should be manageable
      await mcpPage.locator('[data-testid="tab-upload"]').focus();
      await expect(mcpPage.locator('[data-testid="tab-upload"]')).toBeFocused();

      // When tab is activated, focus should move to content if appropriate
      await mcpPage.keyboard.press('Enter');

      // Focus should either stay on tab or move to content area
      const focusedElement = mcpPage.locator(':focus');
      const focusedTestId = await focusedElement.getAttribute('data-testid');

      expect(focusedTestId).toMatch(/(tab-upload|tab-content-upload|upload-)/);

      // Test focus trap within tab content
      await mcpPage.keyboard.press('Tab');
      const nextFocused = await mcpPage.locator(':focus').getAttribute('data-testid');

      // Should focus on interactive element within the tab or next tab
      expect(nextFocused).toBeTruthy();
    });

    test('should support high contrast mode', async ({
      mcpPage,
      visualTester
    }) => {
      // Simulate high contrast mode
      await mcpPage.addStyleTag({
        content: `
          @media (prefers-contrast: high) {
            [data-testid^="tab-"] {
              border: 2px solid;
              background: ButtonFace;
              color: ButtonText;
            }
            [data-testid^="tab-"][aria-selected="true"] {
              background: Highlight;
              color: HighlightText;
            }
          }
        `
      });

      // Emulate high contrast preference
      await mcpPage.emulateMedia({ prefersColorScheme: 'dark', prefersReducedMotion: 'no-preference' });

      // Take screenshot in high contrast mode
      await visualTester.takeScreenshot('tabs-high-contrast-mode');

      // Verify tabs are still interactive
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await expect(mcpPage.locator('[data-testid="tab-visualization"]')).toHaveClass(/active|selected/);
    });
  });

  test.describe('Tab Performance and Edge Cases', () => {
    test('should handle rapid tab switching without errors', async ({
      mcpPage,
      consoleMonitor,
      performanceMonitor
    }) => {
      const tabs = ['upload', 'visualization', 'analysis', 'settings'];

      performanceMonitor.mark('rapid-switching-start');

      // Rapidly switch between tabs
      for (let i = 0; i < 10; i++) {
        const randomTab = tabs[Math.floor(Math.random() * tabs.length)];
        await mcpPage.locator(`[data-testid="tab-${randomTab}"]`).click({ timeout: 1000 });

        // Brief wait to allow processing
        await mcpPage.waitForTimeout(100);
      }

      performanceMonitor.mark('rapid-switching-complete');

      // Verify final state is consistent
      const activeTab = mcpPage.locator('[aria-selected="true"]');
      await expect(activeTab).toHaveCount(1);

      // Verify no console errors from rapid switching
      consoleMonitor.expectNoErrors();

      // Check performance impact
      const metrics = await performanceMonitor.getMetrics();
      expect(metrics.cpuUsage).toBeLessThan(90); // Should remain performant
    });

    test('should maintain tab order consistency', async ({
      mcpPage
    }) => {
      // Get initial tab order
      const initialTabs = await mcpPage.locator('[data-testid^="tab-"]').allTextContents();

      // Interact with tabs
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await mcpPage.locator('[data-testid="tab-settings"]').click();
      await mcpPage.locator('[data-testid="tab-upload"]').click();

      // Verify tab order hasn't changed
      const finalTabs = await mcpPage.locator('[data-testid^="tab-"]').allTextContents();
      expect(finalTabs).toEqual(initialTabs);
    });

    test('should handle browser back/forward with tabs', async ({
      mcpPage
    }) => {
      // Switch to visualization tab
      await mcpPage.locator('[data-testid="tab-visualization"]').click();
      await expect(mcpPage.locator('[data-testid="tab-visualization"]')).toHaveClass(/active|selected/);

      // Switch to settings tab
      await mcpPage.locator('[data-testid="tab-settings"]').click();
      await expect(mcpPage.locator('[data-testid="tab-settings"]')).toHaveClass(/active|selected/);

      // Use browser back button
      await mcpPage.goBack();

      // Should return to visualization tab if history is managed
      // Or remain on settings if tabs don't use history API
      const activeTab = await mcpPage.locator('[aria-selected="true"]').getAttribute('data-testid');
      expect(activeTab).toMatch(/^tab-/);

      // Use browser forward button
      await mcpPage.goForward();

      // Verify consistent state
      const finalActiveTab = await mcpPage.locator('[aria-selected="true"]').getAttribute('data-testid');
      expect(finalActiveTab).toMatch(/^tab-/);
    });
  });
});
