/**
 * MELD Visualizer Data Type Definitions
 * Type-safe interfaces for MELD manufacturing data structures
 */

export namespace MELDData {
  /**
   * Core MELD data point representing a single measurement in time
   */
  export interface DataPoint {
    readonly Date: string;
    readonly Time: string;
    readonly SpinVel: number;
    readonly SpinTrq: number;
    readonly SpinPwr: number;
    readonly SpinSP: number;
    readonly FeedVel: number;
    readonly FeedPos: number;
    readonly FeedTrq: number;
    readonly FRO: number;
    readonly PathVel: number;
    readonly XPos: number;
    readonly XVel: number;
    readonly XTrq: number;
    readonly YPos: number;
    readonly YVel: number;
    readonly YTrq: number;
    readonly ZPos: number;
    readonly ZVel: number;
    readonly ZTrq: number;
    readonly Gcode: number;
    readonly Low: number;
    readonly High: number;
    readonly Ktype1: number;
    readonly Ktype2: number;
    readonly Ktype3: number;
    readonly Ktype4: number;
    readonly O2: number;
    readonly ToolTemp: number;
    readonly Tool2Temp: number;
  }

  /**
   * Collection of MELD data points with metadata
   */
  export interface Dataset {
    readonly data: ReadonlyArray<DataPoint>;
    readonly metadata: DatasetMetadata;
    readonly statistics: DatasetStatistics;
  }

  /**
   * Metadata about a MELD dataset
   */
  export interface DatasetMetadata {
    readonly filename: string;
    readonly fileSize: number;
    readonly recordCount: number;
    readonly startTime: string;
    readonly endTime: string;
    readonly duration: number; // in seconds
    readonly sampleRate: number; // Hz
    readonly version: string;
    readonly machineId?: string;
    readonly operatorId?: string;
    readonly materialType?: string;
    readonly processParameters?: ProcessParameters;
  }

  /**
   * Statistical summary of dataset
   */
  export interface DatasetStatistics {
    readonly temperature: TemperatureStats;
    readonly position: PositionStats;
    readonly velocity: VelocityStats;
    readonly torque: TorqueStats;
    readonly spindle: SpindleStats;
  }

  /**
   * Temperature-related statistics
   */
  export interface TemperatureStats {
    readonly toolTemp: StatsSummary;
    readonly tool2Temp: StatsSummary;
    readonly ktype1: StatsSummary;
    readonly ktype2: StatsSummary;
    readonly ktype3: StatsSummary;
    readonly ktype4: StatsSummary;
  }

  /**
   * Position-related statistics
   */
  export interface PositionStats {
    readonly x: StatsSummary;
    readonly y: StatsSummary;
    readonly z: StatsSummary;
    readonly feedPos: StatsSummary;
  }

  /**
   * Velocity-related statistics
   */
  export interface VelocityStats {
    readonly x: StatsSummary;
    readonly y: StatsSummary;
    readonly z: StatsSummary;
    readonly feed: StatsSummary;
    readonly path: StatsSummary;
    readonly spindle: StatsSummary;
  }

  /**
   * Torque-related statistics
   */
  export interface TorqueStats {
    readonly x: StatsSummary;
    readonly y: StatsSummary;
    readonly z: StatsSummary;
    readonly feed: StatsSummary;
    readonly spindle: StatsSummary;
  }

  /**
   * Spindle-related statistics
   */
  export interface SpindleStats {
    readonly velocity: StatsSummary;
    readonly torque: StatsSummary;
    readonly power: StatsSummary;
    readonly setpoint: StatsSummary;
  }

  /**
   * Generic statistical summary
   */
  export interface StatsSummary {
    readonly min: number;
    readonly max: number;
    readonly mean: number;
    readonly median: number;
    readonly stdDev: number;
    readonly range: number;
  }

  /**
   * Process parameters for MELD manufacturing
   */
  export interface ProcessParameters {
    readonly targetTemperature: number;
    readonly feedRate: number;
    readonly spindleSpeed: number;
    readonly layerHeight: number;
    readonly toolDiameter: number;
    readonly materialFlow?: number;
    readonly coolingRate?: number;
  }

  /**
   * 3D coordinate point
   */
  export interface Point3D {
    readonly x: number;
    readonly y: number;
    readonly z: number;
  }

  /**
   * Enhanced 3D point with additional MELD data
   */
  export interface MELDPoint3D extends Point3D {
    readonly temperature: number;
    readonly velocity: number;
    readonly timestamp: string;
    readonly layer?: number;
    readonly gcode?: number;
  }

  /**
   * Toolpath data structure
   */
  export interface Toolpath {
    readonly points: ReadonlyArray<MELDPoint3D>;
    readonly segments: ReadonlyArray<ToolpathSegment>;
    readonly metadata: ToolpathMetadata;
  }

  /**
   * Individual toolpath segment
   */
  export interface ToolpathSegment {
    readonly startPoint: MELDPoint3D;
    readonly endPoint: MELDPoint3D;
    readonly length: number;
    readonly feedRate: number;
    readonly segmentType: 'linear' | 'arc' | 'rapid';
    readonly gcode: string;
  }

  /**
   * Toolpath metadata
   */
  export interface ToolpathMetadata {
    readonly filename: string;
    readonly totalLength: number;
    readonly estimatedTime: number;
    readonly layerCount: number;
    readonly toolChanges: number;
    readonly boundingBox: BoundingBox3D;
  }

  /**
   * 3D bounding box
   */
  export interface BoundingBox3D {
    readonly min: Point3D;
    readonly max: Point3D;
    readonly center: Point3D;
    readonly dimensions: Point3D;
  }

  /**
   * Data validation result
   */
  export interface ValidationResult {
    readonly isValid: boolean;
    readonly errors: ReadonlyArray<ValidationError>;
    readonly warnings: ReadonlyArray<ValidationWarning>;
    readonly summary: ValidationSummary;
  }

  /**
   * Validation error
   */
  export interface ValidationError {
    readonly field: keyof DataPoint;
    readonly row: number;
    readonly value: unknown;
    readonly message: string;
    readonly severity: 'error' | 'warning';
  }

  /**
   * Validation warning
   */
  export interface ValidationWarning {
    readonly field: keyof DataPoint;
    readonly row: number;
    readonly value: unknown;
    readonly message: string;
    readonly suggestion?: string;
  }

  /**
   * Validation summary
   */
  export interface ValidationSummary {
    readonly totalRows: number;
    readonly validRows: number;
    readonly errorCount: number;
    readonly warningCount: number;
    readonly completeness: number; // percentage
    readonly dataQuality: 'excellent' | 'good' | 'fair' | 'poor';
  }

  /**
   * CSV parsing configuration
   */
  export interface CSVParseOptions {
    readonly delimiter: string;
    readonly skipEmptyLines: boolean;
    readonly trimHeaders: boolean;
    readonly encoding: BufferEncoding;
    readonly maxRows?: number;
    readonly validateOnParse: boolean;
  }

  /**
   * Data export configuration
   */
  export interface ExportOptions {
    readonly format: 'csv' | 'json' | 'parquet';
    readonly includeMetadata: boolean;
    readonly includeStatistics: boolean;
    readonly compression?: 'gzip' | 'bzip2';
    readonly precision?: number;
    readonly dateFormat?: string;
  }
}

/**
 * Type guards for runtime validation
 */
export namespace MELDTypeGuards {
  export function isDataPoint(obj: unknown): obj is MELDData.DataPoint {
    return (
      typeof obj === 'object' &&
      obj !== null &&
      'Date' in obj &&
      'Time' in obj &&
      'XPos' in obj &&
      'YPos' in obj &&
      'ZPos' in obj &&
      'ToolTemp' in obj &&
      typeof (obj as MELDData.DataPoint).XPos === 'number' &&
      typeof (obj as MELDData.DataPoint).YPos === 'number' &&
      typeof (obj as MELDData.DataPoint).ZPos === 'number'
    );
  }

  export function isDataset(obj: unknown): obj is MELDData.Dataset {
    return (
      typeof obj === 'object' &&
      obj !== null &&
      'data' in obj &&
      'metadata' in obj &&
      Array.isArray((obj as MELDData.Dataset).data) &&
      (obj as MELDData.Dataset).data.every(isDataPoint)
    );
  }

  export function isPoint3D(obj: unknown): obj is MELDData.Point3D {
    return (
      typeof obj === 'object' &&
      obj !== null &&
      'x' in obj &&
      'y' in obj &&
      'z' in obj &&
      typeof (obj as MELDData.Point3D).x === 'number' &&
      typeof (obj as MELDData.Point3D).y === 'number' &&
      typeof (obj as MELDData.Point3D).z === 'number'
    );
  }

  export function isMELDPoint3D(obj: unknown): obj is MELDData.MELDPoint3D {
    return (
      isPoint3D(obj) &&
      'temperature' in obj &&
      'velocity' in obj &&
      'timestamp' in obj &&
      typeof (obj as MELDData.MELDPoint3D).temperature === 'number' &&
      typeof (obj as MELDData.MELDPoint3D).velocity === 'number' &&
      typeof (obj as MELDData.MELDPoint3D).timestamp === 'string'
    );
  }
}

/**
 * Utility types for MELD data manipulation
 */
export namespace MELDUtilityTypes {
  /**
   * Extract numeric fields from DataPoint
   */
  export type NumericFields = {
    [K in keyof MELDData.DataPoint]: MELDData.DataPoint[K] extends number ? K : never;
  }[keyof MELDData.DataPoint];

  /**
   * Extract string fields from DataPoint
   */
  export type StringFields = {
    [K in keyof MELDData.DataPoint]: MELDData.DataPoint[K] extends string ? K : never;
  }[keyof MELDData.DataPoint];

  /**
   * Position-related fields
   */
  export type PositionFields = 'XPos' | 'YPos' | 'ZPos' | 'FeedPos';

  /**
   * Velocity-related fields
   */
  export type VelocityFields = 'XVel' | 'YVel' | 'ZVel' | 'FeedVel' | 'PathVel' | 'SpinVel';

  /**
   * Temperature-related fields
   */
  export type TemperatureFields = 'ToolTemp' | 'Tool2Temp' | 'Ktype1' | 'Ktype2' | 'Ktype3' | 'Ktype4';

  /**
   * Torque-related fields
   */
  export type TorqueFields = 'XTrq' | 'YTrq' | 'ZTrq' | 'FeedTrq' | 'SpinTrq';

  /**
   * Partial DataPoint for updates
   */
  export type PartialDataPoint = Partial<MELDData.DataPoint>;

  /**
   * Required fields for minimal data point
   */
  export type MinimalDataPoint = Pick<MELDData.DataPoint, 'Date' | 'Time' | 'XPos' | 'YPos' | 'ZPos'>;

  /**
   * Data point with computed fields
   */
  export type EnhancedDataPoint = MELDData.DataPoint & {
    readonly computedDistance?: number;
    readonly computedSpeed?: number;
    readonly layerNumber?: number;
    readonly segmentId?: string;
  };
}