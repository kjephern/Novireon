import discord
import random

from discord import app_commands
from discord.ext import commands


class Roll:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    roll = app_commands.Group(
        name="roll",
        description="抽籤指令",
    )

    @roll.command(name="pick", description="隨機取數")
    @app_commands.describe(
        max="最大數字 (必須大於 1)",
        count="選擇的數字個數 (預設為 1)",
        replace="是否允許重複選擇 (預設為 False)",
    )
    async def pick(self, itat: discord.Interaction, max: int, count: int = 1, replace: bool = False):
        """從 1 到 max 中隨機選擇 count 個數字。

        參數:
        - max: 最大數字 (必須大於 1)
        - count: 選擇的數字個數 (預設為 1)
        - replace: 是否允許重複選擇 (預設為 False)
        """
        if max < 1:
            await itat.response.send_message("最大數字必須大於 1。", ephemeral=True)
            return

        if count < 1:
            await itat.response.send_message("選擇的數字個數必須至少為 1。", ephemeral=True)
            return

        if count > max and not replace:
            await itat.response.send_message("選個姬芭，我就問了?", ephemeral=True)
            return

        if replace:
            choices = [random.randint(1, max) for _ in range(count)]
        else:
            choices = random.sample(range(1, max + 1), min(count, max))

        await itat.response.send_message(", ".join(map(str, choices)))
