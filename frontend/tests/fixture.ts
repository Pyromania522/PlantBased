import type { Page } from "@playwright/test";

export async function boot(
  page: Page,
  config: Record<string, unknown> = {},
  options: Record<string, unknown> = {},
) {
  await page.goto("/");
  await page.evaluate(
    async ({ config, options }) => {
      await customElements.whenDefined("plantbased-card");
      const w = window as any;
      w.calls = [];
      w.wsCalls = [];
      w.registryEvents = {};
      w.readyEvents = [];
      w.unsubscribed = 0;
      w.defer = false;
      w.fail = false;
      w.registryFail = false;
      const entry = "hub";
      w.devices = [
        {
          id: "hub-device",
          name: "Plant overview",
          name_by_user: null,
          model: null,
          identifiers: [["plantbased", entry]],
        },
        {
          id: "living",
          name: "Living room",
          name_by_user: null,
          model: "Group",
          identifiers: [["plantbased", "living-sub"]],
        },
        {
          id: "empty",
          name: "Empty room",
          name_by_user: null,
          model: "Group",
          identifiers: [["plantbased", "empty-sub"]],
        },
        {
          id: "monstera",
          name: "Monstera",
          name_by_user: null,
          model: "Plant",
          identifiers: [["plantbased", "monstera-sub"]],
        },
        {
          id: "ficus",
          name: "Ficus",
          name_by_user: null,
          model: "Plant",
          identifiers: [["plantbased", "ficus-sub"]],
        },
        {
          id: "foreign",
          name: "Foreign device",
          name_by_user: null,
          model: "Plant",
          identifiers: [["other", "foreign"]],
        },
      ];
      w.areas = [
        {
          area_id: "living-area",
          name: options.language === "de" ? "Wohnzimmer" : "Living room",
        },
        {
          area_id: "bedroom-area",
          name: options.language === "de" ? "Schlafzimmer" : "Bedroom",
        },
      ];
      w.devices.find((device: any) => device.id === "monstera").area_id =
        "living-area";
      w.devices.find((device: any) => device.id === "ficus").area_id =
        "bedroom-area";
      w.entities = [];
      w.states = {};
      const add = (
        device: string,
        sub: string | null,
        key: string,
        value: string,
        attributes = {},
      ) => {
        // Deliberately unrelated entity IDs: cards must resolve the registry.
        const entity_id = `${key.startsWith("needs_") ? "binary_sensor" : "sensor"}.renamed_${w.entities.length}`;
        w.entities.push({
          entity_id,
          platform: "plantbased",
          unique_id: `${sub || entry}_${key}`,
          translation_key: key,
          device_id: device,
          config_entry_id: entry,
          config_subentry_id: sub,
          disabled_by: null,
        });
        w.states[entity_id] = { entity_id, state: value, attributes };
      };
      const addPlant = (
        device: string,
        group: string,
        status: string,
        days: number,
        due: boolean,
      ) => {
        const sub = device + "-sub";
        add(device, sub, "care_status", status, {
          subentry_id: sub,
          group: group ? "Living room" : null,
          group_id: group || null,
          image_preset: device,
          fertilizing_enabled: true,
        });
        add(device, sub, "days_until_watering", String(days));
        add(device, sub, "days_until_fertilizing", String(days + 3));
        add(device, sub, "needs_water", due ? "on" : "off");
        add(device, sub, "needs_fertilizer", due ? "on" : "off");
      };
      addPlant("monstera", "living-sub", "water_and_fertilize", -4, true);
      addPlant("ficus", "living-sub", "ok", 5, false);
      add("living", "living-sub", "total_plants", "2");
      add("empty", "empty-sub", "total_plants", "0");
      for (const [key, value] of [
        ["total_plants", "2"],
        ["plants_needing_water", "1"],
        ["plants_needing_fertilizer", "1"],
        ["plants_overdue", "1"],
      ])
        add("hub-device", null, key, value);
      w.connection = {
        subscribeEvents: async (callback: any, type: string) => {
          (w.registryEvents[type] ??= []).push(callback);
          return () => {
            w.unsubscribed++;
            w.registryEvents[type] = w.registryEvents[type].filter(
              (item: any) => item !== callback,
            );
          };
        },
        addEventListener: (_type: string, callback: any) =>
          w.readyEvents.push(callback),
        removeEventListener: (_type: string, callback: any) => {
          w.readyEvents = w.readyEvents.filter(
            (item: any) => item !== callback,
          );
        },
      };
      w.makeHass = () => ({
        states: { ...w.states },
        locale: { language: options.language || "en" },
        language: "en",
        connected: options.connected !== false,
        user: { is_admin: options.admin !== false },
        connection: w.connection,
        callWS: async (message: any) => {
          w.wsCalls.push(message);
          if (w.registryFail) throw Error("registry down");
          return message.type === "config/entity_registry/list"
            ? structuredClone(w.entities)
            : message.type === "config/area_registry/list"
              ? structuredClone(w.areas)
              : structuredClone(w.devices);
        },
        callService: async (...args: any[]) => {
          w.calls.push(args);
          if (w.fail) throw Error("private server details");
          if (w.defer)
            await new Promise((resolve) => {
              w.resolveAction = resolve;
            });
        },
      });
      w.update = () =>
        document
          .querySelectorAll("#root > *")
          .forEach((card: any) => (card.hass = w.makeHass()));
      w.setState = (device: string, key: string, value: string, attrs = {}) => {
        const e = w.entities.find(
          (e: any) => e.device_id === device && e.translation_key === key,
        );
        w.states[e.entity_id] = {
          ...w.states[e.entity_id],
          state: value,
          attributes: { ...w.states[e.entity_id].attributes, ...attrs },
        };
        w.update();
      };
      w.render = (tag: string, configuration: any) => {
        const card: any = document.createElement(tag);
        card.setConfig({ type: `custom:${tag}`, ...configuration });
        card.hass = w.makeHass();
        document.querySelector("#root")!.append(card);
        return card;
      };
      w.render(
        String(
          options.panel
            ? "plantbased-panel"
            : options.overview
              ? "plantbased-overview-card"
              : "plantbased-card",
        ),
        { device_id: "monstera", ...config },
      );
    },
    { config, options },
  );
}
