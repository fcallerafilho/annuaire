import { useState, useEffect } from 'react';

class FrontendLogger {
    constructor(backendUrl) {
      this.backendUrl = backendUrl;
      this.batchLogs = [];
      this.batchSize = 1;
    }
  
    async log(event) {
      const logEntry = {
        timestamp: new Date().toISOString(),
        event_type: event.type,
        details: event.details,
        user_info: this.getUserInfo(),
        page: window.location.pathname
      };
  
      this.batchLogs.push(logEntry);
  
      if (this.batchLogs.length >= this.batchSize) {
        await this.sendLogs();
      }
    }
  
    getUserInfo() {
      return {
        userAgent: navigator.userAgent,
        language: navigator.language,
        screenResolution: `${window.screen.width}x${window.screen.height}`
      };
    }
  
    async sendLogs() {
        if (this.batchLogs.length === 0) return;

        try {
            const token = localStorage.getItem('token');
            if (!token) {
                console.warn('No authentication token available');
                return;
            }

            const response = await fetch(`${this.backendUrl}/logs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    logs: this.batchLogs
                })
            });
            console.log(process.env.REACT_APP_BACKEND_URL);


            if (response.ok) {
                this.batchLogs = [];
            } else if (response.status === 401) {
                // Token expiré ou invalide
                console.warn('Authentication failed when sending logs');
            }
        } catch (error) {
            console.error('Erreur lors de l\'envoi des logs:', error);
        }
    }
}

const logger = new FrontendLogger(process.env.REACT_APP_API_URL);

export const useLogger = () => {
    const [initialized] = useState(true);
  
    useEffect(() => {
      if (initialized) {
        logger.log({
          type: 'LOGGER_INITIALIZED',
          details: { timestamp: new Date().toISOString() }
        });
      }
    }, [initialized]);
  
    return {
      logNavigation: (path) => {
        logger.log({
          type: 'NAVIGATION',
          details: { path }
        });
      },
      logAction: (action, details = {}) => {
        logger.log({
          type: 'USER_ACTION',
          details: { action, ...details }
        });
      },
      logAuth: (status, details = {}) => {
        logger.log({
          type: 'AUTH',
          details: { status, ...details }
        });
      }
    };
  };


export default logger;