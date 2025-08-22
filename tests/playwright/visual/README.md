# Visual Regression Testing Framework

A comprehensive visual testing suite for the MELD Visualizer Dash application, providing robust visual regression testing, cross-browser consistency validation, and accessibility compliance verification.

## 🎯 Overview

This framework provides:
- **Visual Regression Testing**: Automated screenshot comparison to catch unintended UI changes
- **Cross-Browser Consistency**: Visual validation across Chrome, Firefox, and Safari
- **Responsive Design Testing**: Layout validation across multiple viewports
- **Theme Visual Validation**: Comprehensive testing of light/dark themes and color schemes
- **Component Visual Testing**: Individual component state and interaction validation
- **Animation & Transition Testing**: Smooth animation and transition validation
- **Accessibility Visual Testing**: WCAG compliance and focus indicator validation
- **CSS Validation**: Layout consistency, typography, and performance assessment

## 📁 Framework Structure

```
tests/playwright/visual/
├── README.md                    # This documentation
├── visual-config.ts            # Core configuration and constants
├── visual-utils.ts             # Screenshot utilities and helpers
├── visual-test-suite.ts        # Main test suite orchestration
├── cross-browser-tests.ts      # Cross-browser consistency tests
├── responsive-tests.ts         # Responsive design validation
├── theme-tests.ts             # Theme and color scheme testing
├── component-tests.ts          # Individual component testing
├── animation-tests.ts          # Animation and transition testing
├── accessibility-tests.ts      # Accessibility visual validation
├── css-validation-tests.ts     # CSS and layout validation
└── baselines/                  # Visual baseline screenshots
```

## 🚀 Quick Start

### Prerequisites

Ensure the MELD Visualizer application is running:
```bash
# Start the application
python -m src.meld_visualizer
# Application should be available at http://localhost:8050
```

### Running Visual Tests

```bash
# Run all visual tests
npm run test:visual

# Run specific test categories
npm run test:visual -- --grep "@cross-browser"
npm run test:visual -- --grep "@responsive"
npm run test:visual -- --grep "@theme"
npm run test:visual -- --grep "@accessibility"

# Update visual baselines
npm run update:snapshots

# Run tests in headed mode (see browser)
npm run test:visual:headed

# Run tests with UI mode
npm run test:ui
```

### Using MCP Integration

```bash
# Run visual tests via MCP
python ../run_playwright_mcp_tests.py --type visual

# Run specific visual test category
python ../run_playwright_mcp_tests.py --type visual --grep "@theme"

# Update baselines via MCP
python ../run_playwright_mcp_tests.py --type visual --update-snapshots
```

## 🧪 Test Categories

### 1. Cross-Browser Consistency (`cross-browser-tests.ts`)

Validates visual consistency across different browsers:
- Chrome/Chromium rendering
- Firefox compatibility
- Safari/WebKit consistency
- Typography and font rendering differences
- Form control styling variations
- CSS Grid and Flexbox layout consistency

**Key Tests:**
- Full page layout consistency
- Component rendering differences
- Form controls across browsers
- CSS effects and animations
- Typography rendering

### 2. Responsive Design (`responsive-tests.ts`)

Tests layout behavior across different screen sizes:
- Mobile (375×667, 667×375)
- Tablet (768×1024, 1024×768)
- Desktop (1280×720, 1920×1080, 2560×1440)

**Key Tests:**
- Viewport breakpoint transitions
- Navigation collapse/expansion
- Content reflow and text wrapping
- Image responsiveness
- Form layout adaptation

### 3. Theme Visual Validation (`theme-tests.ts`)

Comprehensive theme testing:
- Light and dark themes
- Bootstrap theme variants (Cerulean, Cosmo, Cyborg, Darkly)
- Color scheme consistency
- Theme transition animations
- Accessibility in different themes

**Key Tests:**
- Theme application across components
- Color contrast validation
- Theme transition smoothness
- Component theming consistency
- Responsive theme behavior

### 4. Component Visual Testing (`component-tests.ts`)

Individual component state validation:
- File upload states (empty, loading, success, error)
- Navigation tab states and transitions
- Plotly graph rendering consistency
- Data table variations
- Export component states

**Key Tests:**
- Component state variations
- Interactive element feedback
- Loading and error states
- Form validation displays
- Button and link styles

### 5. Animation & Transitions (`animation-tests.ts`)

Animation consistency and performance:
- Theme transition animations
- Loading spinner consistency
- Button hover effects
- Form input focus animations
- Plotly graph animations

**Key Tests:**
- Animation smoothness
- Transition timing consistency
- Reduced motion compliance
- Performance impact assessment
- Interactive feedback animations

### 6. Accessibility Visual Testing (`accessibility-tests.ts`)

WCAG compliance and accessibility features:
- Focus indicator visibility
- Color contrast validation
- High contrast mode compatibility
- Screen reader visual context
- Keyboard navigation indicators

**Key Tests:**
- Focus ring visibility
- Color contrast ratios
- High contrast mode support
- ARIA visual indicators
- Error state accessibility

### 7. CSS Validation (`css-validation-tests.ts`)

CSS consistency and performance:
- CSS Grid and Flexbox layouts
- Typography and font stacks
- Custom properties and variables
- Layout stability (CLS)
- Performance metrics

**Key Tests:**
- Layout algorithm consistency
- Typography rendering
- CSS variable functionality
- Layout shift prevention
- Performance impact

## ⚙️ Configuration

### Visual Test Configuration (`visual-config.ts`)

```typescript
// Screenshot comparison settings
export const DEFAULT_VISUAL_CONFIG = {
  threshold: 0.2,           // Pixel difference threshold
  maxDiffPixels: 100,       // Maximum different pixels allowed
  pixelRatio: 1,           // Device pixel ratio
  animations: 'disabled',  // Animation state
  caret: 'hide'            // Text cursor visibility
};

// Browser configurations
export const BROWSER_CONFIGS = {
  chromium: { /* Chrome settings */ },
  firefox: { /* Firefox settings */ },
  webkit: { /* Safari settings */ }
};
```

### Viewport Testing (`RESPONSIVE_VIEWPORTS`)

```typescript
export const RESPONSIVE_VIEWPORTS = {
  mobile: { width: 375, height: 667 },
  tablet: { width: 768, height: 1024 },
  desktop: { width: 1280, height: 720 },
  // ... additional viewports
};
```

### Theme Configurations (`THEME_CONFIGS`)

```typescript
export const THEME_CONFIGS = {
  light: { colorScheme: 'light', mode: 'light' },
  dark: { colorScheme: 'dark', mode: 'dark' },
  bootstrap: { theme: 'BOOTSTRAP' },
  // ... additional themes
};
```

## 🛠️ Utilities and Helpers

### VisualTestUtils Class

```typescript
const visualUtils = new VisualTestUtils(page);

// Wait for animations to complete
await visualUtils.waitForAnimationsToComplete();

// Wait for Plotly graphs to render
await visualUtils.waitForPlotlyRender();

// Set theme and wait for transition
await visualUtils.setTheme('dark');

// Set viewport and wait for layout
await visualUtils.setViewport('tablet');

// Take component screenshot
await visualUtils.screenshotComponent('#component', 'component-name');

// Take full page screenshot
await visualUtils.screenshotFullPage('page-name');
```

### Baseline Management

```typescript
const baselineManager = new BaselineManager();

// Update baselines
await baselineManager.updateBaselines('test-name');

// Compare with baseline
const result = await baselineManager.compareWithBaseline(
  'current-screenshot', 
  'baseline-name'
);
```

## 📊 Test Execution and Reporting

### Running Specific Test Suites

```bash
# Smoke tests (critical components only)
npm run test:visual -- --grep "@smoke"

# Regression tests (comprehensive suite)
npm run test:visual -- --grep "@regression"

# Cross-browser tests
npm run test:visual -- --grep "@cross-browser"

# Performance impact tests
npm run test:visual -- --grep "@performance"
```

### Updating Baselines

When UI changes are intentional:

```bash
# Update all baselines
npm run update:snapshots

# Update specific test baselines
npm run test:visual -- --update-snapshots --grep "component-name"
```

### Test Reports

Visual test reports include:
- HTML report with screenshot comparisons
- JSON results for CI/CD integration
- JUnit XML for test result tracking
- Performance metrics and CLS scores

## 🔧 Debugging and Troubleshooting

### Common Issues

1. **Screenshot Differences**
   - Check if application is running on correct port
   - Verify font loading completion
   - Ensure consistent browser state

2. **Animation Timing Issues**
   - Increase wait times for complex animations
   - Use `waitForAnimationsToComplete()` utility
   - Check reduced motion preferences

3. **Cross-Browser Inconsistencies**
   - Review browser-specific CSS properties
   - Check font availability across browsers
   - Validate vendor prefix usage

### Debug Mode

```bash
# Run tests in debug mode
npm run test:visual -- --debug

# Run with headed browser
npm run test:visual -- --headed

# Use UI mode for interactive debugging
npm run test:ui
```

### Troubleshooting Screenshots

```typescript
// Take debug screenshots
await page.screenshot({ path: 'debug-screenshot.png' });

// Log element information
const element = page.locator('#component');
console.log(await element.boundingBox());

// Check element visibility
console.log(await element.isVisible());
```

## 🎯 Best Practices

### 1. Test Organization
- Group related tests in describe blocks
- Use descriptive test names
- Tag tests appropriately (@visual, @cross-browser, etc.)

### 2. Screenshot Consistency
- Always disable animations for static screenshots
- Wait for content to fully load
- Use consistent viewport sizes
- Mask dynamic content (timestamps, random IDs)

### 3. Baseline Management
- Update baselines only for intentional changes
- Review screenshot diffs carefully
- Keep baseline images in version control
- Document major UI changes

### 4. Performance Considerations
- Run visual tests in parallel when possible
- Use appropriate timeout values
- Monitor test execution time
- Optimize screenshot sizes

### 5. Accessibility Testing
- Include accessibility tests in CI/CD
- Validate focus indicators across themes
- Test color contrast ratios
- Verify high contrast mode compatibility

## 🚀 CI/CD Integration

### GitHub Actions Example

```yaml
name: Visual Regression Tests

on: [push, pull_request]

jobs:
  visual-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd tests/playwright
          npm install
          npx playwright install
      
      - name: Start application
        run: |
          python -m src.meld_visualizer &
          sleep 10
      
      - name: Run visual tests
        run: |
          cd tests/playwright
          npm run test:visual
      
      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: visual-test-results
          path: tests/playwright/visual-report/
```

## 📈 Metrics and Monitoring

The framework tracks:
- Screenshot comparison accuracy
- Test execution performance
- Cross-browser consistency scores
- Accessibility compliance rates
- Layout stability metrics (CLS)
- Animation performance impact

## 🤝 Contributing

When adding new visual tests:

1. Follow existing naming conventions
2. Add appropriate test tags
3. Include comprehensive documentation
4. Update baselines as needed
5. Test across multiple browsers
6. Validate accessibility compliance

## 📚 References

- [Playwright Visual Testing Documentation](https://playwright.dev/docs/test-snapshots)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Web Vitals](https://web.dev/vitals/)
- [CSS Grid Layout](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [CSS Flexbox](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout)

---

## 🔍 Framework Summary

This visual regression testing framework provides comprehensive coverage for:

- ✅ **Visual Regression Detection**: Automated screenshot comparison
- ✅ **Cross-Browser Consistency**: Chrome, Firefox, Safari validation
- ✅ **Responsive Design Testing**: Multiple viewport validation
- ✅ **Theme Compatibility**: Light/dark theme consistency
- ✅ **Component State Testing**: All UI component variations
- ✅ **Animation Validation**: Smooth transitions and effects
- ✅ **Accessibility Compliance**: WCAG 2.1 visual validation
- ✅ **CSS Layout Validation**: Grid, Flexbox, and typography
- ✅ **Performance Assessment**: CLS and layout stability
- ✅ **Baseline Management**: Screenshot comparison utilities

The framework is designed to catch visual regressions early, ensure consistent user experience across browsers and devices, and maintain high accessibility standards for the MELD Visualizer application.