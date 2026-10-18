import { css } from "lit";
export const styles = css`
  :host {
    container-type: inline-size;
    display: block;
    color: var(--primary-text-color, #263b31);
    font-family: var(--paper-font-body1_-_font-family, inherit);
    --pb-green: var(--success-color, #397656);
    --pb-line: var(--divider-color, #dfe6df);
    --pb-muted: var(--secondary-text-color, #66756c);
    --pb-surface: var(--card-background-color, #fff);
  }
  * {
    box-sizing: border-box;
  }
  ha-card {
    display: block;
    overflow: hidden;
    border-radius: var(--ha-card-border-radius, 18px);
    background: var(--ha-card-background, var(--pb-surface));
    border: var(--ha-card-border-width, 1px) solid
      var(--ha-card-border-color, var(--pb-line));
    box-shadow: var(--ha-card-box-shadow, none);
  }
  .header {
    padding: 22px 22px 14px;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 7px;
    color: var(--pb-muted);
    font-size: 11px;
    font-weight: 650;
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }
  .brand::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--pb-green);
  }
  h2 {
    font-size: 23px;
    line-height: 1.25;
    font-weight: 550;
    margin: 9px 0 0;
    letter-spacing: -0.025em;
    overflow-wrap: anywhere;
  }
  h3 {
    font-size: 18px;
    line-height: 1.3;
    font-weight: 600;
    margin: 0;
    overflow-wrap: anywhere;
  }
  p {
    margin: 8px 0 0;
    line-height: 1.5;
    color: var(--pb-muted);
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 290px), 1fr));
    gap: 12px;
    padding: 0 14px 14px;
  }
  .single {
    padding: 0 8px 8px;
  }
  .plant {
    padding: 16px;
    min-width: 0;
    border: 1px solid var(--pb-line);
    border-radius: 14px;
    background: var(--pb-surface);
  }
  .single .plant {
    border: 0;
    padding: 8px 14px 14px;
  }
  .plant-top {
    display: grid;
    grid-template-columns: 78px minmax(0, 1fr);
    align-items: center;
    gap: 16px;
  }
  .illustration {
    width: 78px;
    height: 94px;
    object-fit: contain;
    border-radius: 14px;
    background: color-mix(in srgb, var(--pb-green) 7%, var(--pb-surface));
  }
  .plant-group {
    font-size: 12px;
    margin: 4px 0 8px;
    overflow-wrap: anywhere;
  }
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    border-radius: 20px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: 600;
    line-height: 1.3;
    background: color-mix(in srgb, var(--pb-green) 10%, var(--pb-surface));
    color: var(--pb-green);
  }
  .badge.due {
    color: var(--warning-color, #a66413);
    background: color-mix(
      in srgb,
      var(--warning-color, #a66413) 12%,
      var(--pb-surface)
    );
  }
  .badge.overdue {
    color: var(--error-color, #b94c42);
    background: color-mix(
      in srgb,
      var(--error-color, #b94c42) 10%,
      var(--pb-surface)
    );
  }
  .badge.paused,
  .badge.unavailable {
    color: var(--pb-muted);
    background: var(--secondary-background-color, #f0f2ef);
  }
  .chips {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin: 14px 0;
  }
  .chip {
    min-width: 0;
    padding: 9px 10px;
    border: 1px solid var(--pb-line);
    border-radius: 10px;
  }
  .chip-label {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: var(--pb-muted);
  }
  .chip-value {
    display: block;
    margin-top: 4px;
    font-size: 12px;
    font-weight: 550;
    overflow-wrap: anywhere;
  }
  .chip.active {
    border-color: color-mix(
      in srgb,
      var(--warning-color, #a66413) 40%,
      var(--pb-line)
    );
  }
  .actions {
    display: flex;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 6px;
  }
  button,
  summary {
    font: inherit;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
  }
  button {
    min-height: 44px;
    border: 1px solid var(--pb-line);
    border-radius: 10px;
    padding: 8px 10px;
    background: var(--pb-surface);
    color: var(--primary-text-color, #263b31);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    font-size: 12px;
  }
  button:hover,
  summary:hover {
    background: var(--secondary-background-color, #f0f2ef);
  }
  button.primary {
    color: var(--pb-green);
    background: color-mix(in srgb, var(--pb-green) 7%, var(--pb-surface));
    border-color: color-mix(in srgb, var(--pb-green) 25%, var(--pb-line));
  }
  button:disabled {
    cursor: default;
    opacity: 0.45;
  }
  button:focus-visible,
  summary:focus-visible,
  input:focus-visible,
  select:focus-visible {
    outline: 2px solid var(--primary-color, #397656);
    outline-offset: 3px;
  }
  details {
    position: relative;
  }
  summary {
    list-style: none;
    min-height: 44px;
    min-width: 44px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--pb-line);
    border-radius: 10px;
    color: var(--pb-muted);
  }
  summary::-webkit-details-marker {
    display: none;
  }
  .snooze-menu {
    display: flex;
    flex-direction: column;
    gap: 5px;
    padding-top: 6px;
    min-width: 140px;
  }
  details[open] {
    flex-basis: 100%;
  }
  details[open] summary {
    max-width: 44px;
  }
  .counts {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    padding: 0 22px 20px;
  }
  .count {
    padding: 13px 10px;
    border-radius: 12px;
    background: var(--secondary-background-color, #f2f5f1);
    min-width: 0;
  }
  .count strong {
    display: block;
    margin-top: 7px;
    font-size: 28px;
    font-weight: 550;
    line-height: 1.1;
  }
  .count span {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: var(--pb-muted);
    overflow-wrap: anywhere;
  }
  .count.water {
    background: color-mix(
      in srgb,
      var(--info-color, #3a7c97) 9%,
      var(--pb-surface)
    );
  }
  .count.fertilize {
    background: color-mix(in srgb, var(--pb-green) 9%, var(--pb-surface));
  }
  .count.overdue {
    background: color-mix(
      in srgb,
      var(--error-color, #b94c42) 8%,
      var(--pb-surface)
    );
  }
  .overview-list {
    border-top: 1px solid var(--pb-line);
    padding: 14px;
    display: grid;
    gap: 10px;
  }
  .empty {
    padding: 24px 22px 32px;
    text-align: center;
  }
  .empty img {
    display: block;
    width: 100px;
    height: 114px;
    object-fit: contain;
    margin: 0 auto 14px;
  }
  .empty h3 {
    font-size: 17px;
  }
  .empty p {
    font-size: 13px;
  }
  .feedback {
    padding: 0 22px 12px;
    font-size: 12px;
  }
  .feedback:empty {
    display: none;
  }
  .error {
    color: var(--error-color, #b94c42);
  }
  svg {
    width: 16px;
    height: 16px;
    flex-shrink: 0;
  }
  label {
    display: block;
    font-size: 13px;
    margin: 16px 0 6px;
  }
  input[type="text"],
  select {
    display: block;
    width: 100%;
    min-height: 46px;
    border: 1px solid var(--pb-line);
    border-radius: 10px;
    padding: 10px;
    font: inherit;
    color: inherit;
    background: var(--pb-surface);
  }
  .check {
    display: flex;
    gap: 10px;
    align-items: center;
    min-height: 44px;
  }
  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: var(--pb-green);
  }
  .editor {
    padding: 4px 0 12px;
  }
  @container (min-width:500px) {
    .counts {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }
  @media (prefers-reduced-motion: no-preference) {
    button,
    summary {
      transition: background 0.12s;
    }
  }
`;
