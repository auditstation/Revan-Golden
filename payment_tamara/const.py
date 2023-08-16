
# Currency codes of the currencies supported by Tamara in ISO 4217 format.
SUPPORTED_CURRENCIES = [
    'SAR',  
    'AED',  
]

TRANSACTION_STATUS_MAPPING = {
    'pending': ('approved',),
    'done': ( 'fully_captured'),
    'authorised': ('authorised'),
    'canceled': ('declined', 'expired','canceled'),
}