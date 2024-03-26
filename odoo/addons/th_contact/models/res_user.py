from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import xmlrpc.client

url, db, username, password = 'http://10.10.50.130:8016/', 'base_aff', 'admin', '6bb74aaaae2a0d81b141d4a1bdcfe23f06bd146e'


class ResUsers(models.Model):
    _inherit = "res.users"
    _description = "user"

    def check_user(self, values):
        email = values.get('email', False) if values.get('email', False) else values.get('login', False)
        res_values = {}
        if not email:
            raise ValidationError("Không có email login!")
        if values.get('th_partner_samp', False):
            res_partner = self.env['res.partner'].sudo().create(values)
            res_values = {
                'name': values['name'],
                'login': email,
                'partner_id': res_partner.id if res_partner else False
            }
        values = res_values if res_values else values
        return values

    @api.model
    def create(self, values):
        values = self.check_user(values)
        user = super(ResUsers, self).create(values)
        self.action_reset_password()
        return user
