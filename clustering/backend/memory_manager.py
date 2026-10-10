"""
Unified Memory Manager
Coordinates RAM and model access across Pyramid, Victus, Kali
"""

import json
import redis
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        """Initialize connection to Redis memory broker"""
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.prefix = "memory:"

    def register_device(self, device_name: str, available_ram_gb: float, device_type: str) -> bool:
        """
        Register a device with available RAM

        Args:
            device_name: 'pyramid', 'victus', 'kali'
            available_ram_gb: RAM in GB (e.g., 1.9 for Pyramid)
            device_type: 'orchestrator', 'workhorse', 'security'

        Returns:
            True if registered
        """
        device_key = f"{self.prefix}device:{device_name}"
        device_data = {
            'name': device_name,
            'available_ram_gb': available_ram_gb,
            'device_type': device_type,
            'registered_at': datetime.now().isoformat(),
            'status': 'online'
        }
        self.redis.hset(device_key, mapping=device_data)
        self.redis.expire(device_key, timedelta(hours=1))  # Heartbeat: must re-register
        logger.info(f"Device registered: {device_name} ({available_ram_gb}GB, {device_type})")
        return True

    def get_devices(self) -> Dict[str, dict]:
        """Get all registered devices"""
        devices = {}
        for key in self.redis.scan_iter(f"{self.prefix}device:*"):
            device_name = key.split(':')[2]
            device_data = self.redis.hgetall(key)
            devices[device_name] = device_data
        return devices

    def allocate_model(self, model_name: str, size_gb: float, device_name: str) -> bool:
        """
        Allocate a model to a device's memory

        Returns True if successful, False if not enough RAM
        """
        device_key = f"{self.prefix}device:{device_name}"
        device_data = self.redis.hgetall(device_key)

        if not device_data:
            logger.error(f"Device {device_name} not found")
            return False

        available = float(device_data.get('available_ram_gb', 0))
        if available < size_gb:
            logger.warning(f"Not enough RAM on {device_name}: need {size_gb}GB, have {available}GB")
            return False

        # Record allocation
        alloc_key = f"{self.prefix}allocation:{model_name}:{device_name}"
        self.redis.hset(alloc_key, mapping={
            'model': model_name,
            'device': device_name,
            'size_gb': size_gb,
            'allocated_at': datetime.now().isoformat()
        })

        # Update device available RAM
        new_available = available - size_gb
        self.redis.hset(device_key, 'available_ram_gb', new_available)

        logger.info(f"Model {model_name} allocated to {device_name} ({size_gb}GB)")
        return True

    def deallocate_model(self, model_name: str, device_name: str, size_gb: float) -> bool:
        """Free up model memory"""
        device_key = f"{self.prefix}device:{device_name}"
        device_data = self.redis.hgetall(device_key)

        if not device_data:
            return False

        available = float(device_data.get('available_ram_gb', 0))
        new_available = available + size_gb
        self.redis.hset(device_key, 'available_ram_gb', new_available)

        alloc_key = f"{self.prefix}allocation:{model_name}:{device_name}"
        self.redis.delete(alloc_key)

        logger.info(f"Model {model_name} deallocated from {device_name}")
        return True

    def get_allocated_models(self) -> Dict[str, List[str]]:
        """Get all models currently allocated"""
        allocations = {}
        for key in self.redis.scan_iter(f"{self.prefix}allocation:*"):
            parts = key.split(':')
            device = parts[3]
            model = ':'.join(parts[1:3])  # Handle colons in model names

            if device not in allocations:
                allocations[device] = []
            allocations[device].append(model)

        return allocations

    def find_device_for_task(self, task_type: str, required_ram_gb: float) -> Optional[str]:
        """
        Find best device for a task

        task_type: 'image', 'rag', 'voice', 'reasoning'
        returns: device_name or None
        """
        devices = self.get_devices()

        # Preference order by task type
        preferences = {
            'image': ['victus', 'pyramid'],      # GPU preferred
            'rag': ['victus', 'pyramid'],        # Large RAM preferred
            'voice': ['pyramid', 'victus'],      # Low latency
            'reasoning': ['victus', 'pyramid'],  # Heavy compute
            'security': ['kali', 'victus']       # Safety first
        }

        preferred_devices = preferences.get(task_type, ['victus', 'pyramid', 'kali'])

        for device_name in preferred_devices:
            if device_name in devices:
                available = float(devices[device_name].get('available_ram_gb', 0))
                if available >= required_ram_gb:
                    return device_name

        return None

    def health_check(self) -> Dict[str, bool]:
        """Check system health"""
        devices = self.get_devices()
        health = {}

        for device_name, device_data in devices.items():
            try:
                # Try to ping device via its health endpoint
                # For now, just check if registered recently
                health[device_name] = 'status' in device_data
            except:
                health[device_name] = False

        return health

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mm = MemoryManager()

    # Register devices
    mm.register_device('pyramid', 1.0, 'orchestrator')
    mm.register_device('victus', 8.0, 'workhorse')
    mm.register_device('kali', 4.0, 'security')

    # Check registered devices
    print("Registered devices:", mm.get_devices())

    # Allocate a model
    mm.allocate_model('stable-diffusion', 2.5, 'victus')
    print("Allocations:", mm.get_allocated_models())

    # Find device for a task
    device = mm.find_device_for_task('image', 2.5)
    print(f"Device for image task: {device}")
