from rerechan import *

#CRATE VMESS
@bot.on(events.CallbackQuery(data=b'create-vmess'))
async def create_vmess(event):
	async def create_vmess_(event):
		async with bot.conversation(chat) as user:
			await event.respond('**Username:**')
			user = user.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
			user = (await user).raw_text
		async with bot.conversation(chat) as pw:
			await event.respond("**Quota:**")
			pw = pw.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
			pw = (await pw).raw_text
		async with bot.conversation(chat) as exp:
			await event.respond("**Choose Expiry Day**",buttons=[
[Button.inline(" 1 Day ","1"),
Button.inline(" 7 Day ","7")],
[Button.inline(" 30 Day ","30"),
Button.inline(" 60 Day ","60")]])
			exp = exp.wait_event(events.CallbackQuery)
			exp = (await exp).data.decode("ascii")
		await event.edit("Processing.")
		await event.edit("Processing..")
		await event.edit("Processing...")
		await event.edit("Processing....")
		time.sleep(0)
		await event.edit("`Processing Crate Premium Account`")
		time.sleep(1)
		await event.edit("`Processing... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 84%\n█████████████████████▒▒▒▒ `")
		time.sleep(0)
		await event.edit("`Processing... 100%\n█████████████████████████ `")
		time.sleep(1)
		await event.edit("`Wait.. Setting up an Account`")
		cmd = f'printf "%s\n" "{user}" "{pw}" "{exp}" | add-vmess'
		try:
			a = subprocess.check_output(cmd, shell=True).decode("utf-8")
		except:
			await event.respond("**User Already Exist**")
		else:
			today = DT.date.today()
			later = today + DT.timedelta(days=int(exp))
			b = [x.group() for x in re.finditer("vmess://(.*)",a)]
			print(b)
			z = base64.b64decode(b[0].replace("vmess://","")).decode("ascii")
			z = json.loads(z)
			z1 = base64.b64decode(b[1].replace("vmess://","")).decode("ascii")
			z1 = json.loads(z1)
			msg = f"""
**━━━━━━━━━━━━━━━━━**
 **🟢 VMESS ACCOUNT 🟢**
**━━━━━━━━━━━━━━━━━**
**» Username     :** `{z["ps"]}`
**» Domain       :** `{z["add"]}`
**» User Quota   :** `{pw} GB`
**» port TLS     :** `443`
**» Port NTLS    :** `80, 8880`
**» Port GRPC    :** `443`
**» User ID      :** `{z["id"]}`
**» AlterId      :** `0`
**» Security     :** `auto`
**» NetWork      :** `WebSocket, gRPC`
**» Path         :** `/vmessws, /worryfree, /kuota-habis`
**» Path Dynamic :** `https://bug.com/path`
**» ServiceName  :** `vmess-grpc`
**━━━━━━━━━━━━━━━━━**
**» Link TLS  :** 
`{b[0].strip("'").replace(" ","")}`
**━━━━━━━━━━━━━━━━━**
**» Link NTLS :** 
`{b[1].strip("'").replace(" ","")}`
**━━━━━━━━━━━━━━━━━**
**» HTTP None :** 
`{b[2].strip("'")}`
**━━━━━━━━━━━━━━━━━**
**» HTTP TLS  :** 
`{b[3].strip("'")}`
**━━━━━━━━━━━━━━━━━**
**» SplitTLS  :** 
`{b[4].strip("'")}`
**━━━━━━━━━━━━━━━━━**
**» SplitHTTP :** 
`{b[5].strip("'")}`
**━━━━━━━━━━━━━━━━━**
**» Multipath :** 
`{b[6].strip("'")}`
**━━━━━━━━━━━━━━━━━**
**» Link GRPC :** 
`{b[7].strip("'")}`
**━━━━━━━━━━━━━━━━━**
**» Expired On:** `{later}`
**━━━━━━━━━━━━━━━━━**
"""
			await event.respond(msg)
	chat = event.chat_id
	sender = await event.get_sender()
	a = valid(str(sender.id))
	if a == "true":
		await create_vmess_(event)
	else:
		await event.answer("Akses Ditolak",alert=True)


#CREARE VLESS
@bot.on(events.CallbackQuery(data=b'create-vless'))
async def create_vless(event):
	async def create_vless_(event):
		async with bot.conversation(chat) as user:
			await event.respond('**Username:**')
			user = user.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
			user = (await user).raw_text
		async with bot.conversation(chat) as pw:
			await event.respond("**Quota:**")
			pw = pw.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
			pw = (await pw).raw_text
		async with bot.conversation(chat) as exp:
			await event.respond("**Choose Expiry Day**",buttons=[
[Button.inline(" 1 Day ","1"),
Button.inline(" 7 Day ","7")],
[Button.inline(" 30 Day ","30"),
Button.inline(" 60 Day ","60")]])
			exp = exp.wait_event(events.CallbackQuery)
			exp = (await exp).data.decode("ascii")
		await event.edit("Processing.")
		await event.edit("Processing..")
		await event.edit("Processing...")
		await event.edit("Processing....")
		time.sleep(1)
		await event.edit("`Processing Crate Premium Account`")
		time.sleep(1)
		await event.edit("`Processing... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 84%\n█████████████████████▒▒▒▒ `")
		time.sleep(0)
		await event.edit("`Processing... 100%\n█████████████████████████ `")
		time.sleep(1)
		await event.edit("`Wait.. Setting up an Account`")
		cmd = f'printf "%s\n" "{user}" "{pw}" "{exp}" | add-vless'
		try:
			a = subprocess.check_output(cmd, shell=True).decode("utf-8")
		except:
			await event.respond("**User Already Exist**")
		else:
			today = DT.date.today()
			later = today + DT.timedelta(days=int(exp))
			x = [x.group() for x in re.finditer("vless://(.*)",a)]
			print(x)
			uuid = re.search("vless://(.*?)@",x[0]).group(1)
			msg = f"""
**━━━━━━━━━━━━━━━━━**
** 🟢 Vless Account 🟢**
**━━━━━━━━━━━━━━━━━**
**» Remarks     :** `{user}`
**» Host Server :** `{DOMAIN}`
**» User Quota  :** `{pw} GB`
**» Port TLS    :** `443`
**» Port NTLS   :** `80`
**» Port GRPC    :** `443`
**» NetWork     :** `WebSocket, gRPC`
**» User ID     :** `{uuid}`
**» Path Vless  :** `/vlessws`
**» Path Dynamic:** `https://bug.com/vlessws`
**» ServiceName  :** `vmess-grpc`
**━━━━━━━━━━━━━━━━━**
**» Link TLS : **
`{x[0]}`
**━━━━━━━━━━━━━━━━━**
**» Link NTLS:**
`{x[1].replace(" ","")}`
**━━━━━━━━━━━━━━━━━**
**» HTTP TLS :**
`{x[2].replace(" ","")}`
**━━━━━━━━━━━━━━━━━**
**» HTTP NTLS:**
`{x[3].replace(" ","")}`
**━━━━━━━━━━━━━━━━━**
**» Link GRPC:**
`{x[4].replace(" ","")}`
**━━━━━━━━━━━━━━━━━**
**» Expired Until:** `{later}`
**━━━━━━━━━━━━━━━━━**
"""
			await event.respond(msg)
	chat = event.chat_id
	sender = await event.get_sender()
	a = valid(str(sender.id))
	if a == "true":
		await create_vless_(event)
	else:
		await event.answer("Akses Ditolak",alert=True)


#CREATE TROJAN
@bot.on(events.CallbackQuery(data=b'create-trojan'))
async def create_trojan(event):
	async def create_trojan_(event):
		async with bot.conversation(chat) as user:
			await event.respond('**Username:**')
			user = user.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
			user = (await user).raw_text
		async with bot.conversation(chat) as pw:
			await event.respond("**Quota:**")
			pw = pw.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
			pw = (await pw).raw_text
		async with bot.conversation(chat) as exp:
			await event.respond("**Choose Expiry Day**",buttons=[
[Button.inline(" 1 Day ","1"),
Button.inline(" 7 Day ","7")],
[Button.inline(" 30 Day ","30"),
Button.inline(" 60 Day ","60")]])
			exp = exp.wait_event(events.CallbackQuery)
			exp = (await exp).data.decode("ascii")
		await event.edit("Processing.")
		await event.edit("Processing..")
		await event.edit("Processing...")
		await event.edit("Processing....")
		time.sleep(1)
		await event.edit("`Processing Crate Premium Account`")
		time.sleep(1)
		await event.edit("`Processing... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 84%\n█████████████████████▒▒▒▒ `")
		time.sleep(0)
		await event.edit("`Processing... 100%\n█████████████████████████ `")
		time.sleep(1)
		await event.edit("`Wait.. Setting up an Account`")
		cmd = f'printf "%s\n" "{user}" "{pw}" "{exp}" | add-trojan'
		try:
			a = subprocess.check_output(cmd, shell=True).decode("utf-8")
		except:
			await event.respond("**User Already Exist**")
		else:
			today = DT.date.today()
			later = today + DT.timedelta(days=int(exp))
			b = [x.group() for x in re.finditer("trojan://(.*)",a)]
			print(b)
			uuid = re.search("trojan://(.*?)@",b[0]).group(1)
			msg = f"""
**━━━━━━━━━━━━━━━━━**
**🟢 Trojan Account 🟢**
**━━━━━━━━━━━━━━━━━**
**» Remarks     :** `{user}`
**» Host Server :** `{DOMAIN}`
**» User Quota  :** `{pw} GB`
**» Port TLS    :** `443`
**» User ID     :** `{uuid}`
**━━━━━━━━━━━━━━━━**
**» Link WS  :** 
`{b[0].replace(" ","")}`
**━━━━━━━━━━━━━━━━**
**» HTTP TLS :** 
`{b[1].replace(" ","")}`
**━━━━━━━━━━━━━━━━**
**» Link GRPC:** 
`{b[2].replace(" ","")}`
**━━━━━━━━━━━━━━━━**
**Expired Until:** `{later}`
**━━━━━━━━━━━━━━━━**
"""
			await event.respond(msg)
	chat = event.chat_id
	sender = await event.get_sender()
	a = valid(str(sender.id))
	if a == "true":
		await create_trojan_(event)
	else:
		await event.answer("Akses Ditolak",alert=True)


#CREATE SHADOWSOCKS
@bot.on(events.CallbackQuery(data=b'create-shadowsocks'))
async def create_shadowsocks(event):
	async def create_shadowsocks_(event):
		async with bot.conversation(chat) as user:
			await event.respond('**Username:**')
			user = user.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
			user = (await user).raw_text
		async with bot.conversation(chat) as pw:
			await event.respond("**Quota:**")
			pw = pw.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
			pw = (await pw).raw_text
		async with bot.conversation(chat) as exp:
			await event.respond("**Choose Expiry Day**",buttons=[
[Button.inline(" 1 Day ","1"),
Button.inline(" 7 Day ","7")],
[Button.inline(" 30 Day ","30"),
Button.inline(" 60 Day ","60")]])
			exp = exp.wait_event(events.CallbackQuery)
			exp = (await exp).data.decode("ascii")
		await event.edit("Processing.")
		await event.edit("Processing..")
		await event.edit("Processing...")
		await event.edit("Processing....")
		time.sleep(3)
		await event.edit("`Processing Crate Premium Account`")
		time.sleep(1)
		await event.edit("`Processing... 0%\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 4%\n█▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(2)
		await event.edit("`Processing... 8%\n██▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(3)
		await event.edit("`Processing... 20%\n█████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(2)
		await event.edit("`Processing... 36%\n█████████▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 52%\n█████████████▒▒▒▒▒▒▒▒▒▒▒▒ `")
		time.sleep(1)
		await event.edit("`Processing... 84%\n█████████████████████▒▒▒▒ `")
		time.sleep(0)
		await event.edit("`Processing... 100%\n█████████████████████████ `")
		time.sleep(1)
		await event.edit("`Wait.. Setting up an Account`")
		cmd = f'printf "%s\n" "{user}" "{pw}" "{exp}" | add-ssws'
		try:
			a = subprocess.check_output(cmd, shell=True).decode("utf-8")
		except:
			await event.respond("**User Already Exist**")
		else:
			today = DT.date.today()
			later = today + DT.timedelta(days=int(exp))
			x = [x.group() for x in re.finditer("ss://(.*)",a)]
			print(x)
			uuid = re.search("ss://(.*?)@",x[0]).group(1)
			msg = f"""
**━━━━━━━━━━━━━━━━━**
**🟢SHDWSCSK ACCOUNT🟢**
**━━━━━━━━━━━━━━━━━**
**» Remarks     :** `{user}`
**» Host Server :** `{DOMAIN}`
**» Host XrayDNS:** `{HOST}`
**» User Quota  :** `{pw} GB`
**» Port TLS    :** `443`
**» Password    :** `{uuid}`
**» Cipers      :** `aes-128-gcm`
**» NetWork     :** `WebSocket`
**» Path        :** `/ssws`
**━━━━━━━━━━━━━━━━━**
**» Link TLS    :**
`{x[0]}`
**━━━━━━━━━━━━━━━━━**
**» Expired Until:** `{later}`
**━━━━━━━━━━━━━━━━━**
"""
			await event.respond(msg)
	chat = event.chat_id
	sender = await event.get_sender()
	a = valid(str(sender.id))
	if a == "true":
		await create_shadowsocks_(event)
	else:
		await event.answer("Akses Ditolak",alert=True)

# Trial Vmess
@bot.on(events.CallbackQuery(data=b'trial-vmess'))
async def trial_vmess(event):
    async def trial_vmess_(event):
        cmd = 'trial-vmess'.strip()
        x = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        print(x)
        z = subprocess.check_output(cmd, shell=True).decode("utf-8")
        max_message_length = 4096
        for i in range(0, len(z), max_message_length):
            await event.respond(f"```\n{z[i:i + max_message_length]}\n```")
        
        # Send buttons after the message chunks
        await event.respond("‹ Main Menu ›", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])

    sender = await event.get_sender()
    a = valid(str(sender.id))
    if a == "true":
        await trial_vmess_(event)
    else:
        await event.answer("Access Denied", alert=True)

# Trial Vless
@bot.on(events.CallbackQuery(data=b'trial-vless'))
async def trial_vless(event):
    async def trial_vless_(event):
        cmd = 'trial-vless'.strip()
        x = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        print(x)
        z = subprocess.check_output(cmd, shell=True).decode("utf-8")

        # Split the response if it is too long
        max_message_length = 4096
        for i in range(0, len(z), max_message_length):
            await event.respond(f"```\n{z[i:i + max_message_length]}\n```")
        
        # Send buttons after the message chunks
        await event.respond("‹ Main Menu ›", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])

    sender = await event.get_sender()
    a = valid(str(sender.id))
    if a == "true":
        await trial_vless_(event)
    else:
        await event.answer("Access Denied", alert=True)

# Trial Trojan
@bot.on(events.CallbackQuery(data=b'trial-trojan'))
async def trial_trojan(event):
    async def trial_trojan_(event):
        cmd = 'trial-trojan'.strip()
        x = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        print(x)
        z = subprocess.check_output(cmd, shell=True).decode("utf-8")

        # Split the response if it is too long
        max_message_length = 4096
        for i in range(0, len(z), max_message_length):
            await event.respond(f"```\n{z[i:i + max_message_length]}\n```")
        
        # Send buttons after the message chunks
        await event.respond("‹ Main Menu ›", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])

    sender = await event.get_sender()
    a = valid(str(sender.id))
    if a == "true":
        await trial_trojan_(event)
    else:
        await event.answer("Access Denied", alert=True)

# Trial Shadowsocks
@bot.on(events.CallbackQuery(data=b'trial-shadowsocks'))
async def trial_ssws(event):
    async def trial_ssws_(event):
        cmd = 'trial-ssws'.strip()
        x = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        print(x)
        z = subprocess.check_output(cmd, shell=True).decode("utf-8")

        # Split the response if it is too long
        max_message_length = 4096
        for i in range(0, len(z), max_message_length):
            await event.respond(f"```\n{z[i:i + max_message_length]}\n```")
        
        # Send buttons after the message chunks
        await event.respond("‹ Main Menu ›", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])

    sender = await event.get_sender()
    a = valid(str(sender.id))
    if a == "true":
        await trial_ssws_(event)
    else:
        await event.answer("Access Denied", alert=True)

# CEK IP LOGIN Xray
@bot.on(events.CallbackQuery(data=b'cek-xray'))
async def cek_xray(event):
    async def cek_xray_(event):
        cmd = 'bot-cek-xray'.strip()
        x = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        print(x)
        z = subprocess.check_output(cmd, shell=True).decode("utf-8")

        # Split the response if it is too long
        max_message_length = 4096
        for i in range(0, len(z), max_message_length):
            await event.respond(f"```\n{z[i:i + max_message_length]}\n```\n**» @fn_project**")
        
        # Send buttons after the message chunks
        await event.respond("‹ Main Menu ›", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])

    sender = await event.get_sender()
    a = valid(str(sender.id))
    if a == "true":
        await cek_xray_(event)
    else:
        await event.answer("Access Denied", alert=True)

# List Xray
@bot.on(events.CallbackQuery(data=b'list-xray'))
async def list_xray(event):
    async def list_xray_(event):
        cmd = '/usr/bin/rere/list-xray'.strip()
        x = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        print(x)
        z = subprocess.check_output(cmd, shell=True).decode("utf-8")

        # Split the response if it is too long
        max_message_length = 4096
        for i in range(0, len(z), max_message_length):
            await event.respond(f"**List Total Account Xray**\n```\n{z[i:i + max_message_length]}\n```\n**» @fn_project**")
        
        # Send buttons after the message chunks
        await event.respond("‹ Main Menu ›", buttons=[[Button.inline("‹ Main Menu ›", "menu")]])

    sender = await event.get_sender()
    a = valid(str(sender.id))
    if a == "true":
        await list_xray_(event)
    else:
        await event.answer("Access Denied", alert=True)

@bot.on(events.CallbackQuery(data=b'delete-xray'))
async def delete_xray(event):
	async def delete_xray_(event):
		async with bot.conversation(chat) as user:
			await event.respond('**Username:**')
			user = user.wait_event(events.NewMessage(incoming=True, from_users=sender.id))
			user = (await user).raw_text
		cmd = f'printf "%s\n" "{user}" | bot-delete-xray'
		try:
			a = subprocess.check_output(cmd, shell=True).decode("utf-8")
		except:
			await event.respond("**User Not Found**")
		else:
			msg = f"""**Successfully Deleted**"""
			await event.respond(msg)
	chat = event.chat_id
	sender = await event.get_sender()
	a = valid(str(sender.id))
	if a == "true":
		await delete_xray_(event)
	else:
		await event.answer("Akses Ditolak",alert=True)

@bot.on(events.CallbackQuery(data=b'menu-xray'))
async def menu_xray(event):
    async def menu_xray_(event):
        inline_buttons = [
            [Button.inline("Create Vmess", b'create-vmess'), Button.inline("Create Vless", b'create-vless')],
            [Button.inline("Create Trojan", b'create-trojan'), Button.inline("Create Shadowsocks", b'create-shadowsocks')],
            [Button.inline("Trial Vmess", b'trial-vmess'), Button.inline("Trial Vless", b'trial-vless')],
            [Button.inline("Trial Trojan", b'trial-trojan'), Button.inline("Trial Shadowsocks", b'trial-shadowsocks')],
            [Button.inline("Check Xray Usage", b'cek-xray'), Button.inline("Delete Account", b'delete-xray')],
            [Button.inline("List Total Accounts", b'list-xray')],
            [Button.inline("‹ Main Menu ›", b'menu')]
        ]

        # Fetch IP and ISP info from the API
        z = requests.get("http://ip-api.com/json/?fields=country,region,city,timezone,isp").json()
        
        # Construct the message
        msg = f"""
━━━━━━━━━━━━━━━━━━━━━━━
🟢 **» Service:** `X-RAY/V2RAY`
🟢 **» Hostname:** `{DOMAIN}`
🟢 **» ISP:** `{z["isp"]}`
🟢 **» Country:** `{z["country"]}`
━━━━━━━━━━━━━━━━━━━━━━━
"""
        # Edit the message with inline buttons
        await event.edit(msg, buttons=inline_buttons)

    # Check sender validity
    sender = await event.get_sender()
    is_valid = valid(str(sender.id))
    
    if is_valid == "true":
        await menu_xray_(event)
    else:
        await event.answer("Access Denied", alert=True)