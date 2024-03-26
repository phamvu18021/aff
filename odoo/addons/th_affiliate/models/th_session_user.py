import uuid
from odoo import models, fields, api, _


class ThSessionUser(models.Model):
    _name = "th.session.user"
    _rec_name = 'name'
    _description = "Phiên truy cập của người dùng"

    name = fields.Char("Tên")
    th_user_client_code = fields.Char(default=lambda self: self._default_uuid(), required=True, readonly=True, copy=False, string='Mã code người dùng')
    th_link_tracker_id = fields.Many2one('link.tracker')
    th_web_click_ids = fields.One2many('th.web.click', 'th_session_user_id')
    th_referrer_link = fields.Char('')
    th_website = fields.Char('Tên website')

    @api.model
    def _default_uuid(self):
        return str(uuid.uuid4())

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('customer.visitor.name')
        return super(ThSessionUser, self).create(values)


class ThWebClick(models.Model):
    _name = "th.web.click"
    _description = "Lượt click từ website"

    name = fields.Char('Tên website')
    th_session_user_id = fields.Many2one('th.session.user')
    th_screen_time_start = fields.Datetime('start')
    th_screen_time_end = fields.Datetime('end')
    th_total_time = fields.Char('Tổng giờ')


class ThClickDate(models.Model):
    _name = "th.click.date"
    _description = "Lượt click theo ngày"
    _rec_name = "th_date"

    th_date = fields.Date('Thời gian')
    th_click = fields.Integer('Số lượng')
    th_referrer = fields.Char('Referer', help="Được điều chuyển từ(Facebook, Email, ...)")
    th_link_tracker_id = fields.Many2one('link.tracker', 'Link seeding')
    th_aff_partner_id = fields.Many2one('res.partner', related='th_link_tracker_id.th_aff_partner_id', string="Cộng tác viên", store=True)
    th_affiliate_code = fields.Char(string="Mã Tiếp Thị Liên Kết", related='th_aff_partner_id.th_affiliate_code', store=True)
