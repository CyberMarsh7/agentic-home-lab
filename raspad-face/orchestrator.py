"""
Orchestrator Service
Connects RasPad face to clustering backend
Handles voice requests, routes to agents, returns responses
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sys
import os
from datetime import datetime

# Add clustering backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'clustering', 'backend'))

from memory_manager import MemoryManager
from model_manager import ModelManager
from task_router import TaskRouter

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clustering system
memory_manager = MemoryManager(redis_host='localhost', redis_port=6379)
model_manager = ModelManager(ssd_mount_path='/mnt/data')
task_router = TaskRouter(memory_manager, model_manager)

class CoachAgent:
    """Validates requests before processing"""

    def validate(self, request_text: str, user_context: dict) -> tuple[bool, str]:
        """
        Validate request against safety rules

        Returns:
            (approved: bool, reason: str)
        """

        # Safety rules
        dangerous_patterns = [
            'delete all',
            'rm -rf',
            'format drive',
            'shutdown',
            'reboot',
            'poweroff'
        ]

        request_lower = request_text.lower()

        for pattern in dangerous_patterns:
            if pattern in request_lower:
                return False, f"Dangerous operation: {pattern}"

        # Check for prompt injection attempts
        injection_patterns = ['ignore instructions', 'forget your', 'pretend you are']
        for pattern in injection_patterns:
            if pattern in request_lower:
                return False, f"Injection attempt detected: {pattern}"

        # All clear
        return True, "Approved"

coach = CoachAgent()

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'system_status': task_router.get_system_status()
    })

@app.route('/api/orchestrate', methods=['POST'])
def orchestrate():
    """
    Main orchestration endpoint
    Receives voice request, validates, routes to agents, returns response
    """

    try:
        data = request.json
        user_request = data.get('request', '')

        if not user_request:
            return jsonify({'error': 'No request provided'}), 400

        logger.info(f"Received request: {user_request}")

        # Step 1: Generate task ID
        task_id = f"task_{datetime.now().timestamp()}"

        # Step 2: Determine task type
        task_type = determine_task_type(user_request)
        logger.info(f"Task type: {task_type}")

        # Step 3: Coach validation
        user_context = {'source': 'voice', 'timestamp': datetime.now().isoformat()}
        approved, coach_reason = coach.validate(user_request, user_context)

        if not approved:
            logger.warning(f"Coach rejected: {coach_reason}")
            return jsonify({
                'response': f"I can't do that. {coach_reason}",
                'status': 'rejected',
                'reason': coach_reason
            })

        # Step 4: Submit task
        submit_result = task_router.submit_task(
            task_id=task_id,
            task_type=task_type,
            request={'text': user_request},
            user_context=user_context
        )

        # Step 5: Route task
        route_result = task_router.route_task(
            task_id=task_id,
            coach_approved=True
        )

        if 'error' in route_result:
            return jsonify({
                'response': f"Could not route request: {route_result.get('error', 'Unknown error')}",
                'status': 'failed'
            })

        # Step 6: Execute task (would happen asynchronously in production)
        # For now, return a placeholder response
        response = generate_response(task_type, user_request, route_result)

        # Mark task complete
        task_router.complete_task(task_id, {'response': response})

        return jsonify({
            'response': response,
            'status': 'completed',
            'task_id': task_id,
            'device': route_result.get('device'),
            'model': route_result.get('model')
        })

    except Exception as e:
        logger.error(f"Error in orchestration: {e}")
        return jsonify({
            'error': str(e),
            'response': "I encountered an error processing your request."
        }), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    return jsonify(task_router.get_system_status())

@app.route('/api/devices', methods=['GET'])
def get_devices():
    """List registered devices"""
    return jsonify({
        'devices': memory_manager.get_devices(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/models', methods=['GET'])
def get_models():
    """List available models"""
    return jsonify({
        'status': model_manager.get_status(),
        'available_models': model_manager.list_models(),
        'loaded_models': model_manager.get_loaded_models()
    })

def determine_task_type(request_text: str) -> str:
    """Determine what type of task this is"""

    text_lower = request_text.lower()

    if any(word in text_lower for word in ['image', 'picture', 'draw', 'create image']):
        return 'image'
    elif any(word in text_lower for word in ['rag', 'search', 'knowledge', 'find']):
        return 'rag'
    elif any(word in text_lower for word in ['design', 'layout', 'ui', 'ux']):
        return 'uxui'
    elif any(word in text_lower for word in ['think', 'reason', 'calculate', 'solve']):
        return 'reasoning'
    elif any(word in text_lower for word in ['security', 'check', 'monitor', 'status']):
        return 'security'
    else:
        return 'voice'  # Default conversational

def generate_response(task_type: str, request_text: str, route_info: dict) -> str:
    """Generate a response (placeholder - would be real model inference in production)"""

    device = route_info.get('device', 'unknown')
    model = route_info.get('model', 'default')

    responses = {
        'image': f"I'll generate an image for you on {device} using {model}.",
        'rag': f"Searching knowledge base using {model} on {device}...",
        'uxui': f"Designing layout with {model} on {device}...",
        'reasoning': f"Reasoning through that using {model} on {device}...",
        'security': f"Checking system security via {device}...",
        'voice': f"Got it. I'm processing your request: {request_text[:50]}..."
    }

    return responses.get(task_type, "Processing your request...")

if __name__ == '__main__':
    logger.info("Starting Orchestrator service...")
    logger.info("Memory Manager initialized")
    logger.info("Model Manager initialized")
    logger.info("Task Router initialized")
    logger.info("Coach Agent ready")

    app.run(host='0.0.0.0', port=5000, debug=False)
