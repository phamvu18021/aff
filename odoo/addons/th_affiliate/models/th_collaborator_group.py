import json

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ThCollaboratorGroup(models.Model):
    _name = "th.collaborator.group"
    _description = "Nhóm cộng tác viên"
    _check_company_auto = True

    name = fields.Char('Nhóm cộng tác viên', required=1)
    user_ids = fields.Many2many('res.users', string='Thành viên nhóm')
    user_id = fields.Many2one('res.users', string='Nhóm trưởng')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    th_domain = fields.Char(compute='_compute_th_domain')
    th_domain_user_id = fields.Char(compute='_compute_th_domain')

    def action_find_duplicates(self, x):
        length = len(x)
        duplicates = []
        for i in range(length):
            n = i + 1
            for a in range(n, length):
                if x[i] == x[a] and x[i] not in duplicates:
                    duplicates.append(x[i])
        return duplicates

    @api.depends('company_id')
    def _compute_th_domain(self):
        for rec in self:
            domain1 = []
            domain2 = []
            # 1 user ko được có 2 nhóm CTV
            user_not_in_group = self.search([]).mapped('user_ids').ids

            if rec.company_id:
                domain1.append(('user_ids', 'in', rec.company_id.user_ids.ids))
                if len(user_not_in_group) > 0:
                    domain1.append(('user_ids', 'not in', user_not_in_group))
            rec.th_domain = json.dumps(domain1)

            user_in_group_office = self.env['res.groups'].sudo().search(['|', '|', ('full_name', '=', 'Affiliate / Nhân viên'), ('full_name', '=', 'Affiliate / Quản lý'), ('full_name', '=', 'Affiliate / Quản trị viên')]).users.ids
            list_user = self.action_find_duplicates(user_in_group_office + rec.company_id.user_ids.ids)
            if rec.company_id:
                domain2.append(('user_ids', 'in', rec.company_id.user_ids.ids))
            rec.th_domain_user_id = json.dumps(domain2)

    @api.model
    def create(self, values):
        user_ids = values.get('user_ids', False)
        user_id = values.get('user_id', False)
        if not user_ids or not user_id:
            return super(ThCollaboratorGroup, self).create(values)
        check_user = user_ids[0][2]
        for rec in check_user:
            if user_id:
                self.env['res.partner'].sudo().search([('user_ids', '=', rec)]).write({'th_manager_id': user_id})
        return super(ThCollaboratorGroup, self).create(values)

    def write(self, values):
        list_user = self.user_ids.ids
        user_ids = values.get('user_ids', False)

        if self.user_id and not user_ids:
            for rec in self.mapped('user_ids').ids:
                res = super(ThCollaboratorGroup, self).write(values)
                self.env['res.partner'].sudo().search([('user_ids', '=', rec)]).write({'th_manager_id': self.user_id.id})
            return res

        elif not user_ids and not self.user_id:
            return super(ThCollaboratorGroup, self).write(values)

        check_user = list(set(list_user) ^ set(user_ids[0][2]))
        for rec in check_user:
            # Bỏ người khỏi nhóm
            if len(list_user) > len(user_ids[0][2]):
                self.env['res.partner'].sudo().search([('user_ids', '=', rec)]).write({'th_manager_id': False})

            # Thêm người vào nhóm
            elif len(list_user) < len(user_ids[0][2]) and self.user_id:
                self.env['res.partner'].sudo().search([('user_ids', '=', rec)]).write({'th_manager_id': self.user_id.id})
        return super(ThCollaboratorGroup, self).write(values)

    def unlink(self):
        for record in self:
            self.env['res.partner'].sudo().search([('user_ids', '=', record.mapped('user_ids').ids)]).write({'th_manager_id': False})
        return super(ThCollaboratorGroup, self).unlink()
