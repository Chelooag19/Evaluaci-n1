from flask import Flask, request, jsonify
from uuid import uuid4
import time

app = Flask(__name__)


reminders = []

def validate_content(content):
    """Valida el contenido del recordatorio."""
    if not isinstance(content, str):
        return False, "El contenido debe ser una cadena de texto."
    if not content.strip():
        return False, "El contenido no puede estar vacío o contener solo espacios en blanco."
    if len(content) > 120:
        return False, "El contenido no puede exceder los 120 caracteres."
    return True, ""

def validate_important(important):
    """Valida el valor de 'important'."""
    if not isinstance(important, bool):
        return False, "El valor de 'important' debe ser un booleano."
    return True, ""

@app.route('/api/reminders', methods=['GET'])
def list_reminders():
    """Lista todos los recordatorios, ordenados por importancia y fecha."""
    sorted_reminders = sorted(
        reminders,
        key=lambda x: (-x['important'], x['createdAt'])
    )
    return jsonify(sorted_reminders), 200

@app.route('/api/reminders', methods=['POST'])
def create_reminder():
    """Crea un nuevo recordatorio."""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "El campo 'content' es requerido."}), 400

    content = data['content']
    important = data.get('important', False)

    content_valid, content_error = validate_content(content)
    if not content_valid:
        return jsonify({"error": content_error}), 400

    important_valid, important_error = validate_important(important)
    if not important_valid:
        return jsonify({"error": important_error}), 400

    reminder = {
        'id': str(uuid4()),
        'content': content.strip(),
        'createdAt': int(time.time() * 1000),  
        'important': important
    }

    reminders.append(reminder)
    return jsonify(reminder), 201

@app.route('/api/reminders/<id>', methods=['PATCH'])
def update_reminder(id):
    """Actualiza un recordatorio existente."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se proporcionaron datos para actualizar."}), 400

    reminder = next((r for r in reminders if r['id'] == id), None)
    if not reminder:
        return jsonify({"error": "Recordatorio no encontrado."}), 404

    if 'content' in data:
        content_valid, content_error = validate_content(data['content'])
        if not content_valid:
            return jsonify({"error": content_error}), 400
        reminder['content'] = data['content'].strip()

    if 'important' in data:
        important_valid, important_error = validate_important(data['important'])
        if not important_valid:
            return jsonify({"error": important_error}), 400
        reminder['important'] = data['important']

    return jsonify(reminder), 200

@app.route('/api/reminders/<id>', methods=['DELETE'])
def delete_reminder(id):
    """Elimina un recordatorio."""
    global reminders
    reminder = next((r for r in reminders if r['id'] == id), None)
    if not reminder:
        return jsonify({"error": "Recordatorio no encontrado."}), 404

    reminders = [r for r in reminders if r['id'] != id]
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)