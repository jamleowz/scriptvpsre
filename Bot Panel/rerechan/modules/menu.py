from rerechan import *
from telethon.errors import MessageIdInvalidError  # Impor exception yang benar

@bot.on(events.NewMessage(pattern=r"(?:.menu|/menu|.rere|.dinda)$"))
@bot.on(events.CallbackQuery(data=b'menu'))
async def menu(event):
    inline = [
        [Button.inline(" MENU SSH OVPN", "ssh"),
         Button.inline(" MENU XRAY", "menu-xray")],
        [Button.inline(" MENU TROJANGO", "menu-trojango"),
         Button.inline(" MENU WGCF", "menu-wireguard")],
        [Button.inline(" MENU BACKUP ", "bmenu"),
         Button.inline(" ‹ Back Menu › ", "start")]
    ]
    
    sender = await event.get_sender()
    val = valid(str(sender.id))
    
    if val == "false":
        try:
            await event.answer("Akses Ditolak", alert=True)
        except:
            await event.reply("Akses Ditolak")
    elif val == "true":        
        xr = "cat /etc/xray/config.json | grep \"###\" | wc -l"
        xry = subprocess.check_output(xr, shell=True).decode("ascii")
        sdss = "cat /etc/os-release | grep -w PRETTY_NAME | head -n1 | sed 's/=//g' | sed 's/PRETTY_NAME//g'"
        namaos = subprocess.check_output(sdss, shell=True).decode("ascii")
        ipvps = "curl -s ipv4.icanhazip.com"
        ipsaya = subprocess.check_output(ipvps, shell=True).decode("ascii")
        citys = "cat /root/.city"
        city = subprocess.check_output(citys, shell=True).decode("ascii")
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━ 
    **⚠️ ADMIN PANEL MENU ⚠️**
━━━━━━━━━━━━━━━━━━━━━━━
**🚦 OS     :** `{namaos.strip().replace('"','')}`
**🚦 CITY   :** `{city.strip()}`
**🚦 DOMAIN :** `{DOMAIN}`
**🚦 IP VPS :** `{ipsaya.strip()}`
━━━━━━━━━━━━━━━━━━━━━━━ 
**» 🟢XRAY-ALL    :** `{xry.strip()}` __account__
━━━━━━━━━━━━━━━━━━━━━━━ 
"""
        try:
            x = await event.edit(msg, buttons=inline)
        except MessageIdInvalidError:  # Tangani exception dengan benar
            x = await event.reply(msg, buttons=inline)