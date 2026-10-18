import { expect, test } from "@playwright/test";
import { boot } from "./fixture";

test("sidebar panel shows every plant, images, status, settings and real care targets", async ({
  page,
}) => {
  await boot(page, {}, { panel: true, language: "de" });
  await expect(
    page.getByRole("heading", { name: "Deine Pflanzen" }),
  ).toBeVisible();
  await expect(page.locator("article.plant")).toHaveCount(2);
  await expect(page.locator("main > .counts strong")).toHaveText([
    "2",
    "1",
    "1",
    "1",
  ]);
  await expect(
    page.locator("article.plant").filter({ hasText: "Monstera" }),
  ).toContainText("4 Tage überfällig");
  await expect(
    page.locator("article.plant").filter({ hasText: "Ficus" }),
  ).toContainText("Gut versorgt");
  await expect(
    page.getByRole("link", { name: "Einstellungen" }),
  ).toHaveAttribute("href", "/config/integrations/integration/plantbased");
  await expect(
    page
      .locator("article.plant")
      .filter({ hasText: "Monstera" })
      .getByRole("link"),
  ).toHaveAttribute("href", "/config/devices/device/monstera");
  await page
    .locator("article.plant")
    .filter({ hasText: "Monstera" })
    .getByRole("button", { name: "Gewässert", exact: true })
    .click();
  expect(await page.evaluate(() => (window as any).calls)).toEqual([
    ["plantbased", "mark_watered", {}, { device_id: "monstera" }, false],
  ]);
  await page.evaluate(() => {
    const w = window as any;
    w.menu = [];
    document.addEventListener("hass-toggle-menu", (event) =>
      w.menu.push({ bubbles: event.bubbles, composed: event.composed }),
    );
  });
  await page.getByRole("button", { name: "Seitenleiste öffnen" }).click();
  expect(await page.evaluate(() => (window as any).menu)).toEqual([
    { bubbles: true, composed: true },
  ]);
});

test("group cards include empty groups, member images, due status and scoped actions", async ({
  page,
}) => {
  await boot(page, {}, { panel: true });
  await page.getByRole("button", { name: "Groups", exact: true }).click();
  await expect(page.locator(".collection-card")).toHaveCount(2);
  const group = page.getByRole("article", { name: "Living room", exact: true });
  await expect(group.locator(".collection-images img")).toHaveCount(2);
  await expect(group.locator(".collection-heading .badge")).toHaveText(
    "Overdue",
  );
  await expect(group.locator(".counts strong")).toHaveText([
    "2",
    "1",
    "1",
    "1",
  ]);
  await expect(page.getByText("This group has no plants yet.")).toBeVisible();
  await group.locator(".members > summary").click();
  await expect(group.locator("article.plant")).toHaveCount(2);
  await page.getByLabel("Care due only").check();
  await expect(page.locator(".collection-card")).toHaveCount(1);
  await expect(group.locator("article.plant")).toHaveCount(1);
  await group.getByRole("button", { name: "Watered", exact: true }).click();
  expect(await page.evaluate(() => (window as any).calls[0][3])).toEqual({
    device_id: "monstera",
  });
});

test("area sections follow native area assignments and room renames live", async ({
  page,
}) => {
  await boot(page, {}, { panel: true });
  await page.getByRole("button", { name: "Areas", exact: true }).click();
  await expect(page.locator(".area-section")).toHaveCount(2);
  await expect(page.getByRole("region", { name: "Bedroom" })).toContainText(
    "Ficus",
  );
  await page.evaluate(() => {
    const w = window as any;
    w.devices.find((device: any) => device.id === "ficus").area_id =
      "living-area";
    w.registryEvents.device_registry_updated.forEach((fn: any) => fn());
  });
  await expect(page.locator(".area-section")).toHaveCount(1);
  await expect(
    page.getByRole("region", { name: "Living room" }).locator("article.plant"),
  ).toHaveCount(2);
  await page.evaluate(() => {
    const w = window as any;
    w.areas[0].name = "Sun room";
    w.registryEvents.area_registry_updated.forEach((fn: any) => fn());
  });
  await expect(page.getByRole("region", { name: "Sun room" })).toBeVisible();
  await page.evaluate(() => {
    const w = window as any;
    w.devices.find((device: any) => device.id === "ficus").area_id = null;
    w.registryEvents.device_registry_updated.forEach((fn: any) => fn());
    w.setState("ficus", "care_status", "ok", { group_id: null, group: null });
  });
  await expect(page.getByRole("region", { name: "No area" })).toContainText(
    "Ficus",
  );
  await page.getByRole("button", { name: "Groups", exact: true }).click();
  await expect(
    page.getByRole("article", { name: "No group", exact: true }),
  ).toBeVisible();
});

test("search and care filter work across plants, renamed groups and empty groups", async ({
  page,
}) => {
  await boot(page, {}, { panel: true });
  await page.getByRole("searchbox").fill("bedroom");
  await expect(page.locator("article.plant")).toHaveCount(1);
  await expect(page.locator("article.plant")).toContainText("Ficus");
  await page.getByLabel("Care due only").check();
  await expect(
    page.getByRole("heading", { name: "No matching plants" }),
  ).toBeVisible();
  await page.getByLabel("Care due only").uncheck();
  await page.getByRole("button", { name: "Groups", exact: true }).click();
  await page.getByRole("searchbox").fill("empty");
  await expect(page.locator(".collection-card")).toHaveCount(1);
  await expect(
    page.getByRole("heading", { name: "No matching plants" }),
  ).toHaveCount(0);
  await page.evaluate(() => {
    const w = window as any;
    w.devices.find((device: any) => device.id === "living").name_by_user =
      "<img src=x onerror=alert(1)>";
    w.registryEvents.device_registry_updated.forEach((fn: any) => fn());
  });
  await page.getByRole("searchbox").fill("<img");
  await expect(
    page.getByRole("heading", { name: "<img src=x onerror=alert(1)>" }),
  ).toBeVisible();
  await expect(page.locator("h2 img")).toHaveCount(0);
  await expect(
    page.getByRole("heading", { name: "No matching plants" }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "Plants", exact: true }).click();
  await expect(page.locator("article.plant")).toHaveCount(2);
  await expect(page.locator(".plant-group")).toHaveText([
    "<img src=x onerror=alert(1)>",
    "<img src=x onerror=alert(1)>",
  ]);
});

test("non-admin and disconnected views do not expose administration or enable care", async ({
  page,
}) => {
  await boot(page, {}, { panel: true, admin: false, connected: false });
  await expect(page.locator("article.plant")).toHaveCount(2);
  await expect(page.getByRole("link")).toHaveCount(0);
  await expect(page.getByText("Disconnected.", { exact: false })).toBeVisible();
  for (const button of await page
    .getByRole("button", { name: "Watered", exact: true })
    .all())
    await expect(button).toBeDisabled();
  await page.getByRole("button", { name: "Groups", exact: true }).click();
  await expect(page.getByRole("link")).toHaveCount(0);
});

test("panel retries registry errors and cleans up all three subscriptions", async ({
  page,
}) => {
  await boot(page, {}, { panel: true });
  await expect(page.locator("article.plant")).toHaveCount(2);
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
  await expect(page.locator("article.plant")).toHaveCount(2);
  await page.evaluate(() => (document.querySelector("#root")!.innerHTML = ""));
  await expect
    .poll(() => page.evaluate(() => (window as any).unsubscribed))
    .toBe(3);
  expect(await page.evaluate(() => (window as any).readyEvents.length)).toBe(0);
});

test("panel without plants still shows existing empty groups and an add-plants hint", async ({
  page,
}) => {
  await boot(page, {}, { panel: true });
  await page.evaluate(() => {
    const w = window as any;
    w.devices = w.devices.filter((device: any) => device.model !== "Plant");
    w.registryEvents.device_registry_updated.forEach((fn: any) => fn());
  });
  await expect(
    page.getByRole("heading", { name: "No plants yet" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Groups", exact: true }).click();
  await expect(page.locator(".collection-card")).toHaveCount(2);
  await expect(page.getByText("This group has no plants yet.")).toHaveCount(2);
});

for (const [name, width, dark] of [
  ["desktop", 1280, false],
  ["mobile", 360, false],
  ["dark", 420, true],
] as const) {
  test(`panel ${name}: responsive cards, groups, touch controls and preview`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 1080 });
    await boot(page, {}, { panel: true, language: "de" });
    await page.locator("#root").evaluate((root) => {
      (root as HTMLElement).style.maxWidth = "none";
    });
    if (dark)
      await page.locator("body").evaluate((body) => body.classList.add("dark"));
    await expect(page.locator("article.plant")).toHaveCount(2);
    await expect
      .poll(() =>
        page
          .locator("img.illustration")
          .evaluateAll((images) =>
            images.every(
              (image) => (image as HTMLImageElement).naturalWidth > 0,
            ),
          ),
      )
      .toBe(true);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    for (const button of await page.getByRole("button").all())
      expect((await button.boundingBox())!.height).toBeGreaterThanOrEqual(44);
    await page.screenshot({
      path: `/tmp/plantbased-panel-${name}.png`,
      fullPage: true,
    });
    await page.getByRole("button", { name: "Gruppen", exact: true }).click();
    await expect(page.locator(".collection-card")).toHaveCount(2);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page.screenshot({
      path: `/tmp/plantbased-panel-groups-${name}.png`,
      fullPage: true,
    });
    await page.getByRole("button", { name: "Bereiche", exact: true }).click();
    await expect(page.locator(".area-section")).toHaveCount(2);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
    await page.screenshot({
      path: `/tmp/plantbased-panel-areas-${name}.png`,
      fullPage: true,
    });
  });
}
