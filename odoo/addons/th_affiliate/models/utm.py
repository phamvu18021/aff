# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class UtmCampaign(models.Model):
    _name = 'utm.campaign'
    _inherit = ['utm.campaign', 'mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _rec_name = 'th_title'

    th_title = fields.Char('Tên chiến dịch', required=1)
    title = fields.Char('Mã chiến dịch', required=0, default=lambda self: self.env.company.th_code)
    th_start_date = fields.Date('Ngày bắt đầu', tracking=True, required=1)
    th_end_date = fields.Date('Ngày kết thúc', tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, tracking=True)
    product_line_id = fields.Many2one("th.product.line", string="Dòng sản phẩm", tracking=True)
    th_pay_id = fields.Many2one('th.pay')
    th_proactive_seeding = fields.Boolean(string='Cho phép chủ động seeding', tracking=True, default=True)
    th_product_aff_ids = fields.One2many('th.product.aff', 'campaign_id', tracking=True)

    # @api.constrains('th_title')
    # def _check_campaign(self):
    #     if self.search([('th_title', '=', self.th_title), ('id', '!=', self.id), ('company_id', '=', self.company_id.id)]):
    #         raise ValidationError(_(f'Chiến dịch "{self.th_title}" đã tồn tại'))

    @api.onchange('th_proactive_seeding')
    def check_proactive_seeding(self):
        for rec in self:
            if rec.th_proactive_seeding:
                rec.th_product_aff_ids.th_proactive_seeding = True
            else:
                rec.th_product_aff_ids.th_proactive_seeding = False

    def unlink(self):
        for record in self:
            campaign_ids = self.env['link.tracker'].search([]).mapped('campaign_id').ids
            if campaign_ids and record.id in campaign_ids:
                raise ValidationError("Không thể xóa chiến dịch đã có sản phẩm đi seeding!")
        super(UtmCampaign, self).unlink()

    @api.onchange('th_start_date', 'th_end_date')
    def onchange_date(self):
        for rec in self:
            if rec.th_start_date and rec.th_end_date and rec.th_start_date > rec.th_end_date:
                raise ValidationError(_('Thời gian bắt đầu không thể lớn hơn thời gian kết thúc'))

    @api.model
    def create(self, values):
        if not values.get('name', False):
            raise ValidationError(_('Chưa cấu hình "Đơn vị sở hữu" cho đơn vị này vui lòng báo cho quản trị viên!'))
        res = super(UtmCampaign, self).create(values)
        res.title = res.title + '-' + str(res.id)
        return res
