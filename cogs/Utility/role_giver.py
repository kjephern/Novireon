import discord

from discord import app_commands
from discord import Interaction as Itat
from discord.ext import commands


class RoleGiverView(discord.ui.View):
    def __init__(self, roles: list[discord.Role] = None):
        super().__init__(timeout=None)

        self.menu_custom_id = "role_giver_view"

        if roles is None:
            options = [discord.SelectOption(label="載入中", value="0")]
            max_vals = 1
        else:
            options = [discord.SelectOption(label=role.name[:100], value=str(role.id)) for role in roles]
            max_vals = len(options)

        self.select = discord.ui.Select(
            custom_id=self.menu_custom_id,
            placeholder="請選擇你要的身分組",
            min_values=0,
            max_values=max_vals,
            options=options,
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):

        selected_ids = [int(v) for v in self.select.values]

        menu_role_ids = []
        for action_row in interaction.message.components:
            for child in action_row.children:
                if getattr(child, "custom_id", None) == self.menu_custom_id:
                    menu_role_ids = [int(opt.value) for opt in child.options if opt.value.isdigit()]
                    break

        if not menu_role_ids:
            return await interaction.response.send_message("❌ 無法讀取選單內容。", ephemeral=True)

        user = interaction.user
        guild = interaction.guild

        to_add = []
        to_remove = []

        for role_id in menu_role_ids:
            role = guild.get_role(role_id)
            if not role:
                continue

            if role_id in selected_ids:
                if role not in user.roles:
                    to_add.append(role)
            else:
                if role in user.roles:
                    to_remove.append(role)

        if to_add:
            await user.add_roles(*to_add)
        if to_remove:
            await user.remove_roles(*to_remove)

        await interaction.response.send_message("您的身分組已成功更新！", ephemeral=True)


class RoleSetupView(discord.ui.View):
    def __init__(self, roles: list[discord.Role], title: str):
        super().__init__(timeout=180)
        self.title = title
        self.message = None

        options = [discord.SelectOption(label=role.name[:100], value=str(role.id)) for role in roles]

        self.select = discord.ui.Select(
            placeholder="請勾選要放入此面板的身分組...", min_values=1, max_values=len(options), options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        selected_roles = [interaction.guild.get_role(int(role_id)) for role_id in self.select.values]

        giver_view = RoleGiverView(roles=selected_roles)

        desc = "\n".join([f"▸ {role.mention}" for role in selected_roles])
        embed = discord.Embed(
            title=self.title, description=f"請在下方選單選擇您需要的身分組：\n\n{desc}", color=discord.Colour.blue()
        )

        await interaction.channel.send(embed=embed, view=giver_view)

        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(content="面板建立成功！", view=self)
        self.stop()

    async def on_timeout(self):
        if self.message:
            for item in self.children:
                item.disabled = True
            try:
                await self.message.edit(content="設定已超時，請重新執行指令。", view=self)
            except:
                pass


class RoleGiver:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    role_giver = app_commands.Group(
        name="role_giver",
        description="Player setting up commands.",
        allowed_installs=app_commands.AppInstallationType(guild=True, user=False),
        default_permissions=discord.Permissions(manage_guild=True),
    )

    @role_giver.command(name="creat", description="建立身分組選擇選單")
    async def creat_role_giver(self, itat: Itat, title: str):
        available_roles = []
        for role in itat.guild.roles:
            if role.is_default():
                continue
            if not role.is_assignable():
                continue
            if role.is_bot_managed():
                continue
            if role.is_integration():
                continue
            if role.is_premium_subscriber():
                continue
            available_roles.append(role)

        if len(available_roles) > 25:
            available_roles = available_roles[:25]

        if not available_roles:
            await itat.response.send_message("找不到機器人有權限分配的身分組。", ephemeral=True)
            return

        setup_view = RoleSetupView(roles=available_roles, title=title)

        await itat.response.send_message(content="請選擇你要開放給玩家領取的身分組：", view=setup_view, ephemeral=True)

        setup_view.message = await itat.original_response()
