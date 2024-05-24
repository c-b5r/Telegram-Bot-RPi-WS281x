#!/bin/python3

import asyncio
import colorsys
import os
import time

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from rpi_ws281x import *

# Configuration for WS2812B
LED_COUNT = 150       # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)

CURRENT_COLOR = (0, 0, 0) # Current color of the LEDs (as RGB tuple)
BRIGHTNESS_STEP = 51 # Brightness change step
SATURATION_STEP = 0.2 # Saturation change step

# Create NeoPixel object with appropriate configuration.
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

# Initialize bot and dispatcher
bot = Bot(token=os.environ.get("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Keyboard buttons

## Mapping for keyboard items

def brightness_dec():
    #adjust_brightness(-BRIGHTNESS_STEP)
    adjust_brightness_with_fade(-BRIGHTNESS_STEP)

def brightness_inc():
    #adjust_brightness(BRIGHTNESS_STEP)
    adjust_brightness_with_fade(BRIGHTNESS_STEP)

def saturation_dec():
    #adjust_saturation(-SATURATION_STEP)
    adjust_saturation_with_fade(-SATURATION_STEP)

def saturation_inc():
    #adjust_saturation(SATURATION_STEP)
    adjust_saturation_with_fade(SATURATION_STEP)

controls_map = {
    '🔸': saturation_dec,
    '🔶': saturation_inc,
    '🔅': brightness_dec,
    '🔆': brightness_inc
}

colors_map = {
    '⬛️': (0, 0, 0),
    '🟥': (255, 0, 0),
    '🟧': (255, 127, 0),
    '🟨': (255, 255, 0),
    '🟩': (0, 255, 0),
    '🟦': (0, 0, 255),
    '🟪': (127, 0, 255),
    '⬜️': (255, 255, 255)
}

## Arrange buttons

keyboard_markup = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_markup.row(*controls_map.keys())
keyboard_markup.row(*colors_map.keys())

# Helper functions

## Adjust color, brightness and saturation

def rgb_to_color(rgb):
    """Convert an RGB tuple to NeoPixel Color."""
    return Color(rgb[0], rgb[1], rgb[2])

def set_led_color(rgb):
    """Set color to all LEDs."""
    global CURRENT_COLOR
    CURRENT_COLOR = rgb
    color = rgb_to_color(rgb)
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
    strip.show()

def adjust_brightness(step):
    """Adjust LED brightness."""

    global LED_BRIGHTNESS
    LED_BRIGHTNESS = max(0, min(255, LED_BRIGHTNESS + step))
    strip.setBrightness(round(LED_BRIGHTNESS))
    set_led_color(CURRENT_COLOR)  # Re-apply the current color with new brightness

def adjust_saturation(step):
    """Adjust color saturation."""
    global CURRENT_COLOR
    h, l, s = colorsys.rgb_to_hls(CURRENT_COLOR[0]/255.0, CURRENT_COLOR[1]/255.0, CURRENT_COLOR[2]/255.0)
    s = max(0, min(1, s + step))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    set_led_color((int(r*255), int(g*255), int(b*255)))

## With fade

### Color

def set_led_color_with_fade(new_color, duration=1.0):
    """Set color to all LEDs with a fade effect."""
    global CURRENT_COLOR
    steps = 100
    delay = duration / steps

    for step in range(steps + 1):
        intermediate_color = [int(CURRENT_COLOR[i] + (new_color[i] - CURRENT_COLOR[i]) * step / steps) for i in range(3)]
        color = rgb_to_color(intermediate_color)
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, color)
        strip.show()
        time.sleep(delay)

    CURRENT_COLOR = new_color

### Brightness / Saturation

def adjust_brightness_with_fade(total_step, duration=1.0):
    """Adjust LED brightness with a fade effect."""
    steps = 25  # Number of steps for the fade effect
    delay = duration / steps  # Time delay between each step
    step_size = total_step / steps  # Size of each step

    for _ in range(steps):
        adjust_brightness(step_size)
        time.sleep(delay)

def adjust_saturation_with_fade(total_step, duration=1.0):
    """Adjust color saturation with a fade effect."""
    steps = 25  # Number of steps for the fade effect
    delay = duration / steps  # Time delay between each step
    step_size = total_step / steps  # Size of each step

    for _ in range(steps):
        adjust_saturation(step_size)
        time.sleep(delay)

# Handle incoming messages

## Controls

@dp.message_handler(lambda message: message.text in controls_map.keys())
async def led_color(message: types.Message):
    controls_map[message.text]()
    await message.reply(f"Brightness/saturation changed: {message.text}", reply_markup=keyboard_markup)

## Colors

@dp.message_handler(lambda message: message.text in colors_map.keys())
async def led_color(message: types.Message):
    # set_led_color(colors_map[message.text])
    set_led_color_with_fade(colors_map[message.text])
    await message.reply(f"Color changed to {message.text}", reply_markup=keyboard_markup)


if __name__ == '__main__':
    # Start the bot
    asyncio.run(dp.start_polling())
