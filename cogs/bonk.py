import discord
from discord.ext import commands, tasks, pages
import sqlite3
import json
import os
from discord.ui import InputText, Modal

ALLOWED_USER_IDS = [672804887524016138, 598194942724145203, 726484913599152179]

class SkinInputModal(Modal):
    def __init__(self):
        super().__init__(title="Adicionar nova skin")

        self.name = InputText(label="Nome da Skin", placeholder="Digite o nome da skin")
        self.avatar = InputText(label="Avatar da Skin", placeholder="Digite o avatar da skin")

        self.add_item(self.name)
        self.add_item(self.avatar)

    async def callback(self, interaction: discord.Interaction):
        self.name = self.children[0].value
        self.avatar = self.children[1].value
        await interaction.response.send_message("Informações recebidas. Adicionando skin à database...", ephemeral=True)

class Bonk(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.setup_skin_database.start()
        self.setup_vault_database.start()

    @tasks.loop(count=1)
    async def setup_skin_database(self):
        self.skin_database = sqlite3.connect("skins.db")
        cursor = self.skin_database.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS skins (id INTEGER PRIMARY KEY, name TEXT, avatar TEXT, cred TEXT)")
        self.skin_database.commit()

    @tasks.loop(count=1)
    async def setup_vault_database(self):
        self.vault_database = sqlite3.connect("vault.db")
        cursor = self.vault_database.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS vault (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, avatar TEXT)")
        self.vault_database.commit()

    @commands.slash_command(description="Adiciona um pacote de skin de bonk à database do bot.")
    async def add_skin(self, ctx):
        modal = SkinInputModal()
        await ctx.send_modal(modal)
        await modal.wait()
        if modal.name and modal.avatar:
            cursor = self.skin_database.cursor()
            cursor.execute("INSERT INTO skins (name, avatar, cred) VALUES (?, ?, ?)", (modal.name, modal.avatar, ctx.author.name))
            self.skin_database.commit()
            await ctx.respond("Skin adicionada com sucesso!", ephemeral=True)
        else:
            await ctx.respond("Você não forneceu os detalhes da skin.", ephemeral=True)

    @commands.slash_command(description="Lista os pacotes de skin de bonk na database do bot.")
    async def list_skins(self, ctx):
        cursor = self.skin_database.cursor()
        cursor.execute("SELECT * FROM skins")
        skins = cursor.fetchall()

        skin_pages = [
            discord.Embed(title=f"Skin ID: {skin[0]}", description=f"Nome: {skin[1]}\nCriador: {skin[3]}")
            for skin in skins
        ]

        if skins:
            paginator = pages.Paginator(pages=skin_pages)
            await paginator.respond(ctx.interaction)
        else:
            await ctx.respond("Nenhuma skin encontrada.", ephemeral=True)

    @commands.slash_command(description="Envia um arquivo .blsm da skin solicitada.")
    async def get_skin(self, ctx, skin_id: int):
        cursor = self.skin_database.cursor()
        cursor.execute("SELECT * FROM skins WHERE id=?", (skin_id,))
        skin = cursor.fetchone()
        if skin and skin[3] == ctx.author.id:
            skin_data = [{
                "name": skin[1],
                "avatar": skin[2],
                "cred": skin[3]
            }]
            blsm_data = json.dumps(skin_data)
            file_path = f'skin_{skin_id}.blsm'
            with open(file_path, 'w') as file:
                file.write(blsm_data)
            await ctx.respond(f"Skin {skin_id} carregada com sucesso.", file=discord.File(file_path), ephemeral=True)
            os.remove(file_path)  # Deleta o arquivo após o envio
        else:
            await ctx.send("ID de skin inválido ou você não tem permissão para acessar essa skin.", ephemeral=True)

    @commands.slash_command(description="Adiciona uma skin à sua vault privada.")
    async def add_to_vault(self, ctx):
        modal = SkinInputModal()
        await ctx.send_modal(modal)
        await modal.wait()
        if modal.name and modal.avatar:
            cursor = self.vault_database.cursor()
            cursor.execute("INSERT INTO vault (user_id, name, avatar) VALUES (?, ?, ?)", (ctx.author.id, modal.name, modal.avatar))
            self.vault_database.commit()
            await ctx.respond("Skin adicionada à sua vault privada com sucesso!", ephemeral=True)
        else:
            await ctx.respond("Você não forneceu os detalhes da skin.", ephemeral=True)

    @commands.slash_command(description="Lista as skins na sua vault privada.")
    async def list_vault(self, ctx):
        cursor = self.vault_database.cursor()
        cursor.execute("SELECT * FROM vault WHERE user_id=?", (ctx.author.id,))
        vault_skins = cursor.fetchall()

        vault_pages = [
            discord.Embed(title=f"Skin ID: {skin[0]}", description=f"Nome: {skin[2]}")
            for skin in vault_skins
        ]

        if vault_skins:
            paginator = pages.Paginator(pages=vault_pages)
            await paginator.respond(ctx.interaction, ephemeral=True)
        else:
            await ctx.respond("Nenhuma skin encontrada.", ephemeral=True)

    @commands.slash_command(description="Envia um arquivo .blsm da skin solicitada na sua vault privada.")
    async def get_vault_skin(self, ctx, skin_id: int):
        cursor = self.vault_database.cursor()
        cursor.execute("SELECT * FROM vault WHERE id=? AND user_id=?", (skin_id, ctx.author.id))
        skin = cursor.fetchone()

        aname = ctx.author.name

        if skin:
            skin_data = [{
                "name": skin[2],
                "avatar": skin[3],
                "cred": aname
            }]
            blsm_data = json.dumps(skin_data)
            file_path = f'vault_skin_{skin_id}.blsm'
            with open(file_path, 'w') as file:
                file.write(blsm_data)
            await ctx.respond(f"Skin {skin_id} carregada com sucesso.", file=discord.File(file_path), ephemeral=True)
            os.remove(file_path)  # Deleta o arquivo após o envio
        else:
            await ctx.send("ID de skin inválido ou você não tem permissão para acessar essa skin.", ephemeral=True)

    @commands.slash_command(description="Deleta um pacote de skin de bonk da database do bot.")
    async def delete_skin(self, ctx, skin_id: int):
        if ctx.author.id not in ALLOWED_USER_IDS:
            await ctx.respond("Você não tem permissão para deletar skins.", ephemeral=True)
            return

        cursor = self.skin_database.cursor()
        cursor.execute("SELECT * FROM skins WHERE id=?", (skin_id,))
        skin = cursor.fetchone()
        if skin:
            cursor.execute("DELETE FROM skins WHERE id=?", (skin_id,))
            self.skin_database.commit()
            await ctx.respond(f"Skin {skin_id} deletada com sucesso.", ephemeral=True)
            self.reorder_skins()
        else:
            await ctx.respond("ID de skin inválido.", ephemeral=True)

    @commands.slash_command(description="Deleta um pacote de skin de bonk da sua vault privada.")
    async def delete_skin_vault(self, ctx, skin_id: int):
        cursor = self.vault_database.cursor()
        cursor.execute("SELECT * FROM vault WHERE id=? AND user_id=?", (skin_id, ctx.author.id))
        skin = cursor.fetchone()
        if skin:
            cursor.execute("DELETE FROM vault WHERE id=? AND user_id=?", (skin_id, ctx.author.id))
            self.vault_database.commit()
            await ctx.respond(f"Skin {skin_id} deletada com sucesso.", ephemeral=True)
            self.reorder_vault_skins(ctx.author.id)
        else:
            await ctx.respond("ID de skin inválido.", ephemeral=True)

    def reorder_skins(self):
        cursor = self.skin_database.cursor()
        cursor.execute("SELECT * FROM skins ORDER BY id ASC")
        skins = cursor.fetchall()
        new_id = 1
        for skin in skins:
            cursor.execute("UPDATE skins SET id=? WHERE id=?", (new_id, skin[0]))
            new_id += 1
        self.skin_database.commit()

    def reorder_vault_skins(self, user_id):
        cursor = self.vault_database.cursor()
        cursor.execute("SELECT * FROM vault WHERE user_id=? ORDER BY id ASC", (user_id,))
        skins = cursor.fetchall()
        new_id = 1
        for skin in skins:
            cursor.execute("UPDATE vault SET id=? WHERE id=? AND user_id=?", (new_id, skin[0], user_id))
            new_id += 1
        self.vault_database.commit()

def setup(bot):
    bot.add_cog(Bonk(bot))
