"""
Export Helper Utility
Handles CSV and Excel exports for admin data
"""

import csv
import io
from datetime import datetime
from flask import Response


class ExportHelper:
    """Utility class for exporting data to various formats"""
    
    @staticmethod
    def export_to_csv(data, filename, columns):
        """
        Export data to CSV format
        
        Args:
            data (list): List of dictionaries containing data to export
            filename (str): Name of the file to download
            columns (list): List of column names/keys to include in export
        
        Returns:
            Flask Response with CSV file
        """
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        headers = [col['label'] for col in columns]
        writer.writerow(headers)
        
        # Write data rows
        for row in data:
            csv_row = []
            for col in columns:
                key = col['key']
                value = row.get(key, '')
                
                # Handle None values
                if value is None:
                    value = ''
                
                # Handle datetime objects
                elif isinstance(value, datetime):
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                
                # Convert to string
                csv_row.append(str(value))
            
            writer.writerow(csv_row)
        
        # Create response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )
    
    @staticmethod
    def export_users_csv(users, filename='users_export.csv'):
        """Export users to CSV"""
        columns = [
            {'key': 'id', 'label': 'ID'},
            {'key': 'username', 'label': 'Username'},
            {'key': 'email', 'label': 'Email'},
            {'key': 'first_name', 'label': 'First Name'},
            {'key': 'last_name', 'label': 'Last Name'},
            {'key': 'role', 'label': 'Role'},
            {'key': 'status', 'label': 'Status'},
            {'key': 'phone', 'label': 'Phone'},
            {'key': 'created_at', 'label': 'Created At'},
            {'key': 'last_login', 'label': 'Last Login'}
        ]
        
        return ExportHelper.export_to_csv(users, filename, columns)
    
    @staticmethod
    def export_orders_csv(orders, filename='orders_export.csv'):
        """Export orders to CSV"""
        columns = [
            {'key': 'id', 'label': 'Order ID'},
            {'key': 'order_number', 'label': 'Order Number'},
            {'key': 'customer_name', 'label': 'Customer'},
            {'key': 'customer_email', 'label': 'Email'},
            {'key': 'total_amount', 'label': 'Total Amount'},
            {'key': 'status', 'label': 'Status'},
            {'key': 'payment_method', 'label': 'Payment Method'},
            {'key': 'payment_status', 'label': 'Payment Status'},
            {'key': 'created_at', 'label': 'Order Date'},
            {'key': 'delivered_at', 'label': 'Delivered Date'}
        ]
        
        return ExportHelper.export_to_csv(orders, filename, columns)
    
    @staticmethod
    def export_audit_logs_csv(logs, filename='audit_logs_export.csv'):
        """Export audit logs to CSV"""
        columns = [
            {'key': 'id', 'label': 'Log ID'},
            {'key': 'action', 'label': 'Action'},
            {'key': 'username', 'label': 'User'},
            {'key': 'email', 'label': 'Email'},
            {'key': 'details', 'label': 'Details'},
            {'key': 'ip_address', 'label': 'IP Address'},
            {'key': 'user_agent', 'label': 'User Agent'},
            {'key': 'created_at', 'label': 'Timestamp'}
        ]
        
        return ExportHelper.export_to_csv(logs, filename, columns)
    
    @staticmethod
    def export_products_csv(products, filename='products_export.csv'):
        """Export products to CSV"""
        columns = [
            {'key': 'id', 'label': 'Product ID'},
            {'key': 'name', 'label': 'Product Name'},
            {'key': 'seller_name', 'label': 'Seller'},
            {'key': 'category', 'label': 'Category'},
            {'key': 'price', 'label': 'Price'},
            {'key': 'stock_quantity', 'label': 'Stock'},
            {'key': 'status', 'label': 'Status'},
            {'key': 'pet_type', 'label': 'Pet Type'},
            {'key': 'created_at', 'label': 'Created At'}
        ]
        
        return ExportHelper.export_to_csv(products, filename, columns)
    
    @staticmethod
    def export_seller_requests_csv(requests, filename='seller_requests_export.csv'):
        """Export seller requests to CSV"""
        columns = [
            {'key': 'id', 'label': 'Request ID'},
            {'key': 'first_name', 'label': 'First Name'},
            {'key': 'last_name', 'label': 'Last Name'},
            {'key': 'email', 'label': 'Email'},
            {'key': 'business_name', 'label': 'Business Name'},
            {'key': 'business_phone', 'label': 'Business Phone'},
            {'key': 'status', 'label': 'Status'},
            {'key': 'requested_at', 'label': 'Requested At'},
            {'key': 'reviewed_at', 'label': 'Reviewed At'},
            {'key': 'admin_notes', 'label': 'Admin Notes'}
        ]
        
        return ExportHelper.export_to_csv(requests, filename, columns)
    
    @staticmethod
    def generate_filename(base_name, extension='csv'):
        """Generate a timestamped filename"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{base_name}_{timestamp}.{extension}"
