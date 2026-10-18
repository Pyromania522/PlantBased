import { LitElement, html, nothing, type PropertyValues } from "lit";
import { t } from "./localize";
import { deviceName } from "./model";
import { RegistryController } from "./registry";
import { styles } from "./styles";
import type { CardConfig, HomeAssistant } from "./types";

export class PlantBasedEditor extends LitElement {
  static properties = { hass: { attribute: false }, _config: { state: true } };
  static styles = styles;
  declare hass?: HomeAssistant;
  protected _config: CardConfig = { type: "custom:plantbased-card" };
  protected overview = false;
  private registry = new RegistryController(this);
  setConfig(config: CardConfig) {
    this._config = { ...config };
  }
  protected willUpdate(changed: PropertyValues) {
    if (changed.has("hass")) this.registry.setHass(this.hass);
  }
  private change(key: keyof CardConfig, value: unknown) {
    const config = { ...this._config, [key]: value };
    if (key === "title" && !value) delete config.title;
    this._config = config;
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config },
        bubbles: true,
        composed: true,
      }),
    );
  }
  render() {
    const devices =
      this.registry.data?.devices
        .filter((device) => ["Plant", "Group"].includes(device.model ?? ""))
        .sort((a, b) => deviceName(a).localeCompare(deviceName(b))) ?? [];
    const missing =
      this._config.device_id &&
      !devices.some((device) => device.id === this._config.device_id);
    return html`<div class="editor">
      ${
        !this.overview
          ? html`<label for="device">${t(this.hass, "chooseDevice")}</label
              ><select
                id="device"
                .value=${this._config.device_id || ""}
                @change=${(event: Event) => this.change("device_id", (event.currentTarget as HTMLSelectElement).value)}
              >
                <option value="">${t(this.hass, "chooseDevice")}</option>
                ${missing ? html`<option value=${this._config.device_id}>${t(this.hass, "unavailable")}</option>` : nothing}${devices.map((device) => html`<option value=${device.id}>${deviceName(device)} · ${t(this.hass, device.model === "Plant" ? "plant" : "group")}</option>`)}</select
              >${!devices.length ? html`<p>${t(this.hass, this.registry.data ? "noDevices" : "loading")}</p>` : nothing}${
                this.registry.error
                  ? html`<p role="alert">${t(this.hass, "registryError")}</p>
                      <button @click=${() => this.registry.refresh()}>
                        ${t(this.hass, "retry")}
                      </button>`
                  : nothing
              }`
          : nothing
      } <label for="title">${t(this.hass, "title")}</label
      ><input
        id="title"
        type="text"
        placeholder=${t(this.hass, "titleHint")}
        .value=${this._config.title ?? ""}
        @input=${(event: Event) => this.change("title", (event.currentTarget as HTMLInputElement).value)}
      />
      <label class="check"
        ><input
          type="checkbox"
          .checked=${this._config.show_actions !== false}
          @change=${(event: Event) => this.change("show_actions", (event.currentTarget as HTMLInputElement).checked)}
        />${t(this.hass, "showActions")}</label
      >
    </div>`;
  }
}
export class PlantBasedOverviewEditor extends PlantBasedEditor {
  protected overview = true;
}
