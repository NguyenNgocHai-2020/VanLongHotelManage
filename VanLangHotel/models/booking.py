from odoo import models, fields, api
from datetime import datetime


class Booking(models.Model):
    _name = 'booking'
    _rec_name = 'id'

    customer_id = fields.Many2one(comodel_name='customer', string='Customer')
    check_in = fields.Date(string='Check-in', default=datetime.today())
    check_out = fields.Date(string='Check-out')
    amount_adult = fields.Integer(string='Adult')
    amount_child = fields.Integer(string='Child ')
    cost = fields.Float(compute='_calculate_cost', string='Cost')
    service = fields.Many2many(comodel_name='service', string='Service')
    promotion = fields.Many2one(comodel_name='promotion', string='Promotion')
    room_ids = fields.One2many(comodel_name='room', inverse_name='booking_id', string='Rooms')

    def _calculate_cost(self):
        for booking in self:
            total = 0
            if booking.service:
                for service in booking.service:
                    total += service.price
            if booking.promotion:
                total = total - total * booking.promotion.promotion
            booking.cost = total
