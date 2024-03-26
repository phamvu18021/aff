import xmlrpc

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ThCountryDistrict(models.Model):
    _name = 'th.country.district'
    _description = 'Quận/Huyện'

    name = fields.Char(string='Quận/ Huyện', required=True)
    th_ref = fields.Char(string='Mã Quận/ Huyện', required=True)
    th_state_id = fields.Many2one(comodel_name='res.country.state', required=True, string='Tỉnh/ Thành phố',
                                  domain="[('country_id.code', '=', 'VN')]")

    _sql_constraints = [
        ('name_th_ref_uniq', 'unique(th_state_id, th_ref)', 'Mã của Quận/Huyện không được trùng ở mỗi Tỉnh/TP !')
    ]

    # def create(self, vals_list):
    #     res = super().create(vals_list)
    #     return res
