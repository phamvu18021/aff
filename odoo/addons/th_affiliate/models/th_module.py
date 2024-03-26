from odoo import fields, models

class ThModule(models.Model):
    _name = 'therp.module'
    _description = 'Module AUM'

    name = fields.Char(string='Tên module')
    active = fields.Boolean(string="Active", default=True)