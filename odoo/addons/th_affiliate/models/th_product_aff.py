from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ThProductAff(models.Model):
    _name = "th.product.aff"
    _rec_name = 'name'
    _check_company_auto = True
    _description = "Sản phẩm affiliate"

    name = fields.Char('Tiêu đề', required=1)
    th_link = fields.Char(string='Link', required=1)
    th_seo_description = fields.Text(string='Nội dung mô tả ngắn')
    th_note = fields.Text(string='Lưu ý')
    campaign_id = fields.Many2one('utm.campaign', string='Chiến dịch', ondelete='cascade')
    th_proactive_seeding = fields.Boolean(string='Cho phép chủ động seeding', compute="_compute_th_proactive_seeding", store=True, readonly=False)
    th_delivered = fields.Boolean(string='Đã giao', default=False)
    th_aff_category_id = fields.Many2one('th.product.aff.category', 'Nhóm sản phẩm')
    th_product_image_ids = fields.One2many('th.product.image', 'th_product_aff_id', string="Ảnh sản phẩm")
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.constrains('th_link')
    def _check_link_pro_aff(self):
        for rec in self:
            if 'http' not in rec.th_link and 'https' not in rec.th_link:
                raise ValidationError(_('Link không đúng vui lòng xem lại!'))

            if self.search([('th_link', '=', rec.th_link), ('campaign_id', '=', rec.campaign_id.id), ('id', '!=', rec.id)]):
                raise ValidationError(_(f'Link sản phẩm "{rec.th_link}" đã tồn tại trong chiến dịch!'))

    def action_create_link_tracker(self, user_id=None):
        if not user_id:
            user_id = self.env.user.id
        contact_affiliate = self.env['res.users'].browse(user_id).partner_id
        utm_source_id = False
        utm_source = self.env['utm.source'].sudo().search([('name', '=', contact_affiliate.th_affiliate_code)])
        if not utm_source and contact_affiliate.th_affiliate_code:
            utm_source_id = utm_source.sudo().create({
                'name': contact_affiliate.th_affiliate_code
            })
        if utm_source:
            utm_source_id = utm_source

        if self.th_link:
            link_id = self.env['link.tracker'].sudo().search([('url', '=', self.th_link), ('campaign_id', '=', self.campaign_id.id),
                                                              ('source_id', '=', utm_source_id.id), ('th_product_aff_id', '=', self.id),
                                                              ('th_aff_partner_id', '=', contact_affiliate.id), ('th_type', '=', 'link_seeding'), ('medium_id', '=', False)])
            if not link_id:
                link_id |= self.env['link.tracker'].sudo().create({
                    'url': self.th_link,
                    'campaign_id': self.campaign_id.id if self.campaign_id.id else False,
                    'th_type': 'link_seeding',
                    'source_id': utm_source_id.id if utm_source_id else False,
                    'th_aff_partner_id': contact_affiliate.id,
                    'th_product_aff_id': self.id,
                    'th_title': self.name,
                })
            view_id = self.env.ref('th_affiliate.th_link_tracker_view_form')
            action = self.env["ir.actions.actions"]._for_xml_id("th_affiliate.th_link_tracker_action")
            action['view_mode'] = 'form'
            action['views'] = [(view_id.id, 'form')]
            action['res_id'] = link_id.id
            return action

    @api.depends('campaign_id')
    def _compute_th_proactive_seeding(self):
        for rec in self:
            if rec.campaign_id:
                rec.th_proactive_seeding = rec.campaign_id.th_proactive_seeding
            else:
                rec.th_proactive_seeding = False

    def write(self, values):
        th_link = values.get('th_link', False)
        for rec in self:
            link_tracker = self.env['link.tracker'].search_count([('th_product_aff_id', '=', rec.id)])
            if th_link and link_tracker:
                raise ValidationError(_('Link sản phẩm đang được đi seeding vui lòng không chỉnh sửa link sản phẩm!'))

        return super(ThProductAff, self).write(values)

    def unlink(self):
        for rec in self:
            link_tracker = self.env['link.tracker'].search_count([('th_product_aff_id', '=', rec.id)])
            if link_tracker:
                raise ValidationError(_('Link sản phẩm đang được đi seeding vui lòng không xóa link sản phẩm!'))
        return super(ThProductAff, self).unlink()
