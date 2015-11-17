#!/usr/bin/python

#-------------------------------------------
#	PYGAME EXAMPLE
#-------------------------------------------

import sys, pygame, json, math, random
#PARTICLE EMITTER
#-this is the object that emits the particles
#-and keeps tracks of them-------------------
#--------------------------------------------
class ParticleEmitter:
	#init function
	def __init__(self, pos, plimit, img, scalex):
		self.img = img;											#img for particle
		self.pos = (self.x, self.y) = pos;						#emitter position
		self.plimit = plimit;									#limit how many particles this emitter can spawn
		self.plist = []
		self.threshold = 10		 								#create list for particles
		self.lastEmitted = pygame.time.get_ticks()
		self.spawn = pygame.time.get_ticks()/1000
		self.scalex = scalex;
	#update function
	def update(self, pos, screen):
		if(self.plimit > len(self.plist) and (self.lastEmitted + self.threshold < pygame.time.get_ticks())):	#create more particles if we are not topping the limit
			if(pos == False):
				pos = self.pos;
			particle = Particle(pos, self.img, self.scalex);					#new instance
			self.plist.append(particle);
			self.lastEmitted = pygame.time.get_ticks()
		self.updateParticles(screen)
		if(self.spawn + 3 < pygame.time.get_ticks()/1000):
			return True;
		else:
			return False;
	#update particles
	def updateParticles(self, screen):
		for particle in self.plist:
			alive = particle.update(screen);					#update function returns false if particle should die
			if(alive == False):
				self.plist.remove(particle);
	#distroy all particles
	def cleanAll(self):
		for particle in self.plist:
			self.plist.remove(particle)
#PARTICLE
#--one individual particle
#-------------------------------------------
class Particle():
	#particle init
	def __init__(self, pos, img, scalex):
		self.pos = (self.x, self.y) = pos;
		self.lifetime = random.randrange(15,20);					#each particle have random lifetime
		self.spawntime = pygame.time.get_ticks()/1000;			#remember when it spawned
		self.scalex = self.scaley =  random.uniform(0.15*scalex, 0.25*scalex);	#create random scale for each particle
		self.dx = random.uniform(-2,2);							#and random directional movement vectors
		self.dy = random.uniform(-2,2);
		self.transparency = 255;								#init transparency to 255

		self.image = pygame.image.load(img).convert();
		self.image = pygame.transform.scale(self.image, (int(self.image.get_width()*self.scalex), int(self.image.get_height()*self.scaley)));
		self.image.set_colorkey((255,0,255))

	def update(self, screen):
		self.x += self.dx;														#move particles
		self.y += self.dy;
		#self.image = pygame.transform.scale(self.image, (int(self.image.get_width()*1.04), int(self.image.get_height()*1.04)));
		self.transparency -= 255/self.lifetime									#update transparency
		self.image.set_alpha(self.transparency)									#draw image
		screen.blit(self.image, (self.x, self.y))
		if(pygame.time.get_ticks()/1000 > (self.spawntime + self.lifetime)):	#check if its time to die
			return False;
		return True;

#ACTOR CLASS DEFIN
#-includes some spaceship specific stuff just to make code smaller, not pretty
#-------------------------------------------
class Actor:

	#init the class
	def __init__(self, vector, area, img, font, index):
		(self.x, self.y) = vector
		self.speed = 3
		self.spriteBatch = Sprite("img/"+img+".png", "img/"+img+".json")
		self.proj_list = []
		self.lastShot = 0;
		self.threshold = 0.3
		#create dx and dy in case user wants compicated movement
		(self.dx, self.dy) = (0,0)
		self.oldRotation = 0;
		self.spriteIndex = index;
		self.text = font.render("", 1, (255,255,255));
		self.health = 10;
	#update function dah
	def update(self, screen, font):

		#draw player in pos
		self.spriteBatch.drawSprite(screen, int(self.spriteIndex) ,self.x,self.y, 0.3, 0.3, self.oldRotation);
		#update projectiles
		for projectile in self.proj_list:
			alive = projectile.update(screen) 		#update returns true if projectile is still alive
			if(alive == False): 					#if projectile is dead, destroy it
				self.proj_list.remove(projectile)
	#check collision of two actors
	def checkCollision(self, actor2, threshold):
		if(abs(self.x - actor2.x) < threshold and abs(self.y - actor2.y) < threshold):
			return True
		else:
			return False
	def updateRotation(self, screen, font):
		#calculate new rotation for object
		rotation = calc_rotation(self.x, self.y)+180;
		#if you are moving forward
		if(rotation == self.oldRotation):
			self.spriteIndex = 0;
			self.text = font.render("TURNING FORWARD", 1, (255,255,255));
		elif(rotation < 10 or rotation >350):
			self.text = font.render("TURNING", 1, (0,0,255))
		#if you are moving to left
		elif(rotation > self.oldRotation):
			self.spriteIndex = 1 + (rotation-self.oldRotation)/2;
			if(self.spriteIndex > 3):
				self.spriteIndex = 3;
			self.text = font.render("TURNING LEFT", 1, (255,0,0));
		#and if right
		else:
			self.spriteIndex = 4 + (self.oldRotation - rotation)/2;
			if(self.spriteIndex > 6):
				self.spriteIndex = 6;
			self.text = font.render("TURNING RIGHT", 1, (0,255,0));

		screen.blit(self.text, (300,0))
		rot_text = font.render("rotation: " +str(round(rotation,3)), 1, (255,255,255))
		screen.blit(rot_text, (300, 20))
		#update old rotation
		self.oldRotation = rotation;

	#in case you can shoot with this actor
	def shoot(self, sx, sy):
		#if you can shoot again
		if(self.lastShot+self.threshold<(pygame.time.get_ticks()/1000)):
			speed = 5 							#speed for projectile
			dx = (sx - self.x);					#get the dx and dy for projectile
			dy = (sy - self.y);					#these are members of the directional vector
			mag = math.sqrt(dx*dx + dy*dy)		#get the magnitude (length) for dvec for normalization
			dx = dx/mag*speed					#normalize both members and multiply by speed
			dy = dy/mag*speed
			#create new projectile
			proj = Projectile((dx,dy),(self.x-30, self.y-30), "img/bullet.png")#first directional vector for projectile (look up)
																				#second param is position of the new projectile in world space, witch is actor pos.
																				#we bubblecum the actual position to be in center of the sprite
																				#third param is the image path
			self.proj_list.append(proj)						#add new projectile in list
			self.lastShot = pygame.time.get_ticks()/1000	#and update the lastShot
	#simple move for actor
	def move(self,screen,  x, y, bound):
		self.y -= y*self.speed;		#update x and y of actor by adding given x and y to them multiplied by movement speed
		self.x -= x*self.speed;
		#dont let it get out of the boundaries
		if(bound):
			if(self.x < 0):
				self.x = 0
			if(self.y < 0):
				self.y = 0
			if(self.x > screen.get_width()):
				self.x = screen.get_width();
			if(self.y > screen.get_height()):
				self.y = screen.get_height()
	#WIP
	def moveInSpace(self, x, y):
		self.dx += x/3 - 0.1;
		self.dy += y/3; - 0.1
		if(self.dx > 1):
			self.dx = 1
		if(self.dy > 1):
			self.dy = 1
		#simple set position
	def set_position(self, x, y):
		self.x = x;						#this is in case you have to set new position for the actor
		self.y = y;

#SPRITE BATCH
#-works with multiple frames
#-problems with transform.rotate
#--------------------------------------------
class Sprite:
	#INIT
	def __init__(self, img_path, json_path):
		#create image object based on file and convert it to surface
		self.image = pygame.image.load(img_path).convert()
		#turn black to transparent pixels (create mask)
		self.image.set_colorkey((0,0,0))
		#if this sprite has json defin file
		if(json_path != 0):
			#load the json data from spritebatch defin file
			self.json_data = json.loads(open(json_path, "r", ).read())
			#loop threw all "frames" on file
			self.images = []
			for image in self.json_data["frames"]:
				self.images.append(image)
			#sort images! this is important because otherwise python will always load them in random order!
			self.images.sort()
			#set rotation variable (degrees)
		#else not
		else:
			json_data = json_path;
		self.rotation = 0;
	#sprite drawing function
	def drawSprite(self, screen, index, drawx, drawy, scalex, scaley, rotation):
		if(self.json_data != 0):
			#get the pos (x,y) and width and height of frame (w,h) for given frame from json
			x = self.json_data["frames"][self.images[index]]["frame"]["x"]
			y = self.json_data["frames"][self.images[index]]["frame"]["y"]
			w = self.json_data["frames"][self.images[index]]["frame"]["w"]
			h = self.json_data["frames"][self.images[index]]["frame"]["h"]
			#make 'cut' of the original picture and create sub surf for it
			out = self.image.subsurface(x, y, w, h)
		else:
			out = self.image;
		#rotate this new sprite to face mouse position
		out = pygame.transform.rotate(out, rotation)
		out = pygame.transform.scale(out,  (int(out.get_width()*scalex), int(out.get_height()*scaley)))

		#draw sprite to screen
		screen.blit(out, (drawx-(out.get_width()/2),drawy-(out.get_height()/2)))

#PROJECTILE CLASS DEFIN
#---------------------------------------------------------
class Projectile:
	#projectile init
	#object itself, directional vector (vec2), position vector (vec2), img path
	def __init__(self, dvec, pvec, img):
		self.pos =(self.x, self.y) = pvec;							#set given x and y to new pos
		self. dvec = (self.dx, self.dy) = dvec;							#set directional vector to dx and dy
		self.spawntime = pygame.time.get_ticks();			#get the time of spawn
		self.img = pygame.image.load(img).convert_alpha();	#create new surface (image) for projectile
		self.speed = 4
		#after this we update the rotation of the image
		#the second parameter transforms the direction vector to degrees for transform.rotate
		#we add +90 degrees because the original image is facing left
		self.img = pygame.transform.rotate(self.img, math.atan2(self.dx,self.dy)*180/math.pi+90);
		self.emitter = ParticleEmitter((self.x, self.y), 80,"img/smoke2.png", 1)
		#globalEmitters.append(self.emitter)

	#update function
	def update(self, screen):
		self.x += self.dx*self.speed;									#udpate position
		self.y += self.dy*self.speed;
		self.draw(screen)									#call draw

		self.emitter.update((self.x-self.dvec[0]*8,self.y-self.dvec[1]*8), screen)


		if(self.spawntime+2000 < pygame.time.get_ticks())/1000:	#check if the projectile have lived long enough
																#and return false if it isnt supposed to live anymore
			self.emitter.cleanAll();
			return False
		else:
			return True

	#drawing function
	def draw(self, screen):
		screen.blit(self.img, (self.x, self.y))

#----------------------------------------------------------------------
#calculate the rotation in degrees between pos vec2 and and mouse pos vec2
def calc_rotation(x, y):
	#get the mouse position
	mpos = pygame.mouse.get_pos()
	#mouse x - player x
	dx = mpos[0] - x

	#get dy the same way
	dy = mpos[1] - y
	#the actual math
	return math.atan2(dx,dy)*180/math.pi
#---------------------------------------------------------
def updateAsteroids(asteroids, screen, font, ball):
	#update asteroids
	if(round(pygame.time.get_ticks(),0)%40 == 0):
		side = random.randrange(1,5);
		if(side == 1):
			sx = -20
			sy = random.randrange(0,height)
		elif side == 2:
			sx = width + 20
			sy = random.randrange(0,height)
		elif side == 3:
			sx = random.randrange(0,width)
			sy = height+20
		elif side == 4:
			sx = random.randrange(0,width)
			sy = -20
		asteroid = Actor((sx, sy), (width, height), "asteroid", font, random.randrange(0,2));
		asteroids.append(asteroid)
	for asteroid in asteroids:
		asteroid.update(screen, font);
		asteroid.oldRotation += 1
		speed = 0.5+pygame.time.get_ticks()/100000;
		dx = (asteroid.x - ball.x);					#get the dx and dy for projectile
		dy = (asteroid.y - ball.y);					#these are members of the directional vector
		mag = math.sqrt(dx*dx + dy*dy)				#get the magnitude (length) for dvec for normalization
		dx = dx/mag*speed							#normalize both members and multiply by speed
		dy = dy/mag*speed
		asteroid.move(screen, dx, dy, False);
		hits = asteroid.checkCollision(ball, 50);
		if(asteroid in asteroids and hits):
			asteroids.remove(asteroid)
			ball.health -= 1;
		for bullet in ball.proj_list:
			hits = asteroid.checkCollision(bullet, 50);
			if(bullet in ball.proj_list and hits):
				emitter = ParticleEmitter((asteroid.x, asteroid.y), 10 , "img/smoke2.png", 1.5)
				globalEmitters.append(emitter)
				ball.proj_list.remove(bullet)
				if(asteroid in asteroids):
					asteroids.remove(asteroid)
#----------------------------------------------------------
def updatePlayer(ball, screen, mpos, keys, font):
	#if mouse is pressed, 0 is left, 1 middle and 2 right key
	if pygame.mouse.get_pressed()[0]:
			ball.shoot(mpos[0], mpos[1]);
	#udpate rotation
	ball.updateRotation(screen, font)
	#doe something with
	if keys[pygame.K_w]: #check if array has item K_w
		ball.move(screen, 0, 1, True)
	if keys[pygame.K_s]:
		ball.move(screen, 0, -1, True)
	if keys[pygame.K_a]:
		ball.move(screen, 1, 0, True)
	if keys[pygame.K_d]:
		ball.move(screen, -1, 0, True)
	#update the ball, or "player"
	ball.update(screen, font);

#---------------------------------------------------------
#GLOBAL VARIABLES
#set screen width and height
size = width, height = 800, 640
globalEmitters = [];
#MAIN LOOP
try:
	def main():
		#init pygame core
		pygame.init()
		#create background color
		bgcolor = 50,50,50
		#set pygame display
		screen = pygame.display.set_mode(size)
		#create font to be used in screen drawing
		font = pygame.font.Font(None, 30);
		#create instance of "actor"
		ball = Actor((400,320), (width, height), "spaceship", font, 0)
		asteroids = [];
		while True:
			#clear the screen with black
			screen.fill(bgcolor)
			#get all keys in array for this loop iteration
			keys = pygame.key.get_pressed();
			#get mouse position for this loop
			mpos = pygame.mouse.get_pos();
			#
			for event in pygame.event.get():
				if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
						return
			updatePlayer(ball, screen, mpos, keys, font);
			updateAsteroids(asteroids, screen, font, ball);
			for emitter in globalEmitters:
				if(emitter.update(False, screen)):
					globalEmitters.remove(emitter)
			#write stuff on screen
			text = font.render("x:"+str(mpos[0])+"y:"+str(mpos[1]), 1, (255,255,255))		#define text object
			screen.blit(text, (0,0));														#draw to screen
			text = font.render("time:"+str(pygame.time.get_ticks()/1000),1,(255,255,255));	#redefine text object
			screen.blit(text, (0,20));														#draw redefined text in new position

			text = font.render("health:"+str(ball.health),1,(255,150,150));					#redefine text object
			screen.blit(text, (550,0));
			#draw buffer to screen
			pygame.display.flip()
			clock = pygame.time.Clock()
			clock.tick_busy_loop(60);


	main();
	print("Program ended")
	#pygame.quit();
except SystemExit:
    pygame.quit();
print("Problems shutting down");
sys.exit(1)
