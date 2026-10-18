import { LitElement, css, html, nothing, type PropertyValues } from "lit";
import { t } from "./localize";
import { styles } from "./styles";
import type { AreaEntry, HomeAssistant } from "./types";

interface Field {
  name: string;
  required?: boolean;
  default?: unknown;
  description?: { suggested_value?: unknown };
  selector: {
    text?: { multiline?: boolean };
    area?: unknown;
    number?: { min?: number; max?: number; step?: number };
    boolean?: unknown;
    date?: unknown;
    select?: {
      options: (string | { value: string; label: string })[];
      translation_key?: string;
    };
  };
}
interface FlowStep {
  type: string;
  flow_id: string;
  step_id?: string;
  data_schema?: Field[];
  errors?: Record<string, string>;
}
const BASE = "config/config_entries/subentries/flow";
const HEADERS = { "HA-Frontend-Base": location.origin };

export class PlantBasedCreateDialog extends LitElement {
  static properties = {
    hass: { attribute: false },
    kind: { type: String },
    areas: { attribute: false },
    _step: { state: true },
    _busy: { state: true },
    _loading: { state: true },
    _error: { state: true },
  };
  declare hass: HomeAssistant;
  declare kind: "plant" | "group";
  areas: AreaEntry[] = [];
  private _step?: FlowStep;
  private _busy = false;
  private _loading = true;
  private _error = "";
  private flowId?: string;
  private values: Record<string, unknown> = {};
  private labels: (key: string) => string = () => "";
  private selectorLabels: (key: string) => string = () => "";

  protected firstUpdated(_changed: PropertyValues) {
    this.renderRoot.querySelector("dialog")!.showModal();
    void this.load();
  }
  disconnectedCallback() {
    super.disconnectedCallback();
    void this.discard();
  }
  private async discard() {
    const id = this.flowId;
    this.flowId = undefined;
    if (id) {
      try {
        await this.hass.callApi("DELETE", `${BASE}/${encodeURIComponent(id)}`);
      } catch {
        /* A completed/expired flow no longer needs cleanup. */
      }
    }
  }
  private close() {
    if (this._busy && !this._loading) return;
    this.dispatchEvent(
      new CustomEvent("closed", { bubbles: true, composed: true }),
    );
  }
  private async load() {
    if (this._busy || !this.hass.user?.is_admin) return;
    this._busy = this._loading = true;
    this._error = "";
    try {
      await this.discard();
      const entries = await this.hass.callWS<
        {
          entry_id: string;
          state: string;
          supported_subentry_types: Record<string, unknown>;
        }[]
      >({ type: "config_entries/get", domain: "plantbased" });
      const entry = entries.find(
        (entry) =>
          entry.state === "loaded" &&
          this.kind in entry.supported_subentry_types,
      );
      if (!entry) throw Error("Hub not loaded");
      if (!this.isConnected) return;
      const step = await this.hass.callApi<FlowStep>(
        "POST",
        BASE,
        { handler: [entry.entry_id, this.kind] },
        HEADERS,
      );
      this.flowId = step.flow_id;
      if (!this.isConnected) {
        await this.discard();
        return;
      }
      this.labels = await this.hass.loadBackendTranslation(
        "config_subentries",
        "plantbased",
      );
      this.selectorLabels = await this.hass.loadBackendTranslation(
        "selector",
        "plantbased",
      );
      if (!this.isConnected) return;
      if (
        step.type !== "form" ||
        !step.data_schema?.every((field) =>
          ["text", "area", "number", "boolean", "date", "select"].some(
            (type) => type in field.selector,
          ),
        )
      )
        throw Error("Unexpected schema");
      this.values = Object.fromEntries(
        step.data_schema.map((field) => [
          field.name,
          field.description?.suggested_value ??
            field.default ??
            ("boolean" in field.selector ? false : ""),
        ]),
      );
      this._step = step;
      this._loading = false;
      this._busy = false;
      await this.updateComplete;
      this.renderRoot
        .querySelector<HTMLInputElement>('input[name="name"]')
        ?.focus();
    } catch {
      this._error = t(this.hass, "createLoadError");
      await this.discard();
    } finally {
      this._busy = false;
    }
  }
  private label(field: Field, part = "data") {
    return (
      this.labels(
        `component.plantbased.config_subentries.${this.kind}.step.${this._step?.step_id ?? "user"}.${part}.${field.name}`,
      ) || (part === "data" ? field.name : "")
    );
  }
  private error(key: string) {
    const error = this._step?.errors?.[key];
    return error
      ? this.labels(
          `component.plantbased.config_subentries.${this.kind}.error.${error}`,
        ) || t(this.hass, "createError")
      : "";
  }
  private field(field: Field) {
    const key = field.name;
    const selector = field.selector;
    const value = this.values[key] ?? "";
    let input;
    if ("boolean" in selector)
      input = html`<input
        id=${key}
        name=${key}
        type="checkbox"
        .checked=${value === true}
      />`;
    else if (selector.select || "area" in selector) {
      const options =
        selector.select?.options ??
        this.areas.map((area) => ({ value: area.area_id, label: area.name }));
      input = html`<select id=${key} name=${key} ?required=${field.required}>
        ${!field.required ? html`<option value="" ?selected=${value === ""}>—</option>` : nothing}
        ${options.map((option) => {
          const optionValue =
            typeof option === "string" ? option : option.value;
          const label = selector.select?.translation_key
            ? this.selectorLabels(
                `component.plantbased.selector.${selector.select.translation_key}.options.${optionValue}`,
              )
            : "";
          return html`<option
            value=${optionValue}
            ?selected=${String(value) === optionValue}
          >
            ${label || (typeof option === "string" ? option : option.label)}
          </option>`;
        })}
      </select>`;
    } else if (selector.text?.multiline)
      input = html`<textarea
        id=${key}
        name=${key}
        .value=${String(value)}
        ?required=${field.required}
      ></textarea>`;
    else
      input = html`<input
        id=${key}
        name=${key}
        type=${"number" in selector ? "number" : "date" in selector ? "date" : "text"}
        .value=${String(value)}
        ?required=${field.required}
        min=${selector.number?.min ?? nothing}
        max=${selector.number?.max ?? nothing}
        step=${selector.number?.step ?? nothing}
      />`;
    const error = this.error(key);
    const helper = this.label(field, "data_description");
    return html`<div class="field ${"boolean" in selector ? "boolean" : ""}">
      <label for=${key}
        >${this.label(field)}${field.required && !("boolean" in selector) ? " *" : ""}</label
      >${input} ${helper ? html`<p class="helper">${helper}</p>` : nothing}
      ${error ? html`<p class="error" role="alert">${error}</p>` : nothing}
    </div>`;
  }
  private async submit(event: SubmitEvent) {
    event.preventDefault();
    if (this._busy || !this.flowId || !this.hass.user?.is_admin) return;
    const data = new FormData(event.currentTarget as HTMLFormElement);
    const values: Record<string, unknown> = {};
    for (const field of this._step?.data_schema ?? []) {
      const raw = data.get(field.name);
      if ("boolean" in field.selector)
        values[field.name] = data.has(field.name);
      else if (raw !== null && raw !== "")
        values[field.name] = "number" in field.selector ? Number(raw) : raw;
      else if (field.required) values[field.name] = "";
    }
    this.values = values;
    this._busy = true;
    this._error = "";
    try {
      const result = await this.hass.callApi<FlowStep>(
        "POST",
        `${BASE}/${encodeURIComponent(this.flowId)}`,
        values,
        HEADERS,
      );
      if (!this.isConnected) return;
      if (result.type === "create_entry") {
        this.flowId = undefined;
        this.dispatchEvent(
          new CustomEvent("created", { bubbles: true, composed: true }),
        );
      } else if (result.type === "form") this._step = result;
      else {
        this.flowId = undefined;
        this._loading = true;
        this._error = t(this.hass, "createError");
      }
    } catch {
      this._error = t(this.hass, "createError");
    } finally {
      this._busy = false;
    }
  }
  render() {
    return html`<dialog
      aria-labelledby="create-title"
      @cancel=${(event: Event) => {
        event.preventDefault();
        this.close();
      }}
    >
      <h2 id="create-title">
        ${t(this.hass, this.kind === "plant" ? "addPlant" : "addGroup")}
      </h2>
      ${this._error ? html`<p class="error" role="alert">${this._error}</p>` : nothing}
      ${
        this._loading
          ? html`<p role="status">
                ${!this._error ? t(this.hass, "loading") : ""}
              </p>
              <div class="dialog-actions">
                ${this._error ? html`<button ?disabled=${this._busy} @click=${() => this.load()}>${t(this.hass, "retry")}</button>` : nothing}<button
                  @click=${() => this.close()}
                >
                  ${t(this.hass, "cancel")}
                </button>
              </div>`
          : html`<form @submit=${this.submit}>
              <fieldset ?disabled=${this._busy}>
                <div class="fields">
                  ${this._step?.data_schema?.map((field) => this.field(field))}
                </div>
                ${this.error("base") ? html`<p class="error" role="alert">${this.error("base")}</p>` : nothing}
              </fieldset>
              <div class="dialog-actions">
                <button
                  type="button"
                  ?disabled=${this._busy}
                  @click=${() => this.close()}
                >
                  ${t(this.hass, "cancel")}</button
                ><button class="primary" type="submit" ?disabled=${this._busy}>
                  ${t(this.hass, "create")}
                </button>
              </div>
            </form>`
      }
    </dialog>`;
  }
  static styles = [
    styles,
    css`
      dialog[open] {
        display: flex;
        flex-direction: column;
      }
      dialog {
        width: min(680px, calc(100vw - 32px));
        max-height: 85vh;
        max-height: 85dvh;
        border: 1px solid var(--pb-line);
        border-radius: 18px;
        padding: 24px;
        background: var(--pb-surface);
        color: var(--primary-text-color, #263b31);
        box-shadow: 0 12px 48px #0003;
        overflow: hidden;
      }
      dialog::backdrop {
        background: #0006;
      }
      h2 {
        margin: 0 0 20px;
        flex-shrink: 0;
      }
      form {
        display: flex;
        flex-direction: column;
        min-height: 0;
      }
      fieldset {
        padding: 0;
        margin: 0;
        border: 0;
        min-width: 0;
        min-height: 0;
        overflow: auto;
        padding: 4px;
      }
      .fields {
        display: grid;
        gap: 16px;
      }
      .field {
        min-width: 0;
      }
      label {
        margin: 0 0 6px;
      }
      input:not([type="checkbox"]),
      textarea,
      select {
        width: 100%;
        min-height: 44px;
        font: inherit;
        padding: 10px;
        border: 1px solid var(--pb-line);
        border-radius: 10px;
        color: inherit;
        background: var(--pb-surface);
      }
      textarea {
        min-height: 80px;
        resize: vertical;
      }
      .helper {
        margin: 5px 0 0;
        font-size: 12px;
      }
      .error {
        margin: 7px 0;
        font-size: 13px;
      }
      .boolean {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
      }
      .boolean label {
        margin: 0;
      }
      .dialog-actions {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-top: 22px;
        flex-shrink: 0;
      }
    `,
  ];
}
