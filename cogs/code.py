import discord
from discord.ext import commands
from pyston import File, PystonClient
from pyston.exceptions import *


class Code(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.message_command(description="Execute code")
    async def execute(self, ctx, message: discord.Message):
        await ctx.defer()  # Allow response to take longer than 3 seconds

        code_blocks = get_code_blocks_with_languages(message.content)

        responses = []
        for block in code_blocks:
            try:
                output = await execute_code(block["language"], block["code"])
                result = f"```{str(output)}```"
            except InvalidLanguage:
                result = "Invalid language"
            except TooManyRequests:
                result = "Too many requests. Please slow down"
            except (ExecutionError, InternalServerError, UnexpectedError):
                result = "An unknown error has occured ¯\_(ツ)_/¯"

            responses.append(f'```{block["language"]}\n{block["code"]}```{result}')

        if len(responses) == 0:
            await ctx.respond(
                "This command must be used on a message containing a code block with a language specified"
            )

        response = "\n".join(responses)
        await ctx.respond(response)


async def execute_code(language, code):
    client = PystonClient()

    language = convert_language_alias(language)

    # Check if language is valid
    await client.get_runtimes(language)  # Raises InvalidLanguage if language is invalid

    # Execute code
    result = await client.execute(
        language, [File(code)]
    )  # Raises TooManyRequests, ExecutionError, InternalServerError or UnexpectedError
    return result


# Get code blocks and languages from a message string
def get_code_blocks_with_languages(txt):
    result = []
    blocks = txt.split("```")
    i = 1
    while i < len(blocks) - 1:
        lang_and_code = blocks[i].split("\n", 1)
        result.append({"language": lang_and_code[0], "code": lang_and_code[1]})
        i += 2

    return result


# Convert language to a format that works in Piston
def convert_language_alias(lang):
    if lang.lower() == "c#":
        return "csharp"
    if lang.lower() == "cplusplus":
        return "c++"
    return lang.lower()


def setup(bot):
    bot.add_cog(Code(bot))
