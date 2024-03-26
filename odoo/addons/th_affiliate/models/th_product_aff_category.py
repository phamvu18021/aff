from odoo import tools, models, fields, api, _
from collections import defaultdict

from odoo.exceptions import ValidationError

URL_MAX_SIZE = 10 * 1024 * 1024


class ThProductAffCategory(models.Model):
    _name = 'th.product.aff.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _parent_name = "th_parent_id"
    _parent_store = True
    _rec_name = 'th_complete_name'
    _order = 'th_complete_name'
    _description = "Danh mục sản phẩm affiliate"

    name = fields.Char("Tên nhóm", index='trigram', required=True)
    th_parent_id = fields.Many2one('th.product.aff.category', 'Nhóm cha', index=True, ondelete='cascade', domain="[('id', '!=', id)]")
    th_complete_name = fields.Char('Complete Name', compute='_compute_th_complete_name', recursive=True, store=True)
    parent_path = fields.Char(index=True, unaccent=False)
    th_child_id = fields.One2many('th.product.aff.category', 'th_parent_id', 'Child Categories')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    th_product_category_samp = fields.Integer()

    @api.onchange('name')
    def onchange_name_category(self):
        for rec in self:
            search_name = self.sudo().search([('name', '=', rec.name), ('company_id', '=', self.env.company.id)])
            if search_name and not rec.ids:
                raise ValidationError("The category name already exists!")
            rec.name = rec.name

    @api.depends('name', 'th_parent_id.th_complete_name')
    def _compute_th_complete_name(self):
        for category in self:
            if category.th_parent_id:
                category.th_complete_name = '%s / %s' % (category.th_parent_id.th_complete_name, category.name)
            else:
                category.th_complete_name = category.name

    @api.model
    def create(self, values):
        parent_name = values.get('th_parent_name', False)
        parent_id = values.get('th_parent_id', False)
        children = values.get('children', [])
        if parent_name:
            exist_parent = self.search([('name', '=', parent_name)])
            values['th_parent_id'] = exist_parent.id if exist_parent else self.create({'name': parent_name, 'th_product_category_samp': parent_id}).id
        values.pop('th_parent_name', False)
        values.pop('children', False)
        values.pop('th_parent_id', False)
        res = super(ThProductAffCategory, self).create(values)
        for rec in self.search([('th_product_category_samp', 'in', children)]):
            rec.write({'th_parent_id': res.id})

        return res

    def write(self, values):
        parent_id = values.get('th_parent_id', False)
        parent_name = values.get('th_parent_name', False)
        if parent_name:
            exist_parent = self.search([('name', '=', parent_name)])
            values['th_parent_id'] = exist_parent.id if exist_parent else self.create({'name': parent_name, 'th_product_category_samp': parent_id}).id
        values.pop('th_parent_name', False)
        values.pop('children', False)
        values.pop('th_parent_id', False)

        return super(ThProductAffCategory, self).write(values)

    def unlink(self):
        if self._context.get('delete_api'):
            for rec in self:
                for rec_ch in rec.th_child_id:
                    rec_ch.write({'th_parent_id': False})
        return super().unlink()

