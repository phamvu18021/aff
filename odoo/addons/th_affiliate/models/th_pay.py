from odoo import tools, models, fields, api, _
from collections import defaultdict
from odoo.exceptions import ValidationError
URL_MAX_SIZE = 10 * 1024 * 1024


class LinkTracker(models.Model):
    _name = 'th.pay'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = "Phiếu thanh toán"

    name = fields.Char('Phiếu chi trả')
    th_partner_id = fields.Many2one('res.partner', string="Cộng tác viên")
    th_post_link_ids = fields.One2many('th.post.link', 'th_pay_id', 'Post link')
    state = fields.Selection(selection=[('pending', 'Chờ duyệt'), ('accept', 'Duyệt & chờ thanh toán'), ('cancel', 'Hủy'), ('paid', 'Đã Thanh toán')], tracking=True)
    th_count_correct_link = fields.Integer('Số bài đăng đúng', default=0, compute="_compute_count_post_link")
    th_count_wrong_link = fields.Integer('Số bài đăng không đạt', default=0, compute="_compute_count_post_link")
    th_paid = fields.Float('Tổng chi phí', default=0, digits=(12, 1))
    th_paid_date = fields.Date('Ngày chi trả')
    th_currency_id = fields.Many2one(comodel_name='res.currency', string='Đơn vị tiền tệ', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    th_opportunity_ctv_ids = fields.One2many('th.opportunity.ctv', 'th_pay_id')
    th_payment_batch_id = fields.Many2one('th.payment.batch', ondelete="cascade")
    th_campaign = fields.One2many('utm.campaign', 'th_pay_id')

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        if res['models'].get('th.post.link'):
            res['models']['th.post.link']['state']['selection'] = res['models']['th.post.link']['state']['selection'][1:3]
        return res

    @api.depends('th_post_link_ids')
    def _compute_count_post_link(self):
        for rec in self:
            rec.th_count_wrong_link = len(rec.th_post_link_ids.filtered(lambda l: l.state == 'wrong_request'))
            rec.th_count_correct_link = len(rec.th_post_link_ids.filtered(lambda l: l.state != 'wrong_request'))
            rec.th_paid = sum(rec.th_post_link_ids.filtered(lambda l: l.state not in ['wrong_request']).mapped('th_expense'))

    def action_pending_pay(self):
        for rec in self:
            rec.state = 'pending'

    def action_cancel_pay(self):
        for rec in self:
            rec.state = 'cancel'
            for record in rec.th_post_link_ids:
                record.th_state_pay = 'cancel'

    def action_accept_pay(self):
        for rec in self:
            rec.state = 'accept'

    def th_action_paid(self):
        for rec in self:
            rec.state = 'paid'
            rec.th_paid_date = fields.Date.today()

            for record in rec.th_post_link_ids:
                record.th_state_pay = 'paid'

    def unlink(self):
        for record in self:
            if record.state != 'pending':
                raise ValidationError("Chỉ có thể xóa các bản ghi ở trạng thái chờ duyệt!")
        super(LinkTracker, self).unlink()
