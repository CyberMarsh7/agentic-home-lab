"""
Task Router
Routes requests to appropriate devices based on available resources
"""

import json
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"

class TaskRouter:
    def __init__(self, memory_manager, model_manager):
        """
        Initialize router

        Args:
            memory_manager: MemoryManager instance
            model_manager: ModelManager instance
        """
        self.memory = memory_manager
        self.models = model_manager
        self.pending_tasks = {}
        self.task_history = []

    def submit_task(self, task_id: str, task_type: str, request: Dict, user_context: Dict) -> Dict:
        """
        Submit a task for processing

        Args:
            task_id: Unique task identifier
            task_type: 'image', 'rag', 'voice', 'reasoning', 'system'
            request: Task request data
            user_context: User context (for coach validation)

        Returns:
            Task submission response
        """
        task = {
            'id': task_id,
            'type': task_type,
            'request': request,
            'user_context': user_context,
            'status': TaskStatus.PENDING.value,
            'submitted_at': datetime.now().isoformat(),
            'assigned_device': None,
            'required_model': None,
            'result': None
        }

        self.pending_tasks[task_id] = task
        logger.info(f"Task submitted: {task_id} ({task_type})")

        return {
            'task_id': task_id,
            'status': TaskStatus.PENDING.value,
            'message': 'Task received, awaiting processing'
        }

    def route_task(self, task_id: str, coach_approved: bool, coach_reason: str = "") -> Dict:
        """
        Route a task that has been coach-validated

        Args:
            task_id: Task to route
            coach_approved: Whether coach approved
            coach_reason: Coach's explanation

        Returns:
            Routing result
        """
        if task_id not in self.pending_tasks:
            return {'error': f'Task {task_id} not found'}

        task = self.pending_tasks[task_id]

        if not coach_approved:
            task['status'] = TaskStatus.REJECTED.value
            task['result'] = {'reason': f'Coach rejected: {coach_reason}'}
            logger.warning(f"Task rejected: {task_id} - {coach_reason}")
            return {
                'task_id': task_id,
                'status': TaskStatus.REJECTED.value,
                'reason': coach_reason
            }

        # Find model for task
        model_info = self.models.find_model_for_task(task['type'])
        if not model_info:
            task['status'] = TaskStatus.FAILED.value
            task['result'] = {'error': f'No model available for {task["type"]}'}
            return {
                'task_id': task_id,
                'status': TaskStatus.FAILED.value,
                'error': 'No model available'
            }

        task['required_model'] = model_info['name']

        # Find device with enough RAM
        required_ram = model_info['device_requirements'].get('min_ram_gb', 1.0)
        device = self.memory.find_device_for_task(task['type'], required_ram)

        if not device:
            task['status'] = TaskStatus.FAILED.value
            task['result'] = {'error': 'No device with enough resources'}
            return {
                'task_id': task_id,
                'status': TaskStatus.FAILED.value,
                'error': 'Insufficient resources available'
            }

        task['assigned_device'] = device
        task['status'] = TaskStatus.APPROVED.value

        logger.info(f"Task routed: {task_id} to {device} with model {model_info['name']}")

        return {
            'task_id': task_id,
            'status': TaskStatus.APPROVED.value,
            'device': device,
            'model': model_info['name'],
            'message': f'Task will execute on {device}'
        }

    def complete_task(self, task_id: str, result: Any) -> Dict:
        """Mark task as complete"""
        if task_id not in self.pending_tasks:
            return {'error': f'Task {task_id} not found'}

        task = self.pending_tasks[task_id]
        task['status'] = TaskStatus.COMPLETED.value
        task['result'] = result
        task['completed_at'] = datetime.now().isoformat()

        # Move to history
        self.task_history.append(task)

        logger.info(f"Task completed: {task_id}")

        return {
            'task_id': task_id,
            'status': TaskStatus.COMPLETED.value,
            'result': result
        }

    def fail_task(self, task_id: str, error: str) -> Dict:
        """Mark task as failed"""
        if task_id not in self.pending_tasks:
            return {'error': f'Task {task_id} not found'}

        task = self.pending_tasks[task_id]
        task['status'] = TaskStatus.FAILED.value
        task['result'] = {'error': error}

        self.task_history.append(task)

        logger.error(f"Task failed: {task_id} - {error}")

        return {
            'task_id': task_id,
            'status': TaskStatus.FAILED.value,
            'error': error
        }

    def get_task_status(self, task_id: str) -> Dict:
        """Get current status of a task"""
        if task_id in self.pending_tasks:
            return self.pending_tasks[task_id]

        # Check history
        for task in self.task_history:
            if task['id'] == task_id:
                return task

        return {'error': f'Task {task_id} not found'}

    def get_system_status(self) -> Dict:
        """Get overall system status"""
        return {
            'devices': self.memory.get_devices(),
            'models': self.models.get_status(),
            'pending_tasks': len(self.pending_tasks),
            'completed_tasks': len(self.task_history),
            'health': self.memory.health_check()
        }

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Note: This is a skeleton. Full integration requires
    # actual MemoryManager and ModelManager instances

    print("Task router initialized. See clustering/backend/ for full implementation.")
