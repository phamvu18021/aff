from odoo import models, fields, api, _
from datetime import timedelta

from odoo.exceptions import ValidationError

state_pricelist = [('deploy', 'Triển khai'), ('close', 'Đóng')]


class ThPricelist (models.Model):
    _name = 'th.pricelist'
    _description = 'bảng giá'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=1, string="Tên Hệ số")
    product_pricelist_id = fields.Integer()
    product_pricelist_item_id = fields.Integer()

    th_cost_factor = fields.Float(string='Chi phí', tracking=True, required=True, default=100, digits=(12, 1))
    th_pricelist_history_ids = fields.One2many('th.pricelist.history', 'th_pricelist_id')
    state = fields.Selection(selection=state_pricelist, string='Status',  required=True, copy=False, tracking=True, default='deploy')

    def action_draft(self):
        self.write({'state': 'draft'})

    def action_deploy(self):
        self.write({'state': 'deploy'})

    def action_close(self):
        self.write({'state': 'close'})

    @api.depends('name', 'th_coefficient_convention')
    def _compute_th_show_name(self):
        for rec in self:
            if rec.th_coefficient_convention:
                rec.th_show_name = '%s / %s' % (rec.name, rec.th_coefficient_convention)
            else:
                rec.th_show_name = rec.name

    @api.model
    def create(self, values):
        product_pricelist_id = values.get('product_pricelist_id', False)
        product_pricelist_items = values.get('product_pricelist_items', False)
        if product_pricelist_id and product_pricelist_items:
            for rec in product_pricelist_items:
                data = {
                    'th_cost_factor': rec.get('fixed_price', False),
                    'th_start_date': fields.Date.today() if not rec.get('date_start', False) else rec.get('date_start', False),
                    'th_end_date': False if not rec.get('date_end', False) else rec.get('date_end', False),
                }
                values = {
                    'name': rec['name'],
                    'product_pricelist_id': product_pricelist_id,
                    'product_pricelist_item_id': rec.get('id', False),
                    'th_cost_factor': rec.get('fixed_price', False),
                    'th_pricelist_history_ids': [(0, 0, data)]
                }
                res = super(ThPricelist, self).create(values)
            return res
        return super(ThPricelist, self).create(values)

    def action_write_api(self, values):
        val = {}
        if self._context.get('delete_one', False):
            history = self.env['th.pricelist.history'].search([('th_pricelist_id', '=', self.id), ('th_end_date', '=', False)], limit=1, order='id DESC')
            history.write({'th_end_date': fields.Date.today() if not history.th_end_date else history.th_end_date})

        if self._context.get('write_all', False):
            product_pricelist_items = values.get('product_pricelist_items', False)
            for rec in product_pricelist_items:
                if self.product_pricelist_item_id == rec.get('id', False):
                    val_item = {
                        'th_cost_factor': rec.get('fixed_price', False),
                        'th_start_date': fields.Date.today() if not rec.get('date_start', False) else rec.get('date_start', False),
                        'th_end_date': False if not rec.get('date_end', False) else rec.get('date_end', False),
                    }
                    history = self.env['th.pricelist.history'].search([('th_pricelist_id', '=', self.id)], limit=1, order='id DESC')
                    val = {
                        'th_cost_factor': rec.get('fixed_price', False),
                        'th_pricelist_history_ids': [(1, history.id, val_item)]
                        # 'th_pricelist_history_ids': [(0, 0, val_item)] if history.th_end_date and history.th_end_date != rec.get('date_end', False) else [(1, history.id, val_item)]
                    }
        if val:
            val['state'] = "deploy"
            values.clear()
            values = val
        return self.write(values)

    def unlink(self):
        for rec in self:
            if self.env['th.post.link'].sudo().search([]).mapped('th_pricelist_ids').id == rec.id:
                raise ValidationError("Không thể xóa chính sách hoa hồng đang được sử dụng!")
        result = super(ThPricelist, self).unlink()
        return result


class ThPricelistHistory(models.Model):
    _name = 'th.pricelist.history'
    _description = 'Lịch sử bảng giá'
    _order = 'id desc'

    th_cost_factor = fields.Float(string='Cost/factor', digits=(12, 1))
    th_start_date = fields.Date(string='Start day')
    th_end_date = fields.Date(string='End date')
    th_pricelist_id = fields.Many2one('th.pricelist')

    # def write(self, values):
    #     result = super(ThPricelistHistory, self).write(values)
    #     #
    #     # for rec in self:
    #     #     th_end_date = values.get('th_end_date', False) or rec.th_end_date
    #     #     if th_end_date and rec.th_start_date > th_end_date:
    #     #         raise ValidationError(_('Time cannot overlap'))
    #     return result
