lexicon: dict[str:str] = {
    'msg_from_admin': 'Сообщение от администратора:',
    'start': 'Привет!\n\n',
    'help': '⚛️ Бот позволяет общаться с нейросетью на произвольные темы - может поделиться фактами, консультировать, '
            'отвечать на вопросы и помогать в различных задачах. '
            '\n\n💬 Любое ваше сообщение, кроме команд, запускает чат с нейросетью.'
            '\n\n📝 Отвечая на вопросы, бот использует контекст ваших предыдущих сообщений. '
            'Чтобы начать новый разговор с ботом - удалите текущий контекст с помощью команды.'
            '\n\n⚙️ Список команд:'
            '\n/delete_context - удалить контекст'
            '\n/language - смена языка'
            '\n/model - выбрать модель нейросети'
            '\n/system - задать поведение нейросети'
            '\n/status - посмотреть свой расход токенов'
            '\n/admin - связь с создателем бота'
    ,

    'admin': '📩 Следующее ваше сообщение будет отправлено админу бота. Для отмены нажмите /cancel',
    'admin_sent': '✅ Ваше сообщение передано админу бота:\n',
    'system': 'Задайте системный промпт - это настройка, влияющая на генерацию ответов.'
              '\nНапример:'
              '\n- Используй маты в каждом предложении (<i>работает только с llama3</i>)'
              '\n- Отвечай, как опытный специалист'
              '\n- Отвечай кратко'
              '\nДля отмены или очистки нажмите /cancel'
    ,
    'limit': '⚠️ Вы превысили дневную квоту токенов. Сегодня мною больше нельзя пользоваться, увидимся завтра.',
    'system_ok': '✅ Системный промпт сохранен:\n',
    'cancel': 'Отмена действия. Можете продолжать чат с нейросетью.',

    'delete_context': 'Контекст удален',
    'model': 'Выберите модель нейросети. Сейчас: <code>{}</code>',
    'model_ok': 'Выбана модель: <code>{}</code>',
    'not_visual': 'Чтобы работать с фото, выберите /model <code>gpt-4o</code>',

    'status_adm': 'Расход токенов:'
                  '\n{} ты / {} все за сегодня'
                  '\n{} ты / {} все за все время'
    ,
    'status': 'Расход токенов:'
              '\n{} за сегодня (лимит {})'
              '\n{} за все время'
    ,
    'no_ref': 'Ссылка недействительна. Спросите ссылку у того, кто привел вас к нам.',
    'ban': 'Вам заблокирован доступ к боту.',
    'lang_ok': 'Выбран язык {}. Язык ответов нейросети изменится после удаления контекста.'
               '\nНажмите /help, чтобы увидеть все команды',

}
