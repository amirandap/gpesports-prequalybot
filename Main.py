import pymysql
import discord
import json
import discord
from datetime import datetime,timedelta
from discord.ext import commands,tasks
from dateutil import parser
import traceback
import os
import time

bot = commands.Bot(command_prefix='=',intents = discord.Intents.all())
bot.remove_command('help')
seconds = 0
minutes = 0
hours = 0
days = 0
total_entries = 0
Start_Date_Temp = ''
Start_Date_Temp_DM = ''

@bot.event
async def on_ready():
    print('---------- BOT HAS STARTED -------')
    with open('Settings.json') as f:
        data = json.load(f)
    
    
    await bot.wait_until_ready()
    try:
        channel = await bot.fetch_channel(data['Backend_Channel'])
        await channel.send(f':gear: Subio el bot en **{len(bot.guilds)}** servidor$')
    except Exception:
        pass
    
    # COMMENTED OUT FOR TESTING PURPOSES, ENABLE THESE WHEN YOU ARE GOING FOR LIVE
    fetch_role_data.start()
    fetch_dm_data.start()
    uptime_calc.start()
    send_reminders.start()

running = 'TRUE'

@commands.has_permissions(administrator = True)
@bot.command()
async def break_(ctx):
    global running
    running = 'FALSE'
    await ctx.send(':white_check_mark: Commands have been DISABLED')

@commands.has_permissions(administrator = True)
@bot.command()
async def start(ctx):
    global running
    running = 'TRUE'
    await ctx.send(':white_check_mark: Commands have been ENABLED')

@tasks.loop(seconds = 1)
async def uptime_calc():
    global seconds
    global minutes
    global hours
    global days

    if not seconds > 59:
        seconds += 1
    
    else:
        if not minutes > 59:
            seconds = 0
            minutes += 1
        elif not hours > 23:
            hours += 1
            seconds = 0
            minutes = 0
        else:
            hours = 0
            days += 1
    
    return days,hours,minutes,seconds

@commands.has_permissions(administrator = True)
@bot.command()
async def incidentes(ctx):
    with open('Creds.json','r') as f:
        data = json.load(f)
    host = data['Host']
    user = data['User']
    pass_ = data['Password']
    db_ = data['Database']
    query = ''
    for line in open('Incidents_QUERY.txt'):
        query += line

    port = data['Port']

    conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)

    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute(query)
    """
    incidentes.Incidente - incidentes.Lap
    (incidentes.Reportado | incidentes.Afectado)
    Resolucion: incidentes.Resolucion - incidentes.Reportado)
    """
    
    msg = ''
    
    pending = 0
    total = 0
    completed = 0


    for row in cur.fetchall():
    
        list_header = f"Race Director - {row['Pista']}"
        resolucion = row['Resolucion']
        incidente = row['Incidente']
        lap = row['Lap']
        if lap != '':
            header = f"{incidente} Vuelta: {lap}"
        else:
            header = incidente
            
        reportado = row['Reportado']
        afectado = row['Afectado']
        if resolucion == '':
            if int(row['CHANNELID']) == ctx.channel.id:
                pending += 1
                total += 1
            continue
        else:
            if int(row['CHANNELID']) == ctx.channel.id:
                completed += 1
                total += 1
                msg += f"**{header}**\n{afectado} | {reportado} ({resolucion})\n\n"    

    embed = discord.Embed(color = discord.Color.red(),description = msg,title = list_header)
    if not pending == 0:
        embed.set_footer(text = f'{total} Total | {completed} Listos | {pending} Pendiente')
    
    await ctx.send(embed = embed)
    await ctx.message.delete()
    
@commands.has_permissions(administrator = True)
@bot.command()
async def prequali(ctx,val:str = None,channel:discord.TextChannel = None):

    global running
    if running == 'FALSE':
        pass
    await ctx.message.delete()
    global Start_Date_Temp_F
    global total_entries

    with open('Creds.json') as f:
        data = json.load(f)
       
    
    if not val and not channel:
        host = data['Host']
        user = data['User']
        pass_ = data['Password']
        db_ = data['Database']
        query_ = data['Prequali_Query']

        port = data['Port']
        
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_)
        msg = ''
        num = 1
        with open('Settings.json') as f:
            data = json.load(f)

        for tables in cur.fetchall():
            print('here')         
            user = int(tables['DISCORDID'])
            if user in data['Ignored_Users']:
                pass
            user = ctx.channel.guild.get_member(int(user))
            track_name = tables['Pista']
            tiempo = tables['TIEMPO']
            msg += f"**{num}:** {user.mention}\n> **TIEMPO**: {tiempo}\n\n" 
            num += 1
            total_entries += 1

        
        embed = discord.Embed(color = discord.Color.green(),title = f'TOP Fastest Users {track_name}',description = msg)
        await ctx.send(embed = embed)
        conn.close()

    else:
        print('EXECUTED')
        val = val.lower()

        if val == '-final':

            with open('Settings.json') as f:
                dta = json.load(f)
            
            if not 'Prequali_Role' in dta:
                await ctx.send(":warning: Please set the role with $setrole command")
                return

            host = data['Host']
            user = data['User']
            pass_ = data['Password']
            db_ = data['Database']
            query_ = data['Prequali_Query']
            port = data['Port']
            conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
            
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(query_)
            msg = ''
            num = 1
            with open('Settings.json') as f:
                data = json.load(f)

            for tables in cur.fetchall():      
        
                user = int(tables['DISCORDID'])
                if user in data['Ignored_Users']:
                    continue
                try:
                    user = ctx.channel.guild.get_member(int(user))
                    role = discord.utils.get(ctx.channel.guild.roles,name = data['Prequali_Role'])
                    if role in user.roles:
                        continue
                    await user.add_roles(role)
                    track_name = tables['Pista']
                    tiempo = tables['TIEMPO']
                    msg += f"**{num}:** {user.mention}\n> **TIEMPO**: {tiempo}\n\n" 
                    await user.send(f"Felicidades, has clasificado para la carrera de `{track_name}`, hemos asignado el role `{role}`")
                    num += 1
                    total_entries += 1
                    Last_Role = roles

                except Exception as e:
                    error = traceback.print_exc()
                    channel = await bot.fetch_channel(data['Backend_Channel'])
                    await channel.send(error)
                    continue
                
                    
            embed = discord.Embed(color = discord.Color.green(),title = f'Prequali GP3 - {track_name}',description = msg)
            await ctx.send(embed = embed)
            conn.close()

    
        elif val == '-setchannel':
            with open('Settings.json') as f:
                data = json.load(f)
            if channel == None:
                await ctx.send('Usage: $prequali -setchannel #channel')
                return
            else:
                data['Role_Channel'] = channel.id
                await ctx.send(':white_check_mark: Channel has been saved')
                with open('Settings.json','w') as f:
                    json.dump(data,f,indent = 3)
        
        elif val == '-remind':
            host = data['Host']
            user = data['User']
            pass_ = data['Password']
            db_ = data['Database']
            query1 = ''
            for line in open('Reminder_QUERY.txt'):
                query1 += line
            port = data['Port']
            msg = ''
            num = 1

            conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
            
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(query1)
            with open('Settings.json') as f:
                    data = json.load(f)
            for tables in cur.fetchall():      

                user = int(tables['DISCORDID'])
                channel = await bot.fetch_channel(data['Reminder_Channel'])
                try:
                    user = await bot.fetch_user(int(user))
                    msg += f"**{num}.** {user.mention}\n" 
                    num += 1

                except Exception as e:
                    error = traceback.print_exc()
                    channel = await bot.fetch_channel(data['Backend_Channel'])
                    await channel.send(error)
                    continue

            
            
            embed = discord.Embed(title = f'Recuerden mandar su tiempo para la proxima carrera!',color = discord.Color.orange(),description =msg)
            await ctx.send(embed = embed)
            
            conn.close()
        
        elif val == '-reminddm':

            host = data['Host']
            user = data['User']
            pass_ = data['Password']
            db_ = data['Database']
            query1 = ''
            for line in open('Reminder_QUERY.txt'):
                query1 += line
            port = data['Port']
            msg = ''
            num = 1

            conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
            
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(query1)
            with open('Settings.json') as f:
                data = json.load(f)

            for tables in cur.fetchall():      
                try:
                    user = int(tables['DISCORDID'])
                    if user in data['Ignored_Users']:
                        continue
                except:
                    continue

                channel = await bot.fetch_channel(data['Reminder_Channel'])
                try:
                    user = await bot.fetch_user(int(user))
                    msg += f"**{num}.** {user.mention}\n" 
                    await user.send(f"Recuerda enviar tu tiempo para la carrera del martes")
                    num += 1

                except Exception as e:
                    error = traceback.print_exc()
                    channel = await bot.fetch_channel(data['Backend_Channel'])
                    await channel.send(error)
                    continue
            
            
            embed = discord.Embed(title = f'Recuerden mandar su tiempo para la proxima carrera! | {track_name}',color = discord.Color.orange(),description =msg)
            await ctx.send(embed = embed)
            
            conn.close()
        
        else:
            await ctx.send('Usage: $prequali `<-reminddm>` or `<-remind>` or `<-setchannel>` or `<-final>` or without argument')
            return

                

@commands.has_permissions(administrator = True)
@bot.command(aliases = ['cleanrole','cr'])
async def cleanroles(ctx):
    global running
    if running == 'FALSE':
        return
    await ctx.message.delete()
    global total_entries

    with open('Creds.json') as f:
        data = json.load(f)

    with open('Settings.json') as f:
        dta = json.load(f)

    if not 'Prequali_Role' in dta:
        await ctx.send(":warning: Please set the role with $setrole command")
        return

    host = data['Host']
    user = data['User']
    pass_ = data['Password']
    db_ = data['Database']
    query_ = data['Prequali_Query']
    port = data['Port']
    conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
    
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute(query_)
    num = 1


    for tables in cur.fetchall():      
 
        user = int(tables['DISCORDID'])

        try:
            user = ctx.channel.guild.get_member(int(user))
            role = discord.utils.get(ctx.channel.guild.roles,name = dta['Prequali_Role'])
            if not role in user.roles:
                continue
            await user.remove_roles(role)
            num += 1

        except Exception as e:
     
            error = traceback.print_exc()
            channel = await bot.fetch_channel(dta['Backend_Channel'])
            await channel.send(error)
            continue

    
    if num == 0:
        await ctx.send(':warning: None of the users had a role.')
        await ctx.message_.delete()
        return
    
    await ctx.send(f':white_check_mark: Removed Roles of {num} Users.')
          
            

@tasks.loop(minutes = 29)
async def fetch_role_data():
    global Start_Date_Temp
    global total_entries

    with open('Settings.json') as f:
        dta = json.load(f)

    if not 'Prequali_Role' in dta:
        channel = await bot.fetch_channel(data['Backend_Channel'])
        await channel.send(":warning: Please set the role with $setrole command")
        return

    with open('Creds.json') as f:
        data = json.load(f)

    host = data['Host']
    user = data['User']
    pass_ = data['Password']
    db_ = data['Database']
    query_ = data['Query2']
    port = data['Port']

    if Start_Date_Temp == '':
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_)

 
        for tables in cur.fetchall():  
            
            Start_Date_Temp = tables['start_date']
    

        conn.close()
        
    start_date = datetime.strptime(str(Start_Date_Temp), '%Y-%m-%d %H:%M:%S')
    t1 = parser.parse(str(start_date))
    t2 = parser.parse(str(datetime.now()))
    t3 = t1 - t2
    hours_ = round(t3.total_seconds() / 3600)
    msg = ''
    msg2 = ''
    num = 1
    if hours_ == int(dta['Prequali_Assign_Hours']):
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_)
        for tables in cur.fetchall():      
            user = int(tables['DISCORDID'])
            channel = await bot.fetch_channel(dta['Role_Channel'])

            try:
                print(user)
                print(channel)
                user = channel.guild.get_member(int(user))
                print(user)
                role = discord.utils.get(channel.guild.roles,name = dta['Prequali_Role'])
                if role in user.roles:
                    continue
                await user.add_roles(role)
                track_name = tables['Pista']
                tiempo = tables['TIEMPO']
                msg += f"**{num}.** {tiempo}   |   {user.mention}\n\n" 
                await user.send(f"Felicidades, calificaste para la carrera de GP3 en {track_name} y ya tienes el rol de `{role}`")
                num += 1
                total_entries += 1

            except Exception as e:
                error = traceback.print_exc()
                channel = await bot.fetch_channel(dta['Backend_Channel'])
                await channel.send(error)
                continue

        
        conn.close()
        
    elif hours_ == int(dta['Prequali_Remove_Hours']):
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_)
        for tables in cur.fetchall():
            user = int(tables['DISCORDID'])
            channel = await bot.fetch_channel(dta['Role_Channel'])
            try:
                user = channel.guild.get_member(int(user))
                role = discord.utils.get(channel.guild.roles,name = dta['Prequali_Role'])
                if not role in user.roles:
                    continue
                await user.remove_roles(role)
                msg2 += f"**{num}. {user.name}"
                num += 1

            except Exception as e:
                error = traceback.print_exc()
                channel = await bot.fetch_channel(dta['Backend_Channel'])
                await channel.send(error)
                continue
 
        
        conn.close()
    
    else:
        return
            
    if not msg == '':
        channel = await bot.fetch_channel(dta['Role_Channel'])
        embed = discord.Embed(color = discord.Color.green(),title = f'TOP Fastest Users {track_name}',description = msg)
        await channel.send(embed = embed)
        Start_Date_Temp = ''
        return Start_Date_Temp
    
    if not msg2 == '':
        channel = await bot.fetch_channel(dta['Role_Channel'])
        embed = discord.Embed(color = discord.Color.green(),title = f'Roles Removed | {track_name}',description = msg2)
        await channel.send(embed = embed)
        Start_Date_Temp = ''
        return Start_Date_Temp      

@commands.has_permissions(administrator = True)
@bot.command()
async def parcferme(ctx,val:str = None):
    global running
    if running == 'FALSE':
        pass
    #await ctx.message.delete()
    global Start_Date_Temp_F
    global total_entries

    with open('Settings.json') as f:
        dta = json.load(f)

    with open('Creds.json') as f:
        data = json.load(f)


    host = data['Host']
    user = data['User']
    pass_ = data['Password']
    db_ = data['Database']
    query_ = ''
    for line in open('Parcferme_QUERY.txt'):
        query_ += line

    port = data['Port']
    
    conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
    
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute(query_)
    msg = ''
    users_without_ID = ''
    num = 1
    num2 = 1
    old_channel = 0
    sent_m = ''
    for tables in cur.fetchall():      
        track_name = tables['Pista']
        channel = await bot.fetch_channel(int(tables['Discord Channel ID']))
        if num == 1:
            old_channel = int(tables['Discord Channel ID'])
        else:
            old_channel = int(tables['Discord Channel ID'])

        try:
            user_id = int(tables['Discord_User_ID'])
            if user_id in dta['Ignored_Users']:
                continue
            user = await bot.fetch_user(int(tables['Discord_User_ID']))
            if old_channel == channel.id:
                msg += f"• {user.mention} - {tables['nickname']}\n" 
            else:
                channel = await bot.fetch_channel(int(old_channel))
                embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                description = msg)

                await channel.send(embed = embed)
                if val is None:
                    user_message_temp = 'Todavia no has enviado tu parcferme para la carrera de esta semana. Evita penalidad\n\n[Formulario Parc Ferme](https://gpesportsrd.com/parc)'
                    embed2 = discord.Embed(color = discord.Color.red(),description = user_message_temp)
                    await user.send(embed = embed2)

                sent_m = msg
                msg = ''
                msg += f"• {user.mention}\n" 
                old_channel = int(tables['Discord Channel ID'])
             
            num += 1

        except Exception as e:
  
            users_without_ID += f"**{num2}:** {tables['nickname']}\n"
            if old_channel == channel.id:
                msg += f"• {tables['nickname']}\n" 
                num += 1
            else:
                channel = await bot.fetch_channel(int(old_channel))
                embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                description = msg)
                await channel.send(embed = embed)
                sent_m = msg
                msg = ''
                msg += f"• {tables['nickname']}\n" 
                old_channel = int(tables['Discord Channel ID'])
                num += 1
            
            num2 += 1
            continue
    
    if sent_m == '' and not msg == '':
        if sent_m != msg:
            channel = await bot.fetch_channel(int(old_channel))
            embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
            description = msg)
            await channel.send(embed = embed)

    conn.close()
    if not users_without_ID == '':
        channel = await bot.fetch_channel(dta['Backend_Channel'])
        embed = discord.Embed(color = discord.Color.red(),title = f'Parcferme | Users without USERID',description =users_without_ID)
        await channel.send(embed = embed)

@tasks.loop(minutes= 29)
async def fetch_dm_data():
    global Start_Date_Temp_DM
    global total_entries

    with open('Settings.json') as f:
        dta = json.load(f)

    with open('Creds.json') as f:
        data = json.load(f)


    host = data['Host']
    user = data['User']
    pass_ = data['Password']
    db_ = data['Database']
    query_ = ''
    for line in open(f'Parcferme_QUERY.txt'):
        query_ += line
 
    port = data['Port']

    if Start_Date_Temp_DM == '':
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_)

 
        for tables in cur.fetchall():  
            
            Start_Date_Temp_DM = tables['start_date']
            print(tables)
    

        conn.close()
        
    start_date = datetime.strptime(str(Start_Date_Temp_DM), '%Y-%m-%d %H:%M:%S')
    t1 = parser.parse(str(start_date))
    t2 = parser.parse(str(datetime.now()))
    t3 = t1 - t2
    hours_ = round(t3.total_seconds() / 3600)
    msg = ''
    num = 1
    num2 = 1
    users_without_ID = ''
    old_channel = 0
    sent_m = ''
    if hours_ == int(dta['Parcferme_dm1']):
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_)
        for tables in cur.fetchall():
            track_name = tables['Pista']
            channel = await bot.fetch_channel(int(tables['Parcferme_Channel']))
            if num == 1:
                old_channel = int(tables['Parcferme_Channel'])
            try:
                user = int(tables['DISCORDID'])
                if user in dta['Ignored_Users']:
                    continue
                user = await bot.fetch_user(int(tables['Discord_User_ID']))
                user_message_temp = 'Todavia no has enviado tu parcferme para la carrera de esta semana. Evita penalidad\n\n[Formulario Parc Ferme](https://gpesportsrd.com/parc)'
                embed2 = discord.Embed(color = discord.Color.red(),description = user_message_temp)
                await user.send(embed = embed2)
                if old_channel == channel.id:
                    msg += f"• {user.mention}\n" 
                else:
                    channel = await bot.fetch_channel(int(old_channel))
                    embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                    description = msg)
                    await channel.send(embed = embed)
                    sent_m = msg
                    msg = ''
                    msg += f"• {user.mention}\n" 
                    old_channel = int(tables['Parcferme_Channel'])
                
                num += 1

            except Exception as e:
                users_without_ID += f"**{num2}:** {tables['nickname']}\n"
                if old_channel == channel.id:
                    msg += f"• {tables['nickname']}\n" 
                    num += 1
                else:
        
                    channel = await bot.fetch_channel(int(old_channel))
                    embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                    description = msg)
                    await channel.send(embed = embed)
                    sent_m = msg
                    msg = ''
                    msg += f"• {tables['nickname']}\n" 
                    old_channel = int(tables['Parcferme_Channel'])
                    num += 1
                
                num2 += 1
                continue
        
        conn.close()

    elif hours_ == int(dta['Parcferme_dm2']):
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_)
        for tables in cur.fetchall():    
            track_name = tables['Pista']  
            channel = await bot.fetch_channel(int(tables['Parcferme_Channel']))
            if num == 1:
                old_channel = int(tables['Parcferme_Channel'])
            try:
                user = int(tables['DISCORDID'])
                if user in dta['Ignored_Users']:
                    continue
                user = await bot.fetch_user(int(tables['Discord_User_ID']))
                await user.send('TEXT HERE')
                if old_channel == channel.id:
                    msg += f"• {user.mention}\n" 
                else:
                    channel = await bot.fetch_channel(int(old_channel))
                    embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                    description = msg)
                    await channel.send(embed = embed)
                    sent_m = msg
                    msg = ''
                    msg += f"• {user.mention}\n" 
                    old_channel = int(tables['Parcferme_Channel'])
                
                num += 1

            except Exception as e:
                #print(e)
                users_without_ID += f"**{num2}:** {tables['nickname']}\n"
                if old_channel == channel.id:
                    msg += f"• {tables['nickname']}\n" 
                    num += 1
                else:
        
                    channel = await bot.fetch_channel(int(old_channel))
                    embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                    description = msg)
                    await channel.send(embed = embed)
                    sent_m = msg
                    msg = ''
                    msg += f"• {tables['nickname']}\n" 
                    old_channel = int(tables['Parcferme_Channel'])
                    num += 1
                
                num2 += 1
                continue
        
        conn.close()

    elif hours_ == int(dta['Parcferme_dm3']):
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_)
        for tables in cur.fetchall():      
            track_name = tables['Pista']
            channel = await bot.fetch_channel(int(tables['Parcferme_Channel']))
            if num == 1:
                old_channel = int(tables['Parcferme_Channel'])
            try:
                user = int(tables['DISCORDID'])
                if user in dta['Ignored_Users']:
                    continue
                user = await bot.fetch_user(int(tables['Discord_User_ID']))
                await user.send('TEXT HERE')
                if old_channel == channel.id:
                    msg += f"• {user.mention}\n" 
                else:
                    channel = await bot.fetch_channel(int(old_channel))
                    embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                    description = msg)
                    await channel.send(embed = embed)
                    sent_m = msg
                    msg = ''
                    msg += f"• {user.mention}\n" 
                    old_channel = int(tables['Parcferme_Channel'])
                
                num += 1

            except Exception as e:
                #print(e)
                users_without_ID += f"**{num2}:** {tables['nickname']}\n"
                if old_channel == channel.id:
                    msg += f"• {tables['nickname']}\n" 
                    num += 1
                else:
        
                    channel = await bot.fetch_channel(int(old_channel))
                    embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                    description = msg)
                    await channel.send(embed = embed)
                    sent_m = msg
                    msg = ''
                    msg += f"• {tables['nickname']}\n" 
                    old_channel = int(tables['Parcferme_Channel'])
                    num += 1
                
                num2 += 1
                continue
        
        conn.close()  

    elif hours_ == int(dta['Parcferme_dm4']):
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_)
        for tables in cur.fetchall():      
            track_name = tables['Pista']
            channel = await bot.fetch_channel(int(tables['Parcferme_Channel']))
            if num == 1:
                old_channel = int(tables['Parcferme_Channel'])
            try:
                user = int(tables['DISCORDID'])
                if user in dta['Ignored_Users']:
                    continue
                user = await bot.fetch_user(int(tables['Discord_User_ID']))
                await user.send('TEXT HERE')
                if old_channel == channel.id:
                    msg += f"• {user.mention}\n" 
                else:
                    channel = await bot.fetch_channel(int(old_channel))
                    embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                    description = msg)
                    await channel.send(embed = embed)
                    sent_m = msg
                    msg = ''
                    msg += f"• {user.mention}\n" 
                    old_channel = int(tables['Parcferme_Channel'])
                
                num += 1

            except Exception as e:
                #print(e)
                users_without_ID += f"**{num2}:** {tables['nickname']}\n"
                if old_channel == channel.id:
                    msg += f"• {tables['nickname']}\n" 
                    num += 1
                else:
        
                    channel = await bot.fetch_channel(int(old_channel))
                    embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                    description = msg)
                    await channel.send(embed = embed)
                    sent_m = msg
                    msg = ''
                    msg += f"• {tables['nickname']}\n" 
                    old_channel = int(tables['Parcferme_Channel'])
                    num += 1
                
                num2 += 1
                continue
        
        conn.close()
    elif hours_ == int(dta['Parcferme_dm5']):
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query_)
        for tables in cur.fetchall():    
            track_name = tables['Pista']  
            channel = await bot.fetch_channel(int(tables['Parcferme_Channel']))
            if num == 1:
                old_channel = int(tables['Parcferme_Channel'])
            try:
                user = int(tables['DISCORDID'])
                if user in dta['Ignored_Users']:
                    continue
                user = await bot.fetch_user(int(tables['Discord_User_ID']))
                await user.send('TEXT HERE')
                if old_channel == channel.id:
                    msg += f"• {user.mention}\n" 
                else:
                    channel = await bot.fetch_channel(int(old_channel))
                    embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                    description = msg)
                    await channel.send(embed = embed)
                    sent_m = msg
                    msg = ''
                    msg += f"• {user.mention}\n" 
                    old_channel = int(tables['Parcferme_Channel'])
                
                num += 1

            except Exception as e:
                #print(e)
                users_without_ID += f"**{num2}:** {tables['nickname']}\n"
                if old_channel == channel.id:
                    msg += f"• {tables['nickname']}\n" 
                    num += 1
                else:
        
                    channel = await bot.fetch_channel(int(old_channel))
                    embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
                    description = msg)
                    await channel.send(embed = embed)
                    sent_m = msg
                    msg = ''
                    msg += f"• {tables['nickname']}\n" 
                    old_channel = int(tables['Parcferme_Channel'])
                    num += 1
                
                num2 += 1
                continue
        
        conn.close()
    
    if not users_without_ID == '':
        channel = await bot.fetch_channel(dta['Backend_Channel'])
        embed = discord.Embed(color = discord.Color.red(),title = 'Users Without the USER ID',description =users_without_ID)
        await channel.send(embed = embed)

    if not sent_m == '' and not old_channel == 0:
        if sent_m != msg:
            channel = await bot.fetch_channel(int(old_channel))
            embed = discord.Embed(color = discord.Color.red(),title = f'Parc Ferme Pendiente {track_name}',
            description = msg)
            await channel.send(embed = embed)

@commands.has_permissions(administrator = True)
@bot.command()
async def prequali_setrole(ctx,*,role_name:str = None):
    await ctx.message.delete()
    if not role_name:
        await ctx.send(':information_source: Command Usage: $prequali_setrole `<ROLE NAME`')
        return
    else:
        with open('Settings.json') as f:
            data = json.load(f)
        
        data['Prequali_Role'] = role_name

        with open('Settings.json','w') as f:
            json.dump(data,f,indent = 3)
        
        await ctx.send(':white_check_mark: Role has been Saved')



@commands.has_permissions(administrator = True)
@bot.command()
async def setbackendchannel(ctx,channel:discord.TextChannel = None):
    await ctx.message.delete()
    if not channel:
        await ctx.send(':information_source: Usage: $setchannel `<#channel>`')
        return
    else:
        with open('Settings.json') as f:
            data = json.load(f)
        
        data['Backend_Channel'] = channel.id

        with open('Settings.json','w') as f:
            json.dump(data,f,indent = 3)
        
        await ctx.send(':white_check_mark: Channel has been Saved')

@bot.command()
async def status(ctx):
    path = os.getcwd()
    modification_time = os.path.getmtime(str(path) + '\\Main.py')
    modification_time = time.ctime(modification_time)
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    global total_entries

    with open('Settings.json') as f:
        data = json.load(f)
    
    if not 'Last_Role' in data:
        Last_Role = 'None'
    global days,hours,minutes,seconds
    embed = discord.Embed(color = discord.Color.blue())
    embed.set_author(name ='BOT Statistics',icon_url= bot.user.avatar_url)
    embed.add_field(name = 'Uptime:',value = f'`{days}` D,`{hours}` H,`{minutes}` M,`{seconds}` S',inline = False)
    embed.add_field(name = 'Current Time',value = current_time,inline = False)
    embed.add_field(name = 'Total Entries',value = total_entries,inline = False)
    embed.add_field(name = 'Last Role:',value = Last_Role,inline = False)
    embed.add_field(name = 'Last Modified',value = modification_time,inline = False)
    await ctx.send(embed = embed)
    await ctx.message.delete()

@tasks.loop(minutes = 35)
async def send_reminders():

    with open('Settings.json') as f:
        dta = json.load(f)

    with open('Creds.json') as f:
        data = json.load(f)

    host = data['Host']
    user = data['User']
    pass_ = data['Password']
    db_ = data['Database']
    query1 = ''
    for line in open('Reminder_QUERY.txt'):
        query1 += line
    port = data['Port']
    
    #! NEED TO FIX THIS A BIT, REST ALL GOOD. [ON SUNDAY ETC]
    current_date  = datetime.strftime(datetime.today()  - timedelta(days=datetime.today().weekday() % 7), '%d %H')
    date1 = str(datetime.strftime(datetime.now(),'%d %H'))
    
    msg = ''
    num = 1
    users = []
    if current_date == date1:
        conn = pymysql.connect(host=host,user=user,passwd=pass_,db=db_,port=port)
        
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(query1)

        for tables in cur.fetchall():      
            try:
                user = int(tables['DISCORDID'])
            except:
                continue

            channel = await bot.fetch_channel(dta['Reminder_Channel'])
            try:
                if user in dta['Ignored_Users']:
                    continue
                user = await bot.fetch_user(int(user))
                await user.send(f"REcuerda enviar tu tiempo para la carrera del martes")
                msg += f"**{num}.** {user.mention}\n"
                num += 1

            except Exception as e:
            
                error = traceback.print_exc()
                channel = await bot.fetch_channel(dta['Backend_Channel'])
                await channel.send(error)
                continue

        
        if not msg == '':
            embed = discord.Embed(title = f'Recuerden mandar su tiempo para la proxima carrera! | {track_name}',color = discord.Color.orange(),description =msg)
            await channel.send(embed = embed)
        
        conn.close()

@bot.command()
async def help(ctx):
    embed = discord.Embed(title = 'Commands Help',color = discord.Color.dark_gold())
    embed.add_field(name="break_", value="Break all the commands", inline=False)
    embed.add_field(name="start", value="Start all the commands", inline=False)
    embed.add_field(name="cleanroles", value="Removes all the Prequali Roles", inline=False)
    embed.add_field(name="status", value="Shows the Queries and the bot status", inline=False)
    embed.add_field(name="prequali_setrole", value="Set the role for the Prequali Query", inline=False)
    embed.add_field(name="setbackendchannel", value="Set the default channel", inline=False)
    embed.add_field(name="incidentes", value="Executes the Incidentes Query", inline=False)
    embed.add_field(name="parcferme", value="Usage: $parcferme `<-ignoreuser>` or `Without Arguments`", inline=False)
    embed.add_field(name="prequali", value="Usage: $prequali `<-reminddm>` or `<-remind>` or `<-setchannel>` or `<-final>` or without argument", inline=False)
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.event
async def on_command_error(ctx,error):
    if isinstance(error,commands.CommandNotFound):
        embed = discord.Embed(title = 'Commands Help',color = discord.Color.dark_gold())
        embed.add_field(name="break_", value="Break all the commands", inline=False)
        embed.add_field(name="start", value="Start all the commands", inline=False)
        embed.add_field(name="cleanroles", value="Removes all the Prequali Roles", inline=False)
        embed.add_field(name="status", value="Shows the Queries and the bot status", inline=False)
        embed.add_field(name="prequali_setrole", value="Set the role for the Prequali Query", inline=False)
        embed.add_field(name="setbackendchannel", value="Set the default channel", inline=False)
        embed.add_field(name="incidentes", value="Executes the Incidentes Query", inline=False)
        embed.add_field(name="parcferme", value="Usage: $parcferme `<-ignoreuser>` or `Without Arguments`", inline=False)
        embed.add_field(name="prequali", value="Usage: $prequali `<-reminddm>` or `<-remind>` or `<-setchannel>` or `<-final>` or without argument", inline=False)
        await ctx.send(embed=embed)
        await ctx.message.delete()

with open('Settings.json') as f:
    dd = json.load(f)

TOKEN = dd['Token']
bot.run(TOKEN)
