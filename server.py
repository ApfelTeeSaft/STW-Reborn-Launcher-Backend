import hikari
from flask import Flask, jsonify, request
from flask_cors import CORS
import lightbulb
import requests
import json
from datetime import datetime

# Discord bot
bot = lightbulb.BotApp(token="your_token_here", intents=hikari.Intents.ALL)

# Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

access_status_message = 'Access Allowed'  # Default access status

announcements_file = "announcements.json"

def save_announcements():
    with open(announcements_file, 'w') as file:
        json.dump(announcements_data, file)

def load_announcements():
    global announcements_data
    try:
        with open(announcements_file, 'r') as file:
            announcements_data = json.load(file)
    except FileNotFoundError:
        announcements_data = []

load_announcements()

#overall just endpoints
@app.route('/api/version', methods=['GET'])
def get_version():
    # You can replace this with your actual version
    return jsonify(version='0.2')

@app.route('/api/access_status', methods=['GET'])
def get_access_status():
    return jsonify(message=access_status_message)

@app.route('/api/announcements', methods=['GET'])
def get_announcements():
    sorted_announcements = sorted(announcements_data, key=lambda x: x['datetime'], reverse=True)
    return jsonify({"announcements": sorted_announcements})

#check server status
@bot.command()
@lightbulb.command("server-check", "Checks the Status of the Backend")
@lightbulb.implements(lightbulb.SlashCommand)
async def check_access(ctx: lightbulb.SlashContext) -> None:
    try:
        response = requests.get('http://127.0.0.1:5000/api/access_status')
        response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)

        data = response.json()
        print(data)

        if data["message"] == "Access Denied":
            await ctx.respond("Server is Offline!")
        elif data["message"] == "Access Allowed":
            await ctx.respond("Server is Online!")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        await ctx.respond("Error checking server status.")

#unlock the launcher
@bot.command()
@lightbulb.command("unlock-launcher", "Unlock the Launcher")
@lightbulb.implements(lightbulb.SlashCommand)
async def unlock_launcher(ctx: lightbulb.SlashContext) -> None:
    global access_status_message
    access_status_message = 'Access Allowed'
    await ctx.respond('Access status changed to Allowed.')

#lock the launcher
@bot.command()
@lightbulb.command("lock-launcher", "Lock the launcher")
@lightbulb.implements(lightbulb.SlashCommand)
async def lock_launcher(ctx: lightbulb.SlashContext) -> None:
    global access_status_message
    access_status_message = 'Access Denied'
    await ctx.respond('Access status changed to Denied.')

#announcement adder
@bot.command()
@lightbulb.option("message", "The message of the announcement")
@lightbulb.command("add-announcement", "Add a new announcement")
@lightbulb.implements(lightbulb.SlashCommand)
async def add_announcement_command(ctx: lightbulb.SlashContext) -> None:
    # Static variables for author and avatar change if needed
    author = "ApfelTeeSaft"
    avatar = "https://media.discordapp.net/attachments/786639486041587762/1175142438625611786/avatar.png"

    # Access the value of the "message" option
    message = ctx.options.message

    new_announcement = {
        "author": author,
        "message": message,
        "avatar": avatar,
        "datetime": str(datetime.utcnow())
    }
    announcements_data.append(new_announcement)
    save_announcements()
    await ctx.respond("Announcement added successfully")

# announcement remover next 

# Version command
@bot.command()
@lightbulb.command("version", "get the current version list")
@lightbulb.implements(lightbulb.SlashCommand)
async def get_version(ctx: lightbulb.SlashContext) -> None:
    try:
        response = requests.get('http://127.0.0.1:5000/api/version')
        response.raise_for_status()

        version_data = response.json()
        print(version_data)

        if version_data["version"] == "0.3":
            await ctx.respond(f"Launcher Version: 0.3\nBackend Version: Soon...\nMatchmaker Version: Soon...\nGameserver Version: Soon...")
        else:
            await ctx.respond("Error getting Version list!")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        await ctx.respond("Error checking server status.")

# Run Flask
import threading

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Create threads for Flask
flask_thread = threading.Thread(target=run_flask)

# Start threads
flask_thread.start()

# Start bot
bot.run()