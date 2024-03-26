from odoo import models, fields, api, exceptions, _
from odoo.osv import expression


class ThCountryWard(models.Model):
    _name = 'th.country.ward'
    _description = 'Phường/Xã'

    name = fields.Char(string='Phường/ Xã', required=True)
    th_ref = fields.Char(string='Mã Phường/ Xã', required=True)
    th_district_id = fields.Many2one(comodel_name='th.country.district', string='Quận/ Huyện', required=True)

    _sql_constraints = [
        ('name_th_ref_uniq', 'unique(th_district_id, th_ref)', 'Mã của Phường/Xã không được trùng ở mỗi Quận/Huyện !')
    ]

    @api.model
    def create(self, values):
        # Add code here
        return super(ThCountryWard, self).create(values)
