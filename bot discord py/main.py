import discord
from discord.ext import tasks , commands
import json
import os
from datetime import datetime, timedelta


intents = discord.Intents().all() # pas forcément .all()
bot = commands.Bot(command_prefix = ".", intents=intents)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

@bot.command()
async def pdp(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    embed = discord.Embed(title=f"Photo de profil de {member.name}", color=member.color)
    embed.set_image(url=member.avatar_url)
    await ctx.send(embed=embed)


@bot.event
async def on_member_remove(member):
    channel = member.guild.get_channel(1002581526640328824)
    embed = discord.Embed(title=f"Un membre vient de partir ...!", color=member.color)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="A bientôt sur Development House 👋 !", value=f"{member.name}#{member.discriminator}", inline=False)
    await channel.send(embed=embed)

@bot.command()
async def info(ctx, member: discord.Member = None):
    if not member:
        member = ctx.author
    embed = discord.Embed(title=f"Informations sur {member.name}", color=member.color)
    embed.set_thumbnail(url=member.avatar_url)
    embed.add_field(name="Nom d'utilisateur", value=member.name, inline=False)
    embed.add_field(name="Date d'arrivée sur le serveur", value=member.joined_at.strftime("%d/%m/%Y à %H:%M:%S"), inline=False)
    await ctx.send(embed=embed)






@bot.command()
async def interactive_embed(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("Entrez le titre de l'embed :")
    response = await bot.wait_for("message", check=check)
    title = response.content

    await ctx.send("Entrez la description de l'embed :")
    response = await bot.wait_for("message", check=check)
    description = response.content

    await ctx.send("Entrez l'URL du GIF à afficher (facultatif) :")
    response = await bot.wait_for("message", check=check)
    gif_url = response.content if response.content.startswith("http") else None

    await ctx.send("Combien de champs voulez-vous ajouter ?")
    response = await bot.wait_for("message", check=check)
    num_fields = int(response.content)

    fields = []
    for i in range(num_fields):
        await ctx.send(f"Titre du champ {i+1} :")
        response = await bot.wait_for("message", check=check)
        field_title = response.content

        await ctx.send(f"Description du champ {i+1} :")
        response = await bot.wait_for("message", check=check)
        field_description = response.content

        fields.append((field_title, field_description))

    await ctx.send("Entrez le footer de l'embed (facultatif) :")
    response = await bot.wait_for("message", check=check)
    footer = response.content if response.content else None

    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    if gif_url:
        embed.set_image(url=gif_url)
    for field_title, field_description in fields:
        embed.add_field(name=field_title, value=field_description, inline=False)
    if footer:
        embed.set_footer(text=footer)

    await ctx.send(embed=embed)

     
@bot.command()
async def create_ticket(ctx):
    channel = await ctx.guild.create_text_channel(name=f"ticket-{ctx.author.name}", topic="Support Ticket")
    await channel.set_permissions(ctx.author, read_messages=True, send_messages=True)

    embed = discord.Embed(title="Ticket créé!",
                          description="Vous pouvez maintenant discuter avec notre équipe de support. "
                                      "Si vous avez terminé, vous pouvez fermer le ticket en utilisant "
                                      "la commande !close_ticket.",
                          color=discord.Color.blue())
    await channel.send(embed=embed)

@bot.command()
async def close_ticket(ctx):
    if isinstance(ctx.channel, discord.TextChannel) and ctx.channel.topic == "Support Ticket":
        await ctx.channel.delete()
    else:
        await ctx.send("Vous devez exécuter cette commande dans un canal de ticket!")
        
        
        
        
@bot.command()
async def regles(ctx):
    await ctx.send("Combien de règles voulez-vous ajouter ?")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    # Attend la réponse de l'utilisateur
    msg = await bot.wait_for("message", check=check)

    try:
        nb_regles = int(msg.content)
    except ValueError:
        await ctx.send("Nombre invalide.")
        return

    regles = []
    for i in range(nb_regles):
        await ctx.send(f"Nom de la règle {i+1} :")
        nom = await bot.wait_for("message", check=check)

        await ctx.send(f"Description de la règle {i+1} :")
        desc = await bot.wait_for("message", check=check)

        regles.append((nom.content, desc.content))

    # Affiche les règles
    embed = discord.Embed(title="Règles du serveur", color=0x00ff00)
    for i, (nom, desc) in enumerate(regles):
        embed.add_field(name=f"Règle {i+1} - {nom}", value=desc, inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def role_react(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("Combien de rôles souhaitez-vous ajouter ?")
    response = await bot.wait_for("message", check=check)
    num_roles = int(response.content)

    roles = []
    for i in range(num_roles):
        await ctx.send(f"Nom du rôle {i+1} :")
        role_name = await bot.wait_for("message", check=check)
        await ctx.send(f"Emoji pour le rôle {i+1} :")
        role_emoji = await bot.wait_for("message", check=check)
        role_emoji = role_emoji.content.strip()

        role = discord.utils.get(ctx.guild.roles, name=role_name.content.strip())
        if not role:
            role = await ctx.guild.create_role(name=role_name.content.strip())

        roles.append((role.id, role_emoji))


    embed = discord.Embed(title="Rôles", description="Cliquez sur les réactions ci-dessous pour obtenir les rôles correspondants !", color=discord.Color.blue())
    for role, emoji in roles:
        role_obj = ctx.guild.get_role(role)
        embed.add_field(name=f"{emoji} - {role_obj.name}", value="\u200b", inline=False)


    msg = await ctx.send(embed=embed)

    for _, emoji in roles:
        await msg.add_reaction(emoji)

    def check_reaction(reaction, user):
        return user != bot.user and reaction.message == msg and str(reaction.emoji) in [emoji for _, emoji in roles]

    @bot.event
    async def on_reaction_add(reaction, user):
        if check_reaction(reaction, user):
            for role, emoji in roles:
                if str(reaction.emoji) == emoji:
                    role_id = next((r_id for r_id, r_emoji in roles if r_emoji == str(reaction.emoji)), None)
                    role_obj = user.guild.get_role(role_id)
                    await user.add_roles(role_obj)
                    message = f"Le rôle {role_obj.name} a été ajouté à {user.display_name} !"
                    await user.send(message)
                    break




@bot.command()
async def clear(ctx, amount=5):
    await ctx.message.delete() # supprime la commande de l'utilisateur
    
    if amount <= 0:
        embed = discord.Embed(title="Erreur", description="Veuillez entrer un nombre positif.", color=0xFF0000)
        await ctx.send(embed=embed)
    else:
        await ctx.channel.purge(limit=amount) # supprime les messages dans le canal
    
        embed = discord.Embed(title="Messages Supprimés", description=f"{amount} messages ont été supprimés.", color=0x00FF00)
        await ctx.send(embed=embed)


@bot.event
async def on_member_join(member):
    guild = member.guild
    channel = await guild.create_text_channel(f'{member.name}-chat')
    embed = discord.Embed(title=f'Bienvenue {member.name} sur notre serveur !',
                          description='Nous sommes ravis de t\'accueillir parmi nous !',
                          color=discord.Color.green())
    await channel.send(embed=embed)

    welcome_channel = bot.get_channel(1002581526640328824)
    welcome_embed = discord.Embed(title=f"Oh ? un nouveau membre !", color=member.color)
    welcome_embed.set_thumbnail(url=member.avatar_url)
    welcome_embed.add_field(name="Un membre vient d'arrivé !", value=f"{member.mention}", inline=False)
    welcome_embed.add_field(name="\nNous sommes ravis que tu sois là 👋", value="true")
    await welcome_channel.send(embed=welcome_embed)
 


# Vérifier si le fichier de base de données existe
if not os.path.exists("data.json"):
    with open("data.json", "w") as f:
        json.dump({}, f)

# Charger la base de données
with open("data.json", "r") as f:
    data = json.load(f)


# ID du salon dans lequel afficher les messages de niveau
level_up_channel_id = 1079367280795856908

# XP nécessaire pour passer au niveau suivant
xp_per_level = 250

@bot.event
async def on_ready():
    print("Bot ready")

@bot.event
async def on_message(message):
    # Ignorer les messages envoyés par le bot
    if message.author == bot.user:
        return

    # Ajouter l'expérience de l'utilisateur
    user_id = str(message.author.id)
    if user_id not in data:
        data[user_id] = {"xp": 0, "level": 1}
    data[user_id]["xp"] += 10

    # Vérifier si l'utilisateur a gagné un niveau
    xp = data[user_id]["xp"]
    level = data[user_id]["level"]
    if xp >= level * xp_per_level:
        data[user_id]["level"] += 1
        await level_up_message(message.author, xp, level)

    # Enregistrer les données dans la base de données
    with open("data.json", "w") as f:
        json.dump(data, f)

    await bot.process_commands(message)

async def level_up_message(user, xp, level):
    # Récupérer la place de l'utilisateur sur le serveur
    guild = bot.get_guild(user.guild.id)
    members = sorted(guild.members, key=lambda m: m.joined_at)
    rank = members.index(user) + 1

    # Créer l'embed pour le message de niveau
    embed = discord.Embed(
        title=f"{user.name} a atteint le niveau {level} !",
        description=f"XP : {xp}/{level*xp_per_level}",
        color=0xffd700
    )
    embed.set_thumbnail(url=user.avatar_url)
    embed.add_field(name="Progression", value=f"{xp}/{level*xp_per_level}", inline=False)
    embed.add_field(name="Place sur le serveur", value=f"{rank}/{guild.member_count}", inline=False)
    embed.set_footer(text="Félicitations !")
    level_up_channel = bot.get_channel(level_up_channel_id)
    await level_up_channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def giveaway(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("Quel est le prix du giveaway ?")
    response = await bot.wait_for("message", check=check)
    prize = response.content

    await ctx.send("Combien de gagnants ?")
    response = await bot.wait_for("message", check=check)
    winners = int(response.content)

    await ctx.send("Combien de temps durera le giveaway (en jours) ?")
    response = await bot.wait_for("message", check=check)
    duration = int(response.content)

    end_time = datetime.utcnow() + timedelta(days=duration)

    embed = discord.Embed(title="🎉 **Giveaway** 🎉", description=f"Réagissez avec 🎁 pour participer et tenter de gagner **{winners}** **{prize}**(s) !\nDurée : **{duration}** jours\nFin du giveaway : **{end_time}** (UTC)", color=0x00ff00)
    embed.set_footer(text=f"{winners} gagnant(s) | Débuté par {ctx.author.name}")

    message = await ctx.send(embed=embed)
    await message.add_reaction("🎁")






# ID du salon où le récapitulatif sera envoyé
recap_channel_id = 1080623787059458058

class DailyRecap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_recap.start()

    def cog_unload(self):
        self.daily_recap.cancel()

    @tasks.loop(seconds=60)
    async def daily_recap(self):
        # Heure actuelle en UTC
        now = discord.utils.utcnow()
        # Heure à laquelle le récapitulatif sera envoyé (minuit UTC)
        target_time = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Si l'heure actuelle est minuit UTC
        if now == target_time:
            # ID du serveur
            guild_id = 1002574465802178661
            guild = self.bot.get_guild(guild_id)

            # Nombre de membres qui ont rejoint
            new_members = guild.approximate_member_count - self.bot.previous_member_count
            self.bot.previous_member_count = guild.approximate_member_count

            # Nombre de membres qui ont quitté
            left_members = self.bot.previous_member_count - guild.approximate_member_count
            self.bot.previous_member_count = guild.approximate_member_count

            # Salons les plus fréquentés
            channels = {}
            for channel in guild.text_channels:
                channels[channel] = channel.guild.voice_states.count()

            top_channels = sorted(channels.items(), key=lambda x: x[1], reverse=True)[:3]

            # Membre qui a envoyé le plus de messages
            top_member = max(guild.members, key=lambda member: member.stats.message_count)

            # Création de l'embed
            embed = discord.Embed(title="Récapitulatif quotidien", color=discord.Color.blue())
            embed.add_field(name="Nouveaux membres", value=new_members)
            embed.add_field(name="Membres partis", value=left_members)
            embed.add_field(name="Salons les plus fréquentés", value="\n".join([f"{channel.mention} - {count}" for channel, count in top_channels]))
            embed.add_field(name="Membre le plus actif", value=top_member.mention)
            await guild.get_channel(recap_channel_id).send(embed=embed)

    @daily_recap.before_loop
    async def before_daily_recap(self):
        # Attendre jusqu'à ce qu'il soit minuit UTC
        now = discord.utils.utcnow()
        target_time = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if now < target_time:
            await discord.utils.sleep_until(target_time)
        
        # Initialiser le nombre de membres pour le premier récapitulatif
        guild_id = 1002574465802178661
        guild = self.bot.get_guild(guild_id)
        self.bot.previous_member_count = guild.approximate_member_count

# Ajouter le Cog à l'instance du bot
bot.add_cog(DailyRecap(bot))



bot.run("MTA3OTc5MzY3Nzg0MjUzNDQ0MA.GMuUtG.eQHEaxpRBI3MSg_J6Uk-OakvJLzyOCKfTwqkAQ")
