from PIL import Image, ImageDraw, ImageFont
import datetime
import calendar
from io import BytesIO

font_title = ImageFont.truetype('src/fonts/KGPrimaryWhimsy.ttf', 130)
font_day_number = ImageFont.truetype('src/fonts/KGPrimaryWhimsy.ttf', 50)

SQUARE_DAY_SIZE = (128, 128)
W, H = (1056, 1050)

title_color = (255, 255, 0)

img_day_weekend_true = Image.new('RGB', SQUARE_DAY_SIZE, color = (135, 184, 205))
img_day_weekend_false = Image.new('RGB', SQUARE_DAY_SIZE, color = (11, 161, 112))

zone_days_x_init = 50
zone_days_y_init = 200

month_str = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre'
}

class CalendarGenerator():
    def new_calendar_img(self, month_int, bytes_dict):
        img_base = Image.new('RGB', (W, H), color = (62, 45, 82))
        draw = ImageDraw.Draw(img_base)

        text_title = f"{month_str[month_int]} - 2021"

        w, h = draw.textsize(text_title, font=font_title)
        draw.text(((W-w)/2, 50), text_title, font=font_title, fill=(255, 255, 0))

        day_relative_base = datetime.datetime(2021, month_int, 1).weekday()

        x_inc = 138
        y_inc = 138

        a, total_days = calendar.monthrange(2021, month_int)

        for num_day in range(1, total_days+1):
            day_datetime = datetime.datetime(2021, month_int, num_day)

            day_relative = day_relative_base + num_day

            x = day_relative % 7
            y = int(day_relative / 7)

            x_pos = zone_days_x_init + x * x_inc
            y_pos = zone_days_y_init + y * y_inc

            if day_datetime.weekday() == 6:
                img_base.paste(img_day_weekend_true, (x_pos, y_pos))
            else:
                img_base.paste(img_day_weekend_false, (x_pos, y_pos))

            if num_day in bytes_dict.keys():
                img_avatar = Image.open(BytesIO(bytes_dict[num_day]))
                img_base.paste(img_avatar, (x_pos, y_pos))
            else:
                if day_datetime.weekday() == 6:
                    draw.text((x_pos+5, y_pos+5), str(num_day), font=font_day_number, fill=(112, 103, 110))
                else:
                    draw.text((x_pos+5, y_pos+5), str(num_day), font=font_day_number, fill=(0, 255, 255))

        output_buffer = BytesIO()
        img_base.save(output_buffer, "png")
        output_buffer.seek(0)

        return output_buffer
    
    def avatar_test(self, avatar_bytes):
        img_base = Image.new('RGB', (W, H), color = (0, 0, 0))

        img_avatar = Image.open(BytesIO(avatar_bytes))

        img_base.paste(img_avatar, (300, 300))

        output_buffer = BytesIO()
        img_base.save(output_buffer, "png")
        output_buffer.seek(0)

        return output_buffer
        


    





