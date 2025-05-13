"""
Web server for GPT-Refactor web UI.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Union

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

from ..core.refactor_engine import RefactorEngine
from ..utils.config import Config
from ..utils.file_handler import list_backups, restore_from_backup

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='build')
CORS(app)  # Enable CORS for all routes

# Initialize config and refactor engine
config = Config()
engine = RefactorEngine()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path: str) -> Union[Response, str]:
    """Serve the React frontend."""
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/refactor', methods=['POST'])
def refactor() -> Response:
    """
    API endpoint for code refactoring.
    
    Expected JSON payload:
    {
        "code": "string",  # Code to refactor
        "language": "string",  # Optional, auto-detected if not provided
        "suggestions_only": boolean,  # Optional, defaults to false
        "rules": ["string"]  # Optional list of custom rules
    }
    """
    try:
        data = request.json
        
        if not data or 'code' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: code'
            }), 400
            
        # Get parameters from request
        code = data['code']
        language = data.get('language')
        suggestions_only = data.get('suggestions_only', False)
        rules = data.get('rules', [])
        
        # Mock refactoring result for demo purposes (without API key)
        if language == 'python':
            result = {
                'success': True,
                'original_code': code,
                'refactored_code': """def hello_world():
    \"\"\"Print a greeting message to the console.
    
    This function demonstrates a simple greeting output.
    \"\"\"
    print("Hello, world!")
    
if __name__ == "__main__":
    hello_world()
""",
                'suggestions': [
                    {'text': 'Added docstring to improve documentation'},
                    {'text': 'Added if __name__ block for better module usage'},
                    {'text': 'Used double quotes for string consistency'}
                ],
                'diff': '@@ -1,2 +1,9 @@\n def hello_world():\n-    print(\'Hello, world!\')\n+    """Print a greeting message to the console.\n+    \n+    This function demonstrates a simple greeting output.\n+    """\n+    print("Hello, world!")\n+    \n+if __name__ == "__main__":\n+    hello_world()',
                'language': 'python'
            }
        elif language == 'javascript':
            result = {
                'success': True,
                'original_code': code,
                'refactored_code': """/**
 * Prints a greeting message to the console.
 */
const helloWorld = () => {
  console.log("Hello, world!");
};

// Call the function
helloWorld();
""",
                'suggestions': [
                    {'text': 'Converted function to arrow function for modern syntax'},
                    {'text': 'Added JSDoc comment for better documentation'},
                    {'text': 'Used const for function declaration as it won\'t be reassigned'}
                ],
                'diff': '@@ -1,4 +1,9 @@\n-function helloWorld() {\n-    console.log("Hello, world!");\n+/**\n+ * Prints a greeting message to the console.\n+ */\n+const helloWorld = () => {\n+  console.log("Hello, world!");\n };\n \n+// Call the function\n helloWorld();',
                'language': 'javascript'
            }
        else:
            # Fallback demo response
            result = {
                'success': True,
                'original_code': code,
                'refactored_code': code + "\n// Code has been refactored with best practices\n",
                'suggestions': [
                    {'text': 'Consider adding documentation to explain the code\'s purpose'},
                    {'text': 'Follow language-specific styling conventions'}
                ],
                'diff': '@@ -1,1 +1,2 @@\n ' + code.replace('\n', '\n ') + '\n+// Code has been refactored with best practices',
                'language': language or 'unknown'
            }
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in /api/refactor: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refactor-file', methods=['POST'])
def refactor_file() -> Response:
    """
    API endpoint for refactoring a file.
    
    This endpoint accepts multipart form data with a file upload.
    
    Form fields:
    - file: The file to refactor
    - language: (Optional) Language override
    - suggestions_only: (Optional) Whether to only provide suggestions
    - rules: (Optional) Custom refactoring rules, JSON-encoded list
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Empty filename'
            }), 400
            
        # Save uploaded file to temporary location
        filename = secure_filename(file.filename)
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        file_path = os.path.join(temp_dir, filename)
        file.save(file_path)
        
        # Get parameters from request
        language = request.form.get('language')
        suggestions_only = request.form.get('suggestions_only', 'false').lower() == 'true'
        
        rules = []
        rules_json = request.form.get('rules')
        if rules_json:
            try:
                rules = json.loads(rules_json)
            except:
                rules = []
                
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        # Use the same mock implementation as /api/refactor
        if language == 'python':
            refactored_code = """def main():
    \"\"\"Main function with improved implementation.\"\"\"
    print("Hello, world!")

if __name__ == "__main__":
    main()
"""
        else:
            refactored_code = code + "\n// Refactored with best practices\n"
            
        # Prepare output path
        output_filename = f"refactored_{filename}"
        output_path = os.path.join(temp_dir, output_filename)
        
        # Save the refactored code
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(refactored_code)
                
        result = {
            'success': True,
            'original_code': code,
            'refactored_code': refactored_code,
            'suggestions': [
                {'text': 'Added proper documentation'},
                {'text': 'Improved code structure'}
            ],
            'diff': '@@ -1,1 +1,5 @@\n-print("Hello, world!")\n+def main():\n+    """Main function with improved implementation."""\n+    print("Hello, world!")\n+\n+if __name__ == "__main__":\n+    main()',
            'language': language or 'unknown'
        }
                
        # Clean up temporary files
        try:
            os.remove(file_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        except:
            pass
                
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in /api/refactor-file: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config() -> Response:
    """Get current configuration."""
    try:
        # Filter out sensitive information like API keys
        safe_config = {k: v for k, v in config.config_data.items() if k != 'api_key'}
        return jsonify({
            'success': True,
            'config': safe_config
        })
    except Exception as e:
        logger.error(f"Error in /api/config: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['POST'])
def update_config() -> Response:
    """Update configuration."""
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No configuration provided'
            }), 400
            
        # Update configuration
        for key, value in data.items():
            config.set(key, value)
            
        # Save configuration
        if config.save():
            return jsonify({
                'success': True,
                'message': 'Configuration updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to save configuration'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in /api/config (POST): {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/languages', methods=['GET'])
def get_languages() -> Response:
    """Get supported languages."""
    return jsonify({
        'success': True,
        'languages': [
            {'id': 'python', 'name': 'Python', 'extensions': ['.py']},
            {'id': 'javascript', 'name': 'JavaScript', 'extensions': ['.js', '.jsx']},
            {'id': 'typescript', 'name': 'TypeScript', 'extensions': ['.ts', '.tsx']},
            {'id': 'java', 'name': 'Java', 'extensions': ['.java']},
            {'id': 'cpp', 'name': 'C++', 'extensions': ['.cpp', '.cc', '.h', '.hpp']}
        ]
    })

def start_web_server(host: str = "localhost", port: int = 3000) -> None:
    """
    Start the Flask web server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
    """
    app.run(host=host, port=port, debug=True)