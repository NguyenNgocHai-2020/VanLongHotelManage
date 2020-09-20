from odoo import api, fields, models
from datetime import date
from odoo.exceptions import UserError, ValidationError


class Employee(models.Model):
    _name = 'employee'

    name = fields.Char(string='Name', required=True)
    dob = fields.Date(string='Date of Birth')
    regency = fields.Selection(selection=[('manager', 'Manager'),
                                          ('receptionist', 'Receptionist'),
                                          ('housekeeping', 'Housekeeping')], string='Position')
    address = fields.Char(string='Address')
    phone = fields.Char(string='Phone')

    @api.model
    def create(self, vals):
        if vals.get('name', False):
            vals['name'] = vals['name'].title()
        res = super(Employee, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('name', False):
            vals['name'] = vals['name'].title()
        res = super(Employee, self).write(vals)
        return res

    @api.constrains('phone')
    def validate_phone(self):
        if not self.phone or len(self.phone) > 10 or len(self.phone) < 10:
            raise ValidationError('You must define the phone number consisting of 10 characters.')