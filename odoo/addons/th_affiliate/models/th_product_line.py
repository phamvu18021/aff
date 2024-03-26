from odoo import models, fields


class ThProductLine(models.Model):
    _name = "th.product.line"
    _description = "Các dòng sản phẩm"

    name = fields.Char(string='Tên')
