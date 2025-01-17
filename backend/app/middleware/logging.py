# app/middleware/logging.py
import logging
from datetime import datetime
import json
from flask import request, current_app
from functools import wraps
import os

class SecurityLogger:
    def __init__(self, log_path='logs'):
        self.log_path = log_path
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        
        # Configuration du logger
        self.logger = logging.getLogger('security_logger')
        self.logger.setLevel(logging.INFO)
        
        # Handler pour fichier
        file_handler = logging.FileHandler(f'{log_path}/security.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def log_request(self, request_data, user_info=None):
        """Log une requête avec les informations utilisateur si disponibles"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
        }
        
        # Ajouter les informations utilisateur si disponibles
        if user_info:
            log_entry['user_id'] = user_info.get('user_id')
            log_entry['username'] = user_info.get('username')
            log_entry['role'] = user_info.get('role')

        # Ajouter les données de la requête si présentes
        if request_data:
            # Masquer les mots de passe dans les logs
            if isinstance(request_data, dict):
                safe_data = request_data.copy()
                if 'password' in safe_data:
                    safe_data['password'] = '********'
                if 'old_password' in safe_data:
                    safe_data['old_password'] = '********'
                if 'new_password' in safe_data:
                    safe_data['new_password'] = '********'
                log_entry['request_data'] = safe_data
            else:
                log_entry['request_data'] = request_data

        self.logger.info(json.dumps(log_entry))

def security_logging_middleware(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Récupérer les données de la requête
        request_data = {}
        if request.is_json:
            request_data = request.get_json()
        elif request.form:
            request_data = dict(request.form)
        
        # Récupérer les informations utilisateur si disponibles
        user_info = getattr(request, 'user', None)
        
        # Logger la requête avant le traitement
        current_app.security_logger.log_request(request_data, user_info)
        
        # Exécuter la vue
        response = f(*args, **kwargs)
        
        return response
    return decorated_function