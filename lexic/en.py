lexicon: dict[str:str] = {
    'msg_from_admin': 'Message from administrator:',
    'help': '⚛️ The bot allows you to communicate with the neural network on arbitrary topics - it can share facts, '
            'advise, answer questions and assist with various tasks. '
            '\n\n💬 Any message you send, except commands, starts a chat with the neural network.'
            '\n\n📝 When answering questions, the bot uses the context of your previous messages. '
            'To start a new conversation with the bot, delete the current context using the command.'
            '\n\n⚙️ List of commands:'
            '\n/delete_context - delete context'
            '\n/language - change language'
            '\n/model - change neural network model'
            '\n/admin - contact the bot creator'
    ,

    'start': 'Hello!\n\n',

    'admin': '📩 Your next message will be sent to the bot admin. To cancel, press /cancel',
    'admin_sent': '✅ Message sent to the bot admin:\n',
    'system': 'Set a system prompt - an instruction that affects the generation of responses.'
              '\nFor example:'
              '\n- Use curse words in every sentence'
              '\n- Answer like an experienced specialist'
              '\n- Answer briefly'
              '\nTo cancel or delete, click /cancel'
    ,
    'system_ok': '✅ System prompt saved:\n',
    'cancel': 'Action cancelled. You can continue chatting with the GPT bot.',

    'delete_context': 'Context deleted',
    'model': 'Chose the neural network model',
    'model_ok': 'Model choice saved: {}\n(this does not affect anything yet, in development)',
    'status': 'Unavailable',
    'no_ref': 'The link is invalid. Ask the person who brought you to us for a valid link.',
    'lang_ok': 'Language set to {}. AI response language will change after context deletion.'
               '\nTo see a list of commands, press /help',
    'ban': 'Your access to the bot is limited.',

}
