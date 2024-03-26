import xmlrpc.client
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ThOpportunityCTV(models.Model):
    _name = "th.opportunity.ctv"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Cơ hội CTV"
    _check_company_auto = True

    name = fields.Char("Tên cơ hội", default='Mới')
    th_customer_code = fields.Char("Mã Khách Hàng")
    th_customer = fields.Char("Tên Khách Hàng")
    th_phone = fields.Char("Số điện thoại")
    th_email = fields.Char("Email")
    th_description = fields.Text("Mô tả")
    th_stage = fields.Char("Level")
    th_status_category = fields.Char("Nhóm trạng thái")
    th_status_detail = fields.Char("Trạng thái thái chi tiết")
    th_reason = fields.Char("Lý do ngừng chăm sóc")
    th_product_category = fields.Char("Nhóm sản phẩm")
    th_products = fields.Char("Sản phẩm")
    th_warehouse_id = fields.Many2one('th.warehouse', string='Kho')
    th_pricelist_id = fields.Many2one('th.pricelist', string='Hệ số hoa hồng', tracking=True)
    th_paid = fields.Boolean('Đã thanh toán', tracking=True)
    th_level_up_date = fields.Date('Ngày lên level')
    th_majors = fields.Char('Ngành đăng ký')
    th_university = fields.Char('Trường')
    th_payment_batch_id = fields.Many2one('th.payment.batch')
    th_pay_id = fields.Many2one('th.pay')
    th_partner_id = fields.Many2one('res.partner', string="Cộng tác viên",
                                    default=lambda self: self.env.user.partner_id)
    th_affiliate_code = fields.Char(string='Mã tiếp thị liên kết', related="th_partner_id.th_affiliate_code",
                                    store=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, string='Đơn vị sở hữu')
    th_lead_id_samp = fields.Char('samp', copy=False)
    th_dup_description = fields.Char('Mô tả trùng')
    th_dup_state = fields.Selection(string='Trạng thái', selection=[('processing', 'Đang xử lý'), ('processed', 'Đã xử lý')], default='processing')
    th_dup_result = fields.Char("Kết quả")
    th_caregiver = fields.Char("Người chăm sóc")
    active = fields.Boolean(default=True)

    def th_action_synchronize_data(self, get_ctv=None):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'samp')], limit=1, order='id desc')
        if not server_api:
            return False
        try:
            result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
            db = server_api.th_db_api
            uid_api = server_api.th_uid_api
            password = server_api.th_password
            data_prm_leads = []
            data_apm_leads = []
            data_code_aff = self.env.company.user_ids.mapped('partner_id').filtered((lambda partner: partner.th_affiliate_code)).mapped('th_affiliate_code')
            if get_ctv:
                data_code_aff = self.env['res.partner'].search([('th_affiliate_code', '!=', False)]).mapped('th_affiliate_code')
                return data_code_aff

            # for rec in self.search([('th_paid', '=', False)]):
            #     if self.env.ref('th_affiliate.th_prm_module').id in rec.th_warehouse_id.th_module_ids.ids:
            #         synchronize_data = {
            #             'id': rec.id,
            #             'name_customer': rec.name,
            #             'th_affiliate_code': rec.th_affiliate_code,
            #         }
            #         data_prm_leads.append(synchronize_data)
            #
            #     if self.env.ref('th_affiliate.th_apm_module').id in rec.th_warehouse_id.th_module_ids.ids:
            #         synchronize_data_apm = {
            #             'id': rec.id,
            #             'name_customer': rec.name,
            #             'th_affiliate_code': rec.th_affiliate_code,
            #         }
            #         data_apm_leads.append(synchronize_data_apm)

            # if data_prm_leads or data_code_aff:
            if data_code_aff:
                result_apis.execute_kw(db, uid_api, password, 'prm.lead', 'action_synchronize_data_api', [[], data_code_aff])
                result_apis.execute_kw(db, uid_api, password, 'th.apm', 'check_synchronization', [[], data_code_aff])
                result_apis.execute_kw(db, uid_api, password, 'crm.lead', 'setup_data_crm', [[], data_code_aff])
        except Exception as e:
            raise ValidationError(e)

        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def th_send_data(self, records):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'samp')], limit=1, order='id desc')
        if not server_api:
            return records
        result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
        db = server_api.th_db_api
        uid_api = server_api.th_uid_api
        password = server_api.th_password
        for record in records:
            contact = False
            if not record.th_phone and record.th_email:
                contact = self.search([('id', '!=', record.id), ('name', '=', record.name), ('th_email', '=', record.th_email)])
            elif not record.th_email and record.th_phone:
                contact = self.search([('id', '!=', record.id), ('name', '=', record.name), ('th_phone', '=', record.th_phone)])
            elif record.th_phone and record.th_email:
                contact = self.search([('id', '!=', record.id), ('name', '=', record.name), '|',
                                       ('th_email', '=', record.th_email), ('th_phone', '=', record.th_phone)])
            if contact:
                raise ValidationError('Cơ hội đã tồn tại!')
            data_to_send = {
                'id': record.id,
                'name_customer': record.th_customer,
                'th_ownership_unit_code': record.company_id.th_code if record.company_id else '',
                'th_description': record.th_description,
                'th_affiliate_code': record.th_affiliate_code,
            }
            if record.th_email:
                data_to_send['th_email'] = record.th_email
            if record.th_phone:
                data_to_send['th_phone'] = record.th_phone
            try:
                if self.env.ref('th_affiliate.th_apm_module').id in record.th_warehouse_id.th_module_ids.ids:
                    data_to_send['th_warehouse_code'] = record.th_warehouse_id.th_code if record.th_warehouse_id else ''
                    th_lead_id_samp = result_apis.execute_kw(db, uid_api, password, 'th.apm', 'create', [data_to_send], {'context': {'aff_apm_lead': 'True'}})
                    record.write({'th_lead_id_samp': th_lead_id_samp})

                if self.env.ref('th_affiliate.th_crm_module').id in record.th_warehouse_id.th_module_ids.ids:
                    data_to_send['th_warehouse_code'] = record.th_warehouse_id.th_code if record.th_warehouse_id else ''
                    th_lead_id_samp = result_apis.execute_kw(db, uid_api, password, 'crm.lead', 'create', [data_to_send], {'context': {'aff_crm_lead': 'True'}})
                    record.write({'th_lead_id_samp': th_lead_id_samp})

                if not record.th_warehouse_id:
                    th_lead_id_samp = result_apis.execute_kw(db, uid_api, password, 'prm.lead', 'create', [data_to_send], {'context': {'aff_prm_lead': 'True'}})
                    record.write({'th_lead_id_samp': th_lead_id_samp})

            except Exception as e:
                print(e)
                if 'Fault' in str(e) and 'Trùng' in e.faultString:
                    raise ValidationError('Cơ hội đã bị trùng!')
                else:
                    raise ValidationError(e)

    @api.model
    def create(self, vals):
        if self._context.get('import_file', False):
            if not vals.get('th_warehouse_id', False) and self._context.get('active_id'):
                vals['th_warehouse_id'] = self._context.get('active_id')

            if not vals.get('th_warehouse_id', False) and not self._context.get('active_id'):
                raise ValidationError(_('Không thể import dữ liệu nếu không có kho!'))
            if not vals.get('company_id', False):
                vals['company_id'] = self._context.get('allowed_company_ids', [False])[0]

        records = super(ThOpportunityCTV, self).create(vals)
        if not self._context.get('th_create', False) and not self._context.get('th_test_import', False):
            self.th_send_data(records)
        return records

    # Các hàm đẩy cơ hội từ SamP thì gọi vào hàm này.
    def receive_data(self, data):
        data['th_warehouse_id'] = self.env['th.warehouse'].search([('th_code', '=', self._context.get('origin', 'ko có origin'))], limit=1).id
        company_id = False
        partner = self.env['res.partner'].search([('th_affiliate_code', '=', data.get('th_affiliate_code'))])
        if not partner:
            return {'code': '404', 'message': 'Không tìm thấy công tác viên'}

        if self._context.get('company_code', False):
            company_id = self.env.company.search([('th_code', '=', self._context.get('company_code'))]).id

        if partner and not company_id:
            company_id = self.env['res.partner'].search(
                [('th_affiliate_code', '=', data.get('th_affiliate_code'))]).user_ids.company_id.id

        data['company_id'] = company_id
        rec = self.env['th.opportunity.ctv']
        if self._context.get('th_create', False):
            rec = self.env['th.opportunity.ctv'].create(data)
            # return {'id': rec.id, 'code': '201', 'message': 'Tạo thành công'}
        else:
            rec = self.search([('id', 'in', self._context.get('th_opportunity_aff_id'))])
            rec.write(data)
        return {'id': rec.id, 'code': '201', 'message': 'Tạo thành công'}

    # def write(self, vals):
    #     vals['company_id'] = self.env['res.partner'].search(
    #         [('th_affiliate_code', '=', vals.get('th_affiliate_code'))]).user_ids.company_id.id
    #     return super().write(vals)
