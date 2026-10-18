import { expect, test, type Page } from "@playwright/test";

async function boot(
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
        connected: true,
        connection: w.connection,
        callWS: async (message: any) => {
          w.wsCalls.push(message);
          if (w.registryFail) throw Error("registry down");
          return message.type === "config/entity_registry/list"
            ? structuredClone(w.entities)
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
          options.overview ? "plantbased-overview-card" : "plantbased-card",
        ),
        { device_id: "monstera", ...config },
      );
    },
    { config, options },
  );
}

test("single plant, registry IDs, stable labels, safe actions and independent snooze", async ({
  page,
}) => {
  await boot(page);
  await expect(page.getByRole("heading", { name: "Monstera" })).toBeVisible();
  await expect(page.getByText("4 days overdue")).toBeVisible();
  await page.getByRole("button", { name: "Watered", exact: true }).click();
  await expect
    .poll(() => page.evaluate(() => (window as any).calls))
    .toEqual([
      ["plantbased", "mark_watered", {}, { device_id: "monstera" }, false],
    ]);
  await page.getByLabel("Snooze", { exact: true }).click();
  await page.getByRole("button", { name: "Fertilizing +1 day" }).click();
  expect(await page.evaluate(() => (window as any).calls[1])).toEqual([
    "plantbased",
    "snooze",
    { care_type: "fertilize", days: 1 },
    { device_id: "monstera" },
    false,
  ]);
  const src = await page.locator("img.illustration").getAttribute("src");
  expect(src).toContain(
    "/plantbased/illustrations/monstera.svg?v=browser-test",
  );
  await expect
    .poll(() =>
      page
        .locator("img.illustration")
        .evaluate((image: HTMLImageElement) => image.naturalWidth),
    )
    .toBeGreaterThan(0);
});

test("group contains only its members; device rename and group updates are pushed", async ({
  page,
}) => {
  await boot(page, { device_id: "living" });
  await expect(page.locator("article.plant")).toHaveCount(2);
  await expect(
    page.getByRole("heading", { name: "Living room" }),
  ).toBeVisible();
  await page.evaluate(() => {
    const w = window as any;
    w.devices.find((d: any) => d.id === "monstera").name_by_user = "Mona";
    w.registryEvents.device_registry_updated.forEach((fn: any) => fn());
  });
  await expect(page.getByRole("heading", { name: "Mona" })).toBeVisible();
  await page.evaluate(() => {
    const w = window as any;
    w.setState("ficus", "care_status", "ok", { group_id: null, group: null });
  });
  await expect(page.locator("article.plant")).toHaveCount(1);
});

test("overview counts use hub sensors, live due list, paused and disabled states", async ({
  page,
}) => {
  await boot(page, {}, { overview: true });
  await expect(page.locator(".count strong")).toHaveText(["2", "1", "1", "1"]);
  await expect(page.locator("article.plant")).toHaveCount(1);
  await page.evaluate(() => {
    const w = window as any;
    w.setState("monstera", "care_status", "paused");
    w.setState("monstera", "needs_water", "off");
    w.setState("monstera", "needs_fertilizer", "off");
    for (const key of [
      "plants_needing_water",
      "plants_needing_fertilizer",
      "plants_overdue",
    ])
      w.setState("hub-device", key, "0");
  });
  await expect(
    page.getByRole("heading", { name: "All caught up" }),
  ).toBeVisible();
  await expect(page.locator("article.plant")).toHaveCount(0);
});

test("pending action blocks duplicates and failures are visible without optimistic state", async ({
  page,
}) => {
  await boot(page);
  await page.evaluate(() => ((window as any).defer = true));
  const button = page.getByRole("button", { name: "Watered", exact: true });
  await button.click();
  await expect(button).toBeDisabled();
  await page.evaluate(() => (window as any).resolveAction());
  await expect(button).toBeEnabled();
  await page.evaluate(() => {
    (window as any).defer = false;
    (window as any).fail = true;
  });
  await button.click();
  await expect(page.getByRole("alert")).toContainText(
    "Care could not be saved",
  );
  await expect(page.getByText("4 days overdue")).toBeVisible();
  await expect(page.getByText("private server details")).toHaveCount(0);
});

test("unknown/disconnected plants disable actions; paused retains original dates", async ({
  page,
}) => {
  await boot(page);
  await page.evaluate(() => {
    (window as any).setState("monstera", "care_status", "paused");
  });
  await expect(page.locator(".badge")).toHaveText("Paused");
  await expect(page.getByText("4 days overdue")).toBeVisible();
  await page.evaluate(() => {
    (window as any).setState("monstera", "care_status", "unavailable");
  });
  await expect(page.locator(".badge")).toHaveText("Unavailable");
  await expect(
    page.getByRole("button", { name: "Watered", exact: true }),
  ).toBeDisabled();
});

test("disabled fertilizer and due-today states", async ({ page }) => {
  await boot(page);
  await page.evaluate(() => {
    const w = window as any;
    w.setState("monstera", "care_status", "water", {
      fertilizing_enabled: false,
    });
    w.setState("monstera", "days_until_watering", "0");
    w.setState("monstera", "needs_fertilizer", "off");
  });
  await expect(page.getByText("Not enabled")).toBeVisible();
  await expect(page.getByText("Due today")).toBeVisible();
  await expect(page.locator(".badge")).toHaveText("Care due");
  await expect(
    page.getByRole("button", { name: "Fertilized", exact: true }),
  ).toBeDisabled();
});

test("editor device picker excludes foreign and hub devices and preserves extra config", async ({
  page,
}) => {
  await boot(page);
  await page.evaluate(() => {
    const w = window as any;
    document.querySelector("#root")!.innerHTML = "";
    w.configChanges = [];
    const editor: any = document.createElement("plantbased-card-editor");
    editor.setConfig({
      type: "custom:plantbased-card",
      device_id: "monstera",
      custom_option: "preserved",
    });
    editor.hass = w.makeHass();
    editor.addEventListener("config-changed", (event: any) =>
      w.configChanges.push({
        config: event.detail.config,
        bubbles: event.bubbles,
        composed: event.composed,
      }),
    );
    document.querySelector("#root")!.append(editor);
  });
  await expect(page.locator("select option")).toHaveCount(5);
  await page.getByLabel("Choose a plant or group").selectOption("living");
  await page.getByLabel("Title", { exact: true }).fill("My corner");
  await page.getByLabel("Show care buttons").uncheck();
  const last = await page.evaluate(() => (window as any).configChanges.at(-1));
  expect(last).toMatchObject({
    config: {
      device_id: "living",
      title: "My corner",
      show_actions: false,
      custom_option: "preserved",
    },
    bubbles: true,
    composed: true,
  });
});

test("German locale wins and device/title text is escaped", async ({
  page,
}) => {
  await boot(
    page,
    { title: "<img src=x onerror=alert(1)>" },
    { language: "de-DE" },
  );
  await expect(
    page.getByRole("button", { name: "Gewässert", exact: true }),
  ).toBeVisible();
  await expect(page.getByText("4 Tage überfällig")).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "<img src=x onerror=alert(1)>" }),
  ).toBeVisible();
  expect(await page.locator("h2 img").count()).toBe(0);
});

test("registry failure retries; reconnect and disconnect release subscriptions", async ({
  page,
}) => {
  await boot(page);
  await expect(page.getByRole("heading", { name: "Monstera" })).toBeVisible();
  await page.evaluate(() => {
    const w = window as any;
    w.registryFail = true;
    w.readyEvents.forEach((fn: any) => fn());
  });
  await expect(page.getByRole("alert")).toContainText(
    "Plant information could not be loaded",
  );
  await page.evaluate(() => ((window as any).registryFail = false));
  await page.getByRole("button", { name: "Try again" }).click();
  await expect(page.getByRole("heading", { name: "Monstera" })).toBeVisible();
  await page.evaluate(() => (document.querySelector("#root")!.innerHTML = ""));
  await expect
    .poll(() => page.evaluate(() => (window as any).unsubscribed))
    .toBe(2);
  expect(await page.evaluate(() => (window as any).readyEvents.length)).toBe(0);
});

test("custom image errors fall back locally; unsafe image protocols are rejected", async ({
  page,
}) => {
  await boot(page);
  await page.evaluate(() => {
    (window as any).setState("monstera", "care_status", "water", {
      image_url: "/local/missing.png",
    });
  });
  await expect
    .poll(() => page.locator("img.illustration").getAttribute("src"))
    .toContain("/plantbased/illustrations/monstera.svg");
  await page.evaluate(() => {
    (window as any).setState("monstera", "care_status", "water", {
      image_url: "javascript:alert(1)",
    });
  });
  await expect(page.locator("img.illustration")).toHaveAttribute(
    "src",
    /illustrations\/monstera.svg/,
  );
});

test("empty group, deleted device, no plants and no implicit all-device target", async ({
  page,
}) => {
  await boot(page, { device_id: "empty" });
  await expect(page.getByText("This group has no plants yet.")).toBeVisible();
  await page.evaluate(() => {
    const card: any = document.querySelector("plantbased-card");
    card.setConfig({ type: "custom:plantbased-card", device_id: "missing" });
  });
  await expect(
    page.getByRole("heading", {
      name: "This plant or group is no longer available.",
    }),
  ).toBeVisible();
  await page.evaluate(() => {
    const w = window as any;
    document.querySelector("#root")!.innerHTML = "";
    w.devices = [];
    w.entities = [];
    w.render("plantbased-overview-card", {});
  });
  await expect(
    page.getByRole("heading", { name: "No plants yet" }),
  ).toBeVisible();
  expect(await page.evaluate(() => (window as any).calls.length)).toBe(0);
});

for (const [name, width, dark] of [
  ["mobile", 360, false],
  ["desktop", 820, false],
  ["dark", 420, true],
] as const) {
  test(`responsive ${name} screenshot and touch controls`, async ({ page }) => {
    await page.setViewportSize({ width, height: 1100 });
    await boot(page, {}, { overview: true, language: "de" });
    if (dark)
      await page
        .locator("body")
        .evaluate((element) => element.classList.add("dark"));
    await expect(
      page.getByRole("heading", { name: "Pflanzenübersicht" }),
    ).toBeVisible();
    await expect
      .poll(() =>
        page
          .locator("img.illustration")
          .evaluate((image: HTMLImageElement) => image.naturalWidth),
      )
      .toBeGreaterThan(0);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    for (const box of await page.getByRole("button").all()) {
      expect((await box.boundingBox())!.height).toBeGreaterThanOrEqual(44);
    }
    await page.screenshot({
      path: `/tmp/plantbased-${name}.png`,
      fullPage: true,
    });
  });
}

test("stub configs, invalid configs, overview editor and duplicate module load", async ({
  page,
}) => {
  await boot(page);
  const result = await page.evaluate(async () => {
    const Card: any = customElements.get("plantbased-card");
    const Overview: any = customElements.get("plantbased-overview-card");
    const empty: any = document.createElement("plantbased-card");
    empty.setConfig({
      type: "custom:plantbased-card",
      ...Card.getStubConfig(),
    });
    empty.hass = (window as any).makeHass();
    document.querySelector("#root")!.append(empty);
    const invalid = [];
    for (const config of [
      { device_id: 42 },
      { device_id: "x", title: 42 },
      { device_id: "x", show_actions: "yes" },
    ]) {
      try {
        empty.setConfig(config);
      } catch {
        invalid.push(true);
      }
    }
    await import("/plantbased/plantbased.js?v=another-version");
    const editor: any = Overview.getConfigElement();
    editor.hass = (window as any).makeHass();
    editor.setConfig({
      type: "custom:plantbased-overview-card",
      ...Overview.getStubConfig(),
    });
    document.querySelector("#root")!.append(editor);
    return {
      invalid: invalid.length,
      cards: (window as any).customCards.length,
      size: empty.getCardSize(),
      grid: empty.getGridOptions(),
    };
  });
  expect(result).toMatchObject({
    invalid: 3,
    cards: 2,
    size: 4,
    grid: { columns: 12 },
  });
  await expect(
    page.getByRole("heading", { name: "Choose a plant or group" }),
  ).toBeVisible();
  await expect(
    page
      .locator("plantbased-overview-card-editor")
      .getByLabel("Show care buttons"),
  ).toBeChecked();
});

test("desktop narrow column, keyboard care action and action-free mode", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1200, height: 900 });
  await boot(page, {}, { overview: true });
  await page
    .locator("#root")
    .evaluate((root) => ((root as HTMLElement).style.width = "320px"));
  const button = page.getByRole("button", { name: "Watered", exact: true });
  await button.focus();
  await page.keyboard.press("Enter");
  await expect
    .poll(() => page.evaluate(() => (window as any).calls.length))
    .toBe(1);
  expect(
    await page
      .locator("plantbased-overview-card")
      .evaluate((card) => card.scrollWidth <= card.clientWidth),
  ).toBe(true);
  await page.evaluate(() => {
    const card: any = document.querySelector("plantbased-overview-card");
    card.setConfig({
      type: "custom:plantbased-overview-card",
      show_actions: false,
    });
  });
  await expect(page.getByRole("button")).toHaveCount(0);
});

test("original illustration gallery renders all twelve local SVGs", async ({
  page,
}) => {
  await page.goto("/");
  await page.evaluate(() => {
    const root = document.querySelector("#root") as HTMLElement;
    root.style.gridTemplateColumns = "repeat(4,1fr)";
    for (const name of [
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
    ]) {
      const figure = document.createElement("figure");
      figure.style.margin = "0";
      const image = document.createElement("img");
      image.src = `/plantbased/illustrations/${name}.svg`;
      image.alt = name;
      image.style.width = "100%";
      const caption = document.createElement("figcaption");
      caption.textContent = name;
      caption.style.textAlign = "center";
      caption.style.fontSize = "12px";
      figure.append(image, caption);
      root.append(figure);
    }
  });
  await expect
    .poll(() =>
      page
        .locator("img")
        .evaluateAll((images) =>
          images.every(
            (image) => (image as HTMLImageElement).naturalWidth === 144,
          ),
        ),
    )
    .toBe(true);
  await page.screenshot({
    path: "/tmp/plantbased-illustrations.png",
    fullPage: true,
  });
});
