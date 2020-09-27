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
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('booking', 'Booking'),
                                        ('check_in', 'Check in'),
                                        ('check_out', 'Check out'),
                                        ('paid', 'Paid')], string='State', default='draft')
    amount_adult = fields.Integer(string='Adult')
    amount_child = fields.Integer(string='Child ')
    money_room = fields.Float(compute='_calculate_money_room', store=True)
    service = fields.Many2many(comodel_name='service', string='Service')
    promotion = fields.Many2one(comodel_name='promotion', string='Promotion')
    room_ids = fields.Many2many(comodel_name='room', inverse_name='booking_id', string='Rooms',
                               domain="[('room_state','=','available')]", required=True)
    room_count = fields.Integer(compute='_get_room_count', string='Room Count', store=True)
    note = fields.Text(string='Note')
    surcharge = fields.Float(string='Surcharge')
    promotion_price = fields.Float(compute='_calculate_promotion_price', store=True)
    sum_service = fields.Float(compute='_calculate_sum_service', store=True)
    total_amount = fields.Float(compute='_calculate_total_amount', store=True)

    @api.model
    def create(self, vals):
        vals['booking_id'] = self.env['ir.sequence'].next_by_code('BOOKING_SEQUENCE')
        return super(Booking, self).create(vals)

    @api.depends('room_ids')
    def _get_room_count(self):
        for room in self:
            room.room_count = len(room.room_ids)

    @api.depends('promotion')
    def _calculate_promotion_price(self):
        for booking in self:
            total = 0
            if booking.promotion:
                total = booking.money_room * booking.promotion.promotion
            booking.promotion_price = total

    @api.depends('service')
    def _calculate_sum_service(self):
        for booking in self:
            total = 0
            if booking.service:
                for service in booking.service:
                    total += service.price
            booking.sum_service = total

    @api.depends('room_ids.room_price')
    def _calculate_money_room(self):
        for booking in self:
            total = 0
            for room in booking.room_ids:
                total += room.room_price
            booking.money_room = total

    @api.depends('promotion_price', 'sum_service', 'money_room', 'surcharge')
    def _calculate_total_amount(self):
        for booking in self:
            if booking.surcharge:
                booking.total_amount = booking.money_room + booking.sum_service - booking.promotion_price - booking.surcharge
            else:
                booking.total_amount = booking.money_room + booking.sum_service - booking.promotion_price

    def booking(self):
        self.state = 'booking'

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
