from odoo import api, fields, models
from datetime import date


class Employee(models.Model):
    _name = 'employee'

    name = fields.Char(string='Name')
    dob = fields.Date(string='Date of Birth')
    regency = fields.Selection(selection=[('manager', 'Manager'),
                                          ('receptionist', 'Receptionist'),
                                          ('housekeeping', 'Housekeeping')], string='Position')
    address = fields.Char(string='Address')
    phone = fields.Char(string='Phone')