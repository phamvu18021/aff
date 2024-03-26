import xmlrpc

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


READONLY_STATES = {
    'deploy': [('readonly', True)],
    'close': [('readonly', True)],
}
th_type = [('aff', 'Affiliate'), ('samp', 'Sambala production'), ('vmc', 'VMC')]
state = [('draft', 'Nháp'), ('deploy', 'Triển khai'), ('close', 'Đóng')]


class ThApiServer(models.Model):
    _name = 'th.api.server'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'th_url_api'
    _description = "External server"

    th_url_api = fields.Char('URL server', required=1, states=READONLY_STATES)
    th_user_api = fields.Char('Tài khoản sử dụng API', required=1, states=READONLY_STATES)
    th_password = fields.Char('Key API(password)', required=1, states=READONLY_STATES)
    th_db_api = fields.Char('Cơ sở dữ liệu', required=1, states=READONLY_STATES)
    th_uid_api = fields.Char('Tài khoản kết nối', copy=0)
    state = fields.Selection(selection=state, tracking=True, default='draft')
    th_description = fields.Text("Mô tả")
    th_type = fields.Selection(selection=th_type, tracking=True, required=1, string='Loại', states=READONLY_STATES)

    def action_test_server(self):
        for rec in self:
            try:
                common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(rec.th_url_api))
                result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(rec.th_url_api))
                common.version()
                user_id = common.authenticate(rec.th_db_api, rec.th_user_api, rec.th_password, {})
                if not user_id:
                    raise ValidationError(_(f'Không tìm thấy tài khoản để kết nối tới server!'))

                if rec.th_type == 'samp':
                    res_partner = result_apis.execute_kw(rec.th_db_api, user_id, rec.th_password, 'res.partner', 'check_access_rights', ['read'], {'raise_exception': False})
                    if not res_partner:
                        raise ValidationError('Tài khoản không có quyền truy cập module Liên hệ(res.partner)!')

                    prm_lead = result_apis.execute_kw(rec.th_db_api, user_id, rec.th_password, 'prm.lead', 'check_access_rights', ['read'], {'raise_exception': False})
                    if not prm_lead:
                        raise ValidationError('Tài khoản không có quyền truy cập module PRM(prm.lead)!')

                    crm_lead = result_apis.execute_kw(rec.th_db_api, user_id, rec.th_password, 'crm.lead', 'check_access_rights', ['read'], {'raise_exception': False})
                    if not crm_lead:
                        raise ValidationError('Tài khoản không có quyền truy cập module CRM(crm.lead)!')

                    model_sale_order = result_apis.execute_kw(rec.th_db_api, user_id, rec.th_password, 'sale.order', 'check_access_rights', ['read'], {'raise_exception': False})
                    if not model_sale_order:
                        raise ValidationError('Tài khoản không có quyền truy cập module Bán hàng(sale.order)!')

                    apm_lead = result_apis.execute_kw(rec.th_db_api, user_id, rec.th_password, 'th.apm', 'check_access_rights', ['read'], {'raise_exception': False})
                    if not apm_lead:
                        raise ValidationError('Tài khoản không có quyền truy cập module APM(th.apm)!')

            except Exception as e:
                if 'Object' in str(e) and "doesn't exist" in str(e):
                    raise ValidationError(f"Bảng '{e.faultString.split(' ')[1]}' không tồn tại trong cơ sở dữ liệu {self.th_db_api}")

                if type(e) == ValidationError:
                    raise ValidationError(e)

            rec.write({'th_uid_api': user_id})

        message = _("Kết nối thành công")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_deploy(self):
        if self.state != 'draft':
            raise ValidationError(_("Trạng thái phải là nháp!"))
        if not self.th_uid_api:
            self.action_test_server()

        if self.th_type in self.search([('id', '!=', self.id)]).mapped('th_type'):
            raise ValidationError(_('không thể có 2 server api cùng loại được triển khai!'))

        self.write({
            'state': 'deploy'
        })

    def action_draft(self):
        if self.state != 'close':
            raise ValidationError(_("Trạng thái phải là đóng"))
        self.write({
            'state': 'draft'
        })

    def action_close(self):
        if self.state != 'deploy':
            raise ValidationError(_("Trạng thái phải là triển khai"))
        self.write({
            'state': 'close'
        })

    def write(self, values):
        if values.get('th_url_api', False) \
                or values.get('th_user_api', False) or values.get('th_password', False) \
                or values.get('th_db_api', False) or values.get('th_type', False):
            values['th_uid_api'] = False
        return super(ThApiServer, self).write(values)
