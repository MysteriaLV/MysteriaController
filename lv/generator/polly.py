import boto3

phrases = {
    '31_exit_code': {
        'ru': '<emphasis level="strong">код</emphasis> от выхода из лаборатории 3 1 7 5, повторяю 3 1 7 5',
        'lv': 'Latvian',
        'en': 'The exit code from the lab is 3 1 7 5, I repeat 3 1 7 5'
    },
    'AAA1': {
        'ru': 'Хорошо, я включил вам рентген монитор на стене. Сейчас он загорится. Что-то ещё?',
        'lv': 'Latvian',
        'en': 'Good, I\'m turning on X-Ray monitor on the wall. It will light up soon. Anything else?',
    },
    'ABA1': {
        'ru': 'Вам надо выставить рычаги <break strength="strong"/> и кнопки на пульте в правильной последовательности.',
        'lv': 'Latvian',
        'en': 'You need to operate levers and buttons on the console in right order.'
    },
    'ABA2': {
        'ru': 'Найдите в <emphasis>техническом журнале</emphasis> идентичные планы пульта управления',
        'lv': 'Latvian',
        'en': 'Find identical console in the reference manual book.'
    },
    'ABA3': {
        'ru': 'Нужная вам схема пульта - <emphasis> эр - восемь</emphasis>',
        'lv': 'Latvian',
        'en': 'You need the reference plan <emphasis>R - 8</emphasis>'
    },
    'ACB1': {
        'ru': 'Используйте жесты для открытия секретного ящика',
        'lv': 'Latvian',
        'en': 'Use gestures to open the secret compartment'
    },
    'ACB2': {
        'ru': 'Чтобы узнать нужные жесты, используйте знаки с рентгеновских снимков.',
        'lv': 'Latvian',
        'en': 'To learn the correct gestures - use directions from x-ray photos'
    },
    'ACB3': {
        'ru': 'Полученные знаки изобразите движениями руки перед считывающим устройством под колбами.',
        'lv': 'Latvian',
        'en': 'Please wave you hands in front of sensor under the species tubes according to directions.'
    },
    'BAC1': {
        'ru': 'Чтобы выполнить это задание - вам понадобится несколько членов команды. Соедините руки.',
        'lv': 'Latvian',
        'en': 'To solve this task you will need several players. Connect your hands.'
    },
    'BAC2': {
        'ru': 'Чтобы замкнуть цепь, приложите ладони к выемкам на стене и сомкните руки.',
        'lv': 'Latvian',
        'en': 'To connect the circuit, place your palms on the hand shaped panels on the wall, and connect your hands'
    },
    'BBB1': {
        'ru': 'Да, со светом гораздо лучше видно. Как ещё вам помочь?',
        'lv': 'Latvian',
        'en': 'Yes, it is much better with a light. How else can I help you?'
    },
    'BCA1': {
        'ru': 'Чтобы понять правильную последовательность цветных шаров, соберите цепочку ДНК в инкубаторе.',
        'lv': 'Latvian',
        'en': 'Solve the DNA puzzle to learn the correct sequence of colored balls'
    },
    'BCA2': {
        'ru': 'Цвет шариков соответствуют цветам молекул цепочки ДНК в инкубаторе.',
        'lv': 'Latvian',
        'en': 'Ball colors are equal to the DNA sequence in incubator.'
    },
    'BCB1': {
        'ru': 'Вторую часть кода от выхода получите у меня.',
        'lv': 'Latvian',
        'en': 'Please get the second part of code from me'
    },
    'BCB2': {
        'ru': 'Для подтверждения идентичности введите первую часть кода с пульта сюда.',
        'lv': 'Latvian',
        'en': 'Enter first part of the code here to confirm your authorization'
    },
    'CBA1': {
        'ru': 'Где-то в лаборатории найдите рентгеновские снимки.',
        'lv': 'Latvian',
        'en': 'Find and collect x-ray photos through the lab'
    },
    'CBA2': {
        'ru': 'Определите нужные по серийным номерам - они идут по порядку.',
        'lv': 'Latvian',
        'en': 'Figure out correct serial numbers - they are sequential'
    },
    'CBA3': {
        'ru': 'Разместите снимки друг над другом и вставьте в рентгеновский экран, чтобы увидеть последовательность направлений жестов.',
        'lv': 'Latvian',
        'en': 'Stack correct x-ray photos on the x-ray monitor to reveal gesture directions'
    },
    'CBC1': {
        'ru': 'Запомните пары - колба-кнопка, они загорятся по очереди.',
        'lv': 'Latvian',
        'en': 'Remember the pairs - tube + button, they will light up one by one'
    },
    'CBC2': {
        'ru': 'Обратите внимание, что колба равняется кнопке.',
        'lv': 'Latvian',
        'en': 'Keep in mind that tube equals button'
    },
    'CBC3': {
        'ru': 'Запомните, какую кнопку надо нажать - для загоревшейся синей лампочки.',
        'lv': 'Latvian',
        'en': 'Remember which button you need to press for each blue lamp.'
    },
    'code_error': {
        'ru': 'Стандартный код подсказки, это три буквы - и одна цифра. А то, что вы ввели я не понимаю. Или же этой подсказки не существует.',
        'lv': 'Latvian',
        'en': 'Standard hint code is three letters and one number. I do not understand the code you entered. Or there is no such hint'
    },
    'translator_ready': {
        'ru': '1, 2, 3… Проверка… Компьютер идентифицировал ваш язык как русский. Активирована функция синхронного перевода. Теперь вы сможете понимать капрала.',
        'lv': 'Latvian',
        'en': '1, 2, 3… Testing… Computer identified your language as English. Activating synchronous translation. Now you can understand the corporal.'}
}

polly_client = boto3.Session(
    region_name='us-west-2').client('polly')

for phrase_id, phrase in phrases.items():

    for lang, voice in {'ru': 'Maxim', 'en': 'Brian'}.items():
        print(phrase[lang])
        response = polly_client.synthesize_speech(VoiceId=voice,
                                                  OutputFormat='mp3',
                                                  TextType='ssml',
                                                  Text=f"<speak><amazon:breath/>{phrase[lang]}</speak>")

        file = open(f'audio/{lang}/hints/{phrase_id}.mp3', 'wb')
        file.write(response['AudioStream'].read())
        file.close()
