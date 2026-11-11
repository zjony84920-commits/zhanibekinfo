# ZhanibekInfo — Safari және Google Chrome-ға бейімделген сайт

Бұл — HTML, CSS және JavaScript негізіндегі статикалық сайт. Қазіргі Safari, Google Chrome, Microsoft Edge және Firefox браузерлеріне арналған. Мобильді экрандарға да бейімделген.

## Компьютерде тексеру
1. ZIP архивті шығарып алыңыз.
2. `index.html` файлын Safari немесе Google Chrome арқылы ашыңыз.
3. VS Code қолдансаңыз, папканы ашып, Live Server арқылы іске қосыңыз.

## Google Firebase Hosting арқылы интернетке жариялау
Firebase Hosting HTML, CSS, JavaScript және суреттерді орналастыра алады; сайтқа `web.app` және `firebaseapp.com` қосалқы домендері беріледі.

1. https://console.firebase.google.com/ сайтына Google аккаунтыңызбен кіріңіз.
2. **Create a project** арқылы жаңа жоба ашыңыз.
3. Компьютерге Node.js және Firebase CLI орнатыңыз.
4. Осы папканы терминалда ашып, мына командаларды орындаңыз:

```bash
npm install -g firebase-tools
firebase login
firebase init hosting
```

5. Жоба таңдағанда жаңа Firebase жобаны таңдаңыз. Public directory сұрағына `.` деп жазыңыз. `index.html` бар екенін растаңыз. Бір беттік сайтқа rewrite қажет емес. Егер `firebase init` `firebase.json` файлын қайта жазса, осы папкадағы дайын `firebase.json` мазмұнын қайта қойыңыз.
6. Жариялау командасы:

```bash
firebase deploy --only hosting
```

7. Firebase терминалда дайын сайт адресін көрсетеді: `https://PROJECT_ID.web.app`. `PROJECT_ID` — Firebase жобасының нақты идентификаторы; оны өз жобаңыздан аласыз.

## Өз доменіңізді қосу
Firebase Console → Hosting → Add custom domain арқылы доменді қосып, домен тіркеушісіндегі DNS жазбаларын Firebase көрсеткен мәндерге өзгертіңіз. SSL сертификаты Firebase арқылы беріледі. Доменді алдын ала тіркеу қажет.

**Маңызды:** `Zhanibekinfo.kzinfo` адресі қазір тіркелген/жұмыс істейтін сайт адресі емес. `.kzinfo` ресми жоғарғы деңгейлі домен ретінде расталмаған. `zhanibekinfo.kz` сияқты `.kz` доменін тіркеушіден тексеріңіз. Firebase Hosting-та жарияланғанша сайттың жалпыға ашық сілтемесі болмайды.

## Құрылымы
- `index.html` — сайт мазмұны
- `style.css` — дизайн және responsive layout
- `script.js` — навигация және мобильді мәзір
- `assets/` — фотосуреттер
- `firebase.json` — Google Firebase Hosting конфигурациясы
- `404.html` — табылмаған бетке арналған бет
