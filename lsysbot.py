"""Bot to explore L-systems"""

import traceback
import sys
import random
import discord
from random import randint
from PIL import Image, ImageDraw, ImageColor
import tempfile
import numpy as np
import pickle

#colors=["black", "violet", "indigo", "blue", "green", "yellow", "orange", "red", "pink", "cyan"]

defended=['⚔️','🛡️', '☣️', '🤨', '🕸️']

colors=["black"]

class LSysParser():
    
    def __init__(self, params = None) -> None:
        if params is None:
            self.params = {}
            self.params["rule"] = "R45 L/0.70710678118654752440084436210485 R-45 R-45 L/0.70710678118654752440084436210485 R45"
            self.params["iterations"] = "1"
            self.params["initial_shape"] = "hline4"
            self.params["width"] = "2000"
            self.params["height"] = "2000"
            self.params["start_color"] = "white"
            self.params["end_color"] = "white"
            self.params["background_color"] = "black"
        else:
            self.params = params
        self.file = None 
        self.color_counter = 0
        self.draw = None
        self.segment_quota = 0.0
        self.steps_to_draw = 0.0
        self.steps_drawn = 0.0
        self.step_value = 2
        self.memoized_cos = {}
        self.memoized_sin = {}
    
    def handle_request(self, msg):
        print(msg)
    
    def draw_l(self, img: Image, x1,y1,x2,y2, limit):
        L_position = (x1, y1)
        L_vector = (x2-x1, y2-y1)
        if self.segment_quota <= 0:
            return  
        elif limit == 0:
            self.segment_quota -= 1
            self.steps_drawn += self.step_value
            if self.steps_drawn > self.steps_to_draw:
                self.step_value *= -1
            startcolor = ImageColor.getrgb(self.params["start_color"])
            if len(startcolor) == 3:
                startcolor = (startcolor[0], startcolor[1], startcolor[2], 255)
            endcolor = ImageColor.getrgb(self.params["end_color"])
            if len(endcolor) == 3:
                endcolor = (endcolor[0], endcolor[1], endcolor[2], 255)
            scale = np.abs((self.steps_drawn/self.steps_to_draw))
            newcolor = (max(0, min(255, int(startcolor[0] + (endcolor[0]-startcolor[0])*scale))), max(0, min(255, int(startcolor[1] + (endcolor[1]-startcolor[1])*scale))), max(0, min(255, int(startcolor[2] + (endcolor[2]-startcolor[2])*scale))), max(0, min(255, int(startcolor[3] + (endcolor[3]-startcolor[3])*scale))))
            #print(f"color [{newcolor}]")
            self.draw.line([(x1,y1),(x2, y2)], fill=f"rgba{newcolor}", width=2)
            self.color_counter = ((self.color_counter + 1) % len(colors))
            return
        else:
            commands = self.params["rule"].casefold().split(" ")
            for command in commands:
                match command[0:1]:
                    case 'l':
                        # draw a line segment
                        #print(f"Drawing {command[1:]}")
                        divisor = float(command[2:])
                        #print(f"calling l_draw({L_position[0]}, {L_position[1]}, {L_position[0]+(L_vector[0])/divisor},{L_position[1]+(L_vector[1])/divisor}, {limit-1})")
                        self.draw_l(img, L_position[0], L_position[1], L_position[0]+(L_vector[0])/divisor,L_position[1]+(L_vector[1])/divisor, limit-1)
                        if self.segment_quota <= 0:
                            break
                        L_position = (L_position[0]+(L_vector[0])/divisor,L_position[1]+(L_vector[1])/divisor)
                    case 'r':
                        #print(f"Rotating {command[1:]} degrees.")
                        if command not in self.memoized_cos:    
                            theta = 2*np.pi*float(command[1:])/360.0
                            self.memoized_cos[command] = np.cos(theta)
                            self.memoized_sin[command] = np.sin(theta)
                        
                        costheta = self.memoized_cos[command]
                        sintheta = self.memoized_sin[command]
                        old_vector = L_vector
                        L_vector = (old_vector[0]*costheta - old_vector[1]*sintheta, old_vector[0]*sintheta + old_vector[1]*costheta)
    
    def create_image(self) -> str:
        """Create a new image with the configured parameters.

        Returns:
            str: filename of generated image.
        """
        # check how big this is going to be
        iterations = int(self.params["iterations"])
        complexity = self.params["rule"].casefold().count("l/")
        segments = np.power(complexity, iterations)
        
        print(f"Rule is {self.params['rule']}.  Complexity is {complexity}.  To draw {iterations}, we need {segments} segments.")
        
        
        self.segment_quota = float(min(segments, 1000000))
        self.steps_to_draw = float(segments)
        self.steps_drawn = 0.0
        self.step_value = 2
        
        image = Image.new(mode="RGBA", size=(int(self.params["width"]),int(self.params["height"])), color=ImageColor.getrgb(self.params["background_color"]))
        self.draw = ImageDraw.Draw(image, mode="RGBA")

        # Generate L-System
        # we need a rule of this form:
        # L/3 R-45 L/3 R90 L/3
        try:
            match self.params["initial_shape"].casefold():
                case "hline4":
                    self.draw_l(image, image.width/2-image.width/8, image.height/2, image.width/2+image.width/8, image.height/2, iterations)
                case "hline3":
                    self.draw_l(image, image.width/3, image.height/2, 2*image.width/3, image.height/2, iterations)
                case "hline2":
                    self.draw_l(image, image.width/4, image.height/2, 3*image.width/4, image.height/2, iterations)
                case "hline":
                    self.draw_l(image, image.width/6, image.height/2, 5*image.width/6, image.height/2, iterations)
                case "low+wide":
                    self.draw_l(image, 0, 4*image.height/5, image.width, 4*image.height/5, iterations)
                case "vline":
                    self.draw_l(image, image.width/2, 0, image.width/2, image.height, iterations)
                case "vline2":
                    self.draw_l(image, image.width/2, image.height/2-image.height/3, image.width/2, image.height/2+image.height/3, iterations)
                case "vline3":
                    self.draw_l(image, image.width/2, image.height/2-image.height/4, image.width/2, image.height/2+image.height/4, iterations)
                case "vline4":
                    self.draw_l(image, image.width/2, image.height/2-image.height/5, image.width/2, image.height/2+image.height/5, iterations)
                case "vline5":
                    self.draw_l(image, image.width/2, image.height/2-image.height/6, image.width/2, image.height/2+image.height/6, iterations)
                case "triangle":
                    top = (image.width/2, image.height/6)
                    bottom_left = (image.width/2-image.width/6, image.height/6 + np.power(3, .3333333)*image.width/6) 
                    bottom_right = (image.width/2+image.width/6, image.height/6 + np.power(3, .3333333)*image.width/6)
                    self.steps_to_draw *= 3
                    self.segment_quota *= 3
                    self.draw_l(image,  top[0], top[1], bottom_right[0], bottom_right[1], iterations)
                    self.draw_l(image,  bottom_right[0], bottom_right[1],  bottom_left[0], bottom_left[1], iterations)
                    self.draw_l(image,  bottom_left[0], bottom_left[1],  top[0], top[1], iterations)
                    
                case "2":
                    self.steps_to_draw *= 2
                    self.segment_quota *= 2
                    self.draw_l(image, image.width/6, image.height/2, 5*image.width/6, image.height/2, iterations)
                    self.draw_l(image, 5*image.width/6, image.height/2, image.width/6, image.height/2, iterations)
                
        except Exception as e:
            print(f"Exception while drawing: {e}")
            traceback.print_exception(*sys.exc_info())

        # Save file
        image.save("myimage.png", format="png")
        return "myimage.png"
        

class LSysBot(discord.Client):
    """Bot for finding fun gifs."""

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        
        try:
            with open("my_systems", mode='rb') as catalog:
                self.saved_systems = pickle.load(file=catalog)
        except Exception as e:
            print(f"Couldn't load catalog: {e}")
            self.saved_systems = {}
            
        try:
            with open("my_params", mode='rb') as params:
                saved_params = pickle.load(file=params)
                self.parser = LSysParser(params=saved_params)
        except Exception as e:
            print(f"Couldn't load params: {e}")
            self.parser = LSysParser()


    async def on_ready(self):
        """Handler for connecting to Discord"""
        print('Ready to roll.')
        for server in client.guilds:
            channel = discord.utils.get(server.channels, name='secret-bot-stuff')
            if channel:
                try:
                    pass
                    #await channel.send("Ready for input!")
                except Exception as inst:
                    print(type(inst))
                    print(inst)
                    print("Could not send hello in {0.name} on {0.guild}".format(channel))


    async def on_message(self, message, parse_text=False):
        print('message: {0.content}'.format(message))
        """Handler for messages"""
        
        commands = message.content.casefold().split(" ")
        if commands[0] == "!lsys":
            if commands[1] == "draw":
                await message.add_reaction('🕙')
                self.parser.handle_request(message.content.casefold())
                filename = self.parser.create_image()
                await message.channel.send(file=discord.File(filename))
            elif commands[1] == "sizes":
                await message.channel.send("Available sizes are bandcamp-min, bandcamp, 4k, uhd, qsxga, wqhd, wuxga, fhd, 1080p, svga, vga.  The default is 'bandcamp', 2000x2000 pixels.")
            elif commands[1] == "set":
                args = " ".join(commands[2:]).split("=")
                if len(args) == 2:
                    match args[0]:
                        case "iterations":
                            if int(args[1]) > 9:
                                await message.add_reaction(random.choice(defended))
                            elif int(args[1]) < 0:
                                await message.add_reaction(random.choice(defended))
                            else:
                                self.parser.params[args[0]] = args[1]
                                await message.channel.send(f"Okay, {args[1]} iterations it is!")
                            
                        case "rule":
                            self.parser.params["rule"] = args[1]
                            self.parser.params[args[0]] = args[1]

                        case "size":
                            match args[1].casefold():
                                case "bandcamp-min":
                                    self.parser.params["width"] = "1400"
                                    self.parser.params["height"] = "1400"
                                case "bandcamp":
                                    self.parser.params["width"] = "2000"
                                    self.parser.params["height"] = "2000"
                                case "8k":
                                    self.parser.params["width"] = "7680"
                                    self.parser.params["height"] = "4320"
                                case "4k":
                                    self.parser.params["width"] = "3840"
                                    self.parser.params["height"] = "2160"
                                case "uhd":
                                    self.parser.params["width"] = "3440"
                                    self.parser.params["height"] = "1440"
                                case "wqhd":
                                    self.parser.params["width"] = "2560"
                                    self.parser.params["height"] = "1440"
                                case "wuxga":
                                    self.parser.params["width"] = "1920"
                                    self.parser.params["height"] = "1200"
                                case "fhd":
                                    self.parser.params["width"] = "1920"
                                    self.parser.params["height"] = "1080"
                                case "1080p":
                                    self.parser.params["width"] = "1920"
                                    self.parser.params["height"] = "1080"
                                case "svga":
                                    self.parser.params["width"] = "800"
                                    self.parser.params["height"] = "600"
                                case "vga":
                                    self.parser.params["width"] = "640"
                                    self.parser.params["height"] = "480"
                                case "qsxga":
                                    self.parser.params["width"] = "2560"
                                    self.parser.params["height"] = "2000"
                                case _:
                                    await message.add_reaction('🤨')
                                    
                        case "color":
                            if ':' in args[1].casefold():
                                #gradient
                                colors = args[1].split(":")
                                color = ImageColor.getrgb(colors[0])
                                self.parser.params["start_color"] = colors[0]
                                color = ImageColor.getrgb(colors[1])
                                self.parser.params["end_color"] = colors[1]
                            else:
                                try:
                                    color = ImageColor.getrgb(args[1])
                                    self.parser.params["start_color"] = args[1]
                                    self.parser.params["end_color"] = args[1]
                                except ValueError as e:
                                    await message.channel.send(f"Oops!  I couldn't understand this color: {e}")
                        case _:
                            self.parser.params[args[0]] = args[1]
                    try:
                        with open("my_params", 'wb') as params:
                            pickle.dump(self.parser.params, params)
                    except Exception as e:
                        print(f"Couldn't save params! {e}")

            elif commands[1] == "params":
                await message.channel.send(f"Rule: {self.parser.params['rule'].upper()}\n{self.parser.params}")
                
            elif commands[1] == "save":
                self.saved_systems[commands[2]] = self.parser.params
                with open("my_systems", 'wb') as catalog:
                    pickle.dump(self.saved_systems, catalog)
                    
            elif commands[1] == "load":
                if commands[2] in self.saved_systems:
                    self.parser.params = self.saved_systems[commands[2]]
                    
                    try:
                        with open("my_params", 'wb') as params:
                            pickle.dump(self.parser.params, params)
                    except Exception as e:
                        print(f"Couldn't save params! {e}")
                        
            elif commands[1] == "describe":
                await message.channel.send(f"{commands[2]} is {self.saved_systems[commands[2]]}")
                
            elif commands[1] == "catalog":
                available = ",".join(self.saved_systems.keys())
                await message.channel.send(f"Available plots: {available}")
                


if __name__ == '__main__':
    client = LSysBot(intents=discord.Intents.all() )
    client.run("MTA2NTMzNzQ0MjM0Njk5NTczMg.GnFyc2.skdSRQyRBbCKnZVz5QyUbkgHs7gd4JsKXGs5Jg")