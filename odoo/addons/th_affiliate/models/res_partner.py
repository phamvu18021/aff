from odoo import fields, models, api, _
import xmlrpc.client


class ResPartner(models.Model):
    _inherit = "res.partner"

    th_manager_id = fields.Many2one('res.users', 'Nhóm trưởng')
