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

    @api.onchange('name', 'regency')
    def onchange_login(self):
        if self.name and self.regency:
            name = self.name
            name = name.replace(" ", "")
            self.login = name + "_vlh@gmail.com"




