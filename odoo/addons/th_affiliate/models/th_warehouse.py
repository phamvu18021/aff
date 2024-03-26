import xmlrpc

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ThWarehouse(models.Model):
    _name = "th.warehouse"
    _description = "day la nha kho"

    name = fields.Char(string='Tên')
    th_description = fields.Text(string="Mô tả")
    th_code = fields.Char(string="Mã rút gọn")
    th_module_ids = fields.Many2many(comodel_name='therp.module', column1='th_module_id', column2='th_warehouse_id', string='Phân hệ')
    color = fields.Integer("Color Index", default=0)
    active = fields.Boolean(default=True)

    def th_action_view_lead(self):
        if self._context.get('oder',False):
            action = self.env["ir.actions.actions"]._for_xml_id("th_affiliate.th_aff_order_action")
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("th_affiliate.th_opportunity_ctv_action")
        action['display_name'] = self.name
        return action

    @api.model
    def create(self, values):
        print(values)
        if self._context.get('module', False):
            th_module_ids = self.env['therp.module'].search([('name', 'in', self._context.get('module', []))]).mapped('id')
            values['th_module_ids'] = [[6, 0, th_module_ids]]
        return super(ThWarehouse, self).create(values)

    def write(self, values):
        if self._context.get('module', False):
            th_module_ids = self.env['therp.module'].search([('name', 'in', self._context.get('module', []))]).mapped('id')
            values['th_module_ids'] = [[6, 0, th_module_ids]]
        return super(ThWarehouse, self).write(values)

    def th_sync_warehouse(self):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'samp')], limit=1, order='id desc')
        if not server_api:
            raise ValidationError(_('Không có API kết nối tới Sambala Production!'))
        try:
            result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
        except Exception as e:
            raise e

        db = server_api.th_db_api
        uid_api = server_api.th_uid_api
        password = server_api.th_password

        try:
            result_apis.execute_kw(db, uid_api, password, 'th.origin', 'update_th_warehouse', [[], [], 'write'], {'context': {'sync': True}})
        except Exception as e:
            raise e
