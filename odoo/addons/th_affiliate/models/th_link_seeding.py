# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import random
import requests
import string

from lxml import html
from werkzeug import urls

from odoo import tools, models, fields, api, _
from odoo.exceptions import UserError, ValidationError,Warning
from odoo.osv import expression

URL_MAX_SIZE = 10 * 1024 * 1024


class ThLinkSeeding(models.Model):
    _name = "th.link.seeding"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _description = 'bảng giá'

    name = fields.Char(string='Tiêu đề')
    image = fields.Image(string='Thêm ảnh')
    campaign_id = fields.Many2one('utm.campaign', ondelete='set null', string='Chiến dịch', domain=lambda self: [('th_start_date', '<=', fields.Date.today()), ('th_end_date', '>=', fields.Date.today())], check_company=True, tracking=True)
    th_filename = fields.Char()
    th_medium_ids = fields.One2many('th.utm.medium', 'th_link_seeding_id', string='Kênh', required=1)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    th_aff_category_id = fields.Many2one('th.product.aff.category', 'Nhóm sản phẩm')
    state = fields.Selection(string="Trạng thái", selection=[('draft', 'Nháp'), ('deployment', 'Triển khai'), ('close', 'Đóng')], default='draft')
    th_link_tracker_ids = fields.One2many('link.tracker', 'th_link_seeding_id', string='Link tracker')
    th_deadline = fields.Date(string='Thời hạn')
    th_collaborator_group_ids = fields.Many2many("th.collaborator.group", string=" Nhóm CTV")
    th_type = fields.Selection(string='Giao bài theo', selection=[('by_group', 'Theo nhóm'), ('by_people', 'Theo người')], default='by_group', required=1)
    user_ids = fields.Many2many('res.users', string='Cộng tác viên')
    th_domain = fields.Char(compute='_compute_th_domain')
    th_pro_domain = fields.Char(compute="_compute_th_pro_domain")
    th_product_aff_id = fields.Many2one('th.product.aff', string='Sản phẩm', tracking=True, required=1)

    @api.depends('campaign_id')
    def _compute_th_pro_domain(self):
        for rec in self:
            domain = []
            if rec.campaign_id:
                domain.append(('campaign_id', '=', rec.campaign_id.id))
            rec.th_pro_domain = json.dumps(domain)

    @api.onchange('campaign_id')
    def onchange_method(self):
        for rec in self:
            rec.th_product_aff_id = False

    @api.depends('company_id', 'th_type')
    def _compute_th_domain(self):
        for rec in self:
            domain = []
            if rec.company_id and rec.th_type == 'by_people':
                domain.append(('user_ids', 'in', rec.company_id.user_ids.ids))
            # if rec.company_id and rec.th_type == 'by_group':
            #     th_collaborator_group_ids = self.env['th.collaborator.group'].sudo().search([('company_id', '=', rec.company_id.id)])
            #     domain.append(('th_collaborator_group_ids', 'in', th_collaborator_group_ids.ids))
            rec.th_domain = json.dumps(domain)

    def action_create_link_tracker(self):
        for rec in self:
            list_people = []
            if rec.th_link_tracker_ids:
                raise ValidationError(_('Đã có link seeding không thể giao lại!'))
            if not rec.th_medium_ids:
                raise ValidationError(_('Vui lòng chọn ít nhất 1 kênh để đi seeding'))
            if rec.th_type == 'by_group':
                list_people += rec.th_collaborator_group_ids.user_ids.ids

            if rec.th_type == 'by_people':
                list_people += rec.user_ids.ids

            for person in list_people:
                contact_affiliate = self.env['res.partner'].sudo().search([('user_ids.id', '=', person)], limit=1)
                utm_source_id = False
                utm_source = self.env['utm.source'].sudo().search([('name', '=', contact_affiliate.th_affiliate_code)])
                if not utm_source and contact_affiliate.th_affiliate_code:
                    utm_source_id = utm_source.sudo().create({'name': contact_affiliate.th_affiliate_code})
                if utm_source:
                    utm_source_id = utm_source

                for medium in rec.th_medium_ids:
                    th_odd = medium.th_remaining_number
                    th_odd = medium.th_number_of_requests % len(list_people) if th_odd == -1 else th_odd
                    if rec.th_product_aff_id.th_link and (th_odd != 0 or medium.th_number_of_requests // len(list_people) != 0):
                        self.env['link.tracker'].sudo().create({
                            'th_title': rec.th_product_aff_id.name,
                            'url': rec.th_product_aff_id.th_link,
                            'medium_id': medium.medium_id.id if medium else False,
                            'campaign_id': rec.campaign_id.id if rec.campaign_id.id else False,
                            'th_link_seeding_id': rec.id if rec.id else False,
                            'th_type': 'link_seeding',
                            'source_id': utm_source_id.id if utm_source_id else False,
                            'th_product_aff_id': rec.th_product_aff_id.id,
                            'th_aff_partner_id': contact_affiliate.id,
                            'th_number_of_requests': medium.th_number_of_requests // len(list_people) + 1 if th_odd > 0 else medium.th_number_of_requests // len(list_people),
                        })
                    medium.th_remaining_number = th_odd - 1 if th_odd - 1 > 0 else 0

        self.env['th.utm.medium'].search([]).write({
            'th_remaining_number': -1
        })

    def action_change_state_draft(self):
        self.state = 'draft'
        return True

    def action_change_state_deployment(self):
        self.state = 'deployment'
        return True

    def action_change_state_close(self):
        for rec in self:
            rec.state = 'close'
            rec.th_link_tracker_ids.active = False

    def unlink(self):
        for rec in self:
            if rec.state == 'deployment' or rec.state == 'close':
                raise ValidationError("Bạn không được phép xóa dữ liệu có trạng thái triển khai và đóng!")
            return super(ThLinkSeeding, self).unlink()

    @api.onchange('th_type')
    def onchange_th_type(self):
        for rec in self:
            if rec.th_type == 'by_group':
                rec.user_ids = False
            if rec.th_type == 'by_people':
                rec.th_collaborator_group_ids = False


    # @api.model
    # def create(self, values):
    #     rec = super(ThLinkSeeding, self).create(values)
    #
    #     return rec
    #
    # def write(self, values):
    #     mediums = values.get('th_medium_ids', False)
    #     for rec in self:
    #         if mediums:
    #             pass
    #
    #     return super(ThLinkSeeding, self).write(values)
