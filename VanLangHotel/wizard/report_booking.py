import xlsxwriter
import base64
from odoo import fields, models, api, exceptions
from io import BytesIO
from datetime import datetime
from pytz import timezone
import pytz
from odoo.exceptions import ValidationError


class ReportBooking(models.TransientModel):
    _name = "report.booking"

    @api.model
    def get_default_date_model(self):
        return datetime.now()

    datas = fields.Binary('File', readonly=True)
    datas_fname = fields.Char('Filename', readonly=True)
    date_to = fields.Date(string="Ngày bắt đầu", required=True, default=fields.Date.today)
    date_from = fields.Date(string="Ngày kết thúc", required=True, default=fields.Date.today)

    @api.constrains('date_to', 'date_from')
    def check_date(self):
        for record in self:
            if record.date_to > record.date_from:
                raise exceptions.ValidationError('Ngày bắt đầu không thể lớn hơn ngày kết thúc')

    def print_excel_report(self):
        data = self.read()[0]
        date_to = data['date_to']
        date_from = data['date_from']
        datetime_string = self.get_default_date_model().strftime("%Y-%m-%d %H:%M:%S")
        date_string = self.get_default_date_model().strftime("%Y-%m-%d")
        report_name = 'Báo cáo doanh thu khách sạn Văn Lang'
        user_xls = 'Người Lập Báo Cáo : %s' % self.env.user.name
        date_report = 'Ngày Báo Cáo : %s' % (datetime_string)
        filename = '%s %s' % (report_name, date_string)

        columns = [
            ('STT', 5, 'no', 'no'),
            ('Ngày', 20, 'char', 'char'),
            ('ma_booking', 20, 'char', 'char'),
            ('customer_id', 20, 'char', 'char'),
            ('check_in', 20, 'char', 'char'),
            ('check_out', 20, 'char', 'char'),
            ('total_amount', 35, 'float', 'float'),
        ]

        datetime_format = '%Y-%m-%d %H:%M:%S'
        utc = datetime.now().strftime(datetime_format)
        utc = datetime.strptime(utc, datetime_format)
        tz = self.get_default_date_model().strftime(datetime_format)
        tz = datetime.strptime(tz, datetime_format)
        duration = tz - utc
        hours = duration.seconds / 60 / 60
        if hours > 1 or hours < 1:
            hours = str(hours) + ' hours'
        else:
            hours = str(hours) + ' hour'

        query = """
                SELECT 
                    ((b.create_date AT TIME ZONE 'UTC') AT TIME ZONE 'ICT') :: DATE  as "create_date",
                    b."booking_id" as "ma_booking",           
                    b."customer_id" as "ten_khach_hang",
                    ((b.check_in AT TIME ZONE 'UTC') AT TIME ZONE 'ICT') :: DATE  as "check_in",
                    ((b.check_out AT TIME ZONE 'UTC') AT TIME ZONE 'ICT') :: DATE  as "check_out",
                    b."total_amount" as "total_amount"
                FROM booking as b 
                WHERE ((b.create_date AT TIME ZONE 'UTC') AT TIME ZONE 'ICT') :: DATE BETWEEN '%s' AND '%s' AND b.state != 'booking'
                ORDER BY b.create_date
                """

        self._cr.execute(query % (date_to, date_from))
        result = self._cr.fetchall()

        fp = BytesIO()
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = self.add_workbook_format(workbook)

        worksheet = workbook.add_worksheet(report_name)
        worksheet.merge_range('A2:I3', report_name, wbf['title_doc'])
        worksheet.merge_range('E5:I5', date_report, wbf['content_datetime'])
        worksheet.merge_range('A6:C6', user_xls, wbf['content'])
        row = 8
        col = 0

        for column in columns:
            column_name = column[0]
            column_width = column[1]
            worksheet.set_column(col, col, column_width)
            worksheet.write(row - 1, col, column_name, wbf['header_orange'])

            col += 1

        row += 1
        no = 1

        column_float_number = {}
        for res in result:
            col = 0
            for column in columns:
                column_type = column[2]
                if column_type == 'char':
                    col_value = res[col - 1] if res[col - 1] else ''
                    col_value = str(col_value)
                    wbf_value = wbf['content']
                elif column_type == 'no':
                    col_value = no
                    wbf_value = wbf['content']
                else:
                    col_value = res[col - 1] if res[col - 1] else 0
                    if column_type == 'float':
                        wbf_value = wbf['content_float']
                    else:  # number
                        wbf_value = wbf['content_number']
                    column_float_number[col] = column_float_number.get(col, 0) + col_value
                worksheet.write(row - 1, col, col_value, wbf_value)
                col += 1
            row += 1
            no += 1

        # worksheet.merge_range('A%s:B%s'%(row,row), 'Date', wbf['total_orange'])
        worksheet.merge_range('A%s:B%s' % (row, row), 'Tổng', wbf['total_orange'])
        worksheet.merge_range('C%s:D%s' % (row, row), '', wbf['content'])
        for x in range(len(columns)):
            if x in (0, 1):
                continue
            column_type = columns[x][3]
            if column_type == 'char':
                worksheet.write(row - 1, x, '', wbf['content_datetime'])
            else:
                if column_type == 'float':
                    wbf_value = wbf['total_float_orange']
                else:  # number
                    wbf_value = wbf['total_number_orange']
                if x in column_float_number:
                    worksheet.write(row - 1, x, column_float_number[x], wbf_value)
                else:
                    worksheet.write(row - 1, x, 0, wbf_value)

        workbook.close()
        out = base64.encodestring(fp.getvalue())
        self.write({'datas': out, 'datas_fname': filename})
        fp.close()
        filename += '%2Exlsx'

        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': 'web/content/?model=' + self._name + '&id=' + str(
                self.id) + '&field=datas&download=true&filename=' + filename,
        }

    def add_workbook_format(self, workbook):
        colors = {
            'white_orange': '#FFFFDB',
            'orange': '#FFC300',
            'red': '#FF0000',
            'yellow': '#F6FA03',
        }

        wbf = {}
        wbf['header'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000', 'font_name': 'Georgia'})
        wbf['header'].set_border()

        wbf['header_orange'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': colors['orange'], 'font_color': '#000000',
             'font_name': 'Georgia'})
        wbf['header_orange'].set_border()

        wbf['header_yellow'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': colors['yellow'], 'font_color': '#000000',
             'font_name': 'Georgia'})
        wbf['header_yellow'].set_border()

        wbf['header_no'] = workbook.add_format(
            {'bold': 1, 'align': 'center', 'bg_color': '#FFFFDB', 'font_color': '#000000', 'font_name': 'Georgia'})
        wbf['header_no'].set_border()
        wbf['header_no'].set_align('vcenter')

        wbf['footer'] = workbook.add_format({'align': 'left', 'font_name': 'Georgia'})

        wbf['content_datetime'] = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss', 'font_name': 'Georgia'})
        wbf['content_datetime'].set_left()
        wbf['content_datetime'].set_right()
        wbf['content_datetime'].set_top()
        wbf['content_datetime'].set_bottom()

        wbf['content_date'] = workbook.add_format({'num_format': 'yyyy-mm-dd', 'font_name': 'Georgia'})
        wbf['content_date'].set_left()
        wbf['content_date'].set_right()
        wbf['content_date'].set_top()
        wbf['content_date'].set_bottom()

        wbf['title_doc'] = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_size': 20,
            'font_name': 'Georgia',
        })

        wbf['company'] = workbook.add_format({'align': 'left', 'font_name': 'Georgia'})
        wbf['company'].set_font_size(11)

        wbf['content'] = workbook.add_format()
        wbf['content'].set_left()
        wbf['content'].set_right()
        wbf['content'].set_top()
        wbf['content'].set_bottom()

        wbf['content_float'] = workbook.add_format({'align': 'right', 'num_format': '#,##0.00', 'font_name': 'Georgia'})
        wbf['content_float'].set_right()
        wbf['content_float'].set_left()
        wbf['content_float'].set_top()
        wbf['content_float'].set_bottom()

        wbf['content_number'] = workbook.add_format({'align': 'right', 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['content_number'].set_right()
        wbf['content_number'].set_left()
        wbf['content_number'].set_top()
        wbf['content_number'].set_bottom()

        wbf['content_percent'] = workbook.add_format({'align': 'right', 'num_format': '0.00%', 'font_name': 'Georgia'})
        wbf['content_percent'].set_right()
        wbf['content_percent'].set_left()
        wbf['content_percent'].set_bottom()
        wbf['content_percent'].set_top()

        wbf['total_float'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['white_orange'], 'align': 'right', 'num_format': '#,##0.00',
             'font_name': 'Georgia'})
        wbf['total_float'].set_top()
        wbf['total_float'].set_bottom()
        wbf['total_float'].set_left()
        wbf['total_float'].set_right()

        wbf['total_number'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['white_orange'], 'bold': 1, 'num_format': '#,##0',
             'font_name': 'Georgia'})
        wbf['total_number'].set_top()
        wbf['total_number'].set_bottom()
        wbf['total_number'].set_left()
        wbf['total_number'].set_right()

        wbf['total'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['white_orange'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total'].set_left()
        wbf['total'].set_right()
        wbf['total'].set_top()
        wbf['total'].set_bottom()

        wbf['total_float_yellow'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['yellow'], 'align': 'right', 'num_format': '#,##0.00',
             'font_name': 'Georgia'})
        wbf['total_float_yellow'].set_top()
        wbf['total_float_yellow'].set_bottom()
        wbf['total_float_yellow'].set_left()
        wbf['total_float_yellow'].set_right()

        wbf['total_number_yellow'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['yellow'], 'bold': 1, 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['total_number_yellow'].set_top()
        wbf['total_number_yellow'].set_bottom()
        wbf['total_number_yellow'].set_left()
        wbf['total_number_yellow'].set_right()

        wbf['total_yellow'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['yellow'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total_yellow'].set_left()
        wbf['total_yellow'].set_right()
        wbf['total_yellow'].set_top()
        wbf['total_yellow'].set_bottom()

        wbf['total_float_orange'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['orange'], 'align': 'right', 'num_format': '#,##0.00',
             'font_name': 'Georgia'})
        wbf['total_float_orange'].set_top()
        wbf['total_float_orange'].set_bottom()
        wbf['total_float_orange'].set_left()
        wbf['total_float_orange'].set_right()

        wbf['total_number_orange'] = workbook.add_format(
            {'align': 'right', 'bg_color': colors['orange'], 'bold': 1, 'num_format': '#,##0', 'font_name': 'Georgia'})
        wbf['total_number_orange'].set_top()
        wbf['total_number_orange'].set_bottom()
        wbf['total_number_orange'].set_left()
        wbf['total_number_orange'].set_right()

        wbf['total_orange'] = workbook.add_format(
            {'bold': 1, 'bg_color': colors['orange'], 'align': 'center', 'font_name': 'Georgia'})
        wbf['total_orange'].set_left()
        wbf['total_orange'].set_right()
        wbf['total_orange'].set_top()
        wbf['total_orange'].set_bottom()

        wbf['header_detail_space'] = workbook.add_format({'font_name': 'Georgia'})
        wbf['header_detail_space'].set_left()
        wbf['header_detail_space'].set_right()
        wbf['header_detail_space'].set_top()
        wbf['header_detail_space'].set_bottom()

        wbf['header_detail'] = workbook.add_format({'bg_color': '#E0FFC2', 'font_name': 'Georgia'})
        wbf['header_detail'].set_left()
        wbf['header_detail'].set_right()
        wbf['header_detail'].set_top()
        wbf['header_detail'].set_bottom()

        return wbf, workbook