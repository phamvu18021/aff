import base64
import uuid

from odoo import tools, models, fields, api, _, modules
from collections import defaultdict
from odoo.exceptions import ValidationError
from odoo.modules import get_module_resource

URL_MAX_SIZE = 10 * 1024 * 1024

select_closing_work = ([
        ('pending', 'Chờ nghiệm thu'),
        ('acceptance', 'Nghiệm thu'),
        ('cost_closing', 'Tạm chốt chi phí')])


class LinkTracker(models.Model):
    _name = 'link.tracker'
    _inherit = ['link.tracker', 'mail.thread', 'mail.activity.mixin']

    url = fields.Char(tracking=True)
    th_link_seeding_id = fields.Many2one('th.link.seeding', string="Link gốc", check_company=True)
    th_type = fields.Selection(selection=[('email_marketing', 'Email marketing'), ('link_seeding', 'Link seeding')])
    th_post_link_ids = fields.One2many('th.post.link', 'link_tracker_id', 'Post link')
    th_aff_partner_id = fields.Many2one('res.partner', 'Cộng tác viên', readonly=True)
    th_total_cost = fields.Float('Tổng chi phí', compute="_amount_all", store=True, digits=(12, 1))
    th_closing_work = fields.Selection(selection=select_closing_work, string='Chốt chi phí', tracking=True, default='pending')
    image = fields.Image()
    th_aff_category_id = fields.Many2one(related='th_link_seeding_id.th_aff_category_id', store=True)
    th_count_link_click = fields.Integer('Clicks', default=0)
    th_session_user_ids = fields.One2many('th.session.user', 'th_link_tracker_id')
    th_count_user = fields.Integer('Số người dùng', compute="_compute_th_session_user_ids", store=True)
    th_filename = fields.Char()
    company_id = fields.Many2one('res.company', string='Company', change_default=True, default=lambda self: self.env.company)
    th_own_image = fields.Image(string="image")
    th_number_of_requests = fields.Integer(string='Số lượng yêu cầu')
    th_feedback_of_CTV = fields.Selection([
        ('agree', 'Đồng ý'),
        ('disagree', 'Không đồng ý'),
        ('wait_for_response', 'Chờ phản hồi')],
        default="wait_for_response",
        string="Phản hồi của CTV", required=1, tracking=1)
    th_quantity_done = fields.Integer(string='Số lượng đã làm', compute="_compute_th_quantity_done")
    th_completion_schedule = fields.Integer(string='Tiến độ hoàn thành', compute="_compute_th_completion_schedule")
    th_deadline = fields.Date('Thời hạn', related='th_link_seeding_id.th_deadline')
    th_note = fields.Text(string='Lưu ý', related='th_product_aff_id.th_note')
    th_seo_description = fields.Text(string='Mô tả ngắn', related='th_product_aff_id.th_seo_description')
    th_title = fields.Char(string='Tiêu đề')
    th_the_remaining_amount = fields.Integer(string='Số lượng còn lại', compute="_compute_th_the_remaining_amount")
    th_product_aff_id = fields.Many2one("th.product.aff", string="Sản phẩm")
    th_collaborator_group_id = fields.Many2one("th.collaborator.group", string="Cộng tác viên")
    th_payment_batch_id = fields.Many2one('th.payment.batch')
    th_pay_id = fields.Many2one('th.pay')
    th_product_image_ids = fields.One2many('th.product.image', 'th_product_aff_id', string="Ảnh sản phẩm", readonly=True, related="th_product_aff_id.th_product_image_ids")
    th_count_link_ids = fields.One2many('th.click.date', 'th_link_tracker_id')

    def action_link_seeding(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Link Seeding'),
            'res_model': 'link.tracker',
            'view_mode': 'form',
            'view_id': self.env.ref('th_affiliate.th_link_tracker_view_form').id,
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }
        return action

    # @api.depends('th_aff_partner_id')
    # def _compute_th_title(self):
    #     for rec in self:
    #         if rec.th_aff_partner_id:
    #             rec.th_title = "Link seeding của %s" % rec.th_aff_partner_id.display_name
    #         elif rec.campaign_id and rec.th_aff_partner_id:
    #             rec.th_title = "Link seeding của %s chiến dịch %s" % (rec.th_aff_partner_id.display_name, rec.campaign_id.display_name)
    #         else:
    #             rec.th_title = False

    def _compute_th_the_remaining_amount(self):
        for rec in self:
            rec.th_the_remaining_amount = rec.th_number_of_requests - rec.th_completion_schedule

    @api.depends('th_post_link_ids')
    def _compute_th_quantity_done(self):
        for rec in self:
            rec.th_quantity_done = len(rec.th_post_link_ids)

    @api.depends('th_post_link_ids')
    def _compute_th_completion_schedule(self):
        for rec in self:
            rec.th_completion_schedule = len(rec.th_post_link_ids.search([('state', '=', 'correct_request'), ('link_tracker_id', '=', rec.id)]))

    def get_contract_template(self):
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': 'th_affiliate/static/src/excel/link_bai_dang.xlsx',
        }

    def th_action_view_statistics(self):
        action = self.env['ir.actions.act_window']._for_xml_id('th_affiliate.th_session_user_action')
        action['domain'] = [('th_link_tracker_id', '=', self.id)]
        action['context'] = dict(self._context, create=False)
        return action

    def th_action_click_date_statistics(self):
        action = self.env['ir.actions.act_window']._for_xml_id('th_affiliate.th_click_date_action')
        action['domain'] = [('th_link_tracker_id', '=', self.id)]
        action['context'] = dict(self._context, create=False)
        return action

    @api.depends('th_session_user_ids.th_link_tracker_id')
    def _compute_th_session_user_ids(self):
        if self.ids:
            clicks_data = self.env['th.session.user']._read_group(
                [('th_link_tracker_id', 'in', self.ids)],
                ['th_link_tracker_id'],
                ['th_link_tracker_id']
            )
            mapped_data = {m['th_link_tracker_id'][0]: m['th_link_tracker_id_count'] for m in clicks_data}
        else:
            mapped_data = dict()
        for tracker in self:
            tracker.th_count_user = mapped_data.get(tracker.id, 0)

    @api.depends('th_post_link_ids.th_expense')
    def _amount_all(self):
        total = 0
        link_posts = self.th_post_link_ids
        for link_post in link_posts:
            if link_post.th_expense and link_post.state == "correct_request":
                total = total + float(link_post.th_expense)
        self.th_total_cost = total

    def action_cost_closing(self):
        for rec in self:
            if rec.th_post_link_ids.filtered(lambda p: p.state == 'pending'):
                raise ValidationError(_("Vui lòng duyệt toàn bộ các bài đăng của cộng tác viên!"))
            if rec.th_post_link_ids.filtered(lambda p: p.state == 'correct_request' and not p.th_pricelist_ids):
                raise ValidationError(_("Vui lòng nhập đủ 'Hệ số' cho các bài đăng 'Đúng yêu cầu'!"))
            if rec.th_feedback_of_CTV != 'agree':
                raise ValidationError(_("Chỉ được phép tạm chốt khi có sự đồng ý từ phản hồi của cộng tác viên!"))

            pay_id = self.env['th.pay'].search([('th_partner_id', '=', rec.th_aff_partner_id.id), ('state', '=', 'pending')], limit=1, order='id desc')
            post_link_ids = rec.th_post_link_ids.filtered(lambda p: p.state == 'correct_request' and p.th_pricelist_ids)
            if not pay_id and post_link_ids:
                pay_id = self.env['th.pay'].create({
                    'name': _('Phiếu thanh toán cho %s ngày %s', rec.th_aff_partner_id.name, fields.Date.today()),
                    'th_partner_id': rec.th_aff_partner_id.id,
                    'state': 'pending',
                })
            post_link_ids.write({'th_pay_id': pay_id.id})
            rec.write({'th_closing_work': 'cost_closing'})

    def action_acceptance_closing_work(self):
        for rec in self:
            rec.write({'th_closing_work': 'acceptance'})

    def action_draft_closing_work(self):
        for rec in self:
            rec.write({'th_closing_work': 'pending'})

    def unlink(self):
        for rec in self:
            if rec.th_closing_work != 'pending':
                raise ValidationError('Chỉ xóa link ở trang thái chờ nghiêm thu!')
        return super().unlink()

    @api.model
    def create(self, values):
        user_id = self._uid if not values.get('th_aff_partner_id', False) else values.get('th_aff_partner_id', False)
        utm_source_id = values.get('source_id', False)

        if not utm_source_id:
            contact_affiliate = self.env['res.partner'].sudo().search([('user_ids.id', '=', user_id)], limit=1)
            url = values.get('url', False)
            domain = [('th_aff_partner_id', '=', contact_affiliate.id), ('url', '=', url)]
            link_exit = self.sudo().search(domain)
            if not link_exit:
                utm_source = self.env['utm.source'].sudo().search([('name', '=', contact_affiliate.th_affiliate_code)])
                if not utm_source:
                    utm_source_id = utm_source.sudo().create({'name': contact_affiliate.th_affiliate_code}).id
                else:
                    utm_source_id = utm_source.id
            else:
                raise ValidationError(_('Link đã tồn tại!'))

        values['source_id'] = utm_source_id
        values['th_aff_partner_id'] = contact_affiliate.id if not values.get('th_aff_partner_id', False) else values.get('th_aff_partner_id', False)
        return super(LinkTracker, self).create(values)

    def write(self, values):
        res = super(LinkTracker, self).write(values)
        url = values.get('url', False)
        for rec in self:
            if rec.th_closing_work != 'pending' and url:
                raise ValidationError(_('Chỉ có thể chỉnh sửa link đang chờ nghiệm thu'))
            if rec.create_uid and rec.create_uid.id != self._uid and url:
                raise ValidationError(_('Link này không thuộc quyển sở hữu của bạn'))
        return res

    def th_action_post_link_import(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'import',
            'name': _('Import Link'),
            'params': {
                'context': self.env.context,
                'model': 'th.post.link',
            }
        }

    @api.onchange('th_product_aff_id')
    def _onchange_value_url(self):
        for rec in self:
            if rec.th_product_aff_id:
                rec.url = str(rec.th_product_aff_id.th_link)
            else:
                rec.url = False

    @api.onchange('campaign_id')
    def onchange_value_product(self):
        for rec in self:
            if not rec.campaign_id:
                rec.th_product_aff_id = False
