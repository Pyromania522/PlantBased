import { PlantBasedCard, PlantBasedOverviewCard } from "./cards";
import { PlantBasedEditor, PlantBasedOverviewEditor } from "./editor";
import { PlantBasedPanel } from "./panel";
import { PlantBasedCreateDialog } from "./create-dialog";

for (const [name, implementation] of [
  ["plantbased-card", PlantBasedCard],
  ["plantbased-overview-card", PlantBasedOverviewCard],
  ["plantbased-card-editor", PlantBasedEditor],
  ["plantbased-overview-card-editor", PlantBasedOverviewEditor],
  ["plantbased-panel", PlantBasedPanel],
  ["plantbased-create-dialog", PlantBasedCreateDialog],
] as const) {
  if (!customElements.get(name)) customElements.define(name, implementation);
}
const catalogWindow = window as Window & {
  customCards?: {
    type: string;
    name: string;
    description?: string;
    preview?: boolean;
    documentationURL?: string;
  }[];
};
catalogWindow.customCards ??= [];
for (const [type, name, description] of [
  ["plantbased-card", "PlantBased", "Pflanzenpflege · Plant care"],
  [
    "plantbased-overview-card",
    "PlantBased Overview / Übersicht",
    "Pflanzenübersicht · Plant overview",
  ],
]) {
  if (!catalogWindow.customCards.some((card) => card.type === type))
    catalogWindow.customCards.push({
      type,
      name,
      description,
      preview: true,
      documentationURL: "https://github.com/Pyromania522/PlantBased",
    });
}
