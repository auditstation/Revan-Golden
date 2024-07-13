import base64
import json
import secrets
import string
import logging
from werkzeug import urls
from odoo import http, tools, _, SUPERUSER_ID
from odoo.exceptions import AccessDenied, AccessError, MissingError, UserError, ValidationError
from odoo.http import content_disposition, Controller, request, route
from datetime import date
import requests
import io
import datetime
import PyPDF2
import base64


import codecs
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class DataConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    url_integrate = fields.Char(string="Use Following url",
                                config_parameter='integration_with_dalilee.url_integrate', help="Use Following url")

    user_name = fields.Char(default="Classycom1@hotmail.com", string="Email for Dalilee",
                            config_parameter='integration_with_dalilee.user_name', help="Email")

    password = fields.Char(default="Classy0!&^@410!@", string="Password for Dalilee",
                           config_parameter='integration_with_dalilee.password', help="Password")

    access_token = fields.Char(string="Token",
                               config_parameter='integration_with_dalilee.access_token', help="token")


class LogInfo(models.Model):
    _name = "log.info"

    log_name = fields.Char('Log name', readonly=True)
    description = fields.Char('Description', readonly=True)
    logdetails = fields.Char('Log details', readonly=True)
    log_name = fields.Char('Log name', readonly=True)
    cpid =  fields.Char('cpid', readonly=True)
    created_at = fields.Char('Created at', readonly=True)
    sale_id = fields.Many2one('sale.order')
    order_id = fields.Char('order ID')
    log_id = fields.Integer('log_id')

class UserInherit(models.Model):
    _inherit = "res.users"

    def auth_dalilee(self):
        data = {
            "email": self.env['ir.config_parameter'].sudo().get_param('integration_with_dalilee.user_name'),
            "password": self.env['ir.config_parameter'].sudo().get_param('integration_with_dalilee.password'),
            "password_confirmation": self.env['ir.config_parameter'].sudo().get_param(
                'integration_with_dalilee.password'),
        }

        base_url = self.env['ir.config_parameter'].sudo().get_param('integration_with_dalilee.url_integrate')
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        url = base_url+"login"
       
        create_request_get_data = requests.post(url, data=json.dumps(data), headers=headers)
        response_body = json.loads(create_request_get_data.content)
       
        if 'token' in response_body:
            access_token = response_body['token']
            self.env['ir.config_parameter'].set_param('integration_with_dalilee.access_token', access_token)
            auth = self.env['ir.config_parameter'].sudo().get_param('integration_with_dalilee.access_token')
            return access_token


class SaleOrederInherit(models.Model):
    _inherit = "sale.order"
    orderId = fields.Char('Order Id from Dalilee')
    ship_price = fields.Char('Ship price from Dalilee')
    file_ship = fields.Binary('File from DalileeTrade')
    log_info = fields.One2many(
        'log.info',
        'sale_id',
        string='Order Log',
        
    )
    status_order = fields.Selection([
        ('not','Not'),
        ('I', 'Not Collected'),
        ('completed', 'Delivered'),
        ('F', 'Undelivered'),
        ('pickupbydriver', 'pickup by Driver'),
        ('intransit', 'In Transit'),
        ('receivedbybranch', 'Received by Station'),
        ('return', 'Return'),
        ('logsheetconfirm', 'Order Confirm received in Pickup Station'),
        ('FW', 'Undelivered Back to Warehouse'),
        ('RISS', 'Order arrive in sort station'),
        ('OFD', 'OFD'),
        ('assigned', 'Assigned to driver'),
        ('receivedbyoutlet', 'received by outlet'),
        ('intransittooutlet', 'intransit to outlet'),
        ('intransittostation', 'intransit to station'),
    ], string='Order status')

   
    def call_data(self, url_data, data):
        auth = self.env.user.auth_dalilee()
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('integration_with_dalilee.url_integrate')
      
        headers = {"Authorization": f'Bearer {auth}', "Content-Type": "application/json", "Accept": "application/json"}
        url = base_url + url_data
        create_request_get_data = requests.post(url, data=json.dumps(data), headers=headers)
        response_body_data = json.loads(create_request_get_data.content)
        return response_body_data


    def add_order(self,sale_id):
        data = {
            "customer_name": str(sale_id.partner_id.name),
            "customer_number": str(sale_id.partner_id.phone),
            "order_price": 0,
            "wilaya_id": "1",
            "external_way_bill_number":sale_id.name,
            "address": str(sale_id.partner_shipping_id.country_id.name)+"-"+str(sale_id.partner_shipping_id.state_id.name)+"-"+str(sale_id.partner_shipping_id.street),
            "volume_weight": "2"
        }
    
        response = self.sudo().call_data('add-order', data)
        _logger.info(f'heeeeeeeeeeeeee{response}')
      
        if response['status'] == "success":
           
            # sale_id.status_order = get_key_for_gov(response['data']['status'])
            sale_id.orderId = response['data']['orderId']
            sale_id.ship_price = response['data']['ship_price']

    def get_key_for_gov(self,gov_val):    
        switcher = {
            'Not':'not',
            'Not Collected':'I',
            'Delivered':'completed', 
            'Undelivered':'F',
            'pickup by Driver':'pickupbydriver',
            'In Transit':'intransit',
             'Received by Station':'receivedbybranch',
            'Return':'return',
            'Order Confirm received in Pickup Station':'logsheetconfirm',
            'Undelivered Back to Warehouse':'FW',
            'Order arrive in sort station':'RISS',
            'OFD':'OFD',
            'Assigned to driver':'assigned',
            'received by outlet':'receivedbyoutlet',
            'intransit to outlet':'intransittooutlet',
            'intransit to station':'intransittostation',        
        }    
        return switcher.get(gov_val,'I')
    def action_confirm(self):
        res = super(SaleOrederInherit, self).action_confirm()
        for order in self:
            if order.order_line.filtered(lambda l: l.price_total == 0):
                 order.status_order=self.sudo().get_key_for_gov('Not')
            else:
                self.sudo().add_order(order)
                order.status_order='I'
                self.sudo().order_status()
                
        return res

    def order_log(self):
        for rec in self.env['sale.order'].sudo().search([('state','=', 'sale')]).filtered(
                lambda l: l.create_date.date() >= date.today()
                          and l.create_date.date() <= date.today()):
            if rec.order_line.filtered(lambda l: l.price_total == 0):
                 rec.status_order=self.sudo().get_key_for_gov('Not')
            elif rec.status_order == 'completed' or rec.status_order =='return':
                if rec.orderId:
                    data = {
                        "order_id": rec.orderId,
                
                    }
                    response = self.sudo().call_data('order-logs', data)
                   
                    data_create=[]
                    # if rec.log_info:
                    for i in rec.log_info:
                        data_create.append(i.id)
                    for j in response['data']:
                        
                        if j['id'] not in data_create:
                            logs=self.env['log.info'].sudo().create({
                                "log_name":j['log_name'],
                                "description":j['description'],
                                "logdetails":j['logdetails'],
                                "created_at":j['created_at'],
                                "order_id":j["order_id"],
                                "cpid":j["cpid"],
                                "log_id":j["id"],
                                "sale_id":self.env['sale.order'].sudo().search([('orderId','=',str(j["order_id"]))]).id,
                            })
                            rec.log_info = [(4, logs.id)]



    def order_status(self):
       
        for rec in self.env['sale.order'].sudo().search([('state','=', 'sale')]).filtered(
                    lambda l: l.create_date.date() >= date.today()
                              and l.create_date.date() <= date.today()):
            
            if rec.order_line.filtered(lambda l: l.price_total == 0):
                 rec.status_order=self.sudo().get_key_for_gov('Not')
            elif rec.status_order!='completed' or rec.status_order!='return' or rec.status_order!='not':
               
                
                if rec.orderId:
                   
                    data = {
                        "order_id": rec.orderId,
            
                    }
            
                    response = self.sudo().call_data('order-status', data)
                    
            
                    if response['status'] == "success":
                       
                       
                    
                        rec.sudo().write({'status_order':response['data']['status_code']}) 
                        rec.sudo().order_print()


    def order_print(self):
       
        auth = self.env.user.auth_dalilee()
       
        data = {
            "order_ids": [self.orderId]
    
        }
    
        base_url = self.env['ir.config_parameter'].sudo().get_param('integration_with_dalilee.url_integrate')
      
        headers = {"Authorization": f'Bearer {auth}', "Content-Type": "application/json", "Accept": "application/json"}
        url = base_url + 'print-orders'
        create_request_get_data = requests.post(url, data=json.dumps(data), headers=headers)
        response_body_data = create_request_get_data.content
       
        b64PDF = codecs.encode(response_body_data, 'base64')
        self.file_ship=b64PDF
       

    
        
