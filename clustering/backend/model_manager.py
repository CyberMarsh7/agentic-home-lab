"""
Model Manager
Manages 2TB SSD model library and loading/unloading into shared RAM
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    def __init__(self, ssd_mount_path: str = "/mnt/data"):
        """
        Initialize model manager

        Args:
            ssd_mount_path: Path to 2TB SSD mount point
        """
        self.ssd_path = Path(ssd_mount_path)
        self.models_path = self.ssd_path / "models"
        self.metadata_file = self.models_path / "manifest.json"
        self.models = self._load_manifest()

    def _load_manifest(self) -> Dict:
        """Load or create model manifest"""
        if self.metadata_file.exists():
            with open(self.metadata_file) as f:
                return json.load(f)

        return {
            'models': {},
            'last_updated': datetime.now().isoformat()
        }

    def _save_manifest(self):
        """Save model manifest"""
        self.models['last_updated'] = datetime.now().isoformat()
        self.models_path.mkdir(parents=True, exist_ok=True)

        with open(self.metadata_file, 'w') as f:
            json.dump(self.models, f, indent=2)

    def register_model(self, model_name: str, model_path: str, size_gb: float,
                      model_type: str, device_requirements: Dict) -> bool:
        """
        Register a model in the library

        Args:
            model_name: 'stable-diffusion', 'llama-2-7b', etc.
            model_path: Relative path from /mnt/data/models
            size_gb: Model size in GB
            model_type: 'image', 'text', 'vision', 'rag'
            device_requirements: {'min_ram_gb': 2.5, 'gpu': True, 'device_pref': 'victus'}
        """
        model_key = model_name

        self.models['models'][model_key] = {
            'name': model_name,
            'path': model_path,
            'size_gb': size_gb,
            'type': model_type,
            'device_requirements': device_requirements,
            'registered_at': datetime.now().isoformat(),
            'loaded': False,
            'loaded_on_device': None
        }

        self._save_manifest()
        logger.info(f"Model registered: {model_name} ({size_gb}GB, {model_type})")
        return True

    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get model metadata"""
        return self.models['models'].get(model_name)

    def list_models(self, model_type: Optional[str] = None) -> List[str]:
        """
        List all available models

        Args:
            model_type: Filter by type ('image', 'text', etc.)

        Returns:
            List of model names
        """
        models = []
        for name, info in self.models['models'].items():
            if model_type is None or info.get('type') == model_type:
                models.append(name)
        return models

    def find_model_for_task(self, task_type: str) -> Optional[Dict]:
        """
        Find best model for a task

        task_type: 'image', 'rag', 'voice', 'reasoning'
        returns: Model info dict or None
        """
        # Task to model type mapping
        task_mapping = {
            'image': 'image',
            'rag': 'text',
            'voice': 'text',
            'reasoning': 'text',
            'vision': 'vision'
        }

        model_type = task_mapping.get(task_type, 'text')
        available_models = self.list_models(model_type)

        if not available_models:
            return None

        # Return first available (could add scoring logic here)
        model_name = available_models[0]
        return self.get_model_info(model_name)

    def mark_loaded(self, model_name: str, device_name: str):
        """Mark a model as loaded on a device"""
        if model_name in self.models['models']:
            self.models['models'][model_name]['loaded'] = True
            self.models['models'][model_name]['loaded_on_device'] = device_name
            self._save_manifest()

    def mark_unloaded(self, model_name: str):
        """Mark a model as unloaded"""
        if model_name in self.models['models']:
            self.models['models'][model_name]['loaded'] = False
            self.models['models'][model_name]['loaded_on_device'] = None
            self._save_manifest()

    def get_loaded_models(self) -> Dict[str, List[str]]:
        """Get currently loaded models per device"""
        loaded = {}
        for name, info in self.models['models'].items():
            if info.get('loaded'):
                device = info.get('loaded_on_device')
                if device:
                    if device not in loaded:
                        loaded[device] = []
                    loaded[device].append(name)
        return loaded

    def verify_ssd_space(self) -> Dict:
        """Check available space on 2TB SSD"""
        try:
            import shutil
            stat = shutil.disk_usage(str(self.ssd_path))
            return {
                'total_gb': stat.total / (1024**3),
                'used_gb': stat.used / (1024**3),
                'free_gb': stat.free / (1024**3)
            }
        except Exception as e:
            logger.error(f"Error checking SSD space: {e}")
            return {}

    def get_status(self) -> Dict:
        """Get overall status of model library"""
        total_model_size = sum(
            m.get('size_gb', 0) for m in self.models['models'].values()
        )

        return {
            'total_models': len(self.models['models']),
            'total_model_size_gb': total_model_size,
            'loaded_models': sum(1 for m in self.models['models'].values() if m.get('loaded')),
            'ssd_status': self.verify_ssd_space(),
            'last_updated': self.models.get('last_updated')
        }

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    mm = ModelManager()

    # Register some models
    mm.register_model(
        'stable-diffusion-xl',
        'models/stable-diffusion-xl',
        6.5,
        'image',
        {'min_ram_gb': 3.0, 'gpu': True, 'device_pref': 'victus'}
    )

    mm.register_model(
        'llama-2-7b',
        'models/llama-2-7b',
        3.5,
        'text',
        {'min_ram_gb': 2.0, 'gpu': False, 'device_pref': 'victus'}
    )

    print("Available image models:", mm.list_models('image'))
    print("Status:", mm.get_status())
