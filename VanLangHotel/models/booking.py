from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class Booking(models.Model):
    _name = 'booking'
    _rec_name = 'booking_id'

    booking_id = fields.Char(string='ID', default='New', readonly=1)
    customer_id = fields.Many2one(comodel_name='customer', string='Customer', required=True)
    check_in = fields.Date(string='Check-in', default=datetime.today())
    check_out = fields.Date(string='Check-out')
    state = fields.Selection(selection=[('booking', 'Booking'),
                                        ('check_in', 'Check in'),
                                        ('check_out', 'Check out'),
                                        ('paid', 'Paid')], string='State', default='booking')
    amount_adult = fields.Integer(string='Adult')
    amount_child = fields.Integer(string='Child ')
    cost = fields.Float(compute='_calculate_cost', string='Cost')
    service = fields.Many2many(comodel_name='service', string='Service')
    promotion = fields.Many2one(comodel_name='promotion', string='Promotion')
    room_ids = fields.One2many(comodel_name='room', inverse_name='booking_id', string='Rooms',
                               domain="[('room_state','=','available')]", required=True)
    note = fields.Text(string='Note')
    surcharge = fields.Float(string='Surcharge')

    @api.model
    def create(self, vals):
        vals['booking_id'] = self.env['ir.sequence'].next_by_code('BOOKING_SEQUENCE')
        return super(Booking, self).create(vals)

    def _calculate_cost(self):
        for booking in self:
            total = 0
            for room in booking.room_ids:
                total += room.room_price
            if booking.service:
                for service in booking.service:
                    total = total + service.price
            if booking.promotion:
                total = total - total * booking.promotion.promotion
            if booking.surcharge:
                total = total + booking.surcharge
            booking.cost = total

    def check_in_booking(self):
        self.state = 'check_in'
        self.room_ids.write({'room_state': 'operational'})

    def check_out_booking(self):
        self.state = 'check_out'
        self.room_ids.write({'room_state': 'available'})

    def booking_paid(self):
        self.state = 'paid'

    def cancel_booking(self):
        for booking in self:
            if booking.state != 'booking':
                raise ValidationError("""
                    You can not delete this because this booking is active.
                    Please contact the receptionist,Thank you!!!
                """)
        return super(Booking, self).unlink()
