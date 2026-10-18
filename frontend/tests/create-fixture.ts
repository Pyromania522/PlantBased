import type { Page } from "@playwright/test";
import { readFile } from "node:fs/promises";

export async function installCreateApi(page: Page) {
  const language = await page.evaluate(() =>
    (window as any).makeHass().locale.language.startsWith("de") ? "de" : "en",
  );
  const resources = JSON.parse(
    await readFile(
      `custom_components/plantbased/translations/${language}.json`,
      "utf8",
    ),
  );
  await page.evaluate((resources) => {
    const w = window as any;
    w.apiCalls = [];
    w.flowNumber = 0;
    w.createFail = false;
    w.deferCreate = false;
    w.deferFlow = false;
    w.hubLoaded = true;
    const original = w.makeHass;
    const flowBase = "config/config_entries/subentries/flow";
    const fields = (kind: string) => {
      const schema: any[] = [
        { name: "name", required: true, default: "", selector: { text: {} } },
        { name: "area", required: false, selector: { area: {} } },
        {
          name: "image_preset",
          required: true,
          default: "generic",
          selector: {
            select: {
              options: ["generic", "monstera"],
              translation_key: "image_preset",
            },
          },
        },
      ];
      if (kind === "plant")
        schema.push(
          {
            name: "group",
            description: { suggested_value: "none" },
            selector: {
              select: {
                translation_key: "plant_group",
                options: [
                  { value: "none", label: "No group" },
                  { value: "living-sub", label: "Living room" },
                ],
              },
            },
          },
          { name: "species", selector: { text: {} } },
          { name: "notes", selector: { text: { multiline: true } } },
          { name: "image_url", selector: { text: {} } },
          ...["watering_interval", "fertilizing_interval"].map(
            (name, index) => ({
              name,
              required: true,
              default: index ? 28 : 7,
              selector: { number: { min: 1, max: 365, step: 1 } },
            }),
          ),
          {
            name: "adaptive_watering",
            required: true,
            default: false,
            selector: { boolean: {} },
          },
          {
            name: "fertilizing_enabled",
            required: true,
            default: true,
            selector: { boolean: {} },
          },
          {
            name: "all_year",
            required: true,
            default: false,
            selector: { boolean: {} },
          },
          ...["season_start", "season_end"].map((name, index) => ({
            name,
            required: true,
            default: index ? "9" : "3",
            selector: {
              select: { options: ["1", "3", "9"], translation_key: "month" },
            },
          })),
          ...["initial_last_watered", "initial_last_fertilized"].map(
            (name) => ({
              name,
              required: true,
              default: "2026-06-15",
              selector: { date: {} },
            }),
          ),
        );
      return schema;
    };
    const localize = (key: string) =>
      key
        .replace(/^component\.plantbased\./, "")
        .split(".")
        .reduce((value: any, part: string) => value?.[part], resources) ?? "";
    w.makeHass = () => ({
      ...original(),
      callWS: async (message: any) =>
        message.type === "config_entries/get"
          ? [
              {
                entry_id: "hub",
                state: w.hubLoaded ? "loaded" : "not_loaded",
                supported_subentry_types: { plant: {}, group: {} },
              },
            ]
          : original().callWS(message),
      loadBackendTranslation: async () => localize,
      callApi: async (
        method: string,
        path: string,
        data?: any,
        headers?: any,
      ) => {
        w.apiCalls.push({ method, path, data, headers });
        if (method === "DELETE") return {};
        if (path === flowBase) {
          w.kind = data.handler[1];
          const flow_id = `flow-${++w.flowNumber}`;
          const result = {
            type: "form",
            flow_id,
            step_id: "user",
            data_schema: fields(w.kind),
            errors: {},
          };
          if (w.deferFlow)
            await new Promise((resolve) => {
              w.resolveFlow = () => resolve(undefined);
            });
          return result;
        }
        if (w.createFail) throw Error("private server details");
        if (w.deferCreate)
          await new Promise((resolve) => {
            w.resolveCreate = () => resolve(undefined);
          });
        if (!data.name.trim())
          return {
            type: "form",
            flow_id: "flow-1",
            step_id: "user",
            data_schema: fields(w.kind),
            errors: { name: "name_required" },
          };
        const id = `added-${w.kind}-${w.flowNumber}`;
        w.devices.push({
          id,
          name: data.name,
          model: w.kind === "plant" ? "Plant" : "Group",
          name_by_user: null,
          identifiers: [["plantbased", id]],
          area_id: data.area ?? null,
        });
        w.update();
        return { type: "create_entry", flow_id: "flow-1" };
      },
    });
    w.update();
  }, resources);
}
