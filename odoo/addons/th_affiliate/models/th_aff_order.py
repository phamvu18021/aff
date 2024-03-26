import json
import xmlrpc

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

vmc_state = [('draft', 'Chờ thanh toán'), ('processing', 'Đang xử lý'), ('completed', 'Đã hoàn thành'), ('canceled', 'Đã hủy'), ('refund', 'Đã hoàn lại tiền')]


class ThAffOrder(models.Model):
    _name = "th.aff.order"
    _description = "Đơn hàng Affiliate"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True
    _order = 'th_date_order'

    name = fields.Char('Đơn hàng', required=1)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    th_partner_id = fields.Many2one('res.partner', string="Cộng tác viên")
    th_price = fields.Char('Tổng đơn hàng')
    th_state_vmc = fields.Selection(selection=vmc_state, string="Trạng thái đơn hàng VMC", default='draft')
    th_customer = fields.Char('Khách hàng')
    th_customer_code = fields.Char('Mã khách hàng')
    th_date_order = fields.Datetime('Ngày báo giá')
    th_utm_source = fields.Char('Cộng tác viên')
    th_pricelist_id = fields.Many2one('th.pricelist', string='Hệ số hoa hồng', tracking=True)
    th_utm_campaign = fields.Char('Chiến dịch')
    th_utm_medium = fields.Char('Kênh')
    th_manager_id = fields.Many2one('res.users', 'Nhóm trưởng')
    th_product_ids = fields.One2many('th.product.order', 'th_aff_order_id', string='Sản phẩm order')
    state = fields.Selection(selection=[('unpaid', 'Chưa thanh toán'), ('paid', 'Đã thanh toán'), ('cancel', 'Hủy')], string='Trạng thái thanh toán cho CTV', default='unpaid', tracking=1)
    th_order_vmc_id = fields.Char('id đơn hàng VMC')
    th_api_state = fields.Boolean(default=True)
    th_warehouse_id = fields.Many2one('th.warehouse', string='Kho')
    th_affiliate_code = fields.Char(string="Mã Tiếp Thị Liên Kết", readonly=False, related='th_partner_id.th_affiliate_code')

    def th_action_sync_orders(self):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'samp')], limit=1, order='id desc')
        if not server_api:
            raise ValidationError(_('Không có API kết nối tới Sambala Production!'))
        try:
            result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
        except Exception as e:
            raise ValidationError(e)

        sync_orders = [int(id) for id in self.search([('state', '=', 'unpaid')]).mapped('th_order_vmc_id')]
        # sync_partner = self.env['res.partner'].search([('th_affiliate_code', '!=', False)]).mapped('th_affiliate_code')
        sync_partner = self.env.company.user_ids.mapped('partner_id').filtered((lambda partner: partner.th_affiliate_code)).mapped('th_affiliate_code')
        if not sync_orders and not sync_partner:
            raise ValidationError(_('Không có đơn hàng cần đồng bộ'))
        db = server_api.th_db_api
        uid_api = server_api.th_uid_api
        password = server_api.th_password

        try:
            orders = result_apis.execute_kw(db, uid_api, password, 'sale.order', 'check_synchronization_aff_sale_order', [[], sync_partner])
        except Exception as e:
            raise ValidationError(e)

    def action_paid(self):
        for rec in self:
            rec.state = 'paid'

    def action_unpaid(self):
        for rec in self:
            rec.state = 'unpaid'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    def receive_data_order(self, data):
        if self._context.get('th_create', False):
            data['th_warehouse_id'] = self.env['th.warehouse'].search([('th_code', '=', self._context.get('origin', 'ko có origin'))], limit=1).id
            company_id = False
            partner = self.env['res.partner'].search([('th_affiliate_code', '=', data.get('th_affiliate_code'))])
            if not partner:
                return {'code': '404', 'message': 'Không tìm thấy công tác viên!'}

            if self._context.get('company', False):
                company_id = self.env.company.search([('th_code', '=', self._context.get('company', 'Không có company'))]).id

            if partner and not company_id:
                company_id = partner.user_ids.company_id.id

            data['company_id'] = company_id
            data['th_partner_id'] = partner.id
            rec = self.env['th.aff.order'].create(data)
            return {'id': rec.id, 'code': '201', 'message': 'Tạo thành công!'}
        else:
            rec = self.search([('id', 'in', self._context.get('th_api_aff_order_id'))])
            rec.write(data)
            return {'id': rec.id, 'code': '201', 'message': 'Chỉnh sửa thành công!'}


class ThProductOrder(models.Model):
    _name = "th.product.order"
    _description = "Sản phẩm của đơn hàng"
    _check_company_auto = True

    name = fields.Char('Tên sản phẩm')
    th_quantity = fields.Char('Số lượng')
    th_price = fields.Char('Giá')
    th_aff_order_id = fields.Many2one('th.aff.order', 'Đơn hàng')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    th_product_vmc_id = fields.Char('id sản phẩm VMC')
