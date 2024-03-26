from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ThPaymentBatch(models.Model):
    _name = "th.payment.batch"
    _rec_name = 'name'
    _description = "Đợt thanh toán"

    name = fields.Char('Tên đợt')
    th_campaign = fields.Many2one('utm.campaign', string='Chiến dịch')
    th_start_date = fields.Date('Ngày bắt đầu')
    th_end_date = fields.Date('Ngày kết thúc')
    th_pay_ids = fields.One2many('th.pay', 'th_payment_batch_id')
    state_payment_batch = fields.Selection([('draft', "Nháp"), ('create_pay', "Tạo phiếu")], default='draft')

    @api.constrains('th_start_date', 'th_end_date')
    def check_date_create_payment_batch(self):
        rec_payment_batch = self.env['th.payment.batch'].search([('id', '!=', self.id),
                                                                 ('th_campaign', '=', self.th_campaign.id),
                                                                 '|',
                                                                 '&',('th_start_date', '<=', self.th_start_date),
                                                                 ('th_end_date', '>=', self.th_start_date),
                                                                 '|',
                                                                 '&', ('th_start_date', '<=', self.th_end_date),
                                                                 ('th_end_date', '>=', self.th_end_date),
                                                                 '|',
                                                                 '&', ('th_start_date', '<=', self.th_start_date),
                                                                 ('th_end_date', '>=', self.th_end_date),
                                                                 '&', ('th_start_date', '>=', self.th_start_date),
                                                                 ('th_end_date', '<=', self.th_end_date)
                                                                 ])
        if self.th_start_date and self.th_end_date:
            if self.th_start_date >= self.th_end_date:
                raise ValidationError("Ngày bắt đầu phải nhỏ hơn ngày kết thúc")
            if rec_payment_batch:
                raise ValidationError("Không được tạo đợt thanh toán trùng ngày với đợt đã có")

    def create_pay(self):

        # self = super(ThPaymentBatch, self).create(values)
        post_link_ids = []
        if self.th_campaign.id:
            link_seeding = self.env['link.tracker'].search([
                ('campaign_id', '=', self.th_campaign.id),('create_date', '>=', self.th_start_date),
                ('create_date', '<=', self.th_end_date),
            ])
            for rec in link_seeding:
                post_link = rec.th_post_link_ids.ids
                for n in range(len(post_link)):
                    post_link_ids.append(post_link[n])
        else:
            link_seeding = self.env['link.tracker'].search([
                ('create_date', '>=', self.th_start_date),
                ('create_date', '<=', self.th_end_date),
            ])
            for rec in link_seeding:
                post_link = rec.th_post_link_ids.ids
                for n in range(len(post_link)):
                    post_link_ids.append(post_link[n])
        opportunity_ctv = self.env['th.opportunity.ctv'].search(
            [('create_date', '>=', self.th_start_date), ('create_date', '<=', self.th_end_date),
             ('th_paid', '=', False)])
        if not link_seeding and opportunity_ctv:
            self.env['th.pay'].create({
                'name': _('Phiếu thanh toán cho %s', opportunity_ctv.th_partner_id.name),
                'th_partner_id': opportunity_ctv.th_partner_id.id,
                'state': 'pending',
                'th_post_link_ids': post_link_ids if post_link_ids else False,
                'th_campaign': self.th_campaign,
                'th_opportunity_ctv_ids': opportunity_ctv.ids
            })
        for i in link_seeding:
            pay_id = self.env['th.pay'].search(
                    [('th_campaign', '=', self.th_campaign.id),('th_post_link_ids', 'like', post_link_ids)], limit=1, order='id desc')
            post_links = link_seeding.filtered(
                        lambda p: p.th_aff_partner_id.id == i.th_aff_partner_id.id).th_post_link_ids.filtered(
                        lambda p: p.state == 'correct_request' and p.th_pricelist_ids)
            if not pay_id and post_links:
                self.env['th.pay'].create({
                    'name': _('Phiếu thanh toán cho %s', i.th_aff_partner_id.name),
                    'th_partner_id': i.th_aff_partner_id.id,
                    'state': 'pending',
                    'th_post_link_ids': post_link_ids if post_link_ids else False,
                    'th_campaign': self.th_campaign,
                    'th_opportunity_ctv_ids': opportunity_ctv.ids
        })
        self.state_payment_batch = 'create_pay'
        if not link_seeding and not opportunity_ctv:
            raise ValidationError("Không có link seeding và cơ hội cần tạo phiếu thanh toán! Vui lòng chọn lại ngày hoặc chiến dịch he")
