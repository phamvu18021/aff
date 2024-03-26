# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

_interval_selection = {'minutes': 'Minutes', 'hours': 'Hours', 'days': 'Days'}
_interval_types = {
    'minutes': lambda interval: relativedelta(minutes=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'days': lambda interval: relativedelta(days=interval),
}


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    th_access_interval_number = fields.Integer(string="Thời gian tồn tại")
    th_access_interval_type = fields.Selection(list(_interval_selection.items()))

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].set_param('th_access_interval_number', self.th_access_interval_number)
        self.env['ir.config_parameter'].set_param('th_access_interval_type', self.th_access_interval_type)

    @api.model
    def get_values(self):
        res = super().get_values()
        th_access_interval_number = self.env['ir.config_parameter'].sudo().get_param('th_access_interval_number')
        th_access_interval_type = self.env['ir.config_parameter'].sudo().get_param('th_access_interval_type')

        res.update(th_access_interval_number=th_access_interval_number if int(th_access_interval_number) != 0 else 7,
                   th_access_interval_type=th_access_interval_type if th_access_interval_type else 'days')
        return res
