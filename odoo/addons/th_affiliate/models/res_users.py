from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    th_team_leader_ids = fields.Many2many(comodel_name="res.users", relation="th_aff_leader_ref", column1="th_aff_user", column2="th_aff_leader", string="Đội trưởng", store=True)

    @api.model
    def create(self, values):
        user = super(ResUsers, self).create(values)
        if self.env['res.company'].sudo().search_count([]) <= 1:
            return user
        company = False
        th_own_code = values.get('th_own_code_samp', False)
        company_base = self.env['res.company'].sudo().search([('state', '=', True)])
        if not company_base:
            company_base = self.env.ref('base.main_company')
        if th_own_code:
            company = self.env['res.company'].sudo().search([('th_code', '=', th_own_code), ('state', '!=', True)], limit=1)
        user.sudo().write({'company_ids': [[6, 0, [company_base.id]]], 'company_id': company_base.id})
        if company and company_base.id != company.id and company_base.id in user.company_ids.ids:
            user.sudo().write({'company_ids': [[3, company_base.id], [4, company.id]], 'company_id': company.id})
        return user

    def write(self, values):
        result = super(ResUsers, self).write(values)
        companies = values.get('company_ids', False)
        if companies:
            for company in companies:
                for rec in self:
                    if company[0] == 6:
                        rec.company_id = company[2][0]
                    if company[0] == 4:
                        rec.company_id = company[1]

        return result
