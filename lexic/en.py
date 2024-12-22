lexicon: dict[str:str] = {
    'msg_from_admin': 'Message from administrator:',
    'help': '⚛️ The bot allows you to communicate with the neural network on arbitrary topics - it can share facts, '
            'advise, answer questions, make up selling texts and assist with various tasks. '
            '\n\n💬 Any message you send, except commands, starts a chat with the neural network.'
            '\n\n📝 When answering questions, the bot uses the context of your previous messages. '
            'To start a new conversation with the bot, delete the current context using the command.'
            '\n\n🖼 You can also send a photo and a text question to it in one message. '
            'Photos are not saved in context and are processed out of context.'
            '\n\n⚙️ List of commands:'
            '\n/delete_context - delete context'
            '\n/language - change language'
            '\n/model - change neural network model'
            '\n/system - set neural network behaviour'
            '\n/status - check your token usage'
            '\n/admin - contact the bot creator'
    ,

    'start': 'Hello!\n\n',
    'premium_model': 'This model can be accessed with /premium',
    'premium': 'Payment feature is not yet set up, ask /admin personally for premium status :)',

    'admin': '📩 Your next message will be sent to the bot admin. To cancel, press /cancel',
    'admin_sent': '✅ Message sent to the bot admin:\n',
    'system': 'Set a system prompt - an instruction that affects the generation of responses.'
              '\nFor example:'
              '\n- Use curse words in every sentence (<i>only works for llama3</i>)'
              '\n- Answer like an experienced specialist'
              '\n- Answer briefly'
              '\nTo cancel or reset, click /cancel'
    ,
    'limit': '⚠️ You have exceeded the daily token limit. You cannot use me for today, see you tomorrow.'
             '\nGet rid of limits with /premium',
    'system_ok': '✅ System prompt saved:\n',
    'cancel': 'Action cancelled. You can continue chatting with the GPT bot.',

    'delete_context': '\nContext deleted',
    'model': 'Chose the neural network model. Now you have: <code>{}</code>'
             '\n▫️ mixtral-8x7b - universal'
             '\n▫️ llama3-70b - capable of swearing'
             '\n▫️ codestral - optimized for code generation'
             '\n🔸 o-1 - the smartest and newest (does not support streaming and system prompts), requires /premium'
             '\n▪️ gpt-4o-mini - cannot be chosen, applied automatically to read photos you send'
    ,
    'model_ok': 'Model choice saved: <code>{}</code>',
    'not_visual': '⚠️ To work with photos please select <code>gpt-4o</code>',
    'caption': '⚠️ Send a photo and a text question to it in one message',
    'unsupported_file': '⚠️ Such file type is not yet supported',

    'status_adm': 'Token usage:'
                  '\n{} you / {} all today'
                  '\n{} you / {} all total'
    ,
    'status': 'Token usage:'
              '\n{} today (limit {})'
              '\n{} total'
    ,
    'no_ref': 'The link is invalid. Ask the person who brought you to us for a valid link.',
    'lang_ok': 'Language set to {}',
    'ban': 'Your access to the bot is limited.',

}
