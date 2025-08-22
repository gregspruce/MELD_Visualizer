/**
 * Plotly.js Type Definitions for MELD Visualizer
 * Type-safe interfaces for 3D visualizations and graph interactions
 */

import type { MELDData } from './meld-data';

export namespace PlotlyTypes {
  /**
   * Base Plotly trace interface
   */
  export interface BasePlotlyTrace {
    readonly type: TraceType;
    readonly name?: string;
    readonly visible?: boolean | 'legendonly';
    readonly showlegend?: boolean;
    readonly hoverinfo?: HoverInfo;
    readonly hovertemplate?: string;
    readonly customdata?: ReadonlyArray<unknown>;
    readonly meta?: unknown;
    readonly uid?: string;
  }

  /**
   * Plotly trace types
   */
  export type TraceType = 
    | 'scatter3d'
    | 'surface'
    | 'mesh3d'
    | 'scatter'
    | 'scattergl'
    | 'line'
    | 'bar'
    | 'histogram'
    | 'heatmap'
    | 'contour';

  /**
   * Hover information options
   */
  export type HoverInfo = 
    | 'x'
    | 'y'
    | 'z'
    | 'text'
    | 'name'
    | 'all'
    | 'none'
    | 'skip'
    | string;

  /**
   * 3D scatter plot trace for MELD data visualization
   */
  export interface Scatter3DTrace extends BasePlotlyTrace {
    readonly type: 'scatter3d';
    readonly x: ReadonlyArray<number>;
    readonly y: ReadonlyArray<number>;
    readonly z: ReadonlyArray<number>;
    readonly mode?: 'markers' | 'lines' | 'markers+lines' | 'lines+markers' | 'text' | 'markers+text' | 'lines+text' | 'markers+lines+text';
    readonly marker?: Scatter3DMarker;
    readonly line?: Scatter3DLine;
    readonly text?: ReadonlyArray<string>;
    readonly textposition?: TextPosition;
    readonly connectgaps?: boolean;
    readonly surfaceaxis?: number;
    readonly projection?: Scatter3DProjection;
  }

  /**
   * 3D marker configuration
   */
  export interface Scatter3DMarker {
    readonly size?: number | ReadonlyArray<number>;
    readonly color?: string | ReadonlyArray<string | number>;
    readonly colorscale?: ColorScale;
    readonly cmin?: number;
    readonly cmax?: number;
    readonly showscale?: boolean;
    readonly colorbar?: ColorBar;
    readonly opacity?: number | ReadonlyArray<number>;
    readonly symbol?: string | ReadonlyArray<string>;
    readonly line?: MarkerLine;
    readonly sizemode?: 'diameter' | 'area';
    readonly sizeref?: number;
    readonly sizemin?: number;
    readonly reversescale?: boolean;
  }

  /**
   * 3D line configuration
   */
  export interface Scatter3DLine {
    readonly color?: string | ReadonlyArray<string | number>;
    readonly colorscale?: ColorScale;
    readonly width?: number;
    readonly dash?: DashType;
    readonly cmin?: number;
    readonly cmax?: number;
    readonly showscale?: boolean;
    readonly colorbar?: ColorBar;
    readonly reversescale?: boolean;
  }

  /**
   * Marker line configuration
   */
  export interface MarkerLine {
    readonly color?: string | ReadonlyArray<string | number>;
    readonly colorscale?: ColorScale;
    readonly width?: number | ReadonlyArray<number>;
    readonly cmin?: number;
    readonly cmax?: number;
    readonly showscale?: boolean;
    readonly colorbar?: ColorBar;
    readonly reversescale?: boolean;
  }

  /**
   * Color scale options
   */
  export type ColorScale = 
    | 'Greys'
    | 'YlGnBu'
    | 'Greens'
    | 'YlOrRd'
    | 'Bluered'
    | 'RdBu'
    | 'Reds'
    | 'Blues'
    | 'Picnic'
    | 'Rainbow'
    | 'Portland'
    | 'Jet'
    | 'Hot'
    | 'Blackbody'
    | 'Earth'
    | 'Electric'
    | 'Viridis'
    | 'Plasma'
    | 'Inferno'
    | 'Magma'
    | 'Cividis'
    | ReadonlyArray<[number, string]>;

  /**
   * Line dash types
   */
  export type DashType = 
    | 'solid'
    | 'dot'
    | 'dash'
    | 'longdash'
    | 'dashdot'
    | 'longdashdot';

  /**
   * Text position options
   */
  export type TextPosition = 
    | 'top left'
    | 'top center'
    | 'top right'
    | 'middle left'
    | 'middle center'
    | 'middle right'
    | 'bottom left'
    | 'bottom center'
    | 'bottom right';

  /**
   * 3D projection configuration
   */
  export interface Scatter3DProjection {
    readonly x?: ProjectionAxis;
    readonly y?: ProjectionAxis;
    readonly z?: ProjectionAxis;
  }

  /**
   * Projection axis configuration
   */
  export interface ProjectionAxis {
    readonly show?: boolean;
    readonly opacity?: number;
    readonly scale?: number;
  }

  /**
   * Color bar configuration
   */
  export interface ColorBar {
    readonly thicknessmode?: 'fraction' | 'pixels';
    readonly thickness?: number;
    readonly lenmode?: 'fraction' | 'pixels';
    readonly len?: number;
    readonly x?: number;
    readonly xanchor?: 'left' | 'center' | 'right';
    readonly xpad?: number;
    readonly y?: number;
    readonly yanchor?: 'top' | 'middle' | 'bottom';
    readonly ypad?: number;
    readonly outlinecolor?: string;
    readonly outlinewidth?: number;
    readonly bordercolor?: string;
    readonly borderwidth?: number;
    readonly bgcolor?: string;
    readonly tickmode?: 'auto' | 'linear' | 'array';
    readonly tick0?: number;
    readonly dtick?: number;
    readonly tickvals?: ReadonlyArray<number>;
    readonly ticktext?: ReadonlyArray<string>;
    readonly title?: ColorBarTitle;
  }

  /**
   * Color bar title configuration
   */
  export interface ColorBarTitle {
    readonly text?: string;
    readonly font?: Font;
    readonly side?: 'right' | 'top' | 'bottom';
  }

  /**
   * Font configuration
   */
  export interface Font {
    readonly family?: string;
    readonly size?: number;
    readonly color?: string;
    readonly variant?: 'normal' | 'small-caps';
    readonly weight?: number | 'normal' | 'bold';
    readonly style?: 'normal' | 'italic';
  }

  /**
   * Surface plot trace for MELD temperature visualization
   */
  export interface SurfaceTrace extends BasePlotlyTrace {
    readonly type: 'surface';
    readonly x?: ReadonlyArray<number>;
    readonly y?: ReadonlyArray<number>;
    readonly z: ReadonlyArray<ReadonlyArray<number>>;
    readonly colorscale?: ColorScale;
    readonly reversescale?: boolean;
    readonly showscale?: boolean;
    readonly colorbar?: ColorBar;
    readonly opacity?: number;
    readonly surfacecolor?: ReadonlyArray<ReadonlyArray<number>>;
    readonly contours?: SurfaceContours;
    readonly hidesurface?: boolean;
    readonly lighting?: SurfaceLighting;
    readonly lightposition?: SurfaceLightPosition;
  }

  /**
   * Surface contours configuration
   */
  export interface SurfaceContours {
    readonly x?: ContourAxis;
    readonly y?: ContourAxis;
    readonly z?: ContourAxis;
  }

  /**
   * Contour axis configuration
   */
  export interface ContourAxis {
    readonly show?: boolean;
    readonly start?: number;
    readonly end?: number;
    readonly size?: number;
    readonly color?: string;
    readonly width?: number;
    readonly highlight?: boolean;
    readonly highlightcolor?: string;
    readonly highlightwidth?: number;
  }

  /**
   * Surface lighting configuration
   */
  export interface SurfaceLighting {
    readonly ambient?: number;
    readonly diffuse?: number;
    readonly specular?: number;
    readonly roughness?: number;
    readonly fresnel?: number;
  }

  /**
   * Surface light position
   */
  export interface SurfaceLightPosition {
    readonly x?: number;
    readonly y?: number;
    readonly z?: number;
  }

  /**
   * Plotly layout configuration
   */
  export interface PlotlyLayout {
    readonly title?: string | LayoutTitle;
    readonly width?: number;
    readonly height?: number;
    readonly autosize?: boolean;
    readonly margin?: Margin;
    readonly paper_bgcolor?: string;
    readonly plot_bgcolor?: string;
    readonly font?: Font;
    readonly showlegend?: boolean;
    readonly legend?: Legend;
    readonly scene?: Scene3D;
    readonly xaxis?: Axis;
    readonly yaxis?: Axis;
    readonly annotations?: ReadonlyArray<Annotation>;
    readonly shapes?: ReadonlyArray<Shape>;
    readonly images?: ReadonlyArray<LayoutImage>;
    readonly updatemenus?: ReadonlyArray<UpdateMenu>;
    readonly sliders?: ReadonlyArray<Slider>;
    readonly hoverlabel?: HoverLabel;
    readonly hovermode?: HoverMode;
    readonly dragmode?: DragMode;
    readonly selectdirection?: SelectDirection;
    readonly template?: PlotlyTemplate;
  }

  /**
   * Layout title configuration
   */
  export interface LayoutTitle {
    readonly text: string;
    readonly font?: Font;
    readonly x?: number;
    readonly xanchor?: 'auto' | 'left' | 'center' | 'right';
    readonly y?: number;
    readonly yanchor?: 'auto' | 'top' | 'middle' | 'bottom';
    readonly pad?: Padding;
  }

  /**
   * Layout margin configuration
   */
  export interface Margin {
    readonly l?: number;
    readonly r?: number;
    readonly t?: number;
    readonly b?: number;
    readonly pad?: number;
    readonly autoexpand?: boolean;
  }

  /**
   * Padding configuration
   */
  export interface Padding {
    readonly t?: number;
    readonly r?: number;
    readonly b?: number;
    readonly l?: number;
  }

  /**
   * Legend configuration
   */
  export interface Legend {
    readonly x?: number;
    readonly xanchor?: 'auto' | 'left' | 'center' | 'right';
    readonly y?: number;
    readonly yanchor?: 'auto' | 'top' | 'middle' | 'bottom';
    readonly orientation?: 'v' | 'h';
    readonly bgcolor?: string;
    readonly bordercolor?: string;
    readonly borderwidth?: number;
    readonly font?: Font;
    readonly tracegroupgap?: number;
    readonly itemsizing?: 'trace' | 'constant';
    readonly itemwidth?: number;
    readonly itemclick?: 'toggle' | 'toggleothers' | false;
    readonly itemdoubleclick?: 'toggle' | 'toggleothers' | false;
  }

  /**
   * 3D scene configuration
   */
  export interface Scene3D {
    readonly xaxis?: Scene3DAxis;
    readonly yaxis?: Scene3DAxis;
    readonly zaxis?: Scene3DAxis;
    readonly camera?: Camera3D;
    readonly domain?: SceneDomain;
    readonly aspectmode?: 'auto' | 'cube' | 'data' | 'manual';
    readonly aspectratio?: AspectRatio3D;
    readonly bgcolor?: string;
    readonly dragmode?: '3d' | 'orbit' | 'turntable' | 'zoom' | 'pan' | false;
    readonly hovermode?: 'closest' | false;
    readonly annotations?: ReadonlyArray<Scene3DAnnotation>;
  }

  /**
   * 3D scene axis configuration
   */
  export interface Scene3DAxis {
    readonly title?: string | AxisTitle;
    readonly type?: 'auto' | 'linear' | 'log' | 'date' | 'category';
    readonly range?: [number, number];
    readonly autorange?: boolean | 'reversed';
    readonly showgrid?: boolean;
    readonly gridcolor?: string;
    readonly gridwidth?: number;
    readonly zeroline?: boolean;
    readonly zerolinecolor?: string;
    readonly zerolinewidth?: number;
    readonly showline?: boolean;
    readonly linecolor?: string;
    readonly linewidth?: number;
    readonly showticklabels?: boolean;
    readonly tickfont?: Font;
    readonly tickcolor?: string;
    readonly ticklen?: number;
    readonly tickwidth?: number;
    readonly showspikes?: boolean;
    readonly spikesides?: boolean;
    readonly spikethickness?: number;
    readonly spikecolor?: string;
    readonly showbackground?: boolean;
    readonly backgroundcolor?: string;
    readonly visible?: boolean;
  }

  /**
   * Axis title configuration
   */
  export interface AxisTitle {
    readonly text: string;
    readonly font?: Font;
    readonly standoff?: number;
  }

  /**
   * 3D camera configuration
   */
  export interface Camera3D {
    readonly eye?: Point3DCamera;
    readonly center?: Point3DCamera;
    readonly up?: Point3DCamera;
    readonly projection?: CameraProjection;
  }

  /**
   * 3D camera point
   */
  export interface Point3DCamera {
    readonly x?: number;
    readonly y?: number;
    readonly z?: number;
  }

  /**
   * Camera projection configuration
   */
  export interface CameraProjection {
    readonly type?: 'perspective' | 'orthographic';
  }

  /**
   * Scene domain configuration
   */
  export interface SceneDomain {
    readonly x?: [number, number];
    readonly y?: [number, number];
  }

  /**
   * 3D aspect ratio
   */
  export interface AspectRatio3D {
    readonly x?: number;
    readonly y?: number;
    readonly z?: number;
  }

  /**
   * 3D scene annotation
   */
  export interface Scene3DAnnotation {
    readonly x?: number;
    readonly y?: number;
    readonly z?: number;
    readonly text?: string;
    readonly showarrow?: boolean;
    readonly arrowcolor?: string;
    readonly arrowsize?: number;
    readonly arrowwidth?: number;
    readonly arrowhead?: number;
    readonly font?: Font;
    readonly bgcolor?: string;
    readonly bordercolor?: string;
    readonly borderwidth?: number;
  }

  /**
   * 2D axis configuration
   */
  export interface Axis extends Omit<Scene3DAxis, 'showspikes' | 'spikesides' | 'spikethickness' | 'spikecolor' | 'showbackground' | 'backgroundcolor'> {
    readonly side?: 'top' | 'bottom' | 'left' | 'right';
    readonly overlaying?: string;
    readonly anchor?: string;
    readonly domain?: [number, number];
    readonly position?: number;
    readonly categoryorder?: CategoryOrder;
    readonly categoryarray?: ReadonlyArray<string>;
    readonly showexponent?: 'all' | 'first' | 'last' | 'none';
    readonly exponentformat?: ExponentFormat;
    readonly tickmode?: 'auto' | 'linear' | 'array';
    readonly tick0?: number;
    readonly dtick?: number;
    readonly tickvals?: ReadonlyArray<number>;
    readonly ticktext?: ReadonlyArray<string>;
    readonly ticks?: 'outside' | 'inside' | '';
    readonly mirror?: boolean | 'ticks' | 'all' | 'allticks';
    readonly tickangle?: number;
    readonly tickformat?: string;
    readonly tickprefix?: string;
    readonly ticksuffix?: string;
    readonly separatethousands?: boolean;
  }

  /**
   * Category order options
   */
  export type CategoryOrder = 
    | 'trace'
    | 'category ascending'
    | 'category descending'
    | 'array'
    | 'total ascending'
    | 'total descending'
    | 'min ascending'
    | 'min descending'
    | 'max ascending'
    | 'max descending'
    | 'sum ascending'
    | 'sum descending'
    | 'mean ascending'
    | 'mean descending'
    | 'median ascending'
    | 'median descending';

  /**
   * Exponent format options
   */
  export type ExponentFormat = 'none' | 'e' | 'E' | 'power' | 'SI' | 'B';

  /**
   * Annotation configuration
   */
  export interface Annotation {
    readonly x?: number | string;
    readonly y?: number | string;
    readonly text?: string;
    readonly showarrow?: boolean;
    readonly arrowhead?: number;
    readonly arrowsize?: number;
    readonly arrowwidth?: number;
    readonly arrowcolor?: string;
    readonly ax?: number;
    readonly ay?: number;
    readonly axref?: 'pixel' | 'x' | 'y';
    readonly ayref?: 'pixel' | 'x' | 'y';
    readonly xref?: 'paper' | 'x' | string;
    readonly yref?: 'paper' | 'y' | string;
    readonly xanchor?: 'auto' | 'left' | 'center' | 'right';
    readonly yanchor?: 'auto' | 'top' | 'middle' | 'bottom';
    readonly xshift?: number;
    readonly yshift?: number;
    readonly font?: Font;
    readonly bgcolor?: string;
    readonly bordercolor?: string;
    readonly borderwidth?: number;
    readonly opacity?: number;
    readonly align?: 'left' | 'center' | 'right';
    readonly valign?: 'top' | 'middle' | 'bottom';
    readonly clicktoshow?: boolean | 'onoff' | 'onout';
    readonly captureevents?: boolean;
  }

  /**
   * Shape configuration
   */
  export interface Shape {
    readonly type: 'circle' | 'rect' | 'path' | 'line';
    readonly x0?: number;
    readonly y0?: number;
    readonly x1?: number;
    readonly y1?: number;
    readonly path?: string;
    readonly xref?: 'paper' | 'x' | string;
    readonly yref?: 'paper' | 'y' | string;
    readonly line?: ShapeLine;
    readonly fillcolor?: string;
    readonly fillrule?: 'evenodd' | 'nonzero';
    readonly opacity?: number;
    readonly layer?: 'below' | 'above';
    readonly visible?: boolean;
  }

  /**
   * Shape line configuration
   */
  export interface ShapeLine {
    readonly color?: string;
    readonly width?: number;
    readonly dash?: DashType;
  }

  /**
   * Layout image configuration
   */
  export interface LayoutImage {
    readonly source: string;
    readonly xref?: 'paper' | 'x' | string;
    readonly yref?: 'paper' | 'y' | string;
    readonly x?: number;
    readonly y?: number;
    readonly sizex?: number;
    readonly sizey?: number;
    readonly sizing?: 'fill' | 'contain' | 'stretch';
    readonly opacity?: number;
    readonly layer?: 'below' | 'above';
    readonly visible?: boolean;
    readonly xanchor?: 'left' | 'center' | 'right';
    readonly yanchor?: 'top' | 'middle' | 'bottom';
  }

  /**
   * Update menu configuration
   */
  export interface UpdateMenu {
    readonly type?: 'dropdown' | 'buttons';
    readonly direction?: 'left' | 'right' | 'up' | 'down';
    readonly active?: number;
    readonly showactive?: boolean;
    readonly buttons?: ReadonlyArray<UpdateMenuButton>;
    readonly x?: number;
    readonly xanchor?: 'auto' | 'left' | 'center' | 'right';
    readonly y?: number;
    readonly yanchor?: 'auto' | 'top' | 'middle' | 'bottom';
    readonly pad?: Padding;
    readonly font?: Font;
    readonly bgcolor?: string;
    readonly bordercolor?: string;
    readonly borderwidth?: number;
  }

  /**
   * Update menu button configuration
   */
  export interface UpdateMenuButton {
    readonly label?: string;
    readonly method?: 'restyle' | 'relayout' | 'animate' | 'update' | 'skip';
    readonly args?: ReadonlyArray<unknown>;
    readonly args2?: ReadonlyArray<unknown>;
    readonly execute?: boolean;
    readonly visible?: boolean;
  }

  /**
   * Slider configuration
   */
  export interface Slider {
    readonly steps?: ReadonlyArray<SliderStep>;
    readonly active?: number;
    readonly visible?: boolean;
    readonly x?: number;
    readonly xanchor?: 'auto' | 'left' | 'center' | 'right';
    readonly y?: number;
    readonly yanchor?: 'auto' | 'top' | 'middle' | 'bottom';
    readonly len?: number;
    readonly lenmode?: 'fraction' | 'pixels';
    readonly pad?: Padding;
    readonly currentvalue?: SliderCurrentValue;
    readonly font?: Font;
    readonly bgcolor?: string;
    readonly bordercolor?: string;
    readonly borderwidth?: number;
    readonly tickcolor?: string;
    readonly ticklen?: number;
    readonly tickwidth?: number;
    readonly minorticklen?: number;
    readonly transition?: SliderTransition;
  }

  /**
   * Slider step configuration
   */
  export interface SliderStep {
    readonly label?: string;
    readonly method?: 'restyle' | 'relayout' | 'animate' | 'update' | 'skip';
    readonly args?: ReadonlyArray<unknown>;
    readonly execute?: boolean;
    readonly visible?: boolean;
    readonly value?: string;
  }

  /**
   * Slider current value configuration
   */
  export interface SliderCurrentValue {
    readonly visible?: boolean;
    readonly prefix?: string;
    readonly suffix?: string;
    readonly offset?: number;
    readonly font?: Font;
    readonly xanchor?: 'left' | 'center' | 'right';
  }

  /**
   * Slider transition configuration
   */
  export interface SliderTransition {
    readonly duration?: number;
    readonly easing?: 'linear' | 'quad' | 'cubic' | 'sin' | 'exp' | 'circle' | 'elastic' | 'back' | 'bounce';
  }

  /**
   * Hover label configuration
   */
  export interface HoverLabel {
    readonly bgcolor?: string | ReadonlyArray<string>;
    readonly bordercolor?: string | ReadonlyArray<string>;
    readonly font?: Font;
    readonly align?: 'left' | 'right' | 'auto';
    readonly namelength?: number | ReadonlyArray<number>;
  }

  /**
   * Hover mode options
   */
  export type HoverMode = 'x' | 'y' | 'closest' | 'x unified' | 'y unified' | false;

  /**
   * Drag mode options
   */
  export type DragMode = 
    | 'zoom'
    | 'pan'
    | 'select'
    | 'lasso'
    | 'drawclosedpath'
    | 'drawopenpath'
    | 'drawline'
    | 'drawrect'
    | 'drawcircle'
    | 'orbit'
    | 'turntable'
    | false;

  /**
   * Select direction options
   */
  export type SelectDirection = 'horizontal' | 'vertical' | 'diagonal' | 'any';

  /**
   * Plotly template configuration
   */
  export interface PlotlyTemplate {
    readonly data?: Partial<Record<TraceType, ReadonlyArray<Partial<BasePlotlyTrace>>>>;
    readonly layout?: Partial<PlotlyLayout>;
  }

  /**
   * Plotly configuration options
   */
  export interface PlotlyConfig {
    readonly staticPlot?: boolean;
    readonly editable?: boolean;
    readonly autosizable?: boolean;
    readonly responsive?: boolean;
    readonly queueLength?: number;
    readonly fillFrame?: boolean;
    readonly frameMargins?: number;
    readonly scrollZoom?: boolean;
    readonly doubleClick?: 'reset' | 'autosize' | 'reset+autosize' | false;
    readonly doubleClickDelay?: number;
    readonly showTips?: boolean;
    readonly showLink?: boolean;
    readonly linkText?: string;
    readonly plotlyServerURL?: string;
    readonly modeBarButtonsToRemove?: ReadonlyArray<string>;
    readonly modeBarButtonsToAdd?: ReadonlyArray<unknown>;
    readonly modeBarButtons?: ReadonlyArray<ReadonlyArray<string>>;
    readonly displayModeBar?: boolean | 'hover';
    readonly watermark?: boolean;
    readonly displaylogo?: boolean;
    readonly locale?: string;
    readonly locales?: Record<string, unknown>;
  }

  /**
   * Plotly event data
   */
  export interface PlotlyEventData {
    readonly points?: ReadonlyArray<PlotlyEventPoint>;
    readonly event?: Event;
    readonly range?: PlotlyEventRange;
    readonly selection?: PlotlyEventSelection;
  }

  /**
   * Plotly event point
   */
  export interface PlotlyEventPoint {
    readonly data?: BasePlotlyTrace;
    readonly fullData?: BasePlotlyTrace;
    readonly curveNumber?: number;
    readonly pointNumber?: number;
    readonly pointIndex?: number;
    readonly x?: number;
    readonly y?: number;
    readonly z?: number;
    readonly customdata?: unknown;
  }

  /**
   * Plotly event range (for zoom/pan events)
   */
  export interface PlotlyEventRange {
    readonly 'xaxis.range'?: [number, number];
    readonly 'yaxis.range'?: [number, number];
    readonly 'scene.camera'?: Camera3D;
  }

  /**
   * Plotly event selection
   */
  export interface PlotlyEventSelection {
    readonly points?: ReadonlyArray<PlotlyEventPoint>;
    readonly range?: {
      readonly x?: [number, number];
      readonly y?: [number, number];
    };
    readonly lassoPoints?: {
      readonly x?: ReadonlyArray<number>;
      readonly y?: ReadonlyArray<number>;
    };
  }

  /**
   * MELD-specific plotting utilities
   */
  export interface MELDPlotConfig {
    readonly showToolpath?: boolean;
    readonly showTemperatureGradient?: boolean;
    readonly showVelocityVectors?: boolean;
    readonly colorByTemperature?: boolean;
    readonly colorByVelocity?: boolean;
    readonly colorByLayer?: boolean;
    readonly animateToolpath?: boolean;
    readonly animationDuration?: number;
    readonly cameraPreset?: '3d' | 'top' | 'side' | 'front';
    readonly theme?: 'light' | 'dark' | 'plotly' | 'plotly_dark';
  }
}

/**
 * Utility functions for creating MELD visualizations
 */
export namespace PlotlyMELDUtils {
  /**
   * Create 3D scatter trace from MELD data
   */
  export type CreateScatter3DTrace = (
    data: ReadonlyArray<MELDData.DataPoint>,
    options?: Partial<PlotlyTypes.MELDPlotConfig>
  ) => PlotlyTypes.Scatter3DTrace;

  /**
   * Create temperature surface from MELD data
   */
  export type CreateTemperatureSurface = (
    data: ReadonlyArray<MELDData.DataPoint>,
    gridSize?: { x: number; y: number }
  ) => PlotlyTypes.SurfaceTrace;

  /**
   * Create velocity vector field
   */
  export type CreateVelocityField = (
    data: ReadonlyArray<MELDData.DataPoint>,
    options?: { scale?: number; color?: string }
  ) => PlotlyTypes.Scatter3DTrace;

  /**
   * Generate optimal camera position for MELD data
   */
  export type GetOptimalCamera = (
    data: ReadonlyArray<MELDData.DataPoint>
  ) => PlotlyTypes.Camera3D;

  /**
   * Create animation frames for toolpath
   */
  export type CreateToolpathAnimation = (
    data: ReadonlyArray<MELDData.DataPoint>,
    frameCount?: number
  ) => ReadonlyArray<{
    name: string;
    data: ReadonlyArray<PlotlyTypes.BasePlotlyTrace>;
  }>;
}