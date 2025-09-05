# ❤️ Long Distance Message Box ❤️

Sometimes texting just isn't enough when you're miles apart from someone you care about. I built this WiFi-connected message box as an alternative to those $200 commercial "Loveboxes" – and managed to finish it in 8 hours before my girlfriend's flight back home.

The concept is simple but meaningful: send a message through a web interface, the box chimes when it arrives, and the recipient shakes it to reveal the message on a built-in display. It's like getting a letter in the mail, but with modern IoT tech!

## Features

- Shake-to-reveal messaging with motion detection
- WiFi connectivity for remote message sending
- Custom hand-drawn emoji support with text codes
- Scrolling display for longer messages
- Battery powered with USB-C charging
- Real-time Firebase backend

The hardware centers around a tinyCore microcontroller (my custom ESP32-S3 dev. platform) connected to an ST7735 color display and piezo buzzer. The whole thing fits inside a small velvet box I found at Goodwill. I also created a Python tool for designing the pixel art emojis, since the display library didn't include them.

The web interface is a simple HTML page that connects to Firebase, where both the sender and receiver sides sync their message state. When you send a message, it immediately appears in the database, triggers the notification chime, and displays properly formatted text with emoji parsing.

You can find the full write-up on Instructables!

**📖 Full Tutorial:** [How to Make a Long Distance Message Box - Instructables](https://www.instructables.com/-How-to-Make-a-Long-Distance-Message-Box-/)