import discord
from discord.ext import commands, pages

class Base(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Responde com a latência do bot em milissegundos.")
    async def ping(self, ctx):
        ping = self.bot.latency
        await ctx.respond("Pong!")
        await ctx.respond(f"Meu ping está em {round(ping * 1000)}ms.", ephemeral=True)

    @commands.slash_command(description="Exibe informações sobre os comandos disponíveis.")
    async def help(self, ctx):
        commands_list = [
            ("/ping", "Retorna a latência do bot em milissegundos."),
            ("/add_skin", "Adiciona um pacote de skin de bonk à database do bot."),
            ("/list_skins", "Lista os pacotes de skin de bonk na database do bot."),
            ("/get_skin", "Envia um arquivo .blsm da skin solicitada."),
            ("/add_to_vault", "Adiciona uma skin à sua vault privada."),
            ("/list_vault", "Lista as skins na sua vault privada."),
            ("/get_vault_skin", "Envia um arquivo .blsm da skin solicitada na sua vault privada."),
            ("/delete_skin", "Deleta um pacote de skin de bonk da database do bot. (Apenas para usuários autorizados)"),
            ("/tutorial", "Envia um tutorial de como conseguir o avatar da sua skin de Bonk."),
            ("/delete_skin_vault", "Deleta um pacote de skin de bonk da sua vault privada")
        ]

        command_pages = []
        for command, description in commands_list:
            embed = discord.Embed(
                title="Comando:",
                description=f"{command}\n\nDescrição:\n{description}",
                color=discord.Color.blue()
            )
            command_pages.append(embed)

        paginator = pages.Paginator(pages=command_pages)
        await paginator.respond(ctx.interaction, ephemeral=True)

    @commands.slash_command(description="Envia um tutorial de como usar os comandos do bot de Bonk.io")
    async def tutorial(self, ctx):
        tutorial = [
            "1. Abra o website [Bonk Leagues Skins](https://bonkleagues.io/skins.html#)",
            "2. Faça login com sua conta do Bonk.io",
            "3. Crie uma nova skin no site ou importe sua skin equipada do Bonk.io",
            "4. No 'Skins Manager', arraste para baixo na página e clique em 'Backup Skins'",
            "5. Clique em 'Export All Skins to a File'",
            "6. Abra o arquivo baixado e clique em 'Abrir com Bloco de Notas'",
            "7. Localize a skin que deseja adicionar pelo nome e copie a chave da skin após 'avatar'",
            "8. Cada skin deve estar no formato: [{'name':'Nome da Skin', 'avatar':'Chave da Skin', 'cred':'Bonk Leagues Skin Editor'}]",
            "9. Após copiar a chave da skin, use o comando `/add_skin` para adicionar à lista pública de skins e `/add_skin_private` para adicionar à sua vault privada",
            "10. Coloque o nome desejado para a skin no campo 'Nome' e a chave copiada no campo 'Avatar'",
            "11. Use o comando `/list_skins` para listar as skins públicas e `/list_vault` para listar suas skins privadas",
            "12. Use o comando `/get_skin` ou `/get_vault_skin` seguido pelo ID da skin que deseja instalar",
            "13. Instale o arquivo enviado pelo bot e, no website do Bonk Leagues, vá para a área de 'Backup Skins' e clique em 'Import Skins from a File'",
            "14. Selecione o arquivo da skin que deseja colocar no seu Bonk Leagues e abra-o",
            "15. Na página 'Skins Manager', selecione sua skin instalada e clique em 'Apply' para colocar na sua conta do Bonk.io"
        ]

        tutorial_text = "\n".join(tutorial)
        embed = discord.Embed(
            title="Tutorial: Como usar os comandos do bot de Bonk.io",
            description=tutorial_text,
            color=discord.Color.green()
        )
        embed.set_thumbnail(url="https://i.imgur.com/fKvfiBh.png")  # Adicione um thumbnail opcional
        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Base(bot))
