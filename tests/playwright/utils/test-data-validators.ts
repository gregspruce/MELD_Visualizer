/**
 * TypeScript Utility Functions for Test Data Validation
 * Comprehensive validation and transformation utilities for MELD Visualizer testing
 */

import type { 
  MELDData, 
  TestTypes, 
  DashComponents, 
  PlotlyTypes 
} from '../types';

/**
 * MELD Data Validation Utilities
 */
export class MELDDataValidator {
  private static readonly REQUIRED_FIELDS: Array<keyof MELDData.DataPoint> = [
    'Date', 'Time', 'XPos', 'YPos', 'ZPos', 'ToolTemp'
  ];

  private static readonly NUMERIC_FIELDS: Array<keyof MELDData.DataPoint> = [
    'SpinVel', 'SpinTrq', 'SpinPwr', 'SpinSP', 'FeedVel', 'FeedPos', 'FeedTrq',
    'FRO', 'PathVel', 'XPos', 'XVel', 'XTrq', 'YPos', 'YVel', 'YTrq',
    'ZPos', 'ZVel', 'ZTrq', 'Gcode', 'Low', 'High', 'Ktype1', 'Ktype2',
    'Ktype3', 'Ktype4', 'O2', 'ToolTemp', 'Tool2Temp'
  ];

  private static readonly FIELD_RANGES: Record<string, { min: number; max: number }> = {
    ToolTemp: { min: 0, max: 1000 },
    Tool2Temp: { min: 0, max: 1000 },
    XPos: { min: -1000, max: 1000 },
    YPos: { min: -1000, max: 1000 },
    ZPos: { min: -100, max: 100 },
    SpinVel: { min: 0, max: 10000 },
    SpinPwr: { min: 0, max: 50000 },
    O2: { min: 0, max: 1 },
    Ktype1: { min: 0, max: 2000 },
    Ktype2: { min: 0, max: 2000 },
    Ktype3: { min: 0, max: 2000 },
    Ktype4: { min: 0, max: 2000 }
  };

  /**
   * Validate a single MELD data point with comprehensive checks
   */
  static validateDataPoint(
    point: unknown, 
    rowIndex?: number
  ): { isValid: boolean; errors: MELDData.ValidationError[]; warnings: MELDData.ValidationWarning[] } {
    const errors: MELDData.ValidationError[] = [];
    const warnings: MELDData.ValidationWarning[] = [];

    if (typeof point !== 'object' || point === null) {
      errors.push({
        field: 'Date', // Use a required field as placeholder
        row: rowIndex || 0,
        value: point,
        message: 'Data point must be an object',
        severity: 'error'
      });
      return { isValid: false, errors, warnings };
    }

    const dataPoint = point as Partial<MELDData.DataPoint>;

    // Check required fields
    for (const field of this.REQUIRED_FIELDS) {
      if (dataPoint[field] === undefined || dataPoint[field] === null) {
        errors.push({
          field,
          row: rowIndex || 0,
          value: dataPoint[field],
          message: `Required field '${field}' is missing`,
          severity: 'error'
        });
      }
    }

    // Validate numeric fields
    for (const field of this.NUMERIC_FIELDS) {
      const value = dataPoint[field];
      if (value !== undefined && value !== null) {
        const numericValue = Number(value);
        
        if (isNaN(numericValue)) {
          errors.push({
            field,
            row: rowIndex || 0,
            value,
            message: `Field '${field}' must be numeric, got '${value}'`,
            severity: 'error'
          });
        } else {
          // Check ranges
          const range = this.FIELD_RANGES[field];
          if (range && (numericValue < range.min || numericValue > range.max)) {
            const severity = this.isRangeCritical(field) ? 'error' : 'warning';
            const message = `Field '${field}' value ${numericValue} is outside expected range [${range.min}, ${range.max}]`;
            
            if (severity === 'error') {
              errors.push({ field, row: rowIndex || 0, value, message, severity });
            } else {
              warnings.push({ field, row: rowIndex || 0, value, message });
            }
          }
        }
      }
    }

    // Validate date/time format
    if (dataPoint.Date && typeof dataPoint.Date === 'string') {
      if (!/^\d{4}-\d{2}-\d{2}$/.test(dataPoint.Date)) {
        errors.push({
          field: 'Date',
          row: rowIndex || 0,
          value: dataPoint.Date,
          message: 'Date must be in YYYY-MM-DD format',
          severity: 'error'
        });
      }
    }

    if (dataPoint.Time && typeof dataPoint.Time === 'string') {
      if (!/^\d{2}:\d{2}:\d{2}\.\d{2}$/.test(dataPoint.Time)) {
        warnings.push({
          field: 'Time',
          row: rowIndex || 0,
          value: dataPoint.Time,
          message: 'Time format should be HH:MM:SS.ss',
          suggestion: 'Use format like "10:30:45.00"'
        });
      }
    }

    // Physical consistency checks
    this.performConsistencyChecks(dataPoint, rowIndex || 0, warnings);

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Validate an array of MELD data points
   */
  static validateDataset(data: unknown[]): MELDData.ValidationResult {
    const allErrors: MELDData.ValidationError[] = [];
    const allWarnings: MELDData.ValidationWarning[] = [];
    let validRows = 0;

    if (!Array.isArray(data)) {
      allErrors.push({
        field: 'Date',
        row: 0,
        value: data,
        message: 'Data must be an array',
        severity: 'error'
      });
      
      return {
        isValid: false,
        errors: allErrors,
        warnings: allWarnings,
        summary: {
          totalRows: 0,
          validRows: 0,
          errorCount: 1,
          warningCount: 0,
          completeness: 0,
          dataQuality: 'poor'
        }
      };
    }

    // Validate each row
    data.forEach((point, index) => {
      const result = this.validateDataPoint(point, index);
      allErrors.push(...result.errors);
      allWarnings.push(...result.warnings);
      
      if (result.isValid) {
        validRows++;
      }
    });

    // Calculate completeness
    const completeness = data.length > 0 ? (validRows / data.length) * 100 : 0;

    // Determine data quality
    let dataQuality: MELDData.ValidationSummary['dataQuality'];
    if (completeness >= 95 && allErrors.length === 0) {
      dataQuality = 'excellent';
    } else if (completeness >= 85 && allErrors.length < data.length * 0.1) {
      dataQuality = 'good';
    } else if (completeness >= 70 && allErrors.length < data.length * 0.25) {
      dataQuality = 'fair';
    } else {
      dataQuality = 'poor';
    }

    return {
      isValid: allErrors.length === 0,
      errors: allErrors,
      warnings: allWarnings,
      summary: {
        totalRows: data.length,
        validRows,
        errorCount: allErrors.length,
        warningCount: allWarnings.length,
        completeness,
        dataQuality
      }
    };
  }

  /**
   * Check if a range violation is critical for operation
   */
  private static isRangeCritical(field: string): boolean {
    const criticalFields = ['ToolTemp', 'XPos', 'YPos', 'ZPos'];
    return criticalFields.includes(field);
  }

  /**
   * Perform physics-based consistency checks
   */
  private static performConsistencyChecks(
    point: Partial<MELDData.DataPoint>, 
    rowIndex: number,
    warnings: MELDData.ValidationWarning[]
  ): void {
    // Temperature consistency
    if (point.ToolTemp && point.Tool2Temp) {
      const tempDiff = Math.abs(point.ToolTemp - point.Tool2Temp);
      if (tempDiff > 100) { // More than 100°C difference seems unusual
        warnings.push({
          field: 'ToolTemp',
          row: rowIndex,
          value: `Tool1: ${point.ToolTemp}, Tool2: ${point.Tool2Temp}`,
          message: `Large temperature difference between tools: ${tempDiff}°C`,
          suggestion: 'Verify sensor calibration'
        });
      }
    }

    // Velocity vs position consistency
    if (point.XVel && Math.abs(point.XVel) > 100) {
      warnings.push({
        field: 'XVel',
        row: rowIndex,
        value: point.XVel,
        message: 'Very high X velocity detected',
        suggestion: 'Check for measurement errors'
      });
    }

    // Power vs speed relationship
    if (point.SpinPwr && point.SpinVel) {
      const expectedPowerRange = [point.SpinVel * 0.5, point.SpinVel * 20];
      if (point.SpinPwr < expectedPowerRange[0] || point.SpinPwr > expectedPowerRange[1]) {
        warnings.push({
          field: 'SpinPwr',
          row: rowIndex,
          value: `Power: ${point.SpinPwr}, Speed: ${point.SpinVel}`,
          message: 'Unusual power-to-speed ratio',
          suggestion: 'Verify spindle efficiency parameters'
        });
      }
    }
  }

  /**
   * Parse CSV string to MELD data with validation
   */
  static parseCSV(csvContent: string, options: MELDData.CSVParseOptions = {
    delimiter: ',',
    skipEmptyLines: true,
    trimHeaders: true,
    encoding: 'utf-8',
    validateOnParse: true
  }): { data: MELDData.DataPoint[]; validation: MELDData.ValidationResult } {
    const lines = csvContent.split('\n').filter(line => 
      options.skipEmptyLines ? line.trim() : true
    );

    if (lines.length < 2) {
      const validation: MELDData.ValidationResult = {
        isValid: false,
        errors: [{
          field: 'Date',
          row: 0,
          value: csvContent,
          message: 'CSV must have at least header and one data row',
          severity: 'error'
        }],
        warnings: [],
        summary: {
          totalRows: 0,
          validRows: 0,
          errorCount: 1,
          warningCount: 0,
          completeness: 0,
          dataQuality: 'poor'
        }
      };
      
      return { data: [], validation };
    }

    // Parse header
    const headers = lines[0].split(options.delimiter).map(h => 
      options.trimHeaders ? h.trim() : h
    );

    // Parse data rows
    const dataRows: MELDData.DataPoint[] = [];
    const maxRows = options.maxRows || lines.length - 1;
    
    for (let i = 1; i <= Math.min(maxRows, lines.length - 1); i++) {
      const values = lines[i].split(options.delimiter);
      const row: Partial<MELDData.DataPoint> = {};
      
      headers.forEach((header, index) => {
        const value = values[index]?.trim();
        if (value !== undefined) {
          // Try to convert numeric fields
          if (this.NUMERIC_FIELDS.includes(header as keyof MELDData.DataPoint)) {
            const numericValue = Number(value);
            (row as any)[header] = isNaN(numericValue) ? value : numericValue;
          } else {
            (row as any)[header] = value;
          }
        }
      });
      
      dataRows.push(row as MELDData.DataPoint);
    }

    // Validate if requested
    let validation: MELDData.ValidationResult;
    if (options.validateOnParse) {
      validation = this.validateDataset(dataRows);
    } else {
      validation = {
        isValid: true,
        errors: [],
        warnings: [],
        summary: {
          totalRows: dataRows.length,
          validRows: dataRows.length,
          errorCount: 0,
          warningCount: 0,
          completeness: 100,
          dataQuality: 'excellent'
        }
      };
    }

    return { data: dataRows, validation };
  }
}

/**
 * Test Data Generation Utilities
 */
export class TestDataGenerator {
  /**
   * Generate synthetic MELD dataset for testing
   */
  static generateMELDDataset(config: TestTypes.TestDataGeneratorConfig): MELDData.Dataset {
    const generator = new MELDTestDataGenerator(config);
    const dataPoints = generator.generateDataPoints();
    
    return {
      data: dataPoints,
      metadata: {
        filename: `generated_test_data_${Date.now()}.csv`,
        fileSize: JSON.stringify(dataPoints).length,
        recordCount: dataPoints.length,
        startTime: dataPoints[0]?.Date + 'T' + dataPoints[0]?.Time || '',
        endTime: dataPoints[dataPoints.length - 1]?.Date + 'T' + dataPoints[dataPoints.length - 1]?.Time || '',
        duration: dataPoints.length, // seconds
        sampleRate: 1, // 1 Hz
        version: '1.0.0',
        machineId: 'TEST_MACHINE_001',
        operatorId: 'test_operator',
        materialType: 'Test Aluminum',
        processParameters: {
          targetTemperature: 300,
          feedRate: 10,
          spindleSpeed: 100,
          layerHeight: 2,
          toolDiameter: 5
        }
      },
      statistics: this.calculateStatistics(dataPoints)
    };
  }

  /**
   * Generate test fixtures for various scenarios
   */
  static generateTestFixtures(): {
    minimal: MELDData.Dataset;
    standard: MELDData.Dataset;
    large: MELDData.Dataset;
    edge: MELDData.Dataset;
  } {
    return {
      minimal: this.generateMELDDataset({
        seed: 12345,
        count: 3,
        template: {},
        ranges: {},
        patterns: {},
        distributions: {}
      }),
      
      standard: this.generateMELDDataset({
        seed: 23456,
        count: 100,
        template: {},
        ranges: {
          ToolTemp: [250, 350],
          XPos: [0, 50],
          YPos: [0, 30]
        },
        patterns: {},
        distributions: {
          ToolTemp: 'normal',
          SpinVel: 'normal'
        }
      }),
      
      large: this.generateMELDDataset({
        seed: 34567,
        count: 1000,
        template: {},
        ranges: {},
        patterns: {},
        distributions: {}
      }),
      
      edge: this.generateMELDDataset({
        seed: 45678,
        count: 10,
        template: {},
        ranges: {
          ToolTemp: [999, 1000], // Edge of valid range
          XPos: [-999, 999],
          YPos: [-999, 999],
          ZPos: [-99, 99]
        },
        patterns: {},
        distributions: {}
      })
    };
  }

  /**
   * Calculate comprehensive statistics for a dataset
   */
  private static calculateStatistics(data: MELDData.DataPoint[]): MELDData.DatasetStatistics {
    const calculateStats = (values: number[]): MELDData.StatsSummary => {
      if (values.length === 0) {
        return { min: 0, max: 0, mean: 0, median: 0, stdDev: 0, range: 0 };
      }
      
      const sorted = values.sort((a, b) => a - b);
      const min = sorted[0];
      const max = sorted[sorted.length - 1];
      const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
      const median = sorted.length % 2 === 0
        ? (sorted[sorted.length / 2 - 1] + sorted[sorted.length / 2]) / 2
        : sorted[Math.floor(sorted.length / 2)];
      
      const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
      const stdDev = Math.sqrt(variance);
      const range = max - min;
      
      return { min, max, mean, median, stdDev, range };
    };

    return {
      temperature: {
        toolTemp: calculateStats(data.map(d => d.ToolTemp)),
        tool2Temp: calculateStats(data.map(d => d.Tool2Temp)),
        ktype1: calculateStats(data.map(d => d.Ktype1)),
        ktype2: calculateStats(data.map(d => d.Ktype2)),
        ktype3: calculateStats(data.map(d => d.Ktype3)),
        ktype4: calculateStats(data.map(d => d.Ktype4))
      },
      position: {
        x: calculateStats(data.map(d => d.XPos)),
        y: calculateStats(data.map(d => d.YPos)),
        z: calculateStats(data.map(d => d.ZPos)),
        feedPos: calculateStats(data.map(d => d.FeedPos))
      },
      velocity: {
        x: calculateStats(data.map(d => d.XVel)),
        y: calculateStats(data.map(d => d.YVel)),
        z: calculateStats(data.map(d => d.ZVel)),
        feed: calculateStats(data.map(d => d.FeedVel)),
        path: calculateStats(data.map(d => d.PathVel)),
        spindle: calculateStats(data.map(d => d.SpinVel))
      },
      torque: {
        x: calculateStats(data.map(d => d.XTrq)),
        y: calculateStats(data.map(d => d.YTrq)),
        z: calculateStats(data.map(d => d.ZTrq)),
        feed: calculateStats(data.map(d => d.FeedTrq)),
        spindle: calculateStats(data.map(d => d.SpinTrq))
      },
      spindle: {
        velocity: calculateStats(data.map(d => d.SpinVel)),
        torque: calculateStats(data.map(d => d.SpinTrq)),
        power: calculateStats(data.map(d => d.SpinPwr)),
        setpoint: calculateStats(data.map(d => d.SpinSP))
      }
    };
  }
}

/**
 * Internal test data generator implementation
 */
class MELDTestDataGenerator {
  constructor(private config: TestTypes.TestDataGeneratorConfig) {}

  generateDataPoints(): MELDData.DataPoint[] {
    const points: MELDData.DataPoint[] = [];
    const { count, seed = 12345 } = this.config;
    
    let random = this.createSeededRandom(seed);
    const baseDate = new Date('2024-01-15T10:00:00.000Z');
    
    for (let i = 0; i < count; i++) {
      const timestamp = new Date(baseDate.getTime() + i * 1000);
      
      points.push({
        Date: timestamp.toISOString().split('T')[0],
        Time: timestamp.toTimeString().split(' ')[0] + '.00',
        SpinVel: this.generateValue('SpinVel', random, 50, 150),
        SpinTrq: this.generateValue('SpinTrq', random, 2, 8),
        SpinPwr: this.generateValue('SpinPwr', random, 100, 1200),
        SpinSP: this.generateValue('SpinSP', random, 50, 150),
        FeedVel: this.generateValue('FeedVel', random, 5, 20),
        FeedPos: this.generateValue('FeedPos', random, 0, 100),
        FeedTrq: this.generateValue('FeedTrq', random, 1, 5),
        FRO: 100,
        PathVel: this.generateValue('PathVel', random, 10, 25),
        XPos: this.generateValue('XPos', random, 0, 50),
        XVel: this.generateValue('XVel', random, 0, 10),
        XTrq: this.generateValue('XTrq', random, 0, 5),
        YPos: this.generateValue('YPos', random, 0, 30),
        YVel: this.generateValue('YVel', random, 0, 10),
        YTrq: this.generateValue('YTrq', random, 0, 5),
        ZPos: this.generateValue('ZPos', random, 0, 10),
        ZVel: this.generateValue('ZVel', random, 0, 5),
        ZTrq: this.generateValue('ZTrq', random, 0, 3),
        Gcode: Math.floor(i / 10) + 10,
        Low: this.generateValue('Low', random, 20, 50),
        High: this.generateValue('High', random, 20, 50),
        Ktype1: this.generateValue('Ktype1', random, 200, 500),
        Ktype2: this.generateValue('Ktype2', random, 200, 500),
        Ktype3: this.generateValue('Ktype3', random, 200, 500),
        Ktype4: this.generateValue('Ktype4', random, 200, 500),
        O2: this.generateValue('O2', random, 0.18, 0.25),
        ToolTemp: this.generateValue('ToolTemp', random, 100, 200),
        Tool2Temp: this.generateValue('Tool2Temp', random, 50, 100)
      });
    }
    
    return points;
  }

  private createSeededRandom(seed: number): () => number {
    return () => {
      seed = (seed * 9301 + 49297) % 233280;
      return seed / 233280;
    };
  }

  private generateValue(
    field: keyof MELDData.DataPoint, 
    random: () => number, 
    min: number, 
    max: number
  ): number {
    const range = this.config.ranges?.[field];
    const actualMin = range ? range[0] : min;
    const actualMax = range ? range[1] : max;
    
    const distribution = this.config.distributions?.[field] || 'uniform';
    
    switch (distribution) {
      case 'normal':
        const u1 = random();
        const u2 = random();
        const z0 = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
        const mean = (actualMin + actualMax) / 2;
        const stdDev = (actualMax - actualMin) / 6;
        return Math.max(actualMin, Math.min(actualMax, mean + z0 * stdDev));
      
      case 'exponential':
        const lambda = 1 / ((actualMax - actualMin) / 2);
        return actualMin - Math.log(random()) / lambda;
      
      default:
        return actualMin + random() * (actualMax - actualMin);
    }
  }
}

/**
 * Performance Testing Utilities
 */
export class PerformanceTestUtils {
  /**
   * Create performance assertion builder
   */
  static createPerformanceAssertion(): TestTypes.TestUtilityTypes.ResultFormatter<TestTypes.PerformanceThresholds> {
    return (results: ReadonlyArray<TestTypes.TestResult>): TestTypes.PerformanceThresholds => {
      // Aggregate performance metrics from test results
      const metrics = results
        .map(r => r.performance)
        .filter(p => p !== undefined) as TestTypes.PerformanceMetrics[];
      
      if (metrics.length === 0) {
        return {
          loadTime: 5000,
          renderTime: 2000,
          interactionTime: 100,
          memoryUsage: 100000000,
          cpuUsage: 80,
          networkRequests: 50
        };
      }
      
      return {
        loadTime: Math.max(...metrics.map(m => m.loadTime)),
        renderTime: Math.max(...metrics.map(m => m.renderTime)),
        interactionTime: Math.max(...metrics.map(m => m.interactionTime || 0)),
        memoryUsage: Math.max(...metrics.map(m => m.memoryUsage || 0)),
        cpuUsage: 80, // Would need to be measured separately
        networkRequests: Math.max(...metrics.map(m => m.networkRequests || 0))
      };
    };
  }

  /**
   * Benchmark test execution time
   */
  static async benchmark<T>(
    name: string, 
    testFunction: () => Promise<T>
  ): Promise<{ result: T; duration: number; memoryUsage: number }> {
    const startTime = process.hrtime.bigint();
    const startMemory = process.memoryUsage().heapUsed;
    
    try {
      const result = await testFunction();
      const endTime = process.hrtime.bigint();
      const endMemory = process.memoryUsage().heapUsed;
      
      const duration = Number(endTime - startTime) / 1000000; // Convert to milliseconds
      const memoryUsage = endMemory - startMemory;
      
      console.log(`⏱️  Benchmark "${name}": ${duration.toFixed(2)}ms, Memory: ${memoryUsage} bytes`);
      
      return { result, duration, memoryUsage };
    } catch (error) {
      const endTime = process.hrtime.bigint();
      const duration = Number(endTime - startTime) / 1000000;
      
      console.error(`❌ Benchmark "${name}" failed after ${duration.toFixed(2)}ms:`, error);
      throw error;
    }
  }
}

/**
 * Configuration Validation Utilities
 */
export class ConfigValidator implements TestTypes.ConfigValidator {
  /**
   * Validate test configuration
   */
  validateTestConfig(config: TestTypes.MELDTestConfig): { valid: boolean; errors: ReadonlyArray<string> } {
    const errors: string[] = [];
    
    try {
      // Validate URL
      new URL(config.baseURL);
    } catch {
      errors.push(`Invalid baseURL: ${config.baseURL}`);
    }
    
    // Validate timeouts
    Object.entries(config.timeout).forEach(([key, value]) => {
      if (typeof value !== 'number' || value <= 0) {
        errors.push(`Invalid timeout ${key}: ${value}`);
      }
    });
    
    // Validate viewport
    if (config.viewport.width <= 0 || config.viewport.height <= 0) {
      errors.push(`Invalid viewport dimensions: ${config.viewport.width}x${config.viewport.height}`);
    }
    
    // Validate performance thresholds
    Object.entries(config.performance).forEach(([key, value]) => {
      if (typeof value !== 'number' || value <= 0) {
        errors.push(`Invalid performance threshold ${key}: ${value}`);
      }
    });
    
    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Validate MELD data structure
   */
  validateMELDData(data: unknown): data is MELDData.DataPoint {
    return MELDDataValidator.validateDataPoint(data).isValid;
  }

  /**
   * Validate Plotly configuration
   */
  validatePlotlyConfig(config: unknown): config is PlotlyTypes.PlotlyConfig {
    if (typeof config !== 'object' || config === null) {
      return false;
    }
    
    const plotlyConfig = config as PlotlyTypes.PlotlyConfig;
    
    // Check for valid boolean properties
    const booleanProps = ['staticPlot', 'editable', 'responsive', 'scrollZoom'];
    for (const prop of booleanProps) {
      const value = (plotlyConfig as any)[prop];
      if (value !== undefined && typeof value !== 'boolean') {
        return false;
      }
    }
    
    return true;
  }

  /**
   * Validate page selectors
   */
  validatePageSelectors(selectors: unknown): selectors is TestTypes.PageSelectors {
    if (typeof selectors !== 'object' || selectors === null) {
      return false;
    }
    
    const pageSelectors = selectors as TestTypes.PageSelectors;
    
    // Check required sections
    const requiredSections = ['app', 'upload', 'tabs', 'graph', 'controls', 'table'];
    for (const section of requiredSections) {
      if (!pageSelectors[section as keyof TestTypes.PageSelectors]) {
        return false;
      }
    }
    
    // Check that tab selector is a function
    if (typeof pageSelectors.tabs.tab !== 'function') {
      return false;
    }
    
    return true;
  }
}

// Export singleton instances for convenience
export const meldValidator = new MELDDataValidator();
export const dataGenerator = new TestDataGenerator();
export const performanceUtils = new PerformanceTestUtils();
export const configValidator = new ConfigValidator();