# from web_shop.bot.main import bot
# bot.polling()

from web_shop.bot.main import app, set_webhook

if __name__ == '__main__':
    set.webhook()
    app.run(port = 8000, debug = True)