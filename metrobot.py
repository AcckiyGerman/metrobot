#! python3
''' METRO 2033 BOT'''
print('hello!')
import pyautogui
import time, os, logging, sys, random, copy


# Coordinates of the main game frame.
# Will be ajusted by  function getMainScreen()
# Main Screen width and height is x:760, y:650
WINDOW_X = 0
WINDOW_Y = 0

# Coordinates for different game menu and objects on the screen
# put here center coordinates of object, so bot can click on object
interface = { 
	# game objects:
	'star' : 'img/star.png',
	'shaded_star' : 'img/shaded_star.png',
	'person' : (50, 50),
	'mission1' : (50, 200),
	'chief_tent' : (150, 300),
		'chief_task1' : (560, 230),
		'chief_task2' : (560, 320),
		'chief_task3' : (560, 410),
	'arena' : (325, 250),
	'tent' : (500, 300),
	'trader' : (650, 350),
	# windows headers
	'new_task' : 'new_task',
	'fight_is_over' : 'img/fight_is_over.png',
	'anomalia' : 'img/anomalia.png',
	'task_done' : 'img/mission_done.png',
	'new_level' : 'img/new_level.png',
	# different signs and elements of game
	'arena_need_to_wait' : 'img/arena_need_to_wait.png',
	'energy' : 'img/energy.png',
	'left_bottom_corner' : (10, 640),	# empty place in game window, to click and close
										# some VK notifications
	# buttons:
	'skip_fight' : (380, 25), #'img/skip_fight.png',
	'skip_task_process' : 'img/skip_task_process.png',
	'back_button' : 'img/back_button.png',
	'attack' : (250, 510),
	'change_enemy' : (260, 380),
	'tell' : 'img/tell.png',
	'close_button' : 'img/close_button.png',
	'repeat' : 'img/repeat.png',
}

# pause after every mouse click. if you set this value too low,
# bot will act too quickly for the game programm
pause = 3

#logging.disable(logging.DEBUG) # uncomment to block debug log messages
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', \
					datefmt='%H:%M:%S')

def setGlobalXY(star):
	'''
	'star' image is always on right top corner of game screen, so we
	get tuple of 'star' image coordinates (x, y, width, height)
	and set game window coordinates.
	 '''
	global WINDOW_X
	global WINDOW_Y
	# the game screen is always 760*650 (width, height)
	WINDOW_X = star[0] + star[2] - 760  # left + width of star image - game screen width
	WINDOW_Y = star[1]  # top of star image is also top of the game screen
	logging.info('Game screen coordinates updated: %d: %d' % (WINDOW_X, WINDOW_Y))


def click(interfaceObject, pause=pause):
	link = interface[interfaceObject]
	if type(link) == tuple:  # coordinates
		pos = (link[0] + WINDOW_X, link[1] + WINDOW_Y)
	elif type(link) == str:  # here must be filename of element picture
		pos = pyautogui.locateCenterOnScreen(link)
		if pos == None:
			logging.info("clicking on %s is aborted - can't find image" % interfaceObject)
			return None
	logging.info('clicking on "%s", coords %s' % (interfaceObject, str(pos)))
	pyautogui.click(pos, pause=pause)
	return True

def locateOnScreen(interfaceObject):
	logging.info('trying to locate "%s" on screen' % interfaceObject)
	if type( interface[interfaceObject] ) == tuple:
		logging.info('object is not an image, check your code!')
		raise Exception('given object to find on screen is not an image!')
	
	found = pyautogui.locateOnScreen( interface[interfaceObject] )
	if not found:
		logging.info( "can't locate '%s' on screen :(" % interfaceObject )
	return found

def getMainScreen():
	'''Trying to find game main screen and get to root game windows
		from where all actions is possible:	'''
	logging.info('Trying to recognize game screen...')
	star = locateOnScreen( 'star' )
	if star:
		logging.info('found "star" icon - we are on the root screen')
		setGlobalXY(star)
		return
	else:
		shaded_star = locateOnScreen( 'shaded_star' )
		if shaded_star:
			logging.info('found shaded star, main screen is shaded... some vk notify?')
			setGlobalXY( shaded_star )
			click( 'shaded_star' )
			# we need to click some empty place, otherwise, there will appear popup
			# on 'star' and bot will not recognize 'star' image
			click( 'left_bottom_corner' )
			if locateOnScreen( 'star' ):
				logging.info('found "star" icon - we are on the root screen')
				return

	# if screen is shaded becouse of ingame window - this part will handle it
	for element in ['close_button', 'back_button']:
		if locateOnScreen( element ):
			click( element )
			# sometimes there is two ingame windows, because of some achivements
			# so let's check twice
			getMainScreen()
	
	# if globalXY was set, maybe there is fight going?
	if WINDOW_X != 0:
		click('skip_fight')
		click('close_button')
		if locateOnScreen( 'star' ): return

	logging.info('Could not find any game images :( \n asking user to help me')
	ask_user = pyautogui.confirm('''
		Бот не может найти игру.
	 	Запустите пожалуйста окно с игрой.
	 	Попробовать еще раз?''')
	if ask_user == 'OK':
		getMainScreen()  # running recursively
	else:
		raise Exception('Could not find game on screen. User aborted process.')

def checkNewLvl():
	if locateOnScreen( 'new_level' ):
		logging.info( 'NEW LELEL REACHED :)' )
		click( 'tell' )  # to uncheck 'tell in vk' box
		click( 'close_button' )
	
def chiefTask(task_number):
	'''do n-th task in station chief tent
	there can be 3 tasks, so  'task_number' can be 1,2,3
	'''
	logging.info('TASK FROM STATION DIRECTOR')
	getMainScreen()
	click('chief_tent')
	if not locateOnScreen( 'energy' ):
		logging.info( 'not enouph energy in game to do tasks :(\n returning...')
		# pyautogui.alert('Not enouph energy to do tasks,\nwait till tommorow... :( ')
		# raise Exception('Not enouph energy in game to make tasks :( ')
		return
	click('chief_task' + str(task_number))
	for _ in range(13):
		logging.info('waiting 15 sec...')
		time.sleep(15)
		click( 'skip_fight' )
		if locateOnScreen( 'fight_is_over' ):
			logging.info('fight is over.')
			click('close_button')
			break
	checkNewLvl()
	
def arenaFight():
	'''bot fights on arena'''
	logging.info('ARENA FIGHT')
	getMainScreen()
	click('arena')
	time.sleep(pause)
	if locateOnScreen( 'arena_need_to_wait' ):
		logging.info( 'arena timer is still ticking, return to avoid wasting money...' )
		click('close_button')
		return
	click('attack')
	click('skip_fight')
	click('close_button')
	checkNewLvl()


''' HERE IS MACRO-FUNCTIONS TO CONTROLE WHOLE GAME PROCESS '''
def main():
	'''runs the programm. The metro 2033 game must be visible on the screen.'''
	logging.info('Program started. Ctrl-C to abort.')
	getMainScreen()
	while True:
		for i in [1,2,3]:
			chiefTask(i)
		arenaFight()


if __name__ == "__main__":
	main()
	