import {
  LitElement,
  html,
  svg,
  nothing,
  type PropertyValues,
  type CSSResultGroup,
  type TemplateResult,
} from "lit";
import { dayText, t, type TextKey } from "./localize";
import {
  deviceName,
  entityKey,
  overviewCounts,
  plants,
  presetUrl,
  validateConfig,
} from "./model";
import { RegistryController } from "./registry";
import { styles } from "./styles";
import type { CardConfig, HomeAssistant, Plant } from "./types";

export const icon = (kind: "water" | "leaf" | "clock" | "plants") =>
  html`<svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.7"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    ${kind === "water" ? svg`<path d="M12 3C9 7 5 11 5 15a7 7 0 0 0 14 0c0-4-4-8-7-12Z"/><path d="M8 15a4 4 0 0 0 4 4"/>` : kind === "leaf" ? svg`<path d="M5 20 17 8M5 16C2 6 12 3 21 3c0 9-3 19-13 16"/>` : kind === "clock" ? svg`<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>` : svg`<path d="M7 15h10l-1 6H8l-1-6ZM12 15V6M12 11C4 12 4 5 4 4c6-1 8 3 8 7ZM12 9c0-5 4-6 8-6 0 5-3 8-8 6Z"/>`}
  </svg>`;

export abstract class PlantBasedBase extends LitElement {
  static properties = {
    hass: { attribute: false },
    _config: { state: true },
    _message: { state: true },
    _error: { state: true },
  };
  static styles: CSSResultGroup = styles;
  declare hass?: HomeAssistant;
  protected _config?: CardConfig;
  protected _message = "";
  protected _error = false;
  protected pending = new Set<string>();
  protected registry = new RegistryController(this, this.includeAreas);
  protected get includeAreas() {
    return false;
  }
  protected abstract overview: boolean;
  setConfig(config: CardConfig) {
    this._config = validateConfig(config, this.overview, this.hass);
  }
  protected willUpdate(changed: PropertyValues) {
    if (changed.has("hass")) this.registry.setHass(this.hass);
  }
  getCardSize() {
    return this.overview ? 5 : 4;
  }
  getGridOptions() {
    return { columns: 12, min_columns: 6, min_rows: 3 };
  }
  protected renderStatus() {
    if (this.registry.error)
      return html`<div class="empty" role="alert">
        <p>${t(this.hass, "registryError")}</p>
        <button @click=${() => this.registry.refresh()}>
          ${t(this.hass, "retry")}
        </button>
      </div>`;
    if (!this.hass || !this.registry.data)
      return html`<div class="empty" role="status">
        ${t(this.hass, "loading")}
      </div>`;
    return nothing;
  }
  protected feedback() {
    return html`<div
      class="feedback ${this._error ? "error" : ""}"
      role=${this._error ? "alert" : "status"}
      aria-live="polite"
    >
      ${this._message}
    </div>`;
  }
  private async act(plant: Plant, service: string, care?: string) {
    if (!this.hass || !plant.available || this.pending.has(plant.deviceId))
      return;
    this.pending.add(plant.deviceId);
    this._message = "";
    this.requestUpdate();
    try {
      await this.hass.callService(
        "plantbased",
        service,
        care ? { care_type: care, days: 1 } : {},
        { device_id: plant.deviceId },
        false,
      );
      this._message = t(this.hass, "saved");
      this._error = false;
    } catch {
      this._message = t(this.hass, "actionError");
      this._error = true;
    } finally {
      this.pending.delete(plant.deviceId);
      this.requestUpdate();
    }
  }
  protected plantLinks(_plant: Plant): TemplateResult | typeof nothing {
    return nothing;
  }
  protected row(plant: Plant) {
    const disabled = this.pending.has(plant.deviceId) || !plant.available;
    const paused = plant.tone === "paused";
    return html`<article
      class="plant"
      data-device=${plant.deviceId}
      aria-label=${plant.name}
    >
      <div class="plant-top">
        <img
          class="illustration"
          src=${plant.image}
          alt=""
          loading="lazy"
          referrerpolicy="no-referrer"
          @error=${(event: Event) => {
            const image = event.currentTarget as HTMLImageElement;
            const fallback = presetUrl(plant.preset);
            if (image.src !== fallback) image.src = fallback;
          }}
        />
        <div>
          <h3>${plant.name}</h3>
          ${plant.group ? html`<p class="plant-group">${plant.group}</p>` : nothing}<span
            class="badge ${plant.tone}"
            >${t(this.hass, plant.tone as TextKey)}</span
          >
        </div>
      </div>
      <div class="chips">
        <div class="chip ${plant.waterDue && !paused ? "active" : ""}">
          <span class="chip-label"
            >${icon("water")}${t(this.hass, "water")}</span
          ><span class="chip-value"
            >${dayText(this.hass, plant.available ? plant.waterDays : null)}</span
          >
        </div>
        <div class="chip ${plant.fertilizerDue && !paused ? "active" : ""}">
          <span class="chip-label"
            >${icon("leaf")}${t(this.hass, "fertilize")}</span
          ><span class="chip-value"
            >${!plant.fertilizingEnabled ? t(this.hass, "disabled") : dayText(this.hass, plant.available ? plant.fertilizerDays : null)}</span
          >
        </div>
      </div>
      ${
        this._config?.show_actions === false
          ? nothing
          : html`<div class="actions">
              <button
                class="primary"
                ?disabled=${disabled}
                @click=${() => this.act(plant, "mark_watered")}
              >
                ${icon("water")}${t(this.hass, "watered")}
              </button>
              <button
                ?disabled=${disabled || !plant.fertilizingEnabled}
                @click=${() => this.act(plant, "mark_fertilized")}
              >
                ${icon("leaf")}${t(this.hass, "fertilized")}
              </button>
              ${
                disabled
                  ? html`<button disabled aria-label=${t(this.hass, "snooze")}>
                      ${icon("clock")}
                    </button>`
                  : html`<details>
                      <summary
                        aria-label=${t(this.hass, "snooze")}
                        title=${t(this.hass, "snooze")}
                      >
                        ${icon("clock")}
                      </summary>
                      <div class="snooze-menu">
                        <button
                          @click=${() => this.act(plant, "snooze", "water")}
                        >
                          ${t(this.hass, "snoozeWater")}</button
                        >${plant.fertilizingEnabled ? html`<button @click=${() => this.act(plant, "snooze", "fertilize")}>${t(this.hass, "snoozeFertilizer")}</button>` : nothing}
                      </div>
                    </details>`
              }
            </div>`
      }
      ${this.plantLinks(plant)}
    </article>`;
  }
  protected empty(title: TextKey, hint: TextKey) {
    return html`<div class="empty">
      <img src=${presetUrl("generic")} alt="" />
      <h3>${t(this.hass, title)}</h3>
      <p>${t(this.hass, hint)}</p>
    </div>`;
  }
}

export class PlantBasedCard extends PlantBasedBase {
  protected overview = false;
  static getConfigElement() {
    return document.createElement("plantbased-card-editor");
  }
  static getStubConfig(hass?: HomeAssistant) {
    const device = Object.values(hass?.devices ?? {}).find(
      (device) =>
        ["Plant", "Group"].includes(device.model ?? "") &&
        device.identifiers.some(([domain]) => domain === "plantbased"),
    );
    return { device_id: device?.id ?? "", show_actions: true };
  }
  render() {
    if (!this.hass || !this.registry.data || this.registry.error)
      return html`<ha-card>${this.renderStatus()}</ha-card>`;
    const data = this.registry.data;
    const device = data.devices.find(
      (device) =>
        device.id === this._config?.device_id &&
        ["Plant", "Group"].includes(device.model ?? ""),
    );
    if (!device)
      return html`<ha-card
        >${this.empty(this._config?.device_id ? "missingDevice" : "chooseDevice", "noDevices")}</ha-card
      >`;
    const group = device.model === "Group";
    const subentryId = data.entities.find(
      (entry) => entry.device_id === device.id && entry.config_subentry_id,
    )?.config_subentry_id;
    const members = plants(this.hass, data).filter((plant) =>
      group ? plant.groupId === subentryId : plant.deviceId === device.id,
    );
    return html`<ha-card
      ><header class="header">
        <div class="brand">PlantBased</div>
        ${this._config?.title || group ? html`<h2>${this._config?.title || deviceName(device)}</h2>` : nothing}${group ? html`<p>${members.length} ${t(this.hass, members.length === 1 ? "plant" : "plants")}</p>` : nothing}
      </header>
      ${members.length ? html`<div class=${group ? "grid" : "single"}>${members.map((plant) => this.row(plant))}</div>` : html`<div class="empty"><p>${t(this.hass, "groupEmpty")}</p></div>`}${this.feedback()}</ha-card
    >`;
  }
}

export class PlantBasedOverviewCard extends PlantBasedBase {
  protected overview = true;
  static getConfigElement() {
    return document.createElement("plantbased-overview-card-editor");
  }
  static getStubConfig() {
    return { show_actions: true };
  }
  render() {
    if (!this.hass || !this.registry.data || this.registry.error)
      return html`<ha-card>${this.renderStatus()}</ha-card>`;
    const all = plants(this.hass, this.registry.data);
    const due = all
      .filter((plant) => plant.waterDue || plant.fertilizerDue)
      .sort(
        (a, b) =>
          Number(b.tone === "overdue") - Number(a.tone === "overdue") ||
          a.name.localeCompare(b.name),
      );
    const counts = overviewCounts(this.hass, this.registry.data);
    const keys: TextKey[] = ["total", "water", "fertilize", "overdue"];
    const icons = ["plants", "water", "leaf", "clock"] as const;
    // Check registry ownership, rather than a hard-coded overview entity ID.
    const hasHub = this.registry.data.entities.some(
      (entry) =>
        !entry.config_subentry_id && entityKey(entry) === "total_plants",
    );
    return html`<ha-card
      ><header class="header">
        <div class="brand">PlantBased</div>
        <h2>${this._config?.title || t(this.hass, "overview")}</h2>
      </header>
      <div class="counts">
        ${keys.map((key, index) => html`<div class="count ${key}" aria-label=${t(this.hass, key)}><span>${icon(icons[index])}${t(this.hass, key)}</span><strong>${counts[index] ?? "—"}</strong></div>`)}
      </div>
      ${!all.length ? this.empty("noPlants", "noPlantsHint") : !hasHub || counts.some((count) => count === null) ? html`<div class="empty"><p>${t(this.hass, "unavailable")}</p></div>` : due.length ? html`<div class="overview-list">${due.map((plant) => this.row(plant))}</div>` : this.empty("allDone", "allDoneHint")}${this.feedback()}</ha-card
    >`;
  }
}
