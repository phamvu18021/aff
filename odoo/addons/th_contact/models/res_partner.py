from odoo import fields, models, api, _
import xmlrpc.client

url, db, username, password = 'http://10.10.50.130:8016/', 'base', 'admin', '6bb74aaaae2a0d81b141d4a1bdcfe23f06bd146e'


class ResPartner(models.Model):
    _inherit = "res.partner"

    th_country = fields.Char('Đất nước')
    th_district = fields.Char('Quận/ Huyện')
    th_ward = fields.Char('Phường/ Xã')
    th_customer_code = fields.Char(string="Mã Khách Hàng", readonly=True, tracking=True)
    th_affiliate_code = fields.Char(string="Mã Tiếp Thị Liên Kết", readonly=False, tracking=True)

    th_gender = fields.Selection(string="Giới tính", selection=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác'), ], tracking=True)
    th_phone2 = fields.Char(string="Số điện thoại 2", tracking=True)
    th_citizen_identification = fields.Char(string="Số CMT/ CCCD", tracking=True)
    th_date_identification = fields.Date(string="Ngày cấp CMT/ CCCD", tracking=True)
    th_place_identification = fields.Char(string="Nơi cấp CMT/ CCCD", tracking=True)

    th_bank = fields.Char(string="Ngân hàng", tracking=True)
    th_account_name = fields.Char(string="Tên tài khoản", tracking=True)
    th_account_number = fields.Char(string="Số tài khoản", tracking=True)
    th_account_branch = fields.Char(string="Chi nhánh", tracking=True)
    th_tax_no = fields.Char(string="Mã số thuế", tracking=True)
    th_partner_samp = fields.Char('Contact')
    th_own_code_samp = fields.Char('Mã đơn vị sở hữu')
    th_update_info = fields.Text("Nội dung")

    def action_send_update_info_aff(self):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'samp')], limit=1, order='id desc')
        if not server_api:
            return False
        try:
            result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
        except Exception as e:
            print(e)
            return False

        update_info_aff = {
                "update_info_aff": self.th_update_info,
                "id": self.th_partner_samp,
        }
        db = server_api.th_db_api
        uid_api = server_api.th_uid_api
        password = server_api.th_password

        try:
            exit_uni = result_apis.execute_kw(db, uid_api, password, 'res.partner', 'action_send_update_info',[[],update_info_aff])

        except Exception as e:
            print(e)
    def update_info(self):
        try:
            form_view_id = self.env.ref("th_contact.th_update_info_view_form").id
        except Exception as e:
            form_view_id = False
        return {
            'name': 'Yêu cầu cập nhật',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'views': [(form_view_id, 'form')],
            'res_id': self.id
        }

    @api.model
    def create(self, values):
        th_customer_code = values.get('th_affiliate_code', False)
        if not th_customer_code and values.get('th_pom_id'):
            values['th_customer_code'] = self.env['ir.sequence'].next_by_code('customer.code')
            values['th_affiliate_code'] = self.env['ir.sequence'].next_by_code('affiliate.code')

        return super(ResPartner, self).create(values)

    def write(self, vals):
        return super(ResPartner, self).write(vals)
