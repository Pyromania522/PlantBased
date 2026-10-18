"""Constants for PlantBased."""

DOMAIN = "plantbased"
NAME = "PlantBased"
STORAGE_VERSION = 1
HISTORY_LIMIT = 10
CARE_TYPES = ("water", "fertilize")
NO_GROUP = "none"
# Keep the automatic HA room dashboard focused on status and two countdowns.
HIDDEN_PLANT_ENTITY_KEYS = frozenset(
    {
        "needs_water",
        "needs_fertilizer",
        "mark_watered",
        "mark_fertilized",
        "snooze_watering",
        "snooze_fertilizing",
        "last_watered",
        "last_fertilized",
        "next_watering",
        "next_fertilizing",
    }
)
IMAGE_PRESETS = (
    "generic",
    "monstera",
    "ficus",
    "pothos",
    "snake_plant",
    "succulent",
    "cactus",
    "fern",
    "orchid",
    "herb",
    "palm",
    "hanging_plant",
)
