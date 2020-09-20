from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class Customer(models.Model):
    _name = 'customer'
    _rec_name = 'cus_name'

    cus_name = fields.Char(string='Name', required=True)
    card_id = fields.Char(string='Identity Card')
    phone_number = fields.Char(string='Phone')
    address = fields.Char(string='Address')
    booking_ids = fields.One2many(comodel_name='booking', inverse_name='customer_id', string='Booking')

    @api.model
    def create(self, vals):
        if vals.get('cus_name', False):
            vals['cus_name'] = vals['cus_name'].title()
        res = super(Customer, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('cus_name', False):
            vals['cus_name'] = vals['cus_name'].title()
        res = super(Customer, self).write(vals)
        return res

    @api.constrains('phone_number')
    def validate_phone(self):
        if not self.phone_number or len(self.phone_number) > 10 or len(self.phone_number) < 10:
            raise ValidationError('You must define the phone number consisting of 10 characters.')

    @api.constrains('card_id')
    def validate_card_id(self):
        if not self.card_id or len(self.card_id) > 9 or len(self.card_id) < 9:
            raise ValidationError('You must define the Identity Card consisting of 10 characters.')
