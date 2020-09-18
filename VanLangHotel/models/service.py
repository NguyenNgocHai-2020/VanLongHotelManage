from odoo import api, fields, models


class Service(models.Model):
    _name = 'service'

    name = fields.Char(string='Name', required='1')
    price = fields.Float(string='Price')
