import type {
  CardConfig,
  DeviceEntry,
  EntityEntry,
  HassState,
  HomeAssistant,
  Plant,
  RegistryData,
} from "./types";
import { t } from "./localize";
export const PRESETS = [
  "generic",
  "monstera",
  "ficus",
  "pothos",
  "snake_plant",
  "succulent",
  "cactus",
  "fern",
  "orchid",
  "herb",
  "palm",
  "hanging_plant",
];
export function presetUrl(preset: string): string {
  const base = new URL(import.meta.url);
  const url = new URL(
    `illustrations/${PRESETS.includes(preset) ? preset : "generic"}.svg`,
    base,
  );
  url.search = new URL(import.meta.url).search;
  return url.href;
}
export function safeImage(value: unknown, preset: string): string {
  if (typeof value !== "string") return presetUrl(preset);
  try {
    if (
      value.startsWith("/local/") ||
      value.startsWith("/plantbased/illustrations/")
    )
      return new URL(value, location.origin).href;
    const url = new URL(value);
    if (
      ["http:", "https:"].includes(url.protocol) &&
      !url.username &&
      !url.password
    )
      return url.href;
  } catch {
    /* A local preset is always available. */
  }
  return presetUrl(preset);
}
export function validateConfig(
  config: CardConfig,
  overview = false,
  hass?: HomeAssistant,
): CardConfig {
  if (
    !config ||
    typeof config !== "object" ||
    (!overview &&
      config.device_id !== undefined &&
      typeof config.device_id !== "string")
  )
    throw new Error(t(hass, "invalidConfig"));
  if (config.title !== undefined && typeof config.title !== "string")
    throw new Error(t(hass, "invalidTitle"));
  if (
    config.show_actions !== undefined &&
    typeof config.show_actions !== "boolean"
  )
    throw new Error(t(hass, "invalidActions"));
  return { ...config };
}
export const deviceName = (device: DeviceEntry): string =>
  device.name_by_user || device.name || "PlantBased";
export function entityKey(entry: EntityEntry): string {
  return (
    entry.translation_key ||
    entry.unique_id.slice(
      (entry.config_subentry_id || entry.config_entry_id || "").length + 1,
    )
  );
}
export function stateFor(
  hass: HomeAssistant,
  registry: RegistryData,
  deviceId: string,
  key: string,
): HassState | undefined {
  const entity = registry.entities.find(
    (entry) =>
      entry.device_id === deviceId &&
      entityKey(entry) === key &&
      !entry.disabled_by,
  );
  return entity ? hass.states[entity.entity_id] : undefined;
}
function number(state?: HassState): number | null {
  if (!state || ["unknown", "unavailable", ""].includes(state.state))
    return null;
  const value = Number(state.state);
  return Number.isFinite(value) ? value : null;
}
export function plants(hass: HomeAssistant, registry: RegistryData): Plant[] {
  return registry.devices
    .filter((device) => device.model === "Plant")
    .map((device) => {
      const entries = registry.entities.filter(
        (entry) => entry.device_id === device.id,
      );
      const status = stateFor(hass, registry, device.id, "care_status");
      const attrs = status?.attributes ?? {};
      const subentryId =
        entries.find((entry) => entry.config_subentry_id)?.config_subentry_id ??
        String(attrs.subentry_id ?? "");
      const available =
        !!status &&
        ["ok", "water", "fertilize", "water_and_fertilize", "paused"].includes(
          status.state,
        ) &&
        !device.disabled_by &&
        hass.connected !== false;
      const waterDue =
        available && ["water", "water_and_fertilize"].includes(status!.state);
      const fertilizerDue =
        available &&
        ["fertilize", "water_and_fertilize"].includes(status!.state);
      const waterDays = number(
        stateFor(hass, registry, device.id, "days_until_watering"),
      );
      const fertilizerDays = number(
        stateFor(hass, registry, device.id, "days_until_fertilizing"),
      );
      const state = available ? status!.state : "unavailable";
      const tone: Plant["tone"] = !available
        ? "unavailable"
        : state === "paused"
          ? "paused"
          : (waterDue && waterDays !== null && waterDays < 0) ||
              (fertilizerDue && fertilizerDays !== null && fertilizerDays < 0)
            ? "overdue"
            : waterDue || fertilizerDue
              ? "due"
              : "ok";
      const preset =
        typeof attrs.image_preset === "string" ? attrs.image_preset : "generic";
      return {
        deviceId: device.id,
        subentryId,
        name: deviceName(device),
        group: typeof attrs.group === "string" ? attrs.group : null,
        groupId: typeof attrs.group_id === "string" ? attrs.group_id : null,
        image: safeImage(attrs.image_url, preset),
        preset,
        status: state,
        tone,
        available,
        waterDue,
        fertilizerDue,
        waterDays,
        fertilizerDays,
        fertilizingEnabled: attrs.fertilizing_enabled !== false,
      };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}
export function overviewCounts(
  hass: HomeAssistant,
  registry: RegistryData,
): (number | null)[] {
  return [
    "total_plants",
    "plants_needing_water",
    "plants_needing_fertilizer",
    "plants_overdue",
  ].map((key) => {
    const entity = registry.entities.find(
      (entry) =>
        !entry.config_subentry_id &&
        entityKey(entry) === key &&
        !entry.disabled_by,
    );
    return hass.connected === false
      ? null
      : number(entity ? hass.states[entity.entity_id] : undefined);
  });
}
