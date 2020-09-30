from odoo import models, fields, api
from datetime import date
from odoo.exceptions import UserError, ValidationError


class Booking(models.Model):
    _name = 'booking'
    _rec_name = 'booking_id'

    booking_id = fields.Char(string='ID', default='New', readonly=1)
    customer_id = fields.Many2one(comodel_name='customer', string='Customer', required=True)
    check_in = fields.Date(string='Check-in', default=date.today())
    check_out = fields.Date(string='Check-out', required=True)
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('booking', 'Booking'),
                                        ('check_in', 'Check in'),
                                        ('check_out', 'Check out'),
                                        ('paid', 'Paid')], string='State', default='draft')
    amount_adult = fields.Integer(string='Adult')
    amount_child = fields.Integer(string='Child ')
    service_order = fields.One2many(comodel_name='service_order', inverse_name='booking', string='Service')
    promotion = fields.Many2one(comodel_name='promotion', string='Promotion')
    room_ids = fields.Many2many(comodel_name='room', string='Rooms',
                                required=True)
    room_count = fields.Integer(compute='_get_room_count', string='Room Count', store=True)
    note = fields.Text(string='Note')
    surcharge = fields.Float(string='Surcharge')
    number_of_days_reserved = fields.Integer('Number of days reserved', compute='_calculate_number_of_days_reserved', store=True)
    room_total = fields.Float(compute='_calculate_room_total', store=True)
    promotion_price = fields.Float(compute='_calculate_promotion_price', store=True)
    sum_service_order = fields.Float(compute='_calculate_sum_service_order', store=True)
    total_amount = fields.Float(compute='_calculate_total_amount', store=True)

    _sql_constraints = [
        ('booking_id_uniq', 'unique(booking_id)', 'Booking_id must be unique !'),
    ]

    @api.onchange('room_ids')
    def onchange_room_ids(self):
        result = {}
        domain = {'room_ids': [('room_state', '=', 'available')]}
        result['domain'] = domain
        return result

    @api.constrains('check_in', 'check_out')
    def validate_check_out(self):
        if self.check_out < self.check_in:
            raise ValidationError("""The check out date must be less than the check in date! Please choose again""")


    @api.model
    def create(self, vals):
        vals['booking_id'] = self.env['ir.sequence'].next_by_code('BOOKING_SEQUENCE')
        return super(Booking, self).create(vals)

    @api.depends('room_ids')
    def _get_room_count(self):
        for booking in self:
            booking.room_count = len(booking.room_ids)

    @api.depends('promotion')
    def _calculate_promotion_price(self):
        for booking in self:
            total = 0
            if booking.promotion:
                total = booking.room_total * booking.promotion.promotion
            booking.promotion_price = total

    @api.depends('service_order')
    def _calculate_sum_service_order(self):
        for booking in self:
            total = 0
            if booking.service_order:
                for service in booking.service_order:
                    total += service.price
            booking.sum_service_order = total

    @api.depends('check_in', 'check_out')
    def _calculate_number_of_days_reserved(self):
        for booking in self:
            if booking.check_in and booking.check_out:
                number_day = str(booking.check_out - booking.check_in)
                number_day = number_day[0:2]
                number_day = int(number_day.strip())
                booking.number_of_days_reserved = number_day

    @api.depends('room_ids.room_price', 'number_of_days_reserved')
    def _calculate_room_total(self):
        for booking in self:
            total = 0
            for room in booking.room_ids:
                total += room.room_price
            booking.room_total = total * booking.number_of_days_reserved

    @api.depends('promotion_price', 'sum_service_order', 'room_total', 'surcharge')
    def _calculate_total_amount(self):
        for booking in self:
            if booking.surcharge:
                booking.total_amount = booking.room_total + booking.sum_service_order - booking.promotion_price - booking.surcharge
            else:
                booking.total_amount = booking.room_total + booking.sum_service_order - booking.promotion_price

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
