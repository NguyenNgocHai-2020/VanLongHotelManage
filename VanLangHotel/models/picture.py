from odoo import api, fields, models


class Picture(models.Model):
    _name = 'picture'
    _rec_name = 'id'

    picture = fields.Binary(string='Picture', max_width=1920, max_height=1920)
    room_id = fields.Many2many(comodel_name='room', invisible=True)
