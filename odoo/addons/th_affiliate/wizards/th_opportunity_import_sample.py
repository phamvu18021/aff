from odoo import models, fields, api, _
import xlrd
import base64
import xmlrpc.client

from odoo.exceptions import ValidationError
class ThOpportunityImportTemplate(models.TransientModel):
    _name = "th.opportunity.import.template"
    _description = "Mẫu import cơ hội"

    file_import = fields.Binary(string='Upload File', )
    file_name = fields.Char()

    def action_import_opportunity(self):
        try:
            return self.import_opportunity()
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise ValidationError(_("There was an error while importing opportunity, please contact the administrator!"))


    def import_opportunity(self):
        wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.file_import))
        start_row = 2

        sheet = wb.sheet_by_index(1)
        warehouse_data = []
        for i in range(start_row - 1, sheet.nrows):
            row = sheet.row_values(i)
            name = row[0]
            th_type = row[1].strip().capitalize()
            if th_type == 'Ngắn hạn':
                th_name_type = 'short_term'
            elif th_type == 'Dài hạn':
                th_name_type = 'long_term'
            elif th_type == 'Đối tác':
                th_name_type = 'partner'

            warehouse = {
                'name': name,
                'th_type': th_name_type,
            }
            warehouse_data.append(warehouse)
        for data in warehouse_data:
            warehouse = self.env['th.warehouse'].search([('name', '=', data['name'])], limit=1)
            if warehouse:
                warehouse.write(data)
            else:
                self.env['th.warehouse'].create(data)

        sheet = wb.sheet_by_index(0)
        opportunity_data = []
        for i in range(start_row-1, sheet.nrows):
            row = sheet.row_values(i)
            name = row[0]
            th_mail = row[1]
            th_phone_number = row[2]
            th_description = row[3]
            th_type_ctv = row[4].strip().capitalize()
            if th_type_ctv == 'Ngắn hạn':
                th_type_value_ctv='short_term'
            elif th_type_ctv == 'Dài hạn':
                th_type_value_ctv='long_term'
            elif th_type_ctv == 'Đối tác':
                th_type_value_ctv = 'partner'
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Import error ',
                        'message': 'Check the imported data again ',
                        'type': 'danger',
                        'sticky': True,
                        'next': {'type': 'ir.actions.act_window_close'}
                    }
                }

            th_warehouse_name = row[5]
            th_warehouse = self.env['th.warehouse'].sudo().search([('name', '=', th_warehouse_name)], order='id desc', limit=1)


            opportunity = {
                'name': name,
                'th_mail': th_mail,
                'th_phone_number': th_phone_number,
                'th_description': th_description,
                'th_type_ctv': th_type_value_ctv,
                'th_warehouse': th_warehouse.id,

            }
            opportunity_data.append(opportunity)
        for data in opportunity_data:
            opportunity = self.env['th.opportunity.ctv'].search([('th_mail', '=', data['th_mail'])], limit=1)
            if opportunity:
                opportunity.write(data)
            else:
                self.env['th.opportunity.ctv'].create(data)


        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import successfully',
                'message': 'Data imported successfully',
                'type': 'info',
                'sticky': True,
                'next': {'type': 'ir.actions.act_window_close'}
            }
        }

