from odoo import models, fields, _

state_acceptance = [('draft', 'Nháp'), ('deploy', 'Triển khai'), ('close', 'Đóng')]


class ThBill(models.Model):
    _name = 'th.bill'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char('Tên hóa đơn')
