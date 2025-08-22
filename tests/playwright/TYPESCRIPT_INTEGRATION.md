# TypeScript Integration for MELD Visualizer Test Suite

## Overview

This comprehensive TypeScript integration provides type-safe testing infrastructure for the MELD Visualizer Dash application. The integration includes:

- **Full TypeScript configuration** with strict type checking
- **Type-safe page objects** for all MELD Visualizer components
- **Comprehensive type definitions** for MELD data, Dash components, and Plotly visualizations
- **Enhanced MCP utilities** with complete type safety
- **Validation utilities** for test data and configurations
- **Sample test files** demonstrating best practices

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- TypeScript 5.1+
- Playwright Test Framework
- MELD Visualizer application running

### Installation
```bash
cd tests/playwright
npm install
```

### Type Checking
```bash
# Check all TypeScript types
npm run type-check

# Watch mode for development
npm run build:watch

# Validate strict typing
npm run validate:types
```

### Running Tests
```bash
# Run all tests with TypeScript config
npm run test

# Run with debugging
npm run test:debug

# Run specific test categories
npm run test:e2e
npm run test:performance
npm run test:visual

# Run with different browsers
npm run test:headed
```

## 📁 Project Structure

```
tests/playwright/
├── types/                    # TypeScript type definitions
│   ├── meld-data.d.ts       # MELD manufacturing data types
│   ├── dash-components.d.ts  # Dash component interfaces
│   ├── plotly-types.d.ts    # Plotly visualization types
│   ├── test-types.d.ts      # Test configuration types
│   └── index.d.ts           # Exported type definitions
├── config/                   # Configuration files
│   ├── playwright.config.ts # TypeScript Playwright config
│   └── mcp-utils.ts         # Type-safe MCP utilities
├── fixtures/                # Test fixtures
│   └── mcp-fixtures.ts      # Type-safe fixture definitions
├── utils/                   # Utility functions
│   ├── page-objects.ts      # Type-safe page objects
│   └── test-data-validators.ts # Data validation utilities
├── e2e/                     # End-to-end tests
│   └── meld-visualizer.spec.ts # Sample TypeScript tests
├── tsconfig.json            # TypeScript configuration
└── package.json             # Updated with TS scripts
```

## 🏗️ Architecture

### Type System Hierarchy

```typescript
// Core data types
MELDData.DataPoint → Individual measurement
MELDData.Dataset → Collection with metadata  
MELDData.ValidationResult → Validation outcomes

// UI component types
DashComponents.* → Dash framework components
PlotlyTypes.* → 3D visualization types

// Test infrastructure types  
TestTypes.* → Test configuration and utilities
```

### Key Design Principles

1. **Strict Type Safety**: All functions use strict TypeScript with comprehensive type checking
2. **Immutable Data**: Readonly interfaces prevent accidental mutations
3. **Generic Utilities**: Reusable type-safe utilities for common operations
4. **Error Safety**: Proper error handling with typed exceptions
5. **Performance Focus**: Optimized types for large datasets

## 🔧 Configuration

### TypeScript Configuration (`tsconfig.json`)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "strict": true,
    "noImplicitAny": true,
    "noImplicitReturns": true,
    "exactOptionalPropertyTypes": true,
    "noUncheckedIndexedAccess": true
  }
}
```

### Environment Variables

```bash
# Test execution
BASE_URL=http://localhost:8050
NAVIGATION_TIMEOUT=30000
ACTION_TIMEOUT=10000

# Performance thresholds
LOAD_TIME_THRESHOLD=5000
RENDER_TIME_THRESHOLD=2000

# Visual testing
SCREENSHOT_MODE=only-on-failure
TRACE_MODE=on-first-retry
```

## 📝 Usage Examples

### 1. Type-Safe Page Objects

```typescript
import { test } from '../fixtures/mcp-fixtures';

test('homepage interaction', async ({ homePage }) => {
  await homePage.goto();
  
  // Type-safe theme switching
  await homePage.switchTheme('dark'); // ✅ Valid theme
  // await homePage.switchTheme('invalid'); // ❌ TypeScript error
  
  // Type-safe navigation
  await homePage.navigateToTab('visualization');
});
```

### 2. MELD Data Validation

```typescript
import { MELDDataValidator } from '../utils/test-data-validators';

// Parse and validate CSV data
const { data, validation } = MELDDataValidator.parseCSV(csvContent);

if (validation.isValid) {
  // Type-safe data access
  data.forEach(point => {
    console.log(`Temperature: ${point.ToolTemp}°C`);
    console.log(`Position: (${point.XPos}, ${point.YPos}, ${point.ZPos})`);
  });
}
```

### 3. Performance Testing

```typescript
test('performance validation', async ({ performanceMonitor }) => {
  const metrics = await performanceMonitor.getMetrics();
  
  // Type-safe performance assertions
  expect(metrics).toMeetPerformanceThresholds({
    loadTime: 5000,
    renderTime: 2000,
    memoryUsage: 100_000_000
  });
});
```

### 4. Visual Testing

```typescript
test('visual regression', async ({ visualTester }) => {
  // Type-safe screenshot configuration
  const result = await visualTester.compareScreenshot('homepage', {
    threshold: 0.1,
    fullPage: true,
    animations: 'disabled'
  });
  
  expect(result.passed).toBeTruthy();
});
```

### 5. Network Mocking

```typescript
test('API mocking', async ({ networkMocker }) => {
  // Type-safe callback mocking
  await networkMocker.mockDashCallback('graph-3d', {
    data: [{ type: 'scatter3d', x: [1,2,3], y: [1,2,3], z: [1,2,3] }],
    layout: { title: 'Mock Graph' }
  });
});
```

## 🔍 Type Definitions

### Core MELD Data Types

```typescript
// Individual data point
interface MELDData.DataPoint {
  readonly Date: string;
  readonly Time: string;
  readonly XPos: number;
  readonly YPos: number;
  readonly ZPos: number;
  readonly ToolTemp: number;
  // ... 25+ additional fields
}

// Enhanced 3D point
interface MELDData.MELDPoint3D extends Point3D {
  readonly temperature: number;
  readonly velocity: number;
  readonly timestamp: string;
  readonly layer?: number;
}
```

### Dash Component Types

```typescript
// Theme configuration
interface DashComponents.ThemeConfig {
  readonly name: 'light' | 'dark' | 'plotly' | 'plotly_dark';
  readonly colors: ThemeColors;
  readonly fonts: ThemeFonts;
}

// File upload structure  
interface DashComponents.UploadedFile {
  readonly filename: string;
  readonly contents: string; // base64
  readonly size: number;
  readonly type: string;
}
```

### Plotly Visualization Types

```typescript
// 3D scatter trace
interface PlotlyTypes.Scatter3DTrace {
  readonly type: 'scatter3d';
  readonly x: ReadonlyArray<number>;
  readonly y: ReadonlyArray<number>;
  readonly z: ReadonlyArray<number>;
  readonly marker?: Scatter3DMarker;
}
```

### Test Configuration Types

```typescript
// Complete test configuration
interface TestTypes.MELDTestConfig {
  readonly baseURL: string;
  readonly timeout: TestTimeouts;
  readonly performance: PerformanceThresholds;
  readonly files: TestFileConfig;
}
```

## 🛠️ Development Guidelines

### Writing Type-Safe Tests

1. **Use Typed Fixtures**: Always use the provided typed fixtures
2. **Validate Data**: Use validation utilities for MELD data
3. **Type Assertions**: Prefer type-safe assertions over generic ones
4. **Error Handling**: Handle errors with proper typing
5. **Performance**: Use performance monitoring fixtures

### Best Practices

```typescript
// ✅ Good - Type-safe data handling
const { data, validation } = MELDDataValidator.parseCSV(content);
expect(data).toBeValidMELDData();

// ❌ Avoid - Untyped data access
const data = JSON.parse(content);
expect(data).toBeDefined();

// ✅ Good - Type-safe page interactions
await homePage.switchTheme('dark');
const currentTheme = await homePage.getCurrentTheme();

// ❌ Avoid - Untyped interactions  
await page.click('.theme-toggle');
const theme = await page.evaluate('document.body.className');
```

### Custom Matchers

The integration includes custom Playwright matchers:

```typescript
// Plotly data validation
expect(plotElement).toHavePlotlyData();

// Viewport checks
expect(element).toBeInViewport();

// Performance validation
expect(metrics).toMeetPerformanceThresholds(thresholds);

// MELD data validation
expect(dataArray).toBeValidMELDData();
```

## 🚨 Error Handling

### Common Type Errors

1. **Missing Required Properties**
```typescript
// ❌ Error: Property 'XPos' is missing
const point: MELDData.DataPoint = { Date: '2024-01-01' };

// ✅ Fixed: Include all required properties
const point: MELDData.DataPoint = {
  Date: '2024-01-01',
  Time: '10:00:00.00',
  XPos: 1.0,
  YPos: 2.0,
  ZPos: 3.0,
  ToolTemp: 250.0,
  // ... other required fields
};
```

2. **Invalid Theme Names**
```typescript
// ❌ Error: Argument of type '"blue"' is not assignable
await homePage.switchTheme('blue');

// ✅ Fixed: Use valid theme name
await homePage.switchTheme('dark');
```

3. **Incorrect Data Types**
```typescript
// ❌ Error: Type 'string' is not assignable to type 'number'
const point = { XPos: '1.5', YPos: 2.5, ZPos: 3.5 };

// ✅ Fixed: Use correct numeric types
const point = { XPos: 1.5, YPos: 2.5, ZPos: 3.5 };
```

## 🔬 Testing Features

### Data Generation

```typescript
// Generate synthetic test data
const dataset = TestDataGenerator.generateMELDDataset({
  seed: 12345,
  count: 100,
  ranges: {
    ToolTemp: [200, 400],
    XPos: [0, 50]
  },
  distributions: {
    ToolTemp: 'normal'
  }
});
```

### Performance Benchmarking

```typescript
// Benchmark test execution
const { result, duration, memoryUsage } = await PerformanceTestUtils.benchmark(
  'data-processing',
  async () => {
    return await processLargeDataset(data);
  }
);
```

### Visual Regression

```typescript
// Compare screenshots with configuration
const result = await visualTester.compareScreenshot('component', {
  threshold: 0.1,
  animations: 'disabled',
  clip: { x: 0, y: 0, width: 800, height: 600 }
});
```

## 📊 Monitoring and Debugging

### Performance Monitoring

```typescript
// Track performance checkpoints
performanceMonitor.mark('operation-start');
await performOperation();
performanceMonitor.mark('operation-complete');

const metrics = await performanceMonitor.getMetrics();
console.log('Performance:', metrics);
```

### Console Monitoring

```typescript
// Monitor and validate console output
consoleMonitor.expectNoErrors();
const warnings = consoleMonitor.getWarnings();
expect(warnings).toHaveLength(0);
```

### Network Debugging

```typescript
// Export comprehensive logs
const logs = mcpUtils.exportLogs();
await mcpUtils.saveLogsToFile('debug-session.json');
```

## 🤝 Contributing

### Adding New Types

1. Create type definitions in appropriate `.d.ts` files
2. Export types through `types/index.d.ts`
3. Add validation utilities if needed
4. Update page objects with new functionality
5. Write tests demonstrating usage

### Testing Checklist

- [ ] All types compile without errors (`npm run type-check`)
- [ ] Tests pass with type safety enabled
- [ ] Page objects are properly typed
- [ ] Data validation works correctly
- [ ] Performance monitoring functions
- [ ] Visual regression tests pass
- [ ] Documentation is updated

## 📚 References

- [Playwright TypeScript Guide](https://playwright.dev/docs/test-typescript)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Plotly.js TypeScript Types](https://github.com/plotly/plotly.js/tree/master/src/types)
- [Dash Component Documentation](https://dash.plotly.com/dash-core-components)

## 🐛 Troubleshooting

### Common Issues

1. **TypeScript compilation errors**
   - Run `npm run type-check` for detailed error information
   - Check `tsconfig.json` configuration
   - Verify all imports are properly typed

2. **Runtime type mismatches**
   - Use data validation utilities
   - Check network mocking configurations
   - Validate test data fixtures

3. **Performance test failures**
   - Adjust thresholds in test configuration
   - Monitor system resources during testing
   - Use performance utilities for debugging

4. **Visual regression failures**
   - Check screenshot thresholds
   - Verify browser consistency
   - Update baselines if UI changes are intentional

For additional support, refer to the test logs and performance metrics exported by the MCP utilities.