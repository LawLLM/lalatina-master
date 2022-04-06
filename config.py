import os

# ID del Bot
client_id = 518213843344687130

prefix = "la!"
en_es = "<<"
es_en = ">>"

owners_id = [
    402291352282464259,
    603024644207018001,
    682674409085206621,
    919646375577288725,
]

# Starboard
# general, ajedrez en discord, canales de voz, economia
star_board_category_channels_id = [
    652651049626370087,
    798729997409321002,
    512830421805826051,
    776997219777642526,
]
channel_star_board_id = 892980248197623828

# ID del servidor Panchessco
panchessco_id = 512830421805826048
panchessco_role_staff_id = 892978210101428264
panchessco_role_tournament_manager_id = 956651608857522226
channel_logs_id = 751249228344590396

# PanchesscoBot
token = os.environ.get("BOT_TOKEN")

# CANAL DONDE SE ENVIARÁN LOS ERRORES
channel_fails_id = 826987595472568392

# ROL LEYENDA
role_legend_id = 754818654687985685

# MONGODB CONNECTION
mongoDb_connection = os.environ.get("MONGODB_STRING")

# ROL CUMPLEAÑOS
role_birthday_id = 795376236259049493

# CLAVE DEEPL
deepl_pass = os.environ.get("DEEPL_PASS")
