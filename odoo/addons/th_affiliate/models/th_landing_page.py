from odoo import models, fields,api


class ThLandingPage(models.Model):
    _name = "th.landing.page"
    _description = "day la trang đích"
    _rec_name = 'th_url_fb'

    th_url_fb = fields.Char("Link facebook")
    medium_id = fields.Many2one('utm.medium', string="Kênh", required=1)
    qty = fields.Integer(string="Số lượng thành viên")
    th_classify = fields.Char(string="Phân loại")
    gr_code_seeding = fields.Char("Mã đích seeding")


    @api.onchange('th_url_fb')
    def _compute_link_gr(self):
        for rec in self:
            if rec.th_url_fb:
                print(rec.th_url_fb.rsplit("/")[4])
                rec.gr_code_seeding = rec.th_url_fb.rsplit("/")[4]


