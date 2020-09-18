from odoo import api, fields, models


class Customer(models.Model):
    _name = 'customer'
    _rec_name = 'cus_name'

    cus_name = fields.Char(string='Name')
    card_id = fields.Char(string='Identity Card')
    phone_number = fields.Char(string='Phone')
    address = fields.Char(string='Address')
    booking_ids = fields.One2many(comodel_name='booking', inverse_name='customer_id', string='Booking')
