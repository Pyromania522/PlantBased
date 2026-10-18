export interface HassState {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
}
export interface HAConnection {
  subscribeEvents(callback: () => void, type: string): Promise<() => void>;
  addEventListener(type: string, callback: () => void): void;
  removeEventListener(type: string, callback: () => void): void;
}
export interface HomeAssistant {
  states: Record<string, HassState>;
  devices?: Record<string, DeviceEntry>;
  locale?: { language?: string };
  language?: string;
  connected?: boolean;
  user?: { is_admin: boolean };
  connection: HAConnection;
  callWS<T>(message: { type: string; [key: string]: unknown }): Promise<T>;
  callApi<T>(
    method: string,
    path: string,
    parameters?: unknown,
    headers?: Record<string, string>,
  ): Promise<T>;
  loadBackendTranslation(
    category: string,
    integration: string,
  ): Promise<(key: string) => string>;
  callService(
    domain: string,
    service: string,
    data: Record<string, unknown>,
    target: { device_id: string },
    notifyOnError?: boolean,
  ): Promise<unknown>;
}
export interface EntityEntry {
  entity_id: string;
  platform: string;
  unique_id: string;
  translation_key?: string | null;
  device_id: string | null;
  config_entry_id: string | null;
  config_subentry_id: string | null;
  disabled_by?: string | null;
}
export interface DeviceEntry {
  id: string;
  name: string | null;
  name_by_user: string | null;
  model: string | null;
  identifiers: [string, string][];
  disabled_by?: string | null;
  area_id?: string | null;
}
export interface AreaEntry {
  area_id: string;
  name: string;
}
export interface RegistryData {
  entities: EntityEntry[];
  devices: DeviceEntry[];
  areas?: AreaEntry[];
}
export interface CardConfig {
  type: string;
  device_id?: string;
  title?: string;
  show_actions?: boolean;
}
export interface Plant {
  deviceId: string;
  subentryId: string;
  name: string;
  group: string | null;
  groupId: string | null;
  areaId: string | null;
  area: string | null;
  image: string;
  preset: string;
  status: string;
  tone: "ok" | "due" | "overdue" | "paused" | "unavailable";
  available: boolean;
  waterDue: boolean;
  fertilizerDue: boolean;
  waterDays: number | null;
  fertilizerDays: number | null;
  fertilizingEnabled: boolean;
  adaptiveWatering: boolean;
  waterInterval: number | null;
  learningSamples: number;
}
