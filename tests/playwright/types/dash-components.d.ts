/**
 * Dash Component Type Definitions for MELD Visualizer
 * Type-safe interfaces for Dash application components and interactions
 */

import type { MELDData } from './meld-data';

export namespace DashComponents {
  /**
   * Base Dash component properties
   */
  export interface BaseComponentProps {
    readonly id: string;
    readonly className?: string;
    readonly style?: React.CSSProperties;
    readonly 'data-testid'?: string;
  }

  /**
   * Dash callback context
   */
  export interface CallbackContext {
    readonly triggered: ReadonlyArray<CallbackTrigger>;
    readonly states: Record<string, unknown>;
    readonly inputs: Record<string, unknown>;
    readonly outputs: Record<string, unknown>;
  }

  /**
   * Callback trigger information
   */
  export interface CallbackTrigger {
    readonly prop_id: string;
    readonly value: unknown;
    readonly timestamp: number;
  }

  /**
   * Dash callback response
   */
  export interface CallbackResponse {
    readonly multi: boolean;
    readonly response: Record<string, unknown>;
  }

  /**
   * File upload component props
   */
  export interface UploadProps extends BaseComponentProps {
    readonly accept?: string;
    readonly multiple?: boolean;
    readonly disabled?: boolean;
    readonly maxSize?: number;
    readonly minSize?: number;
  }

  /**
   * File upload data structure
   */
  export interface UploadedFile {
    readonly filename: string;
    readonly contents: string; // base64 encoded
    readonly size: number;
    readonly type: string;
    readonly lastModified: number;
  }

  /**
   * Tab component properties
   */
  export interface TabsProps extends BaseComponentProps {
    readonly value: string;
    readonly children: ReadonlyArray<TabProps>;
    readonly vertical?: boolean;
    readonly mobile_breakpoint?: number;
  }

  /**
   * Individual tab properties
   */
  export interface TabProps extends BaseComponentProps {
    readonly label: string;
    readonly value: string;
    readonly disabled?: boolean;
    readonly selected_className?: string;
  }

  /**
   * Theme configuration
   */
  export interface ThemeConfig {
    readonly name: 'light' | 'dark' | 'plotly' | 'plotly_dark';
    readonly colors: ThemeColors;
    readonly fonts: ThemeFonts;
    readonly layout: ThemeLayout;
  }

  /**
   * Theme color scheme
   */
  export interface ThemeColors {
    readonly primary: string;
    readonly secondary: string;
    readonly background: string;
    readonly surface: string;
    readonly text: string;
    readonly textSecondary: string;
    readonly border: string;
    readonly success: string;
    readonly warning: string;
    readonly error: string;
    readonly info: string;
  }

  /**
   * Theme font configuration
   */
  export interface ThemeFonts {
    readonly family: string;
    readonly size: number;
    readonly weight: string;
    readonly lineHeight: number;
  }

  /**
   * Theme layout configuration
   */
  export interface ThemeLayout {
    readonly borderRadius: number;
    readonly spacing: number;
    readonly shadow: string;
  }

  /**
   * Data table component props
   */
  export interface DataTableProps extends BaseComponentProps {
    readonly data: ReadonlyArray<Record<string, unknown>>;
    readonly columns: ReadonlyArray<DataTableColumn>;
    readonly page_current?: number;
    readonly page_size?: number;
    readonly page_count?: number;
    readonly sort_action?: 'native' | 'custom' | 'none';
    readonly filter_action?: 'native' | 'custom' | 'none';
    readonly row_selectable?: 'single' | 'multi' | false;
    readonly selected_rows?: ReadonlyArray<number>;
    readonly export_format?: 'csv' | 'xlsx';
  }

  /**
   * Data table column definition
   */
  export interface DataTableColumn {
    readonly name: string;
    readonly id: string;
    readonly type?: 'text' | 'numeric' | 'datetime';
    readonly format?: DataTableFormat;
    readonly editable?: boolean;
    readonly hideable?: boolean;
    readonly selectable?: boolean;
    readonly searchable?: boolean;
    readonly sortable?: boolean;
  }

  /**
   * Data table formatting options
   */
  export interface DataTableFormat {
    readonly specifier?: string;
    readonly locale?: {
      readonly symbol?: [string, string];
      readonly decimal?: string;
      readonly group?: string;
    };
  }

  /**
   * Store component for client-side data persistence
   */
  export interface StoreProps extends BaseComponentProps {
    readonly data: unknown;
    readonly storage_type?: 'local' | 'session' | 'memory';
    readonly modified_timestamp?: number;
  }

  /**
   * Loading component props
   */
  export interface LoadingProps extends BaseComponentProps {
    readonly children?: React.ReactNode;
    readonly type?: 'default' | 'circle' | 'dot';
    readonly color?: string;
    readonly loading_state?: LoadingState;
  }

  /**
   * Loading state information
   */
  export interface LoadingState {
    readonly is_loading: boolean;
    readonly prop_name?: string;
    readonly component_name?: string;
  }

  /**
   * Interval component for periodic updates
   */
  export interface IntervalProps extends BaseComponentProps {
    readonly interval: number; // milliseconds
    readonly n_intervals: number;
    readonly disabled?: boolean;
    readonly max_intervals?: number;
  }

  /**
   * Alert/notification component
   */
  export interface AlertProps extends BaseComponentProps {
    readonly children: React.ReactNode;
    readonly color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'light' | 'dark';
    readonly dismissable?: boolean;
    readonly is_open?: boolean;
    readonly fade?: boolean;
    readonly duration?: number;
  }

  /**
   * Modal component props
   */
  export interface ModalProps extends BaseComponentProps {
    readonly children: React.ReactNode;
    readonly is_open: boolean;
    readonly backdrop?: boolean | 'static';
    readonly scrollable?: boolean;
    readonly centered?: boolean;
    readonly size?: 'sm' | 'lg' | 'xl';
    readonly keyboard?: boolean;
  }

  /**
   * Progress bar component
   */
  export interface ProgressProps extends BaseComponentProps {
    readonly value: number;
    readonly max?: number;
    readonly striped?: boolean;
    readonly animated?: boolean;
    readonly color?: string;
    readonly label?: string;
  }

  /**
   * Tooltip component
   */
  export interface TooltipProps extends BaseComponentProps {
    readonly children: React.ReactNode;
    readonly target: string;
    readonly placement?: 'auto' | 'top' | 'bottom' | 'left' | 'right';
    readonly trigger?: 'click' | 'hover' | 'focus';
  }

  /**
   * Button component props
   */
  export interface ButtonProps extends BaseComponentProps {
    readonly children: React.ReactNode;
    readonly color?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info' | 'light' | 'dark';
    readonly size?: 'sm' | 'md' | 'lg';
    readonly outline?: boolean;
    readonly disabled?: boolean;
    readonly loading?: boolean;
    readonly n_clicks?: number;
    readonly type?: 'button' | 'submit' | 'reset';
  }

  /**
   * Input component props
   */
  export interface InputProps extends BaseComponentProps {
    readonly value: string | number;
    readonly type?: 'text' | 'number' | 'password' | 'email' | 'search' | 'tel' | 'url' | 'range';
    readonly placeholder?: string;
    readonly disabled?: boolean;
    readonly readonly?: boolean;
    readonly min?: number;
    readonly max?: number;
    readonly step?: number;
    readonly pattern?: string;
    readonly maxLength?: number;
    readonly minLength?: number;
    readonly debounce?: boolean;
    readonly n_submit?: number;
  }

  /**
   * Dropdown component props
   */
  export interface DropdownProps extends BaseComponentProps {
    readonly options: ReadonlyArray<DropdownOption>;
    readonly value?: string | number | ReadonlyArray<string | number>;
    readonly multi?: boolean;
    readonly placeholder?: string;
    readonly searchable?: boolean;
    readonly clearable?: boolean;
    readonly disabled?: boolean;
    readonly optionHeight?: number;
    readonly maxHeight?: number;
  }

  /**
   * Dropdown option definition
   */
  export interface DropdownOption {
    readonly label: string;
    readonly value: string | number;
    readonly disabled?: boolean;
    readonly title?: string;
  }

  /**
   * Slider component props
   */
  export interface SliderProps extends BaseComponentProps {
    readonly min: number;
    readonly max: number;
    readonly step?: number;
    readonly value?: number;
    readonly marks?: Record<number, string | SliderMark>;
    readonly included?: boolean;
    readonly disabled?: boolean;
    readonly dots?: boolean;
    readonly tooltip?: SliderTooltip;
    readonly vertical?: boolean;
    readonly updatemode?: 'mouseup' | 'drag';
  }

  /**
   * Slider mark configuration
   */
  export interface SliderMark {
    readonly label?: string;
    readonly style?: React.CSSProperties;
  }

  /**
   * Slider tooltip configuration
   */
  export interface SliderTooltip {
    readonly always_visible?: boolean;
    readonly placement?: 'top' | 'bottom' | 'left' | 'right';
  }

  /**
   * Checklist component props
   */
  export interface ChecklistProps extends BaseComponentProps {
    readonly options: ReadonlyArray<ChecklistOption>;
    readonly value?: ReadonlyArray<string | number>;
    readonly inline?: boolean;
    readonly labelStyle?: React.CSSProperties;
    readonly inputStyle?: React.CSSProperties;
  }

  /**
   * Checklist option definition
   */
  export interface ChecklistOption {
    readonly label: string;
    readonly value: string | number;
    readonly disabled?: boolean;
  }

  /**
   * Radio items component props
   */
  export interface RadioItemsProps extends BaseComponentProps {
    readonly options: ReadonlyArray<RadioOption>;
    readonly value?: string | number;
    readonly inline?: boolean;
    readonly labelStyle?: React.CSSProperties;
    readonly inputStyle?: React.CSSProperties;
  }

  /**
   * Radio option definition
   */
  export interface RadioOption {
    readonly label: string;
    readonly value: string | number;
    readonly disabled?: boolean;
  }
}

/**
 * Type guards for Dash components
 */
export namespace DashTypeGuards {
  export function isCallbackContext(obj: unknown): obj is DashComponents.CallbackContext {
    return (
      typeof obj === 'object' &&
      obj !== null &&
      'triggered' in obj &&
      Array.isArray((obj as DashComponents.CallbackContext).triggered)
    );
  }

  export function isUploadedFile(obj: unknown): obj is DashComponents.UploadedFile {
    return (
      typeof obj === 'object' &&
      obj !== null &&
      'filename' in obj &&
      'contents' in obj &&
      'size' in obj &&
      typeof (obj as DashComponents.UploadedFile).filename === 'string' &&
      typeof (obj as DashComponents.UploadedFile).contents === 'string' &&
      typeof (obj as DashComponents.UploadedFile).size === 'number'
    );
  }

  export function isThemeConfig(obj: unknown): obj is DashComponents.ThemeConfig {
    return (
      typeof obj === 'object' &&
      obj !== null &&
      'name' in obj &&
      'colors' in obj &&
      typeof (obj as DashComponents.ThemeConfig).name === 'string'
    );
  }
}

/**
 * Utility types for Dash components
 */
export namespace DashUtilityTypes {
  /**
   * Extract component IDs from props
   */
  export type ComponentId<T extends DashComponents.BaseComponentProps> = T['id'];

  /**
   * Component props without base props
   */
  export type ComponentSpecificProps<T extends DashComponents.BaseComponentProps> = Omit<T, keyof DashComponents.BaseComponentProps>;

  /**
   * Callback input/output specification
   */
  export type CallbackIOSpec = {
    readonly component_id: string;
    readonly component_property: string;
  };

  /**
   * Multi-output callback specification
   */
  export type MultiOutputCallback = {
    readonly outputs: ReadonlyArray<CallbackIOSpec>;
    readonly inputs: ReadonlyArray<CallbackIOSpec>;
    readonly state?: ReadonlyArray<CallbackIOSpec>;
  };

  /**
   * Component state for testing
   */
  export type ComponentState<T extends DashComponents.BaseComponentProps> = {
    readonly id: ComponentId<T>;
    readonly props: Partial<T>;
    readonly children?: unknown;
  };

  /**
   * App layout structure for testing
   */
  export type AppLayout = {
    readonly components: ReadonlyArray<ComponentState<DashComponents.BaseComponentProps>>;
    readonly callbacks: ReadonlyArray<MultiOutputCallback>;
    readonly stores: ReadonlyArray<DashComponents.StoreProps>;
  };
}