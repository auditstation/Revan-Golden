-- disable mercado_pago payment provider
UPDATE payment_provider
   SET tamara_api_token = NULL,
   tamara_notification_token = NULL;
