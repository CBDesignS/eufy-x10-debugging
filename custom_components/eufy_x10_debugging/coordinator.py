"""Data update coordinator for Eufy X10 Pro Omni Debugging integration."""
import asyncio
import base64
import json
import logging
import time
from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN, 
    UPDATE_INTERVAL, 
    MONITORED_KEYS, 
    CONF_DEBUG_MODE,
    CLEAN_SPEED_NAMES,
    WORK_STATUS_MAP
)

_LOGGER = logging.getLogger(__name__)


class EufyX10DebugCoordinator(DataUpdateCoordinator):
    """Eufy X10 Debugging data coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.device_id = entry.data["device_id"]
        self.username = entry.data["username"]
        self.password = entry.data["password"]
        self.debug_mode = entry.data.get("debug_mode", True)
        
        # Store raw data for debugging
        self.raw_data: Dict[str, Any] = {}
        self.parsed_data: Dict[str, Any] = {}
        self.last_update: Optional[float] = None
        self.update_count = 0
        
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{self.device_id}",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from Eufy API."""
        try:
            self.update_count += 1
            if self.debug_mode:
                _LOGGER.info("=== EUFY X10 DEBUG UPDATE #%d ===", self.update_count)
            
            # Fetch the raw data
            await self._fetch_eufy_data()
            
            # Process and log the data
            await self._process_data()
            
            self.last_update = time.time()
            return self.parsed_data
            
        except Exception as err:
            _LOGGER.error("Error fetching data from Eufy API: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _fetch_eufy_data(self):
        """
        Mock function to fetch data - REPLACE THIS with actual API calls.
        
        This simulates the REST API response you would get from your Eufy device.
        Replace this entire method with your actual Eufy login and data fetching logic.
        """
        # Mock data that simulates what you'd get from the REST API
        # Based on your research findings
        mock_data = {
            "163": 85,  # Battery percentage (NEW Android App - 100% accuracy)
            "167": "PAo6CgUIABC4AhgEGFRKJw==",  # Water tank data (Key 167, Byte 4)
            "177": "MgowCAEQABgEGlVKFw==",  # Alternative water tank source
            "178": "OAo2CAEQABgEGlVlIw==",  # Real-time data
            "168": "QWNjZXNzb3JpZXMgZGF0YSBoZXJl",  # Accessories status
            "153": 5,  # Work status (5 = cleaning)
            "152": True,  # Play/pause state
            "158": 2,  # Clean speed (2 = turbo)
            "154": "Q2xlYW5pbmcgcGFyYW1ldGVycw==",  # Cleaning parameters
            "155": "RGlyZWN0aW9uIGRhdGE=",  # Direction
            "160": False,  # Find robot
            "173": "R28gaG9tZSBkYXRh",  # Go home
            "timestamp": int(time.time()),
        }
        
        # Simulate some variation in data
        import random
        mock_data["163"] = random.randint(80, 95)  # Battery varies
        mock_data["158"] = random.randint(0, 3)    # Clean speed varies
        
        self.raw_data = mock_data
        
        if self.debug_mode:
            _LOGGER.info("=== EUFY X10 DEBUG: RAW API DATA ===")
            _LOGGER.info("Device ID: %s", self.device_id)
            _LOGGER.info("Raw data keys: %s", list(mock_data.keys()))
            _LOGGER.info("Total keys received: %d", len(mock_data))
            
            for key, value in mock_data.items():
                if isinstance(value, str) and len(value) > 50:
                    _LOGGER.info("Key %s: %s... (truncated)", key, value[:50])
                else:
                    _LOGGER.info("Key %s: %s", key, value)

    async def _process_data(self):
        """Process the raw data and extract useful information."""
        self.parsed_data = {
            "device_id": self.device_id,
            "battery": None,
            "water_tank": None,
            "clean_speed": None,
            "work_status": None,
            "play_pause": None,
            "raw_keys": list(self.raw_data.keys()),
            "monitored_keys_found": [],
            "monitored_keys_missing": [],
            "last_update": time.time(),
            "update_count": self.update_count,
        }
        
        # Check which monitored keys are present/missing
        for key in MONITORED_KEYS:
            if key in self.raw_data:
                self.parsed_data["monitored_keys_found"].append(key)
            else:
                self.parsed_data["monitored_keys_missing"].append(key)
        
        # Process battery (Key 163) - NEW Android App source
        await self._process_battery()
        
        # Process water tank (Key 167, Byte 4) - NEW Android App source  
        await self._process_water_tank()
        
        # Process clean speed (Key 158)
        await self._process_clean_speed()
        
        # Process work status (Key 153)
        await self._process_work_status()
        
        # Process play/pause (Key 152)
        await self._process_play_pause()
        
        # Log summary
        if self.debug_mode:
            _LOGGER.info("=== PROCESSING SUMMARY ===")
            _LOGGER.info("Battery: %s%%", self.parsed_data["battery"])
            _LOGGER.info("Water Tank: %s%%", self.parsed_data["water_tank"])
            _LOGGER.info("Clean Speed: %s", self.parsed_data["clean_speed"])
            _LOGGER.info("Work Status: %s", self.parsed_data["work_status"])
            _LOGGER.info("Keys Found: %s", self.parsed_data["monitored_keys_found"])
            _LOGGER.info("Keys Missing: %s", self.parsed_data["monitored_keys_missing"])

    async def _process_battery(self):
        """Process battery data from Key 163 (NEW Android App)."""
        if "163" not in self.raw_data:
            return
            
        try:
            battery = int(self.raw_data["163"])
            self.parsed_data["battery"] = max(0, min(100, battery))
            
            if self.debug_mode:
                _LOGGER.info("=== BATTERY PROCESSING (NEW ANDROID APP) ===")
                _LOGGER.info("Key 163 Raw Value: %s", self.raw_data["163"])
                _LOGGER.info("Battery Level: %d%%", self.parsed_data["battery"])
                _LOGGER.info("Data Source: Key 163 (100%% accuracy)")
                
        except (ValueError, TypeError) as e:
            _LOGGER.error("Error processing battery data from Key 163: %s", e)

    async def _process_water_tank(self):
        """Process water tank data from Key 167, Byte 4 (NEW Android App)."""
        if "167" not in self.raw_data:
            return
            
        try:
            base64_data = self.raw_data["167"]
            if isinstance(base64_data, str):
                binary_data = base64.b64decode(base64_data)
                
                if self.debug_mode:
                    _LOGGER.info("=== WATER TANK PROCESSING (NEW ANDROID APP) ===")
                    _LOGGER.info("Key 167 Base64: %s", base64_data)
                    _LOGGER.info("Binary length: %d bytes", len(binary_data))
                    _LOGGER.info("Binary hex: %s", binary_data.hex())
                
                if len(binary_data) > 4:
                    raw_value = binary_data[4]  # Byte 4
                    # Using scale 255->100 method (gives 82% for raw 210)
                    water_pct = min(100, int((raw_value * 100) / 255))
                    self.parsed_data["water_tank"] = water_pct
                    
                    if self.debug_mode:
                        _LOGGER.info("Byte 4 raw value: %d (0x%02x)", raw_value, raw_value)
                        _LOGGER.info("Water tank percentage: %d%%", water_pct)
                        _LOGGER.info("Data Source: Key 167 Byte 4 (82%% accuracy)")
                        
        except Exception as e:
            _LOGGER.error("Error processing water tank data from Key 167: %s", e)

    async def _process_clean_speed(self):
        """Process clean speed from Key 158."""
        if "158" not in self.raw_data:
            return
            
        try:
            speed_raw = self.raw_data["158"]
            if isinstance(speed_raw, int) and 0 <= speed_raw < len(CLEAN_SPEED_NAMES):
                speed_name = CLEAN_SPEED_NAMES[speed_raw]
                self.parsed_data["clean_speed"] = speed_name
                
                if self.debug_mode:
                    _LOGGER.info("=== CLEAN SPEED PROCESSING ===")
                    _LOGGER.info("Key 158 raw: %s", speed_raw)
                    _LOGGER.info("Clean speed: %s", speed_name)
                    _LOGGER.info("Available speeds: %s", CLEAN_SPEED_NAMES)
                    
        except Exception as e:
            _LOGGER.error("Error processing clean speed from Key 158: %s", e)

    async def _process_work_status(self):
        """Process work status from Key 153."""
        if "153" not in self.raw_data:
            return
            
        try:
            status_raw = self.raw_data["153"]
            if isinstance(status_raw, int) and status_raw in WORK_STATUS_MAP:
                status_name = WORK_STATUS_MAP[status_raw]
                self.parsed_data["work_status"] = status_name
                
                if self.debug_mode:
                    _LOGGER.info("=== WORK STATUS PROCESSING ===")
                    _LOGGER.info("Key 153 raw: %s", status_raw)
                    _LOGGER.info("Work status: %s", status_name)
                    
        except Exception as e:
            _LOGGER.error("Error processing work status from Key 153: %s", e)

    async def _process_play_pause(self):
        """Process play/pause state from Key 152."""
        if "152" not in self.raw_data:
            return
            
        try:
            play_pause = bool(self.raw_data["152"])
            self.parsed_data["play_pause"] = play_pause
            
            if self.debug_mode:
                _LOGGER.info("=== PLAY/PAUSE PROCESSING ===")
                _LOGGER.info("Key 152 raw: %s", self.raw_data["152"])
                _LOGGER.info("Play/Pause state: %s", "Playing" if play_pause else "Paused")
                
        except Exception as e:
            _LOGGER.error("Error processing play/pause from Key 152: %s", e)

    async def async_shutdown(self):
        """Shutdown the coordinator."""
        if self.debug_mode:
            _LOGGER.info("=== EUFY X10 DEBUG COORDINATOR SHUTDOWN ===")
            _LOGGER.info("Total updates processed: %d", self.update_count)
            _LOGGER.info("Device ID: %s", self.device_id)
        
        # Add any cleanup logic here if needed