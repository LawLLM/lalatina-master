from PIL import Image, ImageDraw, ImageFont
import datetime
import calendar
from io import BytesIO

font_title = ImageFont.truetype('src/fonts/KGPrimaryWhimsy.ttf', 130)
font_day_number = ImageFont.truetype('src/fonts/KGPrimaryWhimsy.ttf', 90)
font_day_str = ImageFont.truetype('src/fonts/KGPrimaryWhimsy.ttf', 90)

img_mask = Image.open('src/images/mask2.png')

SQUARE_W = 128
SQUARE_DAY_SIZE = (SQUARE_W, SQUARE_W)
W, H = (1056, 824)

title_color = (255, 255, 0)

img_day_weekend_true = Image.new('RGB', SQUARE_DAY_SIZE, color = (135, 184, 205))
img_day_weekend_false = Image.new('RGB', SQUARE_DAY_SIZE, color = (11, 161, 112))

zone_day_str_y = 150

zone_days_x_init = 50
zone_days_y_init = 250

today_datetime = datetime.datetime.now()

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

day_str = {
    0: 'D',
    1: 'L',
    2: 'M',
    3: 'M',
    4: 'J',
    5: 'V',
    6: 'S'
}

class CalendarGenerator():
    def new_calendar_img(self, month_int, bytes_dict):
        day_relative_base = datetime.datetime(2021, month_int, 1).weekday()
        if day_relative_base == 6:
            day_relative_base = -1
        a, total_days = calendar.monthrange(2021, month_int)
        max_day_num = day_relative_base + total_days
        y = int(max_day_num / 7)

        x_inc = 138
        y_inc = 138
        
        img_base = Image.new('RGB', (W, H+y_inc*(y-3)), color = (62, 45, 82))
        draw = ImageDraw.Draw(img_base)

        text_title = f"{month_str[month_int]} - 2021"

        w, h = draw.textsize(text_title, font=font_title)
        draw.text(((W-w)/2, 10), text_title, font=font_title, fill=(255, 255, 0))

        for i in range(7):
            day_name = day_str[i]

            w_d, h_d = draw.textsize(day_name, font=font_day_str)

            pos_day_name_x = zone_days_x_init + i * x_inc + x_inc/2 - w_d/2

            draw.text((pos_day_name_x, zone_day_str_y), day_name, font=font_day_str, fill=(255, 165, 0))

        for num_day in range(1, total_days+1):
            day_datetime = datetime.datetime(2021, month_int, num_day)

            day_relative = day_relative_base + num_day

            x = day_relative % 7
            y = int(day_relative / 7)

            x_pos = zone_days_x_init + x * x_inc
            y_pos = zone_days_y_init + y * y_inc

            if day_datetime.weekday() == 6:
                img_base.paste(img_day_weekend_true, (x_pos, y_pos), img_mask)
            else:
                img_base.paste(img_day_weekend_false, (x_pos, y_pos), img_mask)

            if num_day in bytes_dict.keys():
                img_avatar = Image.open(BytesIO(bytes_dict[num_day]))
                img_base.paste(img_avatar, (x_pos, y_pos), img_mask)
            else:
                size_day_number = draw.textsize(str(num_day), font=font_day_number)
                pos_day_number_x = x_pos + SQUARE_W/2 - size_day_number[0]/2
                pos_day_number_y = y_pos + SQUARE_W/2 - size_day_number[1]/2

                pos_day_number = (pos_day_number_x, pos_day_number_y)
                #pos_day_number = (x_pos+5, y_pos+5)

                if day_datetime.weekday() == 6:
                    draw.text(pos_day_number, str(num_day), font=font_day_number, fill=(112, 103, 110))
                else:
                    draw.text(pos_day_number, str(num_day), font=font_day_number, fill=(0, 255, 255))
        
            if day_datetime.year == today_datetime.year and day_datetime.month == today_datetime.month and day_datetime.day == today_datetime.day:
                rectangle_coord = (x_pos-5, y_pos-5, x_pos + SQUARE_W+5, y_pos + SQUARE_W+5)
                draw.rounded_rectangle(rectangle_coord, radius=18, fill=None, outline=(255, 0, 0), width=10)                

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
        


    





