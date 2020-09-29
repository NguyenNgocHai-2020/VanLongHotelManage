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
    booking_count = fields.Integer(string='Booking Count', compute='_booking_count')
    total_spending = fields.Float(string='Total spending', compute='_total_spending_customer')

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

    @api.depends('booking_ids')
    def _booking_count(self):
        for customer in self:
            customer.booking_count = len(customer.booking_ids)

    @api.depends('booking_ids')
    def _total_spending_customer(self):
        for cus in self:
            if cus.booking_ids:
                total_booking_price = 0
                for booking in cus.booking_ids:
                    total_booking_price += booking.total_amount
                cus.total_spending = total_booking_price
            else:
                cus.total_spending = 0

    @api.constrains('phone_number')
    def validate_phone(self):
        if not self.phone_number or len(self.phone_number) > 10 or len(self.phone_number) < 10:
            raise ValidationError('You must define the phone number consisting of 10 characters.')

    @api.constrains('card_id')
    def validate_card_id(self):
        if not self.card_id or len(self.card_id) > 9 or len(self.card_id) < 9:
            raise ValidationError('You must define the Identity Card consisting of 10 characters.')
