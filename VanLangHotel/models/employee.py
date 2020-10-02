from odoo import api, fields, models
from datetime import date
from odoo.exceptions import UserError, ValidationError
from ast import literal_eval


class Employee(models.Model):
    _inherit = 'res.users'

    dob = fields.Date(string='Date')
    regency = fields.Selection(selection=[('manager', 'Manager'),
                                          ('receptionist', 'Receptionist'),
                                          ('housekeeping', 'Housekeeping')], string='Position')
    booking_ids = fields.One2many(comodel_name='booking', inverse_name='employee_id')

