"""Constants for Eufy X10 Pro Omni Debugging integration."""

DOMAIN = "eufy_x10_debugging"
CONF_USERNAME = "username"
CONF_PASSWORD = "password" 
CONF_DEVICE_ID = "device_id"
CONF_DEBUG_MODE = "debug_mode"

# Update interval in seconds
UPDATE_INTERVAL = 10

# Data keys we want to monitor based on research
MONITORED_KEYS = [
    "163",  # Battery (NEW Android App - 100% accuracy)
    "167",  # Water tank data (Key 167, Byte 4 - 82% accuracy)
    "177",  # Alternative water tank source
    "178",  # Real-time data source
    "168",  # Accessories status
    "153",  # Work status/mode
    "152",  # Play/pause commands
    "158",  # Clean speed settings
    "154",  # Cleaning parameters
    "155",  # Direction controls
    "160",  # Find robot
    "173",  # Go home commands
]

# Clean speed mappings
CLEAN_SPEED_NAMES = ["quiet", "standard", "turbo", "max"]

# Work status mappings
WORK_STATUS_MAP = {
    0: "standby",
    1: "sleep", 
    2: "fault",
    3: "charging",
    4: "fast_mapping",
    5: "cleaning",
    6: "remote_ctrl",
    7: "go_home",
    8: "cruising"
}