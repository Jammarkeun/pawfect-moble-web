"""
Centralized error handling and logging utilities for Pawfect Finds.
Provides structured logging, error tracking, and decorators for consistent error handling.
"""
import logging
import traceback
import functools
from datetime import datetime
from flask import jsonify, request, session
from typing import Callable, Any, Dict, Optional
import sys

# Configure structured logger
class StructuredLogger:
    """Custom structured logger with context support"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with appropriate handlers and formatters"""
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Format: timestamp - level - module - message
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)
    
    def _get_context(self) -> Dict[str, Any]:
        """Get current request context"""
        try:
            return {
                'user_id': session.get('user_id'),
                'role': session.get('user_role'),
                'ip': request.remote_addr if request else None,
                'endpoint': request.endpoint if request else None,
                'method': request.method if request else None,
            }
        except RuntimeError:  # Outside request context
            return {}
    
    def _format_message(self, message: str, extra: Optional[Dict] = None) -> str:
        """Format message with context"""
        context = self._get_context()
        if extra:
            context.update(extra)
        
        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items() if v)
            return f"{message} | {context_str}" if context_str else message
        return message
    
    def info(self, message: str, extra: Optional[Dict] = None):
        """Log info message"""
        self.logger.info(self._format_message(message, extra))
    
    def warning(self, message: str, extra: Optional[Dict] = None):
        """Log warning message"""
        self.logger.warning(self._format_message(message, extra))
    
    def error(self, message: str, exc_info: bool = False, extra: Optional[Dict] = None):
        """Log error message"""
        self.logger.error(self._format_message(message, extra), exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = True, extra: Optional[Dict] = None):
        """Log critical message"""
        self.logger.critical(self._format_message(message, extra), exc_info=exc_info)
    
    def debug(self, message: str, extra: Optional[Dict] = None):
        """Log debug message"""
        self.logger.debug(self._format_message(message, extra))


# Global logger instance
logger = StructuredLogger(__name__)


def handle_errors(default_message: str = "An error occurred", 
                 return_json: bool = True,
                 status_code: int = 500):
    """
    Decorator to handle errors in route handlers.
    Logs errors and returns appropriate error responses.
    
    Args:
        default_message: Default error message to return to user
        return_json: Whether to return JSON response (True) or render error page (False)
        status_code: HTTP status code for error response
    
    Example:
        @app.route('/api/data')
        @handle_errors("Failed to fetch data")
        def get_data():
            # Your code here
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log the full error
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    exc_info=True,
                    extra={'function': func.__name__}
                )
                
                # Return appropriate response
                if return_json:
                    return jsonify({
                        'success': False,
                        'error': default_message,
                        'details': str(e) if current_app.debug else None
                    }), status_code
                else:
                    from flask import render_template, current_app
                    return render_template(
                        'error.html',
                        error=default_message,
                        details=str(e) if current_app.debug else None
                    ), status_code
        
        return wrapper
    return decorator


def log_function_call(log_args: bool = False, log_result: bool = False):
    """
    Decorator to log function calls with optional argument and result logging.
    
    Args:
        log_args: Whether to log function arguments
        log_result: Whether to log function result
    
    Example:
        @log_function_call(log_args=True)
        def process_order(order_id):
            # Your code here
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            # Log function call
            log_msg = f"Calling {func_name}"
            if log_args:
                log_msg += f" with args={args}, kwargs={kwargs}"
            logger.info(log_msg)
            
            try:
                result = func(*args, **kwargs)
                
                # Log result if requested
                if log_result:
                    logger.info(f"{func_name} returned: {result}")
                
                return result
            except Exception as e:
                logger.error(f"Error in {func_name}: {str(e)}", exc_info=True)
                raise
        
        return wrapper
    return decorator


class ErrorHandler:
    """Centralized error handler for the application"""
    
    @staticmethod
    def handle_database_error(error: Exception, operation: str) -> Dict[str, Any]:
        """Handle database errors"""
        logger.error(
            f"Database error during {operation}: {str(error)}",
            exc_info=True,
            extra={'operation': operation}
        )
        return {
            'success': False,
            'error': 'Database operation failed',
            'operation': operation
        }
    
    @staticmethod
    def handle_validation_error(error: Exception, field: Optional[str] = None) -> Dict[str, Any]:
        """Handle validation errors"""
        logger.warning(
            f"Validation error{' for field ' + field if field else ''}: {str(error)}",
            extra={'field': field}
        )
        return {
            'success': False,
            'error': 'Validation failed',
            'field': field,
            'details': str(error)
        }
    
    @staticmethod
    def handle_authentication_error(message: str = "Authentication failed") -> Dict[str, Any]:
        """Handle authentication errors"""
        logger.warning(f"Authentication error: {message}")
        return {
            'success': False,
            'error': message,
            'code': 'AUTH_FAILED'
        }
    
    @staticmethod
    def handle_authorization_error(message: str = "Unauthorized access") -> Dict[str, Any]:
        """Handle authorization errors"""
        logger.warning(f"Authorization error: {message}")
        return {
            'success': False,
            'error': message,
            'code': 'UNAUTHORIZED'
        }
    
    @staticmethod
    def handle_not_found_error(resource: str) -> Dict[str, Any]:
        """Handle not found errors"""
        logger.info(f"Resource not found: {resource}")
        return {
            'success': False,
            'error': f'{resource} not found',
            'code': 'NOT_FOUND'
        }
    
    @staticmethod
    def handle_file_upload_error(error: Exception) -> Dict[str, Any]:
        """Handle file upload errors"""
        logger.error(f"File upload error: {str(error)}", exc_info=True)
        return {
            'success': False,
            'error': 'File upload failed',
            'details': str(error)
        }
    
    @staticmethod
    def handle_external_service_error(service: str, error: Exception) -> Dict[str, Any]:
        """Handle external service errors (email, payment, etc.)"""
        logger.error(
            f"External service error ({service}): {str(error)}",
            exc_info=True,
            extra={'service': service}
        )
        return {
            'success': False,
            'error': f'{service} service unavailable',
            'code': 'SERVICE_ERROR'
        }


def log_error_to_file(error: Exception, context: Optional[Dict] = None):
    """
    Log error to a dedicated error log file with full context.
    
    Args:
        error: The exception to log
        context: Additional context information
    """
    import os
    
    log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"errors_{datetime.now().strftime('%Y%m%d')}.log")
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Error: {type(error).__name__}: {str(error)}\n")
        
        if context:
            f.write(f"Context: {context}\n")
        
        f.write(f"\nTraceback:\n")
        f.write(traceback.format_exc())
        f.write(f"\n{'='*80}\n")


# Convenience function to get logger for specific modules
def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance for a specific module"""
    return StructuredLogger(name)
