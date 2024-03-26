import json

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class th_batch_create_link_wizard(models.TransientModel):
    _name = "th.create.link.wizard"
    _description = "Batch update for "
    _check_company_auto = True

    user_ids = fields.Many2many('res.users', string='Công tác viên')
    th_domain = fields.Char(compute='_compute_th_domain')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def create_multi_update(self):
        ids = self.env.context['active_ids']
        th_product_aff = self.env["th.product.aff"].browse(ids)
        user_ids = self.user_ids
        if not user_ids:
            user_ids = self.env.user
        for user_id in user_ids:
            for pro_item in th_product_aff:
                pro_item.action_create_link_tracker(user_id.id)

    @api.depends('company_id', 'user_ids')
    def _compute_th_domain(self):
        for rec in self:
            domain = []
            if rec.company_id:
                domain.append(('user_ids', 'in', rec.company_id.user_ids.ids))
            rec.th_domain = json.dumps(domain)
