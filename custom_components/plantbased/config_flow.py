"""UI-only configuration for the single PlantBased hub."""

from datetime import date
from typing import Any
from urllib.parse import urlsplit

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.core import callback
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import selector
from homeassistant.util import dt as dt_util

from .areas import (
    async_change_group_area,
    inherited_area,
    plant_area,
)
from .const import DOMAIN, IMAGE_PRESETS, NAME, NO_GROUP
from .registry import device_for_subentry
from .reminder_options import ReminderOptions, available_targets
from .schema import schema as vol


class PlantBasedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Create one local hub after explicit confirmation."""

    VERSION = 1
    MINOR_VERSION = 2

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return PlantBasedOptionsFlow()

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Expose Add plant/Add group on HA's integration card."""
        return {"plant": PlantSubentryFlow, "group": GroupSubentryFlow}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm setup without requesting sensors, accounts, or credentials."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(title=NAME, data={})

        return self.async_show_form(step_id="user")


class PlantBasedOptionsFlow(OptionsFlow):
    """Configure reminders without a second reload listener or YAML."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        choices = available_targets(self.hass)
        available = {choice["value"] for choice in choices}
        errors: dict[str, str] = {}
        if user_input is not None:
            options = ReminderOptions.from_data(user_input)
            if any(target not in available for target in options.targets):
                errors["notify_targets"] = "invalid_target"
            elif options.enabled and not (options.targets or options.persistent):
                errors["base"] = "target_required"
            elif options.at.tzinfo is not None:
                errors["reminder_time"] = "local_time_required"
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        **user_input,
                        "reminder_time": options.at.isoformat(),
                        "notify_targets": list(options.targets),
                    },
                )
        defaults = dict(self.config_entry.options)
        if user_input is not None:
            defaults.update(user_input)
        # Keep stale values visible so users can remove a disappeared target.
        for target in defaults.get("notify_targets", []):
            if target not in available:
                choices.append({"value": target, "label": target.partition(":")[2]})
        fields: dict[Any, Any] = {}
        for key, default in (
            ("reminder_enabled", False),
            ("repeat_daily", True),
            ("persistent_notification", False),
            ("snooze_action", True),
        ):
            fields[vol.Required(key, default=defaults.get(key, default))] = (
                selector.BooleanSelector()
            )
        fields[
            vol.Required(
                "reminder_time", default=defaults.get("reminder_time", "09:00:00")
            )
        ] = selector.TimeSelector()
        fields[
            vol.Required("notify_targets", default=defaults.get("notify_targets", []))
        ] = selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=choices,
                multiple=True,
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        )
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(fields), errors=errors
        )


class CareSubentryFlow(ConfigSubentryFlow):
    """Shared validated, UI-only create/reconfigure lifecycle."""

    kind = "group"

    def _schema(self, reconfigure: bool) -> vol.Schema:
        defaults = dict(self._get_reconfigure_subentry().data) if reconfigure else {}
        if reconfigure and (
            self.kind == "group"
            or not inherited_area(self.hass, self._get_entry(), defaults)
        ):
            subentry = self._get_reconfigure_subentry()
            if device := device_for_subentry(
                self.hass, self._get_entry().entry_id, subentry.subentry_id
            ):
                defaults["area"] = device.area_id
        fields: dict[Any, Any] = {
            vol.Required(
                "name", default=defaults.get("name", "")
            ): selector.TextSelector(),
            vol.Optional(
                "area", description={"suggested_value": defaults.get("area")}
            ): selector.AreaSelector(),
            vol.Required(
                "image_preset", default=defaults.get("image_preset", "generic")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(IMAGE_PRESETS),
                    translation_key="image_preset",
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
        }
        if self.kind == "plant":
            groups: list[selector.SelectOptionDict] = [
                {"value": NO_GROUP, "label": "No group"}
            ]
            groups.extend(
                {"value": key, "label": sub.title}
                for key, sub in self._get_entry().subentries.items()
                if sub.subentry_type == "group"
            )
            fields[
                vol.Optional(
                    "group",
                    description={"suggested_value": defaults.get("group") or NO_GROUP},
                )
            ] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=groups,
                    translation_key="plant_group",
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            )
            for key in ("species", "notes", "location_note", "image_url"):
                fields[
                    vol.Optional(
                        key, description={"suggested_value": defaults.get(key, "")}
                    )
                ] = selector.TextSelector(
                    selector.TextSelectorConfig(multiline=key == "notes")
                )
            for key, default in (
                ("watering_interval", 7),
                ("fertilizing_interval", 28),
            ):
                fields[vol.Required(key, default=defaults.get(key, default))] = (
                    selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=365, step=1, mode=selector.NumberSelectorMode.BOX
                        )
                    )
                )
            for key, default in (
                ("adaptive_watering", False),
                ("fertilizing_enabled", True),
                ("all_year", False),
            ):
                fields[vol.Required(key, default=defaults.get(key, default))] = (
                    selector.BooleanSelector()
                )
            for key, default in (("season_start", 3), ("season_end", 9)):
                fields[vol.Required(key, default=str(defaults.get(key, default)))] = (
                    selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[str(month) for month in range(1, 13)],
                            translation_key="month",
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    )
                )
            if not reconfigure:
                for key in ("initial_last_watered", "initial_last_fertilized"):
                    fields[
                        vol.Required(key, default=dt_util.now().date().isoformat())
                    ] = selector.DateSelector()
        return vol.Schema(fields)

    def _validate(
        self, user_input: dict[str, Any], reconfigure: bool
    ) -> tuple[dict[str, Any], dict[str, str]]:
        # HA validates the displayed schema before invoking the step. Validate
        # live references here too: an area/group may have disappeared meanwhile.
        data = dict(user_input)
        data["name"] = data["name"].strip()
        data["area"] = data.get("area") or None
        if not data["name"]:
            return data, {"name": "name_required"}
        if area_id := data.get("area"):
            if ar.async_get(self.hass).async_get_area(area_id) is None:
                return data, {"area": "invalid_area"}
        if self.kind == "plant":
            for key in ("species", "notes", "location_note", "image_url"):
                data.setdefault(key, "")
            data["group"] = (
                None if data.get("group") == NO_GROUP else data.get("group") or None
            )
            group = self._get_entry().subentries.get(data["group"])
            if data["group"] and (group is None or group.subentry_type != "group"):
                return data, {"group": "invalid_group"}
            for key in ("watering_interval", "fertilizing_interval"):
                if not float(data[key]).is_integer():
                    return data, {key: "invalid_interval"}
                data[key] = int(data[key])
            for key in ("season_start", "season_end"):
                data[key] = int(data[key])
            image = data.get("image_url", "").strip()
            try:
                url = urlsplit(image)
                valid_image = (
                    not image
                    or (
                        image.startswith("/local/")
                        and not url.scheme
                        and not url.netloc
                    )
                    or (
                        url.scheme in ("http", "https")
                        and bool(url.hostname)
                        and not url.username
                        and not url.password
                    )
                )
            except ValueError:
                valid_image = False
            if not valid_image:
                return data, {"image_url": "invalid_image"}
            data["image_url"] = image
            if not reconfigure:
                for key in ("initial_last_watered", "initial_last_fertilized"):
                    if date.fromisoformat(data[key]) > dt_util.now().date():
                        return data, {key: "future_date"}
        return data, {}

    async def _async_step(
        self, user_input: dict[str, Any] | None, reconfigure: bool
    ) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            data, errors = self._validate(user_input, reconfigure)
            if not errors:
                if not reconfigure:
                    return self.async_create_entry(title=data["name"], data=data)
                entry, subentry = self._get_entry(), self._get_reconfigure_subentry()
                update_plant_area = self.kind == "plant" and (
                    subentry.data.get("area") != data.get("area")
                    or subentry.data.get("group") != data.get("group")
                )
                if self.kind == "group" and subentry.data.get("area") != data.get(
                    "area"
                ):
                    async_change_group_area(
                        self.hass, entry, subentry.subentry_id, data.get("area")
                    )
                # Preserve creation-only seeds; editable dates use the date entities.
                result = self.async_update_and_abort(
                    entry,
                    subentry,
                    title=data["name"],
                    data={**subentry.data, **data, "area": data.get("area")},
                )
                if update_plant_area:
                    registry = dr.async_get(self.hass)
                    if device := device_for_subentry(
                        self.hass, entry.entry_id, subentry.subentry_id
                    ):
                        registry.async_update_device(
                            device.id, area_id=plant_area(self.hass, entry, data)
                        )
                return result
        return self.async_show_form(
            step_id="reconfigure" if reconfigure else "user",
            data_schema=self._schema(reconfigure),
            errors=errors,
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add one configured subentry; HA generates its immutable subentry ID."""
        return await self._async_step(user_input, False)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Keep the subentry ID and its runtime history while changing settings."""
        return await self._async_step(user_input, True)


class PlantSubentryFlow(CareSubentryFlow):
    """Create and reconfigure plants."""

    kind = "plant"


class GroupSubentryFlow(CareSubentryFlow):
    """Create and reconfigure groups."""

    kind = "group"
