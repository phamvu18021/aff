from odoo import models, _

class SampleImportXlsx(models.TransientModel):
    _name = 'report.th_affiliate.sample_import_xlsx'
    _description = "sample import Xlsx"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        for obj in partners:
            sheet = workbook.add_worksheet('sheet1')
            sheet2 = workbook.add_worksheet('sheet2')
            self.generate_header(workbook, sheet,sheet2)
            self.generate_data(workbook, sheet)
            self.format_xlsx_sheet(sheet,sheet2)

    def generate_header(self, workbook, sheet,sheet2):
        sub_header = workbook.add_format({'bold': True, 'font_name': 'Times New Roman', 'font_size': 13, 'border': 1})
        sheet2.write(0, 0, "Tên", sub_header)
        sheet2.write(0, 1, "Loại", sub_header)

        sheet.write(0, 0, "Tên Khách Hàng", sub_header)
        sheet.write(0, 1, "Email", sub_header)
        sheet.write(0, 2, "Số Điện Thoại ", sub_header)
        sheet.write(0, 3, "Mô tả", sub_header)
        sheet.write(0, 4, "Loại", sub_header)
        sheet.write(0, 5, "Kho", sub_header)


    def generate_data(self, workbook, sheet):
        row_index = 1
        record_with_largest_id = self.env['th.opportunity.ctv'].sudo().search([], order='id desc', limit=1)
        data_format = workbook.add_format(
            {'font_name': 'Times New Roman', 'font_size': 13, 'num_format': '@', 'right': 1, 'bottom': 3})
        if record_with_largest_id.th_type_ctv == 'short_term':
            th_type_value_ctv = 'Ngắn hạn'
        elif record_with_largest_id.th_type_ctv == 'long_term':
            th_type_value_ctv = 'Dài hạn'
        elif record_with_largest_id.th_type_ctv == 'partner':
            th_type_value_ctv = 'Đối tác'


        if record_with_largest_id:
            sheet.write(row_index, 0, record_with_largest_id.name or '', data_format)
            sheet.write(row_index, 1, record_with_largest_id.th_mail or '', data_format)
            sheet.write(row_index, 2, record_with_largest_id.th_phone_number or '',data_format)
            sheet.write(row_index, 3, record_with_largest_id.th_description or '',data_format)
            sheet.write(row_index, 4, th_type_value_ctv or '', data_format)  #
            warehouse_name = record_with_largest_id.th_warehouse.name if record_with_largest_id.th_warehouse else ''
            sheet.write(row_index, 5, warehouse_name, data_format)


    def format_xlsx_sheet(self, sheet,sheet2):
        sheet2.set_column(0, 0, 22)
        sheet2.set_column(1, 1, 35)

        sheet.set_column(0, 0, 22)
        sheet.set_column(1, 1, 35)
        sheet.set_column(2, 2, 35)
        sheet.set_column(3, 3, 35)
        sheet.set_column(4, 4, 35)
        sheet.set_column(5, 5, 30)


    def action_report_excel(self):
        res = self.sudo().create({})
        return res.id