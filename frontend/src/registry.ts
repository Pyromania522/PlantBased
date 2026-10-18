import type { ReactiveController, ReactiveControllerHost } from "lit";
import type {
  HAConnection,
  HomeAssistant,
  RegistryData,
  EntityEntry,
  DeviceEntry,
} from "./types";

export class RegistryController implements ReactiveController {
  data?: RegistryData;
  error = false;
  private hass?: HomeAssistant;
  private connection?: HAConnection;
  private connected = false;
  private generation = 0;
  private unsubs: (() => void)[] = [];
  private loading = false;
  private dirty = false;
  constructor(private host: ReactiveControllerHost) {
    host.addController(this);
  }
  hostConnected() {
    this.connected = true;
    this.attach();
  }
  hostDisconnected() {
    this.connected = false;
    this.detach();
  }
  setHass(hass?: HomeAssistant) {
    this.hass = hass;
    if (hass?.connection !== this.connection) {
      this.detach();
      this.data = undefined;
      this.error = false;
      this.attach();
    }
  }
  private onReady = () => {
    void this.refresh();
  };
  private attach() {
    if (!this.connected || !this.hass || this.connection) return;
    const connection = (this.connection = this.hass.connection);
    const generation = this.generation;
    connection.addEventListener("ready", this.onReady);
    for (const type of ["entity_registry_updated", "device_registry_updated"]) {
      void connection
        .subscribeEvents(this.onReady, type)
        .then((unsub) => {
          if (generation !== this.generation) unsub();
          else this.unsubs.push(unsub);
        })
        .catch(() => {
          if (generation === this.generation) {
            this.error = true;
            this.host.requestUpdate();
          }
        });
    }
    void this.refresh();
  }
  private detach() {
    this.generation++;
    this.connection?.removeEventListener("ready", this.onReady);
    this.connection = undefined;
    this.unsubs.splice(0).forEach((unsub) => unsub());
    this.loading = false;
    this.dirty = false;
  }
  async refresh() {
    if (!this.hass || !this.connected) return;
    if (this.loading) {
      this.dirty = true;
      return;
    }
    const generation = this.generation;
    this.loading = true;
    try {
      const [entities, devices] = await Promise.all([
        this.hass.callWS<EntityEntry[]>({
          type: "config/entity_registry/list",
        }),
        this.hass.callWS<DeviceEntry[]>({
          type: "config/device_registry/list",
        }),
      ]);
      if (generation !== this.generation) return;
      this.data = {
        entities: entities.filter((entry) => entry.platform === "plantbased"),
        devices: devices.filter((device) =>
          device.identifiers.some(([domain]) => domain === "plantbased"),
        ),
      };
      this.error = false;
    } catch {
      if (generation === this.generation) this.error = true;
    } finally {
      if (generation === this.generation) {
        this.loading = false;
        this.host.requestUpdate();
        if (this.dirty) {
          this.dirty = false;
          void this.refresh();
        }
      }
    }
  }
}
