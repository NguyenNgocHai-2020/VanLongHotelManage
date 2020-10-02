from odoo import api, fields, models


class Service(models.Model):
    _name = 'service'

    name = fields.Char(string='Name', required='1')
    quantity = fields.Float(string='Quantity', required='1')


class Service_Order(models.Model):
    _name = 'service_order'

    service_id = fields.Many2one(comodel_name='service', string='Service')
    name = fields.Char(related='service_id.name')
    quantity = fields.Float(related='service_id.quantity')
    amount = fields.Integer(string='Amount', default=1)
    price = fields.Float('Price', compute='_calculate_price_service', store=True)
    booking_id = fields.Many2one(comodel_name='booking', string='Booking')

    @api.depends('service_id.quantity', 'amount')
    def _calculate_price_service(self):
        for service_order in self:
            if service_order.service_id:
                for service in service_order.service_id:
                    service_order.price = service_order.amount * service.quantity
