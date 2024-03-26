from odoo import models, fields


class ThUtmMedium(models.Model):
    _name = "th.utm.medium"
    _description = "Th Utm Medium do nếu 1 kênh có nhiều link seeding ko thể điền số lượng mặc định cho kênh gốc được"

    th_number_of_requests = fields.Integer(string="Số lượng yêu cầu", default=1)
    medium_id = fields.Many2one('utm.medium', string="Kênh", required=1)
    th_link_seeding_id = fields.Many2one('th.link.seeding')
    th_remaining_number = fields.Integer(string="Số lượng yêu cầu còn lại", default=-1)
