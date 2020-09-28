from odoo import api, fields, models


class Rooms(models.Model):
    _name = 'room'
    _rec_name = 'room_code'

    room_avatar = fields.Binary(string='Image')
    room_code = fields.Char(string='Room ID', required=True)
    room_type = fields.Selection(selection=[('standard', 'Standard'),
                                            ('superior', 'Superior'),
                                            ('deluxe', 'Deluxe'),
                                            ('suite', 'Suite')],
                                 string='Type Room', default='superior')
    room_state = fields.Selection(selection=[('available', 'Available'),
                                             ('operational', 'Operational')],
                                  string='State', default='available')
    room_price = fields.Float(string='Price (VNĐ) ')
    room_description = fields.Html(string='Description')

    air_conditioned = fields.Boolean('Air Conditioned')
    Bathrobe = fields.Boolean('Bathrobe')
    Direct_dial_phone = fields.Boolean('Direct dial phone')
    Electronic_door_locks = fields.Boolean('Electronic door locks')
    Electronic_smoke_detector = fields.Boolean('Electronic smoke detector')

    Lake_view = fields.Boolean('Lake view')
    Laundry_service = fields.Boolean('Laundry service')
    Safety_box = fields.Boolean('Safety box')
    Refrigerator = fields.Boolean('Refrigerator')
    Iron_and_board = fields.Boolean('Iron and board (on request)')
    Work_desk = fields.Boolean('Work desk')
    Slippers = fields.Boolean('Slippers')
    Smoking_rooms_available = fields.Boolean('Smoking rooms available')
    Cable_movie_channel = fields.Boolean('Cable movie channel')
    Television = fields.Boolean('Television')
    Radio = fields.Boolean('Radio')
    Cd_player = fields.Boolean('Cd player')
    Ipod_docks = fields.Boolean('Ipod docks')
    Free_wifi = fields.Boolean('Free wifi')
    Free_internet_access = fields.Boolean('Free internet access')
    Hair_dryer = fields.Boolean('Hair dryer')
    Shower = fields.Boolean('Shower')
    Bathtub = fields.Boolean('Bathtub')
    Extra_bed = fields.Boolean('Extra bed')
    Sofa_bed = fields.Boolean('Sofa bed')
    Living_room = fields.Boolean('Living room')
    Parking = fields.Boolean('Parking')
    coffee_tea = fields.Boolean('Fresh ground coffee & loose leaf tea')
    extra_persons_allowed = fields.Boolean('Maximum extra persons allowed')

    booking_id = fields.Many2many(comodel_name='booking', string='Booking')
    pictures = fields.One2many(comodel_name='picture', inverse_name='room_id', string='Image')


    @api.onchange('room_type')
    def get_default_price_room(self):
        if self.room_type == 'standard':
            self.price_room = 1125936.68
        elif self.room_type == 'superior':
            self.price_room = 1414285.71
        elif self.room_type == 'deluxe':
            self.price_room = 3311688.31
        else:
            self.price_room = 4783549.78
