import { expect, test } from "@playwright/test";
import { boot } from "./fixture";
import { installCreateApi } from "./create-fixture";

for (const kind of ["plant", "group"] as const) {
  test(`overview creates a ${kind} using native schema defaults and stays on the page`, async ({
    page,
  }) => {
    await boot(page, {}, { panel: true });
    await installCreateApi(page);
    await page
      .getByRole("button", {
        name: kind === "plant" ? "Add plant" : "Add group",
        exact: true,
      })
      .click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await expect(dialog.getByLabel("Name", { exact: false })).toBeFocused();
    await dialog.getByLabel("Name", { exact: false }).fill("New from overview");
    await dialog
      .getByLabel("Area", { exact: false })
      .selectOption("living-area");
    if (kind === "plant") {
      await expect(
        dialog.getByLabel("Learn watering rhythm"),
      ).not.toBeChecked();
      await dialog.getByLabel("Learn watering rhythm").check();
      await expect(
        dialog.getByLabel("Watering interval", { exact: false }),
      ).toHaveValue("7");
      await expect(
        dialog.getByLabel("Last watered", { exact: false }),
      ).toHaveValue("2026-06-15");
      await dialog.getByLabel("Watering interval", { exact: false }).fill("12");
      await dialog.getByLabel("Enable fertilizing").uncheck();
      await expect(
        dialog.getByLabel("Group (optional)", { exact: true }),
      ).toHaveValue("none");
    }
    await dialog.getByRole("button", { name: "Create", exact: true }).click();
    await expect(dialog).toHaveCount(0);
    await expect(
      page.getByRole("heading", { name: "Your plants" }),
    ).toBeVisible();
    const calls = await page.evaluate(() => (window as any).apiCalls);
    expect(calls[0]).toMatchObject({
      method: "POST",
      path: "config/config_entries/subentries/flow",
      data: { handler: ["hub", kind] },
    });
    expect(calls[1].data).toMatchObject({
      name: "New from overview",
      area: "living-area",
      image_preset: "generic",
    });
    if (kind === "plant") {
      expect(calls[1].data).toMatchObject({
        group: "none",
        adaptive_watering: true,
        watering_interval: 12,
        fertilizing_enabled: false,
        all_year: false,
        initial_last_watered: "2026-06-15",
      });
      expect(calls[1].data).not.toHaveProperty("image_url");
      await expect(
        page.getByRole("heading", { name: "New from overview" }),
      ).toBeVisible();
    } else {
      await page.getByRole("button", { name: "Groups", exact: true }).click();
      await expect(
        page.getByRole("heading", { name: "New from overview" }),
      ).toBeVisible();
    }
    expect(calls.filter((call: any) => call.method === "DELETE")).toHaveLength(
      0,
    );
  });
}

test("cancel removes an unfinished native flow and creates no device", async ({
  page,
}) => {
  await boot(page, {}, { panel: true, language: "de" });
  await installCreateApi(page);
  await page
    .getByRole("button", { name: "Pflanze hinzufügen", exact: true })
    .click();
  const dialog = page.getByRole("dialog");
  await expect(
    dialog.getByLabel("Gruppe (optional)", { exact: true }),
  ).toHaveValue("none");
  await expect(
    dialog.getByRole("option", { name: "Keine Gruppe", exact: true }),
  ).toHaveCount(1);
  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          (window as any).apiCalls.filter(
            (call: any) => call.method === "DELETE",
          ).length,
      ),
    )
    .toBe(1);
  await expect(page.locator("article.plant")).toHaveCount(2);
});

test("validation and request failures keep values, suppress duplicates and expose no server details", async ({
  page,
}) => {
  await boot(page, {}, { panel: true });
  await installCreateApi(page);
  await page.getByRole("button", { name: "Add group", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Name", { exact: false }).fill("   ");
  await dialog.getByRole("button", { name: "Create", exact: true }).click();
  await expect(dialog.getByRole("alert")).toHaveText("Enter a name.");
  await dialog.getByLabel("Name", { exact: false }).fill("My group");
  await page.evaluate(() => {
    (window as any).createFail = true;
  });
  await dialog.getByRole("button", { name: "Create", exact: true }).click();
  await expect(
    dialog.getByText("Could not add this plant or group.", { exact: false }),
  ).toBeVisible();
  await expect(dialog.getByText("private server details")).toHaveCount(0);
  await expect(dialog.getByLabel("Name", { exact: false })).toHaveValue(
    "My group",
  );
  await page.evaluate(() => {
    const w = window as any;
    w.createFail = false;
    w.deferCreate = true;
  });
  const button = dialog.getByRole("button", { name: "Create", exact: true });
  await button.click();
  await expect(button).toBeDisabled();
  await page.keyboard.press("Escape");
  await expect(dialog).toBeVisible();
  expect(
    await page.evaluate(
      () =>
        (window as any).apiCalls.filter((call: any) => call.method === "POST")
          .length,
    ),
  ).toBe(4);
  await page.evaluate(() => (window as any).resolveCreate());
  await expect(dialog).toHaveCount(0);
});

test("an unloaded hub is retryable and a late flow is cleaned up after navigation", async ({
  page,
}) => {
  await boot(page, {}, { panel: true });
  await installCreateApi(page);
  await page.evaluate(() => {
    (window as any).hubLoaded = false;
  });
  await page.getByRole("button", { name: "Add plant", exact: true }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByRole("alert")).toContainText(
    "setup form could not be loaded",
  );
  await page.evaluate(() => {
    const w = window as any;
    w.hubLoaded = true;
    w.deferFlow = true;
  });
  await dialog.getByRole("button", { name: "Try again" }).click();
  await expect
    .poll(() => page.evaluate(() => !!(window as any).resolveFlow))
    .toBe(true);
  await page.evaluate(() => {
    document.querySelector("#root")!.innerHTML = "";
    (window as any).resolveFlow();
  });
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          (window as any).apiCalls.filter(
            (call: any) => call.method === "DELETE",
          ).length,
      ),
    )
    .toBe(1);
});

test("mobile creation form fits, remains keyboard accessible and restricts non-admins", async ({
  page,
}) => {
  await page.setViewportSize({ width: 360, height: 800 });
  await boot(page, {}, { panel: true, language: "de" });
  await installCreateApi(page);
  await page
    .getByRole("button", { name: "Pflanze hinzufügen", exact: true })
    .click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByLabel("Name", { exact: false })).toBeFocused();
  const box = (await dialog.boundingBox())!;
  expect(box.x).toBeGreaterThanOrEqual(0);
  expect(box.x + box.width).toBeLessThanOrEqual(360);
  await expect(
    dialog.getByRole("button", { name: "Abbrechen", exact: true }),
  ).toBeInViewport();
  await expect(
    dialog.getByRole("button", { name: "Anlegen", exact: true }),
  ).toBeInViewport();
  await page.screenshot({
    path: "/tmp/plantbased-create-mobile.png",
    fullPage: true,
  });
  await page.keyboard.press("Escape");
  await boot(page, {}, { panel: true, admin: false });
  await expect(
    page.getByRole("button", { name: "Add plant", exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Add group", exact: true }),
  ).toHaveCount(0);
});
