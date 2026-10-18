import { css, html, nothing } from "lit";
import { repeat } from "lit/directives/repeat.js";
import { PlantBasedBase, icon } from "./cards";
import { t, type TextKey } from "./localize";
import { deviceName, plants, presetUrl } from "./model";
import { styles } from "./styles";
import type { Plant } from "./types";

type View = "plants" | "groups" | "areas";
interface Collection {
  id: string;
  name: string;
  members: Plant[];
  deviceId?: string;
}

export class PlantBasedPanel extends PlantBasedBase {
  static properties = {
    ...PlantBasedBase.properties,
    narrow: { type: Boolean },
    _view: { state: true },
    _search: { state: true },
    _dueOnly: { state: true },
  };
  protected overview = true;
  protected get includeAreas() {
    return true;
  }
  narrow = false;
  private _view: View = "plants";
  private _search = "";
  private _dueOnly = false;

  private image(plant?: Plant) {
    return html`<img
      src=${plant?.image ?? presetUrl("generic")}
      alt=""
      loading="lazy"
      referrerpolicy="no-referrer"
      @error=${(event: Event) => {
        const image = event.currentTarget as HTMLImageElement;
        const fallback = presetUrl(plant?.preset ?? "generic");
        if (image.src !== fallback) image.src = fallback;
      }}
    />`;
  }

  protected plantLinks(plant: Plant) {
    return html`<footer class="plant-footer">
      <span>${plant.area ?? t(this.hass, "noArea")}</span>
      ${this.hass?.user?.is_admin ? html`<a href=${`/config/devices/device/${encodeURIComponent(plant.deviceId)}`}>${t(this.hass, "details")}</a>` : nothing}
    </footer>`;
  }

  private counts(members: Plant[]) {
    const values = [
      members.length,
      members.filter((p) => p.waterDue).length,
      members.filter((p) => p.fertilizerDue).length,
      members.filter((p) => p.tone === "overdue").length,
    ];
    const keys: TextKey[] = ["total", "water", "fertilize", "overdue"];
    const icons = ["plants", "water", "leaf", "clock"] as const;
    return html`<div class="counts">
      ${keys.map((key, index) => html`<div class="count ${key}"><span>${icon(icons[index])}${t(this.hass, key)}</span><strong>${values[index]}</strong></div>`)}
    </div>`;
  }

  private plantMatches(plant: Plant) {
    const query = this._search.trim().toLocaleLowerCase();
    return (
      (!this._dueOnly || plant.waterDue || plant.fertilizerDue) &&
      (!query ||
        [plant.name, plant.group, plant.area].some((value) =>
          value?.toLocaleLowerCase().includes(query),
        ))
    );
  }

  private collections(all: Plant[]): Collection[] {
    const data = this.registry.data!;
    if (this._view === "areas") {
      const areas = new Map<string, Collection>();
      for (const plant of all) {
        const id = plant.areaId ?? "";
        if (!areas.has(id))
          areas.set(id, {
            id,
            name: plant.area ?? t(this.hass, "noArea"),
            members: [],
          });
        areas.get(id)!.members.push(plant);
      }
      return [...areas.values()].sort((a, b) => a.name.localeCompare(b.name));
    }
    const groups = data.devices
      .filter((device) => device.model === "Group")
      .map((device) => {
        const id =
          data.entities.find(
            (entity) =>
              entity.device_id === device.id && entity.config_subentry_id,
          )?.config_subentry_id ??
          device.identifiers.find(([domain]) => domain === "plantbased")?.[1] ??
          device.id;
        return {
          id,
          deviceId: device.id,
          name: deviceName(device),
          members: all.filter((plant) => plant.groupId === id),
        };
      });
    const unassigned = all.filter(
      (plant) => !groups.some((group) => group.id === plant.groupId),
    );
    const result: Collection[] = groups;
    if (unassigned.length)
      result.push({
        id: "unassigned",
        name: t(this.hass, "noGroup"),
        members: unassigned,
      });
    return result.sort((a, b) => a.name.localeCompare(b.name));
  }

  private visibleCollections(all: Plant[]) {
    const query = this._search.trim().toLocaleLowerCase();
    return this.collections(all)
      .map((collection) => {
        const nameMatches = collection.name.toLocaleLowerCase().includes(query);
        const shown = collection.members.filter((plant) =>
          nameMatches
            ? !this._dueOnly || plant.waterDue || plant.fertilizerDue
            : this.plantMatches(plant),
        );
        return {
          collection,
          shown,
          visible:
            shown.length > 0 ||
            (!collection.members.length && nameMatches && !this._dueOnly),
        };
      })
      .filter((item) => item.visible);
  }

  private collection(collection: Collection, shown: Plant[]) {
    if (this._view === "areas")
      return html`<section class="area-section" aria-label=${collection.name}>
        <div class="section-title">
          <h2>${collection.name}</h2>
          <span
            >${shown.length}
            ${t(this.hass, shown.length === 1 ? "plant" : "plants")}</span
          >
        </div>
        <div class="plant-grid">
          ${repeat(
            shown,
            (plant) => plant.deviceId,
            (plant) => this.row(plant),
          )}
        </div>
      </section>`;
    const tone =
      ["overdue", "due", "unavailable", "paused", "ok"].find((tone) =>
        collection.members.some((plant) => plant.tone === tone),
      ) ?? "ok";
    return html`<article class="collection-card" aria-label=${collection.name}>
      <div class="collection-heading">
        <div class="collection-images">
          ${(collection.members.length ? collection.members.slice(0, 3) : [undefined]).map((plant) => this.image(plant))}
        </div>
        <div>
          <h2>${collection.name}</h2>
          <p>
            ${collection.members.length}
            ${t(this.hass, collection.members.length === 1 ? "plant" : "plants")}
          </p>
          ${collection.members.length ? html`<span class="badge ${tone}">${t(this.hass, tone as TextKey)}</span>` : nothing}
        </div>
      </div>
      ${this.counts(collection.members)}
      ${
        shown.length
          ? html`<details class="members">
              <summary>${t(this.hass, "showPlants")} · ${shown.length}</summary>
              <div class="member-grid">
                ${repeat(
                  shown,
                  (plant) => plant.deviceId,
                  (plant) => this.row(plant),
                )}
              </div>
            </details>`
          : html`<p class="group-empty">${t(this.hass, "groupEmpty")}</p>`
      }
      ${collection.deviceId && this.hass?.user?.is_admin ? html`<a class="collection-link" href=${`/config/devices/device/${encodeURIComponent(collection.deviceId)}`}>${t(this.hass, "groupDetails")}</a>` : nothing}
    </article>`;
  }

  render() {
    const all =
      this.hass && this.registry.data
        ? plants(this.hass, this.registry.data)
        : [];
    const shown = all.filter((plant) => this.plantMatches(plant));
    const collections = this.registry.data ? this.visibleCollections(all) : [];
    return html`<div class="toolbar">
        <button
          class="menu"
          aria-label=${t(this.hass, "openMenu")}
          @click=${() => this.dispatchEvent(new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }))}
        >
          ☰
        </button>
        <span class="toolbar-brand">${icon("plants")} PlantBased</span>
        ${this.hass?.user?.is_admin ? html`<a class="settings" href="/config/integrations/integration/plantbased">${t(this.hass, "settings")}</a>` : nothing}
      </div>
      <main>
        <header class="page-heading">
          <div class="brand">PlantBased</div>
          <h1>${t(this.hass, "yourPlants")}</h1>
          <p>${t(this.hass, "panelHint")}</p>
        </header>
        ${this.renderStatus()}
        ${
          this.hass && this.registry.data && !this.registry.error
            ? html`
                ${this.counts(all)}
                <div class="controls">
                  <nav aria-label=${t(this.hass, "view")}>
                    ${(["plants", "groups", "areas"] as const).map(
                      (view) =>
                        html`<button
                          aria-pressed=${this._view === view}
                          @click=${() => {
                            this._view = view;
                          }}
                        >
                          ${t(this.hass, view)}
                        </button>`,
                    )}
                  </nav>
                  <label class="search"
                    ><span>${t(this.hass, "search")}</span
                    ><input
                      type="search"
                      .value=${this._search}
                      placeholder=${t(this.hass, "searchHint")}
                      @input=${(event: Event) => {
                        this._search = (event.target as HTMLInputElement).value;
                      }}
                  /></label>
                  <label class="due-filter"
                    ><input
                      type="checkbox"
                      .checked=${this._dueOnly}
                      @change=${(event: Event) => {
                        this._dueOnly = (
                          event.target as HTMLInputElement
                        ).checked;
                      }}
                    />${t(this.hass, "dueOnly")}</label
                  >
                </div>
                ${
                  !all.length &&
                  (this._view !== "groups" ||
                    !this.registry.data.devices.some(
                      (device) => device.model === "Group",
                    ))
                    ? this.empty("noPlants", "noPlantsHint")
                    : this._view === "plants"
                      ? shown.length
                        ? html`<div class="plant-grid">
                            ${repeat(
                              shown,
                              (plant) => plant.deviceId,
                              (plant) => this.row(plant),
                            )}
                          </div>`
                        : this.empty("noMatches", "noMatchesHint")
                      : html`<div
                            class=${this._view === "groups" ? "collection-grid" : "area-list"}
                          >
                            ${repeat(
                              collections,
                              ({ collection }) =>
                                `${this._view}:${collection.id}`,
                              ({ collection, shown }) =>
                                this.collection(collection, shown),
                            )}
                          </div>
                          ${!collections.length ? this.empty("noMatches", "noMatchesHint") : nothing}`
                }
                ${this.hass.connected === false ? html`<p role="status" class="offline">${t(this.hass, "offline")}</p>` : nothing}
                ${this.feedback()}
              `
            : nothing
        }
      </main>`;
  }

  static styles = [
    styles,
    css`
      :host {
        min-height: 100%;
        background: var(--primary-background-color, #f6f8f4);
      }
      .toolbar {
        min-height: 64px;
        padding: 8px 24px;
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 1px solid var(--pb-line);
        background: var(--app-header-background-color, var(--pb-surface));
        color: var(--app-header-text-color, var(--primary-text-color));
      }
      .toolbar-brand {
        display: inline-flex;
        align-items: center;
        gap: 9px;
        font-weight: 600;
      }
      .toolbar-brand svg {
        width: 24px;
        height: 24px;
        color: var(--pb-green);
      }
      .menu {
        width: 44px;
        border: 0;
        font-size: 22px;
        color: inherit;
        background: transparent;
      }
      a {
        color: var(--primary-color, #397656);
        text-underline-offset: 3px;
        font-size: 13px;
        min-height: 44px;
        display: inline-flex;
        align-items: center;
      }
      a:focus-visible {
        outline: 2px solid var(--primary-color, #397656);
        outline-offset: 3px;
      }
      .settings {
        margin-left: auto;
        font-weight: 600;
      }
      main {
        max-width: 1360px;
        margin: 0 auto;
        padding: 36px 32px 48px;
      }
      .page-heading {
        margin-bottom: 26px;
      }
      h1 {
        font-size: clamp(28px, 4vw, 38px);
        font-weight: 550;
        letter-spacing: -0.04em;
        margin: 10px 0 0;
      }
      .page-heading p {
        margin-top: 10px;
      }
      .counts {
        padding: 0;
        gap: 12px;
        grid-template-columns: repeat(4, minmax(0, 1fr));
      }
      .count {
        background: var(--pb-surface);
        border: 1px solid var(--pb-line);
        padding: 16px;
      }
      .count strong {
        font-size: 30px;
      }
      .controls {
        display: flex;
        flex-wrap: wrap;
        align-items: end;
        gap: 16px;
        margin: 28px 0 22px;
      }
      nav {
        display: inline-flex;
        padding: 4px;
        gap: 3px;
        border: 1px solid var(--pb-line);
        border-radius: 13px;
        background: var(--pb-surface);
      }
      nav button {
        border: 0;
        padding: 8px 18px;
        font-size: 13px;
      }
      nav button[aria-pressed="true"] {
        background: color-mix(in srgb, var(--pb-green) 12%, var(--pb-surface));
        color: var(--pb-green);
        font-weight: 600;
      }
      label {
        margin: 0;
      }
      .search {
        flex: 1;
        min-width: 180px;
      }
      .search span {
        display: block;
        font-size: 11px;
        color: var(--pb-muted);
        margin: 0 0 6px 2px;
      }
      input[type="search"] {
        width: 100%;
        min-height: 46px;
        padding: 10px 14px;
        border-radius: 10px;
        border: 1px solid var(--pb-line);
        background: var(--pb-surface);
        font: inherit;
        color: inherit;
        font-size: 13px;
      }
      .due-filter {
        display: flex;
        align-items: center;
        gap: 8px;
        min-height: 46px;
        cursor: pointer;
      }
      .plant-grid,
      .member-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr));
        gap: 16px;
      }
      .plant {
        padding: 20px;
      }
      .plant-top {
        grid-template-columns: 94px minmax(0, 1fr);
        gap: 16px;
      }
      .illustration {
        width: 94px;
        height: 112px;
      }
      .plant-footer {
        border-top: 1px solid var(--pb-line);
        margin-top: 14px;
        padding-top: 4px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .plant-footer span {
        color: var(--pb-muted);
        font-size: 12px;
        overflow-wrap: anywhere;
      }
      .collection-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr));
        gap: 18px;
        align-items: start;
      }
      .collection-card {
        min-width: 0;
        background: var(--pb-surface);
        border: 1px solid var(--pb-line);
        border-radius: 16px;
        padding: 22px;
      }
      .collection-heading {
        display: flex;
        align-items: center;
        gap: 18px;
        margin-bottom: 20px;
      }
      .collection-heading h2 {
        margin-top: 0;
        font-size: 21px;
      }
      .collection-heading p {
        font-size: 12px;
        margin: 4px 0 7px;
      }
      .collection-images {
        display: flex;
        min-width: 100px;
        padding-left: 8px;
      }
      .collection-images img {
        width: 62px;
        height: 88px;
        object-fit: contain;
        border-radius: 12px;
        background: var(--secondary-background-color, #f2f5ef);
        border: 2px solid var(--pb-surface);
        margin-left: -8px;
      }
      .collection-card .counts {
        gap: 6px;
      }
      .collection-card .count {
        padding: 10px 8px;
      }
      .collection-card .count strong {
        font-size: 22px;
      }
      .members {
        margin-top: 18px;
      }
      .members summary {
        display: inline-flex;
        min-width: 150px;
        padding: 10px 14px;
        font-size: 13px;
        color: var(--pb-green);
      }
      .member-grid {
        margin-top: 14px;
      }
      .collection-link {
        margin-top: 10px;
      }
      .group-empty {
        font-size: 13px;
        padding: 16px 0 6px;
      }
      .section-title {
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 0 0 16px;
      }
      .section-title h2 {
        margin: 0;
      }
      .section-title span {
        font-size: 12px;
        color: var(--pb-muted);
      }
      .area-section + .area-section {
        margin-top: 30px;
      }
      .feedback {
        padding: 18px 0 0;
      }
      .offline {
        font-size: 13px;
      }
      @media (max-width: 600px) {
        main {
          padding: 24px 16px 32px;
        }
        .toolbar {
          padding: 8px 12px;
        }
        .counts {
          grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .controls {
          align-items: stretch;
          gap: 12px;
        }
        nav {
          width: 100%;
        }
        nav button {
          flex: 1;
        }
        .collection-card {
          padding: 16px;
        }
        .collection-images img {
          width: 48px;
        }
        .collection-images {
          min-width: 65px;
        }
        .plant {
          padding: 16px;
        }
      }
    `,
  ];
}
