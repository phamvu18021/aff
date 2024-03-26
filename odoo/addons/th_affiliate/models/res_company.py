
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    state = fields.Boolean(default=False, string="Là công ty mặc định")
    th_code = fields.Char('Mã đơn vị sở hữu')

    @api.constrains('state')
    def _check_is_company(self):
        if len(self.search([('state', '=', True)]).mapped('state')) > 1:
            raise ValidationError(_('Đã có công ty mặc định!'))

    def write(self, values):
        list_user = self.user_ids.ids
        user_ids = values.get('user_ids', False)
        company_base = self.sudo().search([('state', '=', True)])

        if not user_ids:
            return super(ResCompany, self).write(values)

        # xóa khỏi company(self)
        # cho vào công ty mặc định với company_ids == 0
        # nếu len(company_ids) >= 1 chuyển company_id về company_id != self.id
        check_user = list(set(list_user) ^ set(user_ids[0][2]))
        if company_base and len(list_user) > len(user_ids[0][2]) and self != company_base:
            if check_user:
                for rec in self.env['res.users'].sudo().search([('id', 'in', check_user)]):
                    if len(rec.company_ids) - 1 == 0:
                        rec.sudo().write({'company_ids': [[4, company_base.id]], 'company_id': self.id})
                    else:
                        com_default = list(set(rec.company_ids.ids) ^ set(self.ids))
                        rec.sudo().write({'company_id': com_default[0]})

        # Thêm vào company(self)
        # Xóa khỏi công ty mặc định
        elif len(list_user) < len(user_ids[0][2]) and company_base:
            users = self.env['res.users'].sudo().search([('id', 'in', check_user)])
            check_user_remove = list(set(company_base.user_ids.ids) ^ set(check_user))
            for rec in users:
                if check_user_remove and company_base.id in rec.company_ids.ids:
                    rec.sudo().write({'company_ids': [[3, company_base.id], [4, self.id]], 'company_id': self.id})
        return super(ResCompany, self).write(values)
