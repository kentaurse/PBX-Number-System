# PBX Configuration
PBX_CONFIG = {
    'OKI_CROSSCORE': {
        'type': 'OKI',
        'model': 'CrossCore2',
        'host': '10.183.5.58',  # From screenshot
        'port': 5060,  # Default SIP port, adjust if needed
        'protocol': 'TCP'
    }
}

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'database': 'crm_db',
    'user': 'user',
    'password': 'password'
} 