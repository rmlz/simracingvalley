# -*- coding: utf-8 -*-
"""
Created on Fri Oct  4 23:06:15 2019

@author: Ramon Barros
@github: https://github.com/rmlz

I'm a Python student that have been trying to create useful scripts for the Simracing Community. 
Also I may thanks all the people that helped me to develop the Simracing Valley Community:

Alisson Zanoni
Aparicio Felix Neto
Aurea Barros
Carlos Eduardo Pinto
Celso Pedri
Cesar Louro
Fabio Krek
Fernando Bueno
Glenio Lobo
Gracas Barros
Gustavo Pinto
Hernani Klehm
Iovan Lima
Maikon Sulivan
Matheus Manarim
Nicolas Sanchez Ernest
Pedro Phelipe Porto
Rodrigo Lepri
Rodrigo Vicente
Tadeu Costa
Tayane Campos

This script is made to run an Automobilista Server
based on the time scheduled in a database;

PUT THIS FILE INSIDE THE DEDICATED_SERVER.EXE FOLDER!

'Curitiba Full / 3.71 KM'
'Curitiba Outer Circuit / 2.60 KM'
"""
#For Rating
from collections import defaultdict, Counter
from itertools import groupby
from pprint import pprint
from trueskill import Rating, rate, quality

#For parsing
import os 
import subprocess
import time
from datetime import date, datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
from bs4 import BeautifulSoup as BS
import re
from operator import itemgetter
from bson.objectid import ObjectId

client = MongoClient("mongodb+srv://public:publicpassword@brazilavrank-2ccxo.mongodb.net/test") #EDIT THIS
db = client.ValleyAlliance
dbusers = client.users
srv_opt = db.ServerOptions
cursor = db.RaceResult.find()
rating_cursor = db.Drivers.find()
path_to_watch = 'C:\\Users\\YOURS-PC\\Documents\\Automobilista\\userdata\\LOG\\Results' #EDIT THIS


config_file_path = 'C:\\Users\\YOURS-PC\\Documents\\Automobilista\\userdata\\DedicatedServer' #EDIT THIS


before = dict([(f, None) for f in os.listdir(path_to_watch)])
#before = {}


def serverconfig(race):
    
    options = srv_opt.find_one()
    carlist = options['cars']
    car = race['cars']
    
    for car_opt in carlist:
        if car[0] == car_opt[0]:
            car = car_opt[1]
    #1439
    startpractime = int(race['starttime'][0])*60 + int(race['starttime'][1]) #ingame hour
    realtimestart = int(race['time'].split(':')[0])*60 + int(race['time'].split(':')[1]) #realtime
    startqualytime = startpractime + int(race['session'][0]) #ingame hour
    realqualytime = realtimestart + int(race['session'][0]) #realtime
    startracetime = startqualytime + int(race['session'][1]) #ingame hour
    realracetime = realqualytime + int(race['session'][1])#realtime
    if startpractime > 1439:
        startpractime = startpractime - 1439
    if startqualytime > 1439:
        startqualytime = startqualytime - 1439
    if startracetime > 1439:
        startracetime = startracetime - 1439
    startpractime = str(startpractime)
    startqualytime = str(startqualytime)
    starttime = '{:02d}:{:02d}'.format(*divmod(realracetime,60))
    startracetime = str(startracetime)
    
    
    allowed_cars = race['cars'][2] 
    
    multiplayer_conf = '''//[[gMa1.002f (c)2007    ]] [[            ]]
[MULTIPLAYER]
[ Multiplayer General Options ]
Network Connection Type="3" // 0=56k, 1=256k/64k, 2=1MB/256k, 3=2MB/512k, 4=5MB/1MB, 5=10MB/2MB, 6=LAN, 7=custom
Upstream KBPS="'''+race['upstream']+'''"512" // Rated uploading speed of connection, in kilobits per second
Downstream KBPS="'''+race['downstream']+'''" // Rated downloading speed of connection, in kilobits per second
Multiplayer Enum Type="1" // where to look for servers: 0=LAN, 1=Internet
Net Flush Threshold="472" // threshold for auto-accumulation flush while building data chunks (default is standard MTU of 536, minus 64 bytes room for layer headers: 472)
Net Join Timeout="180.00000" // How long to wait (without a response) before a game join will be considered a failure
Gamelist AutoRefresh (LAN)="1" // if true, the gamelist will auto refresh on page activation if LAN refresh type is selected
Query Port Start="34597" // range is 1025 - 65535
Port Start="34697" // range is 1025 - 65535
Authenticator Port="8766" // range is 1025 - 65535
Master Server Updater Port="27016" // range is 1025 - 65535
Game List Sort Method="1" // 0=Sort by name, 1=Sort by ping, 2=Sort by circuit, 3=Sort by players
Allow Chat In Car="1" // whether to allow incoming chats to appear while in car
Autoscroll Chat="1" // whether to auto-scroll chatbox as new chats arrive
Colorcode Chat="0" // whether to color-code chats in the chatbox
Display Laggy Labels="0" // whether to display vehicle labels on vehicles with laggy connections
Delay Vehicle Graphics="1" // if true, delay loading vehicle graphics when clients join in order to reduce the pause
Temporary Vehicle Graphics="10" // number of vehicle graphical instances to load at init time for temporary use when clients join (if number is exceeded, quality will deteriorate)
Extrapolation Time="2.00000" // Extrapolation time (in seconds) before car disappears
Position Spring="16.00000" // Position spring at 1000ms latency (lower latencies have stronger springs, higher latencies have same springs)
Orientation Spring="28.00000" // Orientation spring at 1000ms latency
Damping Multiplier="1.00000" // 1.0 = critical damping, higher values are overdamped, lower values are underdamped and not recommended
Path Prediction="1.00000" // Influence of the AI path on remote vehicle prediction (0.0-1.0)
Remote Vehicle Collision="200.00000" // Maximum distance from current vehicle that we will run collision on remote vehicles to prevent them from appearing to go through walls
Concurrent Server Updates="1000" // servers in join list, should be less for modem users, more for broadband (game now automatically finds more if (3 * download_kbps) exceeds this number)
Request Autodownloads="0" // Set to 1 if you want to automatically download files from a server you are joining, if you do not already have them.
Leave/Join Messages="3" // 0=none 1=in-car 2=monitor 3=both
Alternate Matchmaker Address="match.reizastudios.com" // Address of the alternate ISI Matchmaking server
Matchmaker TCP Port="40001" // TCP port to use when communicating with the Matchmaking Server
Matchmaker UDP Port="40002" // UDP port to use when communicating with the Matchmaking Server
Default IP Address="127.0.0.1" // IP to show as default in the Add Game menu
Enable Voice Chat="0" // Set to 1 if you want to turn on voice chat
Buddy List Announce="1" // whether to allow other players to see what game you are in
Auto Join Chat Server="1" // Whether to auto join to lobby chat during start up
Spectator Mode="0" // Join games in spectator mode (rather than with a separate vehicle)
Show Seating="1" // Show vehicle seating and status (driver/passenger/spectator) when vehicle labels are on
Lobby Chat Nickname="" // Nickname to use in Lobby Chat, if this is blank player name will be used
Live Updates="1" // whether to download news and UI elements on game load. (28.8s turn this off)
Auto Exit="0" // whether to automatically exit after leaving auto-hosted/auto-joined games
RaceCast Auto Login="1" // whether to auto login to RaceCast on startup
Force Lan="0" // Whether the lobby should default to Lan servers
Seconds for Autoload="0.00000" // How many seconds will the game wait before jumping into the first server in the list. 0 means no autoload

[ Multiplayer Server Options ]
Default Game Name="['''+starttime+''']Simracingvalley.com" // Name of last multiplayer game we hosted
Collision Fade Thresh="0.70000" // Collision impacts are reduced to zero at this latency
Post Results="0" // whether servers will post race results on the Internet
Announce Allowed="0" // servers should pass the firewall test before being allowed to list on the matchmaker
Announce Host="1" // whether servers will attempt to register with the matchmaking service
Closed MP Qualify Sessions="0" // if true, the session will be closed during qualify, so as to not disturb the participants
Spectators When Closed="1" // whether spectators are allowed to join closed sessions
Driver Swap Setups="1" // whether vehicle setup is transferred during driver swaps (except steering lock and brake pressure) ... note that UI garage is now loaded for vehicle when you become a passenger
Nagle Algorithm="0" // whether server's system messages are delayed for better packing (lower bandwidth, but some clients see unacceptable delays)
Dedicated Target FPS Rate="250" // Target sampling rate for dedicated server (higher #s reduce latency slightly but increase CPU usage)
Loading Sleep Time="0" // Milliseconds that dedicated server sleeps between each instance while loading tracks and vehicles
Loading Priority="1" // Dedicated server's priority level when loading tracks and vehicles: 0=low, 1=normal, 2=high
Pause While Zero Players="0" // Whether to pause a dedicated server (and stay in practice session) if no human players are present
Report Mismatches="3" // server should report mismatches for: 0=physics/GDB/srs only, 1=physics/GDB/SRS/EXE, 2=physics/GDB/SRS/track geometry, 3=everything
Mismatch Response="1" // how the server responds to mismatches: 0=does nothing, 1=kicks the mismatched client at the beginning of the Race session, 2=kicks client immediately, 3=kicks client from Qualifying or Race
Allowed Traction Control="'''+race['help'][0]+'''" // max level 0-3
Allowed Antilock Brakes="'''+race['help'][1]+'''" // max level 0-2
Allowed Stability Control="'''+race['help'][2]+'''" // max level 0-2
Allowed Auto Shift="'''+race['help'][3]+'''" // max level 0-3
Allowed Auto Clutch="'''+race['help'][4]+'''" // max level 0-1
Allowed Invulnerability="'''+race['help'][5]+'''" // max level 0-1
Allowed Opposite Lock="'''+race['help'][6]+'''" // max level 0-1
Allowed Steering Help="'''+race['help'][7]+'''" // max level 0-3
Allowed Brake Help="'''+race['help'][8]+'''" // max level 0-2
Allowed Spin Recovery="'''+race['help'][9]+'''" // max level 0-1
Allowed Auto Pit="'''+race['help'][10]+'''" // max level 0-1
Allowed Auto Lift="'''+race['help'][11]+'''" // max level 0-1
Allowed Auto Blip="'''+race['help'][12]+'''" // max level 0-1
Allowed Driving Line="'''+race['help'][13]+'''" // max level 0-1
Forced Driving View="'''+race['carviews'][1]+'''" // 0=no restrictions on driving view, 1=cockpit/tv cockpit/nosecam only, 2=cockpit/nosecam only, 3=cockpit only
Must Be Stopped="0" // Whether drivers must come to a complete stop before exiting back to the monitor
Allow AI Toggle="0" // Whether users are allowed to toggle to AI control on the fly
Allow Spectators="1" // Whether to allow spectator clients to join the server.
Allow Passengers="1" // Whether to allow spectators to join a car as a co-driver/passenger.  If set to 1 and Allow Spectators is set to 0, spectators will be kicked from the game during the Race Session.
Allow Hotswaps="0" // 0=drivers can only change at pitstops using the pit menu, 1=Drivers can switch at anytime with the Driver Hotswap key
Allow Spectator Chat="1" // Whether to allow spectators to send chat messages
Allow Passenger Chat="1" // Whether to allow passengers to send chat messages
Max MP Players="20"
Max Data Client="128" // if desired, a per-client upload limit (in kbps) will be used if lower than the computed throttle rate
Unique Vehicle Check="0" // server setting, will check client vehicles to deny duplicates of the same vehicle
Minimum AI="0" // server will ensure this number of AI, but only at the beginning of practice/qual sessions
Maximum AI="0" // prevent more than this # of AI (there may be other limits)
Vote Percentage Add AI="50" // must EXCEED this percentage to pass vote for adding AI (set to 100 to disable)
Vote Percentage Next Session="60" // must EXCEED this percentage to pass vote to advance to next session (set to 100 to disable)
Vote Percentage Other="70" // must EXCEED this percentage to pass vote for race restart, event restart, or load next race (set to 100 to disable)
Vote Min Voters="2" // minimum voters required to call vote (except for adding AIs)
Vote Max Race Restarts="1" // maximum race restarts called by vote
SuperAdminPassword="baralho123" // Chat "/admin <password>" to become super-admin. Super-admins are secret and can change the regular admin password with "/apwd <new_password>" (which also removes all current regular admin control).
Admin Password="srv127" // Chat "/admin <password>" to become admin (make sure admin and super-admin passwords are different).  Exit or chat "/admin" to become non-admin.  One super-admin plus three regular admins are now allowed.
Admin Functionality="1" // 0 = non-admin's can NEVER call or vote, 1 = non-admin's can't call or vote if admin is present, 2 = non-admin's can call and vote, but admin's vote wins, 3 = if non-admin calls, all voting is normal, but any admin calls win instantly
Allow Any Event="1" // 0 = don't allow users to vote for specific tracks, 1 = allow users to vote for any track in server list, 2 = allow users to vote for any track, note that admins can do anything
Practice 1 Time="'''+race['session'][0]+'''" // 0 = use default from GDB, otherwise this is # of minutes for practice 1 (1-10 by 1, 15-90 by 5, 105-165 by 15)
Qualifying Time="'''+race['session'][1]+'''" // 0 = use default from GDB, otherwise this is # of minutes for qualifying (1-10 by 1, 15-90 by 5, 105-165 by 15)
Qualifying Laps="'''+race['session'][2]+'''" // 0 = use default from GDB, otherwise this is # of laps allowed in qualifying
Warmup Time="'''+race['session'][3]+'''" // 0 = use default from GDB, otherwise this is # of minutes for warmup (1-10 by 1, 15-90 by 5, 105-165 by 15)
Allow Hotlap Completion="16" // Allow hotlap completion before switching sessions (1=practice1 ... 16=qual, 32=warmup, 63=all)
Delay Between Sessions="30.00000" // Dedicated server delay before switching sessions automatically (after hotlaps are completed, if option is enabled), previously hardcoded to 45
Delay After Race="90.00000" // Dedicated server additional delay (added to "Delay Between Sessions" before loading next track
Server Session End Timeout="300" // Session is advanced automatically after N seconds after completion (non-dedicated server only)
Enable Autodownloads="0" // Whether to allow clients to autodownload files that they are missing.
Enable Voice Chat Server="0" // Whether to turn on the voice chat server.
Enable Voice Chat Echo="0" // Allow the voice chatters to hear themselves.
RC Rank Type="0" // Type of ranking used to allow people to join: 0=off, 1=overall, 2=series, 3=vehicle
RC Rank Minimum="0.00000" // Minimum normalized ranking (of given type) for people to join
RC Rank Maximum="1.00000" // Maximum normalized ranking (of given type) for people to join
Unthrottle Prefix="_" // Prefix of any clients to be unthrottled (use with caution!)
Unthrottle ID="-9999999" // Unique ID of client to be unthrottled (use with caution!)
Lessen Restrictions="1" // Allows careful users to test the limits
Join Password="'''+race['password']+'''" // Password for clients to join game
MOTD="Cadastre-se em www.simracingvalley.com " // Corridas todos os dias" // Message of the day
Anti Cutting Rules="1" // Activates or deactivates the anti-cutting rules
Cut Warnings="3" // Number of cut warnings before penalization
Disable Radar="1" // Activates or deactivates de radar rules in multiplayer
Escape to Pit Rules="'''+race['pitreturns'][1]+'''" // When can you escape to pits, 0 = Always, 1 = When stopped, 2 = In Pit Box Only (Tow to Pits option adds delay before can go to track again.), 3 = As In Pit Box Only but with even longer delays.
Mid Race Full Course Yellow="0" // 2 full course yellow laps in mid race
    ''' 
    ########################################################################
    #\\\\\\\\\\\\\\\\\\\\\\##\\\\\\\\\\\\\\\\\\\\\\##\\\\\\\\\\\\\\\\\\\\\\#
    ########################################################################
    #//////////////////////##//////////////////////##//////////////////////#
    ########################################################################
    plrfile = '''//[[gMa1.002f (c)2007    ]] [[            ]]
//*****************************************************************
//*                                                               *
//*  Player File                                                  *
//*                                                               *
//*  Edit at your own risk!                                       *
//*                                                               *
//*  Copyright (c) 1999-2009 Image Space Incorporated             *
//*  All rights reserved.                                         *
//*                                                               *
//*****************************************************************

[ SCENE ]
'''+race['tracks'][2]+'''

[ DRIVER ]
RaceCast Email="" // The email you are registered with on racecast.rfactor.net
RaceCast Password="" // Your password on racecast.rfactor.net
Vehicle File=""
Team=""
Original Driver=""
Nationality=""
Birth Date=""
Location=""
Game Description="'''+car+'''" // The current mod file (*.srs) to load
Season="" // The current season within the given game
Helmet=""
Unique ID="-14920" // Helps to uniquely identify in multiplayer (along with name) if leaving and coming back
Starting Driver="0" // Zero-based index of starting driver (0=driver1, 1=driver2, 2=driver3, etc.)
AI Controls Driver="2" // Bitfield defining which drivers the AI controls (0=none, 1=driver1, 2=driver2, 3=driver1+driver2, etc.)
Driver Hotswap Delay="3.00000" // Delay in seconds between switching controls to AI or remote driver
Save Game Description='''+car+'''" // Restore if changed during multiplayer
Save Season="" // Restore if changed during multiplayer
Save Vehicle File="" // Restore if changed during multiplayer

[ CHAT ]
Quick Chat #1="Slowing to pit"
Quick Chat #2="Leaving pits"
Quick Chat #3="Go Left"
Quick Chat #4="Go Right"
Quick Chat #5="Thank you"
Quick Chat #6="Sorry"
Quick Chat #7="Be careful at the first corner"
Quick Chat #8="Good job"
Quick Chat #9="Good race"
Quick Chat #10="/vote yes"
Quick Chat #11="/vote no"
Quick Chat #12="/ping"

[ DRIVING AIDS ]
Steering Help="0" // Now 3 levels, although full level now comes with a weight penalty by default
Throttle Control="0"
Brake Help="0"
Antilock Brakes="0"
Spin Recovery="0"
Invulnerability="0"
Autopit="0"
Opposite Lock="0"
Stability Control="0"
Driving Line="0" // Visible Driving Line & Accelerate / Brake Aid.
No AI Control="1" // AI never has control over car (except autopit)
Pitcrew Push="1" // When out of fuel in pitlane, allows pitcrew to push car (use throttle and gear selection to direct)
Auto Clutch="1"
Auto Lift="1" // Whether to automatically lift with manual shifting but auto-clutch (non-semiautomatic trans only)
Auto Blip="1" // Whether to automatically blip with manual shifting but auto-clutch (non-semiautomatic trans only)
Auto Ignition="1" // Whether to automatically start the ignition of the engine
Shift Mode="0"
Repeat Shifts="4" // 0 = no repeat shift detection, 1 = detect and eliminate accidental repeat shifts within 100ms, 2 = 150ms, 3 = 200ms, 4 = 250ms, 5 = prevent shifting again before previous shift is completed
Manual Shift Override Time="0.60000" // How long after a manual shift until auto shifting resumes (if auto-shifting is enabled)
Auto Shift Override Time="0.55000" // How long after an automatic shift before user is allowed to manually shift
Hold Clutch On Start="1" // For auto-shifting only: whether to hold clutch for standing start (to allow revving without moving)
Track Markers="1" // Extra track markers for turning and braking
Data Acquisition Version="0" // Version of vehicle data to write out
Data Acquisition Rate="8"
Data Acquisition In Race="1"
Data Acquisition EXE="DataAnalysis.exe"
Data Acquisition File="C:\\Users\\pbarr\\OneDrive\\Documents\\Automobilista\\userdata\\vehicledata.spt"
Alternate Collision="0" // Temporary variable as we develop new collision system.  NOT AVAILABLE IN THIS VERSION
Display Boost Time="150" // Max countdown in seconds till next boost (-1 to disable)

[ Mechanical Failures ]
QUICK Failure Rate="1" // Mechanical failure rate (0-none, 1-normal, 2-timescaled, disabled: 3-season)
MULTI Failure Rate="'''+race['mechfailures'][1]+'''"

[ Race Conditions ]
Run Practice1="1"
Run Practice2="0"
Run Practice3="0"
Run Practice4="0"
QUICK Num Qual Sessions="1" // range: 0-1
MULTI Num Qual Sessions="1"
Run Warmup="'''+race['warmups'][1]+'''"
QUICK Num Race Sessions="1" // range: 1-4
MULTI Num Race Sessions="1"
Race Timer="3600" // Seconds between displaying time remaining in race other than 1/5/10/30 minutes (zero disables)
Recon Pit Open="300" // Time that pits remain open for recon laps (real-life is 900 seconds)
Recon Pit Closed="150" // Time that pits are closed before formation lap (real-life is 900 seconds)
Recon Timer="1" // Whether timer is displayed in message box
Double File Override="-1" // Whether restarts can be converted to double file (-1=use SRS default, 0=no, 1+=minimum laps left to restart double-file)
Lucky Dog Override="-1" // Where lucky dog is applied (-1=use SRS default, 0=nowhere, 1=ovals, 2=road courses, 3=everywhere)
QUICK Reconnaissance="0" // Reconnaissance laps
MULTI Reconnaissance="0"
QUICK Grid Walkthrough="1" // Cinematic walkthrough of vehicles before race
MULTI Grid Walkthrough="0"
QUICK Formation Lap="4" // 0=standing start, 1=formation lap & standing start, 2=lap behind safety car & rolling start, 3=use track default, 4=fast rolling start
MULTI Formation Lap="'''+race['starttypes'][1]+'''"
Force Formation="0" // if Formation Lap is Use Track Default, add the following to force: 1=standing start formations on, 2=standing formations off, 4=rolling start formations on, 8=rolling formations off
QUICK Unsportsmanlike Sensitivitity="1.50000" // 0.1 - 10.0: Higher number = less sensitive checking for unsportsmanlike driving
MULTI Unsportsmanlike Sensitivitity="1.38118"
QUICK Safety Car Collidable="1" // Whether safety car is collidable
MULTI Safety Car Collidable="1"
QUICK Safety Car Thresh="0.00000" // Threshold for bringing out safety car (lower numbers -> more full-course yellows), please note that there are now SRS multipliers for this value
MULTI Safety Car Thresh="0.50000"
Adjust Frozen Order="0.80000" // Moves vehicles down the frozen track order under the safety car if they are causing the yellow and being passed.  0.0=off, 0.1-0.9=apply liberally, 1.0+=apply conservatively
QUICK Flag Rules="2" // Level of rule enforcement, 0=none, 1=penalties only, 2=penalties & full-course yellows
MULTI Flag Rules="'''+race['flags'][1]+'''"
QUICK BlueFlags="7" // 0=none, 1=show but never penalize, 2=show and penalize if following within 0.7 seconds, 3=0.9s, 4=1.1s, 5=1.3s, 6=1.5s, 7=use SRS value "BlueFlags=<0-6>" (default is 3)
MULTI BlueFlags="7"
QUICK Weather="0" // Random/season/sunny/etc.
MULTI Weather="0"
QUICK TimeScaledWeather="1" // Whether weather time is scaled with session length
MULTI TimeScaledWeather="1"
Practice1StartingTime="'''+startpractime+'''" // -3=random, -2=random daytime, -1=default SRS, 0-1439=minutes after midnight
QualifyingStartingTime="'''+startqualytime+'''" // -3=random, -2=random daytime, -1=default SRS, 0-1439=minutes after midnight
QualifyingDurationTime="5" //  0=Default in the series, 1-60=minutes of duration for qualification session
WarmupStartingTime="'''+startracetime+'''" // -3=random, -2=random daytime, -1=default SRS, 0-1439=minutes after midnight
QUICK RaceStartingTime="-1" // -3=random, -2=random daytime, -1=default SRS, 0-1439=minutes after midnight to start race
MULTI RaceStartingTime="'''+startracetime+'''"
QUICK RaceTimeScale="0" // 0 - 60 = multiply time by given factor
MULTI RaceTimeScale="'''+race['timescales'][1]+'''"
QUICK PrivateQualifying="2" // 0=all cars qualify visibly on track together, 1=only one car is visible at a time, 2=use default from SRS, season, or track entry PrivateQualifying=<0 or 1>
MULTI PrivateQualifying="1"
QUICK ParcFerme="3" // 0=off, 1=no setup changes allowed between qual and race except for 'Free Settings'), 2=same unless rain, 3=use SRS default 'ParcFerme=<0-2>'
MULTI ParcFerme="3"
QUICK InitialTrackConditions="2" // 0=None, 1=Light, 2=Medium, 3=Heavy, 4=Max
MULTI InitialTrackConditions="'''+race['trackconds'][1]+'''"
QUICK TrackProgressionRate="1" // 0=None, 1=Normal, 2=2x, 3=3x, 4=4x, 5=5x
MULTI TrackProgressionRate="'''+race['trackprogresses'][1]+'''"

[ Sound Options ]
Net Race Warning="Default\\racestart.wav" // Signal that multiplayer game has moved to race session (empty this if you don't want the game to automatically take window focus)
Maximum Samples="64" // Maximum sound effects playing simultaneously
Music="1" // Music Toggle
Track Load Commentary="1" // Whether or not the commentator should talk during track loading
Realtime In Monitor="1" // Whether to play realtime sounds in monitor
SoundFX Volume="1.00000" // 0.0-1.0
Engines Volume="1.00000" // 0.0-1.0
Tires Volume="0.80000" // 0.0-2.0
Wind Volume="1.00000" // 0.0-1.0
Traction Control="1.50000" // Volume multiplier
Viewed Vehicle Volume Ratio="1.00000" // Additional volume multiplier for player's vehicle
Opponent Vehicle Volume Ratio="0.50000" // Additional volume multiplier for other vehicles
UI Sounds="1.00000" // UI sound effects volume
Music Volume="0.50000" // 0.0-1.0
Pit Volume="0.50000" // 0.0-1.0, controls volume of pit sounds while you're at the monitor
Spotter Volume="0.75000" // 0.0-1.0
Camera Volume="1.00000" // 0.0-1.0
Trackside-Camera Volume="1.50000" // 0.0 - 3.0
Master Audio Volume="1.00000" // 0.0-1.0
Sound Detail Level="3" // 0 = LOW, 1=MID, 2=HIGH, 3=FULL
Speed Of Sound="343.42001" // 343.42 m/s at sea level at 20 degrees celsius for dry air
General Reverb Level="2"
Global Reverb Decay Time="0.50000" // Range 0.1 - 4.0
Global Reverb Predelay Time="0.14500" // Range 0.0 - 0.25
Global Reverb Damping Level="0.80000" // Range 0.0 - 1.0, lower numbers=more high frequency filtered out
Nearby Reverb Multiplier="1.25000" // Range 0.1 - 8.0, 1.0 - linear rise of reverb amount with distance from sound source, over 1.0 - slower, under 1.0 = quicker
Nearby Reverb Min Level="0.30000" // Range 0.0 - 1.0 - 0.0 - reverb level zero when very close, 1.0 - reverb 100% (scaling with distance ineffective). Old default: 0.2
Reverb Max Dist="750.00000" // Range 40.0 - 4000.0 - distance between listener and sound source after which reverb wet level starts to decrease
Reverb Volume="1.00000" // Use this to control reverb volume live on track
Reverb - Center speaker volume="0.00000" // Fine tune reveb per speaker pair with these settings, effective only in surround mode
Reverb - Front speakers volume="0.25000"
Reverb - Side speakers volume="0.25000"
Reverb - Rear speakers volume="1.00000"
Drivetrain sound effects reverb vol="1.00000"
Surface sound effects reverb vol="0.50000"
Other sound effects reverb vol="0.30000"
Low Pass Damping="0.80000" // Range 0.01 - 8.0 - higher number - quicker low pass frequency drop
Crowd AttenRange="50.00000" // Volume range parameter
Crowd AttenShape="0.77500" // Shape of volume attenuation
Crowd AttenAmbient="2.00000" // Ambient range where volume is maximum
Airhorn Range="75.00000"
Airhorn Shape="0.75000"
Airhorn Ambient="2.50000"
Public Address Range="50.00000"
Public Address Shape="0.75000"
Public Address Ambient="2.50000"
Pithorn Range="30.00000"
Pithorn Shape="0.45000"
Pithorn Ambient="1.50000"
Helicopter Range="75.00000"
Helicopter Shape="0.70000"
Helicopter Ambient="2.50000"
Ambient Sounds Occlusion Level="0.50000" // Occlusion to use when in cockpit camera for ambient misc effects
Ambient Sounds Occlusion Increase Mult="0.25000"
Speaker distance="1.00000" // Approximate speaker distance to listener
Surround Pan Linearity="0.50000" // Surround panning exponent for flattening volume when sound pans around
Speed Volume Effects="0.25000" // Effect of sound waves spread at speed, 0.0 to disable
Trackside Camera Audio Directionality="0.35000" // Higher the number, more of the sound on the rear of camera is rejected. Stereo mode only. Max=0.75

[ Graphic Options ]
TV Overlay="4" // 0 = off, 1 = timing & general info only, 2 = no standings,  3 = no extras, just standings, time & general info, 4 = all
TV Overlay External="4" // Which elements to show on external cameras. 0 = none, 1 = timing & general info only, 2 = no standings,  3 = no extras, just standings, time & general info, 4 = all
Texture Detail="3"
Vertical FOV Angle="9" // 9=use default, otherwise is the FOV for attached cameras (horiz is calculated based on aspect ratio)
Rearview="1" // 0=Off, 1=In-car only, 2=Center and Side, 3=Center only, 4=Side only (virtual mirrors only, in-car mirrors are on/off)
Allow Rearview In Swingman="0"
Virtual Rearview In Cockpit="0"
Rearview Width="60.00000"
Rearview Height="15.00000"
Rearview Cull="1" // Whether to cull objects in the rearview based on visgroups in the SCN file
Seat Adjustment Aft="0.00000"
Seat Adjustment Up="0.00000"
Mirror Adjustment Horizontal="0.00000"
Mirror Adjustment Vertical="0.00000"
Cockpit Vibration Mult1="0.20000" // Primary vibration multiplier affects eyepoint position (base magnitude is in VEH or cockpit file)
Cockpit Vibration Freq1="42.00000" // Primary rate of vibration affects eyepoint position (higher framerates allow higher rates)
Cockpit Vibration Mult2="0.28000" // Secondary vibration multiplier affects eyepoint orientation (base magnitude is in VEH or cockpit file)
Cockpit Vibration Freq2="56.00000" // Secondary rate of vibration affects eyepoint orientation
Moving Rearview="1" // Whether mirrors respond to head movement in cockpit (0=none, 1=position-only, 2=FOV-only, 3=both) - add 4 if you want to IGNORE head-tracking movement
Rearview_Front_Clip="0.00000" // Front plane distance for mirror (0.0 = use default for scene)
Rearview_Back_Clip="0.00000" // Back plane distance for mirror (0.0 = use default for scene)
Rearview Particles="1"
Self In TV Rearview="0" // add values for any that should be visible (0=none): 1=rear wing & wheels, 2=body & susp, 4=cockpit, 8=steering wheel (15=all)
Self In Cockpit Rearview="15" // add values for any that should be visible (0=none): 1=rear wing & wheels, 2=body & susp, 4=cockpit, 8=steering wheel (15=all)
Backfire Anim Speed="60.00000"
Warning Light Anim Speed="4.00000" // Safety car light animation
Steering Wheel="0" // 0=moving steering wheel, 1=non-moving steering wheel, 2=no steering wheel (in cockpit only while player-controlled)
Box Outline="16711680" // whether to draw box on ground around pitstall and grid location when necessary; -1=off, 0-16777215=RGB color
Allow Letterboxing="0" // whether we allow letterboxing (during replays, for example)
Logo Seconds="0" // puts up logo at corner of screen for first X seconds of each session
HUD="7"
Track Map Overlay="3" // 0=Off, 1=Fixed, 2=Follow, 3=Follow Zoom
Track Map Sessions="3" // 0=off 1=race-only 2=non-race-only 3=all sessions
Track Map Road Width="0" // 0=fixed 1=real
Track Map Size="1.00000" // Scales the track map size down
Start Lights Overlay="1" // 0=Off, 1=On
HUD Type="1" // 0=None, 1=Native, 2=Dynhud
HUD Tachometer="1" // 0=Off, 1=Default
HUD MFD="3"
HUD Delta="1" // Delta Timing Element, 0=Off, 1=Attached to Timing Element, 2=Top Centre of Screen.
HUD Style="0" // Delta Timing Style, 0=Bar always grows from the left, 1=Bar is centred, grows to left for up, to the right for down, 2=Off
External Overlays="1" // What overlays to show on none attached cameras, 0=None, 1=Broadcast, 2=Messages, 4=Flags, 8=HUD
LCD Display Modes="15" // Add the modes to allow them: 1=status 2=aids 4=engine/brake temps 8=race info 16=standings 32=timing
Display Vehicle Labels="0" // 0=never 1=single-player 2=multi-player 3=always
Player Detail="3"
Player Texture Override="-1" // For player's vehicle textures: -1=use Player Detail, 0-3=override value
Opponent Detail="2"
Opponent Texture Override="-1" // For opponents' vehicle textures: -1=use Opponent Detail, 0-3=override value
Load Opponent Cockpits="1" // Whether to load gauges and LCD for opponents, don't turn off if you're planning on hot-swapping vehicles in multiplayer
Garage Detail="0.50000" // LOD multiplier when vehicle is in garage (0.01-1.00)
Shadows="3"
Shadow Blur="1"
Shadow Cache="1"
Pitcrew Detail="2"
Special FX="4"
Lightning Probability="1.00000" // Probability of seeing lightning (0.0-1.5)
Thunder Probability="1.50000" // Probability of hearing thunder (0.0-1.5)
Cloud Scroll="0.00000" // Maximum cloud scrolling rate (0.000-0.010)
Cloud Blend="0" // Whether to roll the rainy cloud map in across sky (only works with overhead not cylinder skies)
Skybox Positioning="1.00000" // Numbers less than 1.0 cause the skybox to get closer as you drive towards it
Shadow Updates="8" // Static shadow updates per frame (Shadow Updates * Sky Update Frames should exceed number of static shadows on track)
Sky Update Frames="150" // Frames between sky and light updates
Vehicle Flow Radius="4.00000" // Vehicle sphere radius for smoke/flames/dust/spray
Vehicle Flow Offset="3.10000" // Offset below vehicle where sphere center is located
Engine Emitter Flow="1" // Whether engine smoke/flames flow over emitting vehicle
Tire Emitter Flow="1" // Whether tire smoke/dust flow over emitting vehicle
Smoke Flow="1" // Whether all smoke/flames/dust flow over non-emitting vehicles
Raindrop Flow="0" // Add to enable: 1=flow over current 2=flow over other vehicles
Rainspray Flow="0" // Add to enable: 1=flow over current 2=flow over other vehicles
Spark Flow="1" // Add to enable: 1=flow over current 2=flow over other vehicles
Glance Rate="18.08000" // Rate to follow controller for glancing
Look Up/Down Angle="0.40000" // Angle to look up/down (pitch) w/ controller in radians (= degrees / 57)
Leanahead Angle="0.00000" // Angle to lean head (roll) w/ steering in radians (= degrees / 57)
Look Roll Angle="0.75000" // Angle to lean head (roll) w/ controller in radians (= degrees / 57)
Glance Angle="0.75000" // Angle to look left/right (yaw) w/ controller in radians (= degrees / 57)
Lookahead Angle="0.00000" // Angle to lookahead (yaw) w/ steering in radians (= degrees / 57)
Head Physics="0.50000" // Fraction of head physics movement applied to cockpit view (position AND rotation)
Head Rotation="1.00000" // Additional head physics multiplier affecting rotation only
Exaggerate Yaw="0.0000000119" // Visually exaggerates the heading angle of the vehicle by rotating the head (which may improve "feel")
Overlay Height="0.04000" // Distance from geometry to help sort drawing skids and grooves
Overlay Z Bias="1" // Draw-sorting bias for skids and grooves (0 = none)
Track Detail="3"
Groove="1"
MIP Mapping="1"
Compressed Textures="1"
Max Visible Vehicles="30"
Extra Visible Vehicles="105" // Extra vehicles shown in non-driving situations
Shadows In TV Cockpit="1"
Wheels Visible In Cockpit="1" // Suggestion: add FrontWheelsInCockpit=? to the individual VEH files instead
In Car Dash="2"
Starting View="1"
Player Livery="" // Overrides default paint job for track
Mipmap Adjust Mode="1" // 0 = Disabled, 1 = Clamp, 2 = Bias
Mipmap Bias="-0.25000"
Allow HUD in cockpit="1"
Allow Swingman in Pitlane="1"
Display Icons="2" // Icons displayed if HUD is off: 0 = none, 1 = flags only, 2 = all
Auto Detail Framerate="0" // Details and visible vehicles will be automatically reduced (by up to half) if framerate is under this threshold (0 to disable)
Max Framerate="120" // 0 to disable, for regular exe only, see multiplayer.ini for dedicated server framerate, new: use negative values for alternate timing
Delay Video Swap="0" // Whether to delay video swap if card is busy - this should only be used if framerate clearly improves - otherwise it is only delaying response time
Always Rebuild HAT="0" // Build HAT database everytime tracks are loaded (for development purposes)
UI Background Animation="1"
Low Detail UI="0"
Widescreen Overlays="1"
Texture Filter="3" // Texture Filtering level: 0 = bilinear, 1 = trilinear, 2 = X2 AF, 3 = X4 AF, 4 = X8 AF, 5 = X16 AF
Max Headlights="15" // Max headlights visible relative to your car.
Headlights On Cars="1" // Headlights illuminate other cars.
Screenshot File Type="0" // 0=default (jpg), 1=bmp, 2=jpg, 3=png, 4=dds
Suspension Animation LOD="350.00000" // Level of detail of the animation suspension
Deactivate Track Scoreboard="0" // Deactivates scoreboards if 1
Cockpit Preferences="0" // Force Cockpit Options. 0=respect upgades, 1=arms on default cockpit, 2=arms left cockpit, 3=arms right cockpit, 4=default cockpit, 5=left cockpit, 6=right cockpit
Driver Arm Rotation Lock="1" // When Driver Arms are on, do we wish to lock the amount of angle steering. Disabling this will result in graphical glitches.

[ Game Options ]
Championship Basic Rules="1"
Basic Rules="0"
Basic Display="0"
Audio PostFX="3"
QUICK Damage Multiplier="100" // 100 should approximate real life
MULTI Damage Multiplier="'''+race['damages'][1]+'''"
Record Replays="1" // whether to record replays or not
Save All Replay Sessions="1" // whether to save the replay from each session
Record To Memory="0" // record replays to memory rather than disk (may possibly reduce stuttering, but at your own risk because memory usage will be significant for long races)
Compress Replay="1" // whether to compress VCR file (uses less disk space but takes more time to write)
Replay Wraparound="0" // whether replays wraparound in the fridge
Auto Monitor Replay="1" // whether to automatically start a replay when returning to monitor
Record Hotlaps="1" // whether to record hotlaps or not (must have replay recording on)
Instant Replay Length="80"
Replay Fidelity="4"
Super Player Replay="1" // record player at higher frequency
Number Track Replays="5" // how many replays to store for each track (using default naming convention only!)
Number Race Results="100" // how many results files to store (using default naming convention only!)
Multi-session Results="0" // whether to store all sessions at a track in a single results file, new default is one session per file
Disconnected Results="1" // show results for clients disconnected at end of prac/qual/warmup
Private Test Day="1"
Starting Pos="0" // Only used if no qualifying session in single-player
Difficulty="0"
QUICK AI Driver Strength="95" // 100 should approximate real life
MULTI AI Driver Strength="95"
AI Power Calibration="7" // Adjustments with AI strength (0=none, or add the following: 1=power, 2=gearing, 4=fuel)
AI Fuel Mult="0.99000" // Additional fuel multiplier for AIs because of their driving style
AI Tire Model="0.40000" // 0.0 = use AI peak slip, 1.0 = use player's dynamic slip, or a blend between the two (can be overrode in TBC with AITireModel)
AI Brake_Power Usage="0.99800" // Fraction of theoretical brake power that AI attempt to use (can be overrode in HDV)
AI Brake_Grip Usage="0.99000" // Fraction of theoretical brake grip that AI attempt to use (can be overrode in HDV)
AI Corner_Grip Usage="0.99000" // Fraction of theoretical cornering grip that AI attempt to use (can be overrode in HDV)
AI Max Load="40000.00000" // Maximum total load to set up theoretical performance tables (can be overrode in HDV)
AI Min Radius="20.00000" // Minimum radius turn to set up theoretical performance tables (can be overrode in HDV)
AI to AI Collision Rate="80" // Detection rate per second (1-40) for AI-to-AI collisions
Auto Line Smooth="0" // 1 = fastest line, 2 = inside/outside, 3 = fastest and inside/outside
Message Center Detail="3"
Message Time="5"
Message Center Position="1" // 0 = left, 1 = right
Spotter Detail="3" // 0 = Off, 1 = Spotter, 2 = Spotter + Flags, 3 = Spotter + Flags + Pit Notifications, 4 = All Messages
Spotter Spot="1" // Enable car left/car right Spotter messages
Spotter Behind="7.50000" // Range behind at which spotter may comment on vehicles around you (range ahead is 40% of this value because those vehicles are easier to see)
Spotter Text="1" // Enable printing Spotter subtitles to Message Center
Play Movies="1"
Race Stint Offset="0" // Offset each scheduled pitstop in case you want to carry extra fuel
Relative Fuel Strategy="1" // Show how much fuel to ADD, rather than how much TOTAL fuel to fill the tank up to (note: new default is true)
Smart Pitcrew="1" // Pitcrew does things even if you mistakenly forgot to ask (one example is changing a damaged tire)
Automatic Pit Menu="4" // brings up pit menu automatically: 0=disabled, 1=upon pit ENTRY, change cockpit menu but do not bring up HUD, 2=pit ENTRY->cockpit & HUD, 3=pit REQUEST->cockpit menu only, 4=pit REQUEST->cockpit & HUD
Miscellaneous="1"
Autocalibrate AI Mode="0" // When in a test day with 1 AI, AI will attempt to perfect his driving line, and save his knowledge for future use
Find Default Setup="1" // If 1, attempts to ensure player has default setup ... only works well if only one vehicle class in SRS
Ghost AI="0" // If 1, AI car will ignore others and be uncollidable.  disabled for standard builds
Anti Cutting Rules="1" // Activates or deactivates the anti cutting rules
Disable Radars="0" // Deactivates radar if placed on a track
Mid Race Full Course Yellow="0" // 2 full course yellow laps in mid race
Cut Warnings="3" // Number of cut warnings before penalization
Return to Pit Rules="'''+race['pitreturns'][1]+'''" // What happens when you escape back to pits, 0 = Always Instant, 1 = Vehicle must be stopped & instant, 2 = Vehicle must be stopped & 'towed' to pits with semi realistic timings, 3 = Vehicle must be stopped & 'towed' to pits with realistic timings
Relevant Setups Only="1" // 0 = show all setups in folder, 1 = only show setups for your current vehicle
Keep Received Setups="1" // 0=do not accept, 1=keep until next track, 2=keep until exit, 3=keep forever
Camera Orientation Rate="1.00000" // Percetage of camera orientation rate from modern default to old one
QUICK FreeSettings="-1" // -1=use SRS/season/GDB default, or add to allow minor changes with fixed/parc ferme setups: 1=steering lock, 2=brake pressure, 4=starting fuel, 8=fuel strategy 16=tire compound, 32=brake bias, 64=front wing, 128=engine settings
MULTI FreeSettings="-1"
Fixed Setups="'''+race['fixsetups'][1]+'''" // use fixed setups specified in UserData\\<plr>\\FavoriteAndFixedSetups.gal (based on track and vehicle class)
Fixed AI Setups="0" // whether AI use the fixed setups, only applicable if "Fixed Setups" is also enabled (and can be used in single player to have the AIs use your favorite setup)
Fixed Upgrades="'''+race['fixupgrades'][1]+'''" // whether multiplayer vehicles use the closest standard upgrade class package
Disable NetComm="0" // If 1, network features are disabled
AI Limiter="0.00000" // Range: 0.0 (no limiting) - 1.0 (limiting used to make racing closer but also make more driver differences on flat-out tracks)
AI Mistakes="0.10000" // a range of (intentional) AI mistakes from 0.0 (none) to 1.0 (sometimes).  Anything above 1.0 multiplies the frequency
AI Aggression="0.75000"
Display Driver Stats="0"
Display Track Stats="0"
Settings Type="6"
Drift mode="0" // This value can't be edited by user
Exit Confirmation Menu="2" // 0=none, 1=race only, 2=always
Monitor AI Postfix="" // what is displayed after AI driver names in monitor (multiplayer only)
Monitor Admin Postfix="*" // what is displayed after multiplayer administrator driver names in monitor
Realtime Splits="1" // 0=show race splits at sectors only, 1=realtime splits (can be toggled while driving with pit decrement key
Standings Display="3" // standings scroll with pit up/down keys: 0=no wraparound, 1=wraparound, 2=auto-scroll (can be changed while driving with pit increment key), 3=Paginate
Standings Focus="0" // Standings Time Gaps to be focused on 0) Currently Viewing Driver or 1) Leader
Show Extra Lap="1" // 0 = show laps completed, 1 = show lap you are on
One Lap To Go Warning="1" // Race only: 0=none, 1=message, 2=white flag, 3=both, Race+Qual: add 4.  Feature not implemented for timed races or lapped vehicles.
Pitstop Description="1" // Gives extra info about what's taking time in pitstop
Measurement Units="0" // Units for everything EXCEPT speed (0 = metric, 1 = english/imperial)
Speed Units="1" // 0 = MPH, 1 = KPH
Damper Units="0" // Display dampers (shocks) in garage as: 0 = setting (e.g. 1-20), 1 = rate (e.g. 1000-9000 N/m/s)
Horizontal Tire Temps="1" // In garage options
QUICK Race Finish Criteria="2" // 0=distance, 1=laps, 2=time, 3=laps&time
MULTI Race Finish Criteria="'''+race['racefinishes'][1]+'''"
QUICK Race Laps="5"
MULTI Race Laps="'''+race['session'][5]+'''"
QUICK Race Time="50" // minutes
MULTI Race Time="'''+race['session'][4]+'''"
QUICK Race Distance="2.00000"
MULTI Race Distance="2.00000"
QUICK Speed Compensation="0" // 0 (none) - 10 (max)
MULTI Speed Compensation="0"
Speed Comp Dist="500.00000" // <= 2.0: fraction of track length, > 2.0: actual distance in meters for max speed comp
QUICK Opponents="9"
MULTI Opponents="9"
Vehicle Removal="30.00000" // Seconds until stationary vehicle is removed from track
Debris Removal="30.00000" // Seconds until stationary debris is removed from track
Parts Duration="1000.00000" // Seconds after parts break off before disappearing
QUICK CrashRecovery="3" // 0=none, 1=artificially keep cars on track, 2=flip cars upright, 3=both
MULTI CrashRecovery="0"
QUICK Fuel Consumption Multiplier="1"
MULTI Fuel Consumption Multiplier="'''+race['fueltires'][1]+'''"
QUICK Tire Wear Multiplier="1"
MULTI Tire Wear Multiplier="'''+race['fueltires'][1]+'''"
Auto-change Opponent List="1" // whether to change the single-player allowed vehicle filter when player changes vehicles
CURNT Allowed Vehicles="'''+allowed_cars+'''"
CURNT Random Opponents="1" // Whether the number of opponents for each class is randomly picked from the selected classes
PRACT Allowed Vehicles="'''+allowed_cars+'''"
PRACT Random Opponents="1" // Whether the number of opponents for each class is randomly picked from the selected classes
TIMET Allowed Vehicles="'''+allowed_cars+'''"
TIMET Random Opponents="1" // Whether the number of opponents for each class is randomly picked from the selected classes
QUICK Allowed Vehicles="'''+allowed_cars+'''"
QUICK Random Opponents="1" // Whether the number of opponents for each class is randomly picked from the selected classes
GPRIX Allowed Vehicles="'''+allowed_cars+'''"
GPRIX Random Opponents="1" // Whether the number of opponents for each class is randomly picked from the selected classes
CHAMP Allowed Vehicles="'''+allowed_cars+'''"
CHAMP Random Opponents="1" // Whether the number of opponents for each class is randomly picked from the selected classes
MULTI Allowed Vehicles="'''+allowed_cars+'''"
MULTI Random Opponents="1" // Whether the number of opponents for each class is randomly picked from the selected classes
RPLAY Allowed Vehicles="'''+allowed_cars+'''"
RPLAY Random Opponents="1" // Whether the number of opponents for each class is randomly picked from the selected classes
Inactive Sleep Time="25" // Number of milliseconds to sleep each message loop if the game is not the active application (-1 to disable).  will give more CPU to other apps when minimized, etc.
Active Sleep Time="-1" // ms to sleep each loop if the game is the active app (-1 to disable).  Consider setting to 1 or more if you are running a dedicated server on the same machine.
QUICK Tire Sets="0"
MULTI Tire Sets="'''+race['tiresets'][1]+'''"

[ Miscellaneous ]
PlayerFilesReadOnly="0"
Key Repeat Rate="1"
AVI export width="800"
AVI export height="600"
AVI export framerate="30.00000"
AVI export quality="95.00000"
AVI compressor fourcc="cvid" // Changes compression algorithm

[ Controls ]
Current Control File="Controller"

[ Plugins ]
DynHud Overlay="Original" // Name of the folder under Plugins/DynHud/Config/Overlays/
    '''
    ########################################################################
    #\\\\\\\\\\\\\\\\\\\\\\##\\\\\\\\\\\\\\\\\\\\\\##\\\\\\\\\\\\\\\\\\\\\\#
    ########################################################################
    #//////////////////////##//////////////////////##//////////////////////#
    ########################################################################
    
    inifile = '''//[[gMa1.002f (c)2007    ]] [[            ]]
//
// Dedicated Server configuration file
//

// Note: most settings are now using the regular player file variables where available.  Other variables
//       including LessenRestrictions, Password, and driving aids are now in the multiplayer.ini file.
[SETTINGS]
MaxClients='''+str(race['maxplayers'])+'''  // use this variable or the commandline option "+maxplayers <X>" only if you need to override the multiplayer.ini variable "Max MP Players"

// Available track list depends on the track filter in the SRS file.
// See comments for chat command to load a specific track directly.
[TRACKS]
'''+race['tracks'][1]+'''
    '''
    
    
    
    
    
    with open(config_file_path+'\\Dedicated'+car.strip('srs')+'ini', 'w') as f:
        f.write(inifile)
    with open(config_file_path+'\\DedicatedServer.plr', 'w') as f:
        f.write(plrfile)
    with open(config_file_path+'\\Multiplayer.ini', 'w') as f:
        f.write(multiplayer_conf)
        


def xmlparser(file):
    client = MongoClient("mongodb+srv://public:publicpassword@brazilavrank-2ccxo.mongodb.net/test") #EDIT THIS
    db = client.ValleyAlliance
    srv_opt = client.ServerOptions
    dbusers = client.users
    cursor = db.RaceResult.find()
    rating_cursor = db.Drivers.find()
    incident_sum = [] 
    steamidlist = [[],[]]   
    incident_list = [[],[],[]]
    inc_dict_list= []
    schedrace = db.ScheduledRace.find().sort([('timestamp', ASCENDING)])[0]
    minimumraces = 2
    minimumplayers = 2
    
    f = open(path_to_watch + '\\' + file)
    soup = BS(f, 'xml')
    filename = file
    #print(filename)

    tableDict = {}
    finalresultlist = []
    timestamp = soup.find("DateTime").contents[0]
    tableDict['timestamp'] = timestamp #timestamp
    tableDict['racedate'] = datetime.fromtimestamp(int
         (timestamp)).strftime('%Y-%m-%d %I:%M %p %Z') #human_date
    
    if file.endswith('P1.xml'):
        tableDict['practicefilename'] = filename #Nome do arquivo
    elif file.endswith('Q1.xml'):
        tableDict['qualifyfilename'] = filename #Nome do arquivo
    elif file.endswith('R1.xml'):
        tableDict['racefilename'] = filename #Nome do arquivo
    else:
        tableDict['TBDfilename'] = filename
    
    
    name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content = [
            [],[],[],[],[],[],[],[],[],[]
            ]
    playnum = 0
    for item in soup.find_all('SteamID'):
        if int(item.contents[0]) != 0:
            playnum += 1
    print('The session had ' + str(playnum) + ' total players')
    
        
      
    ##############################
    #Saves [[],[Pos]]
    print('Parsing the XML...')
    for Position in soup.find_all('Position'):
        pos_cont = Position.contents
        if int(pos_cont[0]) == -1:
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[2].append('DNF')
        elif int(pos_cont[0]) < 10:
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[2].append('0'+pos_cont[0])
        else:
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[2].append(pos_cont[0])
    print('Parse positions, Done!')        
    ##############################
    #Saves [[Drivername],[]]
    for Name in soup.find_all('Name'):
        name_cont = Name.contents
        name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[0].append(name_cont[0])
        steamidlist[1].append(name_cont[0].upper().title())
    print('Parse Driver names, Done!')
    #############################
    #Getting STEAM_ID, USERID, END POSITION Values and ALL LAPS for each driver
    for SteamID in soup.find_all('SteamID'):
        steamid_cont = SteamID.contents
        user = dbusers.users.find_one({'steam_id': steamid_cont[0]})
        name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[1].append(steamid_cont[0])
        try:
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[6].append(user['_id'])
        except:
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[6].append('')
        steamidlist[0].append(steamid_cont[0])
    if soup.find_all('GridPos') == []:
        pass
    else:
        for gridpos in soup.find_all('GridPos'):
            st_position = gridpos.contents
            if int(st_position[0]) < 10:
                name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[3].append('0'+st_position[0])
            else:
                name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[3].append(st_position[0])
    print('Parse SteamID, Done!')
    print('--------------------')
    for driver in soup.find_all('Driver'):
        laplist = []
        print('Starting to Parse Drivers Laps!')    
    
        for lap in driver.find_all('Lap'):
            lapdict = {}
            laptime = lap.contents[0]
            fuel = float(lap['fuel']) * 100
            position = lap['p']
            
            
            
            if int(lap['p']) < 10:
                position = '0' + position

            lapdict['position'] = position
            lapdict['fuel'] = str(round(fuel, 2)) + '%'
            
            try:
                lap_s1 = float(lap['s1']) * 1000
                s, ms = divmod(lap_s1, 1000)
                m, s= divmod(s, 60)
                h, m = divmod(m, 60)
                lapdict['s1'] = ("%d:%02d:%02d:%03d" % (h, m, s, ms))
            except:
                lapdict['s1'] = '--:--:--:---'

            try:
                lap_s2 = float(lap['s2']) * 1000
                s, ms = divmod(lap_s2, 1000)
                m, s= divmod(s, 60)
                h, m = divmod(m, 60)
                lapdict['s2'] = ("%d:%02d:%02d:%03d" % (h, m, s, ms))
            except:
                lapdict['s2'] = '--:--:--:---'
            try:
                lap_s3 = float(lap['s3']) * 1000
                s, ms = divmod(lap_s3, 1000)
                m, s= divmod(s, 60)
                h, m = divmod(m, 60)
                lapdict['s3'] = ("%d:%02d:%02d:%03d" % (h, m, s, ms))
            except:
                lapdict['s3'] = '--:--:--:---'

            try:
                laptime = float(lap.contents[0]) * 1000
                s, ms = divmod(laptime, 1000)
                m, s= divmod(s, 60)
                h, m = divmod(m, 60)
                lapdict['laptime'] = ("%d:%02d:%02d:%03d" % (h, m, s, ms))
            except:
                if str(laptime) == '--.----':
                    lapdict['laptime'] = 'ALERTA - Corte de Pista ou Volta não Completada'


            laplist.append(lapdict)
        for j in range(len(laplist)):
            if j == 0:
                s1_index = j
                s2_index = j
                s3_index = j
                bl_index = j
                if laplist[j]['s1'] == '--:--:--:---' :
                    laplist[j]['bests1'] = False
                else:
                    laplist[j]['bests1'] = True
                    
                if laplist[j]['s2'] == '--:--:--:---' :
                    laplist[j]['bests2'] = False
                else:
                    laplist[j]['bests2'] = True
                    
                if laplist[j]['s3'] == '--:--:--:---' :
                    laplist[j]['bests3'] = False
                else:
                    laplist[j]['bests3'] = True
                    
                if laplist[j]['laptime'] == 'ALERTA - Corte de Pista ou Volta não Completada' :
                    laplist[j]['bestlap'] = False
                else:
                    laplist[j]['bestlap'] = True
                    
                
                
            else:
                if laplist[j]['s1'] == '--:--:--:---' :
                    laplist[j]['bests1'] = False
                elif (laplist[j]['s1'] < laplist[s1_index]['s1'] ) or (laplist[s1_index]['s1'] == '--:--:--:---'):
                    laplist[j]['bests1'] = True
                    laplist[s1_index]['bests1'] = False
                    s1_index = j
                else:
                    laplist[j]['bests1'] = False

                if laplist[j]['s2'] == '--:--:--:---' :
                    laplist[j]['bests2'] = False
                elif (laplist[j]['s2'] < laplist[s2_index]['s2']) or (laplist[s2_index]['s2'] == '--:--:--:---'):
                    laplist[j]['bests2'] = True
                    laplist[s2_index]['bests2'] = False
                    s2_index = j
                else:
                    laplist[j]['bests2'] = False

                if laplist[j]['s3'] == '--:--:--:---' :
                    laplist[j]['bests3'] = False
                elif (laplist[j]['s3'] < laplist[s3_index]['s3']) or (laplist[s3_index]['s3'] == '--:--:--:---'):
                    laplist[j]['bests3'] = True
                    laplist[s3_index]['bests3'] = False
                    s3_index = j
                else:
                    laplist[j]['bests3'] = False

                if laplist[j]['laptime'] == 'ALERTA - Corte de Pista ou Volta não Completada' :
                    laplist[j]['bestlap'] = False
                elif (laplist[j]['laptime'] < laplist[bl_index]['laptime'] or (laplist[bl_index]['laptime'] == 'ALERTA - Corte de Pista ou Volta não Completada')):
                    laplist[j]['bestlap'] = True
                    laplist[bl_index]['bestlap'] = False
                    bl_index = j
                else:
                    laplist[j]['bestlap'] = False


            
        name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[4].append(laplist)
        try:
            bestlap = driver.find_all('BestLapTime')
            bestlaptime = float(bestlap[0].contents[0]) * 1000
            s, ms = divmod(bestlaptime, 1000)
            m, s= divmod(s, 60)
            h, m = divmod(m, 60)
            fulltime = "%d:%02d:%02d:%03d" % (h, m, s, ms)
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[7].append(fulltime)
        except:
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[7].append('-:--:--:---')

            
       
        print('Drivers laps, Done!')
        if file.endswith('R1.xml'):
            finishtime = driver.find_all('FinishTime')
            try:
                finishtime = float(finishtime[0].contents[0]) * 1000
                s, ms = divmod(finishtime, 1000)
                m, s= divmod(s, 60)
                h, m = divmod(m, 60)
                finishtime = "%d:%02d:%02d:%03d" % (h, m, s, ms)
            except Exception as e:
                print(str(e))
                time.sleep(30)
                status = driver.find_all('FinishStatus')
                finishtime = status[0].contents[0]
            
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[5].append(finishtime)
            
            lapsled = driver.find_all('LapsLed')
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[8].append(lapsled[0].contents[0])

        

        
        finishstatus = driver.find_all('FinishStatus')
        if finishstatus[0].contents[0] == 'Finished Normally':
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[9].append('Completada')
        elif finishstatus[0].contents[0] == 'DNF':
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[9].append('Não Completada')
        else:
            name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[9].append('Desconhecido?')

        print('Race Session, driver Status, Done!')

        
            
        

    
    ##############################
    #START RETRIEVE RACE'S INCIDENTS
    print('Retrieving Session incidents...')
    for incident in soup.find_all('Incident'):
        incident_cont = incident.contents[0]
        et = incident['et']
        

        try:
            m = re.match(r'(?P<driver1>.*) reported contact (?P<value>.*) with another vehicle (?P<driver2>.*)', incident_cont)
            incident_list[0].append(m.group('driver1').split('(')[0])
            incident_list[1].append(m.group('driver2').split('(')[0])
            if float(et) < 250:
                incvalue = float(m.group('value').split('(')[1].split(')')[0]) * 2
                incident_list[2].append(incvalue)
            else:
                incident_list[2].append(float(m.group('value').split('(')[1].split(')')[0]))
        except:
            m = re.match(r'(?P<driver1>.*) reported contact (?P<value>.*) with (?P<driver2>.*)', incident_cont)
            incident_list[0].append(m.group('driver1').split('(')[0])
            incident_list[1].append(m.group('driver2').split('(')[0])
            if float(et) < 250:
                incvalue = float(m.group('value').split('(')[1].split(')')[0]) * 2
                incident_list[2].append(incvalue)
            else:
                incident_list[2].append(float(m.group('value').split('(')[1].split(')')[0]))


    names_list = []
    #LIST UNIQUE DRIVER NAMES INSIDE THE INCIDENTS_LIST
    for driver1 in incident_list[0]:
        names_list.append(driver1) #adiciona o nome do piloto
    for driver2 in incident_list[1]:
        names_list.append(driver2)
    names_set = set(names_list)


    #########################################################
    #Start defining the sum of incidents values for a driver
    #Summing the Incident values into driver's object in database
    #It's important to set up the parameters before running the code
    ###########--------PARAMETERS---------#############
    max_incidents = float(16) #Max log value for penalization
    startQR = float(10) #Start value of QualityRating. The value goes down
    rate_for_incidents = startQR/max_incidents #parameter that changes log values to QR values
    ###########--------PARAMETERS---------#############

    incident = float(0)
    print('...')
    #print(incident_list)
    #print(name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[0])
    for j in range(len(name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[0])):
        for i in range(len(incident_list[1])):

            if (name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[0][j] == incident_list[0][i]):
                if (incident_list[1][i] == 'Wing' or
                    incident_list[1][i] == 'Part' or
                    incident_list[1][i] == 'Wheel' or
                    incident_list[1][i] == 'Cone' or
                    incident_list[1][i] == 'Sign' or
                    incident_list[1][i] == 'Post'):
                    #incident_list[1][i] == 'Immovable' or
                    incident += 0
                elif incident_list[1][i] == 'Immovable':
                    incident += (incident_list[2][i]*0.7)
                else:
                    incident += incident_list[2][i]
                    
            if (name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[0][j] == incident_list[1][i]):
                incident += incident_list[2][i]
            #print(incident)
        st_id = name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[1][j]
        rated_incident = rate_for_incidents * incident
        #print(rated_incident, incident)
        inc_dict_list.append({'steamID':st_id, 'incidents': round(rated_incident, 2)})
        incident_sum.append(incident)
        incident = float(0)
    print('Session Incidents, Done!')
    print('------------------------')
    ###########################################################################
    #/////////////////////////////////////////////////////////////////////////#
    #HERE WE INCLUDE THE INCIDENTS POINTS FOR THE RACERESULT TABLE IN DATABASE#
    #/////////////////////////////////////////////////////////////////////////#
    ###########################################################################
    print('Putting all together into the Race Result...')
    for i in range(len(name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[0])):
        if not name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[3]:
            finalresult = {'position': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[2][i],
                           'driver': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[0][i],
                           'laps': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[4][i],
                           'steamID': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[1][i],
                           'userid': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[6][i],
                           'incidents': float(0),
                           'finishstatus': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[9][i],
                           'bestlap': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[7][i]
                           }
        else:
            finalresult = {'position': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[2][i],
                           'driver': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[0][i],
                           'laps': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[4][i],
                           'fulltime': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[5][i],
                           'steamID': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[1][i],
                           'userid': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[6][i],
                           'incidents': float(0),
                           'st_position': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[3][i],
                           'lapsled' : name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[8][i],
                           'finishstatus': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[9][i],
                           'bestlap': name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[7][i]
                           }
        for incident_dict in inc_dict_list:
            if (finalresult['steamID'] == incident_dict['steamID']):
                finalresult['incidents'] = incident_dict['incidents']
        finalresultlist.append(finalresult)
    ##########################
    #CREATING PLAYER INSIDE DB IF IT DOESNOT EXISTS!
    ##########################
    print('Creating player into db if it doesnt exist...')
    c_images = db.Classimages.find_one()
    for i in range(len(steamidlist[0])):
        driver_id = steamidlist[0][i]
        name = steamidlist[1][i]
        if (driver_id != '0'):
            if (db.Drivers.count_documents({'steamID': driver_id}) == 0):
                namesdict = {}
                namesdict['unique_name'] = name
                namesdict['races_done'] = 0
                namesdict['steamID'] = driver_id
                rating = Rating()
                rating_dict = {'mu': rating.mu, 'sigma': rating.sigma}
                namesdict['rating'] = rating_dict
                namesdict['points'] = 'TBD'
                namesdict['top10'] = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, 
                         '6': 0, '7': 0, '8': 0, '9': 0, '10':0}
                namesdict['penalized'] = False
                namesdict['incidents'] = 0
                namesdict['classimg'] = c_images['not_ranked']
                namesdict['pole'] = 0
                namesdict['votes'] = 0
                db.Drivers.insert_one(namesdict)
            #CREATING DRIVER DICT IN THE SEASONAL DRIVERS DB
            if (db.SeasonDrivers.count_documents({'steamID': driver_id}) == 0):
                seasonnamesdict = {}
                seasonnamesdict['unique_name'] = name
                seasonnamesdict['races_done'] = 0
                seasonnamesdict['steamID'] = driver_id
                seasonrating = Rating()
                seasonrating_dict = {'mu': seasonrating.mu, 'sigma': seasonrating.sigma}
                seasonnamesdict['rating'] = seasonrating_dict
                seasonnamesdict['points'] = 'TBD'
                seasonnamesdict['top10'] = {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, 
                         '6': 0, '7': 0, '8': 0, '9': 0, '10':0}
                seasonnamesdict['penalized'] = False
                seasonnamesdict['incidents'] = 0
                seasonnamesdict['classimg'] = c_images['not_ranked']
                seasonnamesdict['pole'] = 0
                seasonnamesdict['votes'] = 0
                db.SeasonDrivers.insert_one(seasonnamesdict)
    ###################################
    #SAVING THE DATA TO THE RIGHT KEY IN DICTIONARY
    ###################################
    
    
    if file.endswith('P1.xml'):
        tableDict['practice'] = finalresultlist
    elif file.endswith('Q1.xml'):
        tableDict['qualify'] = finalresultlist
    elif file.endswith('R1.xml'):
        tableDict['race'] = finalresultlist

    else:
        tableDict['TBD'] = finalresultlist
        
        
    #### UPDATING THE Top5, POLES, Top10, etc directly in DB ####
    if 'race' in tableDict and schedrace['official'] == True:
        while True:
            try:
                for i in range(len(steamidlist[0])):
                    steamID = steamidlist[0][i]
                    #print(steamID)
                    if (db.RaceResult.count_documents({'racefilename': file}) == 0):
                        update = db.Drivers.update_one({'steamID': steamID},
                                               {'$inc': {'races_done': 1,
                                                         'races_15': 1}})
                    if (db.RaceResult.count_documents({'racefilename': file}) == 0):
                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                               {'$inc': {'races_done': 1,
                                                         'races_15': 1}})
                        #print(db.Drivers.find_one({'steamID': steamID}))
                        for item in tableDict['race']:
                            if  item['steamID'] == steamID and item['steamID'] != 0:
                                if (item['st_position'] == '01'):
                                    update_pole = db.Drivers.update_one({'steamID': steamID},
                                                           {'$inc': {'pole': 1}})
                                if (int(item['position']) <= 10):
                                    if (int(item['position']) == 1):
                                        update = db.Drivers.update_one({'steamID': steamID},
                                                                            {'$inc': {'top10.1': 1}})
                                        #print('chegou em primeiro', item['driver'])
                                    if (int(item['position']) == 2):
                                        update = db.Drivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.2':1}})
                                        #print('chegou em segundo', item['driver'])
                                    if (int(item['position']) == 3):
                                        update = db.Drivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.3': 1}})
                                        #print('chegou em terceiro', item['driver'])
                                    if (int(item['position']) == 4):
                                        update = db.Drivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.4': 1}})
                                    if (int(item['position']) == 5):
                                        update = db.Drivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.5': 1}})
                                    if (int(item['position']) == 6):
                                        update = db.Drivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.6': 1}})
                                    if (int(item['position']) == 7):
                                        update = db.Drivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.7': 1}})
                                    if (int(item['position']) == 8):
                                        update = db.Drivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.8': 1}})
                                    if (int(item['position']) == 9):
                                        update = db.Drivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.9': 1}})
                                    if (int(item['position']) == 10):
                                        update = db.Drivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.10': 1}})
                                #Updating SEASON TOP5 and ETC
                    
                                if (item['st_position'] == '01'):
                                    update_pole = db.SeasonDrivers.update_one({'steamID': steamID},
                                                           {'$inc': {'pole': 1}})
                                if (int(item['position']) <= 10):
                                    if (int(item['position']) == 1):
                                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                                                            {'$inc': {'top10.1': 1}})
                                        #print('chegou em primeiro', item['driver'])
                                    if (int(item['position']) == 2):
                                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.2':1}})
                                        #print('chegou em segundo', item['driver'])
                                    if (int(item['position']) == 3):
                                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.3': 1}})
                                        #print('chegou em terceiro', item['driver'])
                                    if (int(item['position']) == 4):
                                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.4': 1}})
                                    if (int(item['position']) == 5):
                                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.5': 1}})
                                    if (int(item['position']) == 6):
                                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.6': 1}})
                                    if (int(item['position']) == 7):
                                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.7': 1}})
                                    if (int(item['position']) == 8):
                                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.8': 1}})
                                    if (int(item['position']) == 9):
                                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.9': 1}})
                                    if (int(item['position']) == 10):
                                        update = db.SeasonDrivers.update_one({'steamID': steamID},
                                                        {'$inc': {'top10.10': 1}})
                                
                                
            except Exception as e:
                print(str(e), 'Could not update Top5')
                time.sleep(30)
                continue
            print('Top5 and poles update done...')
            break
 
    ######## UPLOADING HISTORIC DATA TO INCIDENT HISTORIC DATABASES ###########
    if file.endswith('R1.xml') and schedrace['official'] == True:
        print('Starting to create historic data for the race')
        incident_historic_dict = {}
        incident_historic_list = []
        
        
        tableDict['racefilename'] = filename
        
        participants = schedrace['participants']
        if (db.RaceResult.count_documents({'racefilename': filename}) == 0):    
            for driver in rating_cursor:
                #print(driver)
                #print('----------------------------------------------------')
            
                incident_historic_dict['filename'] = filename
            
                for item in inc_dict_list:
                    drsteamid = item['steamID']
                    incident = item['incidents']
                    if (driver['steamID'] == drsteamid):
                        steamid = driver['steamID']
                        
                    
                        rating_cursor = db.Drivers.find()
                        incidentupdate = driver['incidents'] + incident
                        db.Drivers.update_one({'steamID': steamid}, {'$set': {'incidents': incidentupdate}})
                        if steamid != '0':
                            incident_historic_list.append({
                                    'steamID': steamid, 
                                    'incidents': incidentupdate,
                                    'raceincidents': incident})
        
            if (db.HistIncident.count_documents({'filename': filename}) == 0):
                incident_historic_dict['result'] = incident_historic_list
                db.HistIncident.insert_one(incident_historic_dict)
        
        #UPDATING HISTORIC SEASON DATA
        season_incident_historic_dict = {}
        season_incident_historic_list = []
        season_rating_cursor = db.SeasonDrivers.find()
        for driver in season_rating_cursor:
                #print(driver)
                #print('----------------------------------------------------')
            
                season_incident_historic_dict['filename'] = filename
            
                for item in inc_dict_list:
                    drsteamid = item['steamID']
                    incident = item['incidents']
                    if (driver['steamID'] == drsteamid):
                        steamid = driver['steamID']
                        
                    
                        season_rating_cursor = db.SeasonDrivers.find()
                        incidentupdate = driver['incidents'] + incident
                        db.SeasonDrivers.update_one({'steamID': steamid}, {'$set': {'incidents': incidentupdate}})
                        if steamid != '0':
                            season_incident_historic_list.append({
                                    'steamID': steamid, 
                                    'incidents': incidentupdate,
                                    'raceincidents': incident})
        
        if (db.SeasonHistIncident.count_documents({'filename': filename}) == 0):
            print('inserting doc to SeasonHistIncident')
            season_incident_historic_dict['result'] = season_incident_historic_list
            db.SeasonHistIncident.insert_one(season_incident_historic_dict)
                
    
    
    
   ##########################################################################
    # CREATING RATING VALUES
    tableDict['rated'] = False #Changes to true if the race is rated using the code below
    if file.endswith('R1.xml') and schedrace['official'] == True:
        print('Start ranking phase...')
        ratings = {}
        season_ratings = {}
        for i in range(len(tableDict['race'])):
            for key, val in tableDict['race'][i].items():            
                if (key == 'steamID'):
                    for d in db.Drivers.find({'steamID': val}):
                        mu = d['rating']['mu']
                        sigma = d['rating']['sigma']
                        ratings[val] = Rating(mu, sigma)
                    for dr in db.SeasonDrivers.find({'steamID': val}):
                        mu = dr['rating']['mu']
                        sigma = dr['rating']['sigma']
                        season_ratings[val] = Rating(mu, sigma)
                        
        #print('before')
        #print(ratings)
        
        
        
        #START UPDATING RATING FOR A RACE
        #print(db.RaceResult.count_documents({'filename': filename})==0, filename)
        
        if (db.RaceResult.count_documents({'filename': filename}) == 0):   
            print('Updating ranking...')
            participants = []
            not_participants = []
            for item in schedrace['participants']: #collect the registered participants of the race
                participants.append(item['steamid'])
            if (len(participants) < minimumplayers):
                print('The race ' + file + ' had only ' + str(len(participants)) + 'players, and will not be rated')
            else:
                tableDict['rated'] = True
        
            
            tableDict['race'] = finalresultlist
                
            results = []
            finalresult = tableDict['race']
            filename = tableDict['racefilename']
            result_tuple = ()
            for item in finalresult:
                result_tuple = (filename, item['steamID'], (int(item['position'])))
                print(result_tuple)
                if result_tuple[1] != '0' and result_tuple[1] in participants:
                    results.append(result_tuple)
                
                #pprint(dict(ratings))
            #pprint(results)
            
            try:
                for game_id, result in groupby(results, lambda x: x[0]):
                    result = list(result)
                    #pprint(game_id)
                    #pprint(result)
                    rating_groups = [(ratings[name],) for game_id, name, rank in result] #rating names for race X
                    season_rating_groups = [(season_ratings[name],) for game_id, name, rank in result]
                    #print(quality(rating_groups))
                    ranks = [rank for game_id, name, rank in result]
                    if len(rating_groups) >= minimumplayers:
                        new_rate = rate(rating_groups, ranks=ranks)
                        season_new_rate = rate(season_rating_groups, ranks=ranks)
                        for x, (game_id, name, rank) in enumerate(result):
                            ratings[name], = new_rate[x]
                            season_ratings[name], = season_new_rate[x]
                    
                #print('after')
                #print(ratings)
            
            #///RATING UPDATE///
                if file.endswith('R1.xml'):
                    historicdata = {}
                    historiclist = []
                    season_historicdata = {}
                    season_historiclist = []
                    historicdata['filename'] = filename
                    season_historicdata['filename'] = filename
                    season_rating_cursor = db.SeasonDrivers.find()
                    
                    #GLOBAL RATING UPDATE LOOP
                    for driver in rating_cursor:
                        while True:
                            try:
                                client = MongoClient("mongodb+srv://public:publicpassword@brazilavrank-2ccxo.mongodb.net/test") #EDIT THIS
                                db = client.ValleyAlliance
                                cursor = db.RaceResult.find()
                                rating_cursor = db.Drivers.find()
                                for rating in ratings.items():
                                    if (driver['steamID'] == rating[0]):
                                        if driver['steamID'] != '0': #ALL AI DRIVERS HAS STEAMID = 0
                                            
                                            dbdriver = db.Drivers.find_one({'steamID': rating[0]})
                                            if dbdriver['races_done'] > minimumraces:
                                                historiclist.append({'steamID': rating[0], 'mu': rating[1].mu, 'sigma': rating[1].sigma, 'points':rating[1].mu - 3*rating[1].sigma})
                                                update = db.Drivers.update_one({'steamID': rating[0]}, {'$set':
                                                    {'rating': {'mu': rating[1].mu, 'sigma': rating[1].sigma}, 
                                                    'points': rating[1].mu - 3*rating[1].sigma}})
                                            else:
                                                historiclist.append({'steamID': rating[0], 'mu': rating[1].mu, 'sigma': rating[1].sigma, 'points':0})
                                                update = db.Drivers.update_one({'steamID': rating[0]}, {'$set':
                                                    {'rating': {'mu': rating[1].mu, 'sigma': rating[1].sigma, 'points': 0} 
                                                    }})
                                break
                            except Exception as e:
                                print("Could not connect to database, trying again in " + str(sleep) + ' seconds!')
                                time.sleep(sleep)
                    
                    
                    #SEASON RATING UPDATE LOOP
                    for driver in season_rating_cursor:
                        while True:
                            try:
                                client = MongoClient("mongodb+srv://public:publicpassword@brazilavrank-2ccxo.mongodb.net/test") #EDIT THIS
                                db = client.ValleyAlliance
                                cursor = db.RaceResult.find()
                                season_rating_cursor = db.SeasonDrivers.find()
                                for rating in season_ratings.items():
                                    if (driver['steamID'] == rating[0]):
                                        if driver['steamID'] != '0': #ALL AI DRIVERS HAS STEAMID = 0
                                            
                                            dbdriver = db.SeasonDrivers.find_one({'steamID': rating[0]})
                                            if dbdriver['races_done'] > minimumraces:
                                                season_historiclist.append({'steamID': rating[0], 'mu': rating[1].mu, 'sigma': rating[1].sigma, 'points':rating[1].mu - 3*rating[1].sigma})
                                                update = db.SeasonDrivers.update_one({'steamID': rating[0]}, {'$set':
                                                    {'rating': {'mu': rating[1].mu, 'sigma': rating[1].sigma}, 
                                                    'points': rating[1].mu - 3*rating[1].sigma}})
                                            else:
                                                season_historiclist.append({'steamID': rating[0], 'mu': rating[1].mu, 'sigma': rating[1].sigma, 'points':0})
                                                season_update = db.SeasonDrivers.update_one({'steamID': rating[0]}, {'$set':
                                                    {'rating': {'mu': rating[1].mu, 'sigma': rating[1].sigma, 'points': 0} 
                                                    }})
                                break
                            except Exception as e:
                                print("Could not connect to database, trying again in " + str(sleep) + ' seconds!')
                                time.sleep(sleep)
                    
                historicdata['result'] = historiclist 
                season_historicdata['result'] = season_historiclist
                db.HistRating.insert_one(historicdata)
                db.SeasonHistRating.insert_one(season_historicdata)
                print('Ranking DONE!')
            except Exception as e:
                print('rating error', str(e))
    else:
        print('The race is not an official race and will not be rated')
    
    if file.endswith('R1.xml'):
        print('updating the classes')
        try:
            drivers = db.Drivers.find().sort([('points', 1)])
            c_images = db.Classimages.find_one()
            
            driverList = []
            for driver in drivers:
                #print(driver['steamID'])
                
                #pprint(driver)
                if driver['races_done'] == 0:
                    incidents = 0
                else:
                    incidents = round(driver['incidents'] / driver['races_done'])
                if driver['points'] == 'TBD':
                    driverItem = {
                            'steamid': driver['steamID'],
                            'points': float(0),
                            'incidents': incidents,
                            'races': driver['races_done'],
                            'classimg': driver['classimg']
                            }
                elif int(driver['points']) <= 0:
                    driverItem = {
                            'steamid': driver['steamID'],
                            'points': float(0),
                            'incidents': incidents,
                            'races': driver['races_done'],
                            'classimg': driver['classimg']
                            }
                else:
                    if driver['races_done'] < 4:
                        driverItem = {
                            'steamid': driver['steamID'],
                            'points': float(0),
                            'incidents': incidents,
                            'races': driver['races_done'],
                            'classimg': driver['classimg']
                            }
                    else:
                        driverItem = {
                            'steamid': driver['steamID'],
                            'points': round(driver['points'], 3) * 1000,
                            'incidents': incidents,
                            'races': driver['races_done'],
                            'classimg': driver['classimg']
                            }
                    
                    
                driverList.append(driverItem)
                if type(driver['points']) != str:
                    if (driver['points'] < 0):
                        db.Drivers.update_one({
                                'steamID': driver['steamID']}, {'$set': {'points': 0}})
                            
                
            
            sortdriverList = sorted(driverList, key=itemgetter('points'), reverse=True)
            totaldrivers = len(sortdriverList) + 1
            #pprint(driverList)
            #print(driverList, sortdriverList)
            
             
            
            before_positions = db.HistRank.find().sort([('_id', -1)])[0]['positions']
            positions = {'filename': file,
                         'positions': []}
            for item in driverList:
                if (item['races'] > 4):
                    #print(item)
                    item['classimg'] = ''
                    db.Drivers.update_one({'steamID': item['steamid']}, {'$set': {'classimg': ''}})
                else:
                    item['points'] = 0
                    item['classimg'] = c_images['not_ranked']
                    db.Drivers.update_one({'steamID': item['steamid']}, {'$set': {'classimg': c_images['not_ranked']}})
       
            for i in range(len(sortdriverList)):
                #print(i)
                if (sortdriverList[i]['classimg'] != c_images['not_ranked']):
                    if (0 <= i <= 15):
                        print(i, 'CHAMPION')
                        db.Drivers.update_one({
                            'steamID': sortdriverList[i]['steamid']}, {'$set': {'classimg': c_images['champion'],
                                                                                 'rank_pos': int(i+1)}})
                        for points in before_positions:
                            delta = 0
                            if points['steamID'] == sortdriverList[i]['steamid']:
                                delta = sortdriverList[i]['points'] - points['points'] 
                            
                            
                        positions['positions'].append({'steamID': sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': sortdriverList[i]['points'],
                                                         'delta': delta})
                            
                    elif (15 < i <= 31): 
                        print(i, 'CHALLENGER')
                        db.Drivers.update_one({
                            'steamID': sortdriverList[i]['steamid']}, {'$set': {'classimg': c_images['challenger'],
                                                                                 'rank_pos': int(i+1)}})
                        for points in before_positions:
                            delta = 0
                            if points['steamID'] == sortdriverList[i]['steamid']:
                                delta = sortdriverList[i]['points'] - points['points'] 
                            
                            
                        positions['positions'].append({'steamID': sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': sortdriverList[i]['points'],
                                                         'delta': delta})
                    else:
                        if int(sortdriverList[i]['points']) >= 19000:
                            print(i, 'JUNIOR')
                            db.Drivers.update_one({
                            'steamID': sortdriverList[i]['steamid']}, {'$set': {'classimg': c_images['junior'],
                                                                                 'rank_pos': int(i+1)}})
                            for points in before_positions:
                                delta = 0
                                if points['steamID'] == sortdriverList[i]['steamid']:
                                    delta = sortdriverList[i]['points'] - points['points'] 
                            
                            
                            positions['positions'].append({'steamID': sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': sortdriverList[i]['points'],
                                                         'delta': delta})
                        elif 19000 > int(sortdriverList[i]['points']) >= 15000:
                            print(i, 'AMATEUR')
                            db.Drivers.update_one({
                            'steamID': sortdriverList[i]['steamid']}, {'$set': {'classimg': c_images['amateur'],
                                                                                 'rank_pos': int(i+1)}})
                            for points in before_positions:
                                delta = 0
                                if points['steamID'] == sortdriverList[i]['steamid']:
                                    delta = sortdriverList[i]['points'] - points['points'] 
                            
                            
                            positions['positions'].append({'steamID': sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': sortdriverList[i]['points'],
                                                         'delta': delta})
                        elif 15000 > int(sortdriverList[i]['points']):
                            print(i, 'APPRENTICE')
                            db.Drivers.update_one({
                            'steamID': sortdriverList[i]['steamid']}, {'$set': {'classimg': c_images['apprentice'],
                                                                                 'rank_pos': int(i+1)}})
                            for points in before_positions:
                                delta = 0
                                if points['steamID'] == sortdriverList[i]['steamid']:
                                    delta = sortdriverList[i]['points'] - points['points'] 
                            
                            
                            positions['positions'].append({'steamID': sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': sortdriverList[i]['points'],
                                                         'delta': delta})
                                
    
                
                        else:
                            db.Drivers.update_one({
                                        'steamID': sortdriverList[i]['steamid']}, {'$set': {'points': 0,
                                                                                         'rank_pos': int(i+1)}})
                            positions['positions'].append({'steamID': sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': sortdriverList[i]['points'],
                                                         'delta': delta})
            if schedrace['official'] == True:
                db.HistRank.insert_one(positions)
                
                   
        except Exception as e:
            print('error','sortdriverList', str(e))
        
        #SEASON CLASSES UPDATE
        try:
            season_drivers = db.SeasonDrivers.find().sort([('points', 1)])
            
            season_driverList = []
            for sdriver in season_drivers:
                #print(driver['steamID'])
                
                #pprint(driver)
                if sdriver['races_done'] == 0:
                    incidents = 0
                else:
                    incidents = round(sdriver['incidents'] / sdriver['races_done'])
                if sdriver['points'] == 'TBD':
                    driverItem = {
                            'steamid': sdriver['steamID'],
                            'points': float(0),
                            'incidents': incidents,
                            'races': sdriver['races_done'],
                            'classimg': driver['classimg']
                            }
                elif int(driver['points']) <= 0:
                    driverItem = {
                            'steamid': sdriver['steamID'],
                            'points': float(0),
                            'incidents': incidents,
                            'races': sdriver['races_done'],
                            'classimg': sdriver['classimg']
                            }
                else:
                    if driver['races_done'] < 4:
                        driverItem = {
                            'steamid': sdriver['steamID'],
                            'points': float(0),
                            'incidents': incidents,
                            'races': sdriver['races_done'],
                            'classimg': sdriver['classimg']
                            }
                    else:
                        driverItem = {
                            'steamid': sdriver['steamID'],
                            'points': round(sdriver['points'], 3) * 1000,
                            'incidents': incidents,
                            'races': sdriver['races_done'],
                            'classimg': sdriver['classimg']
                            }
                    
                    
                
                if type(sdriver['points']) != str:
                    if (sdriver['points'] < 0):
                        db.SeasonDrivers.update_one({
                                'steamID': sdriver['steamID']}, {'$set': {'points': 0}})
                season_driverList.append(driverItem)
            
            season_sortdriverList = sorted(season_driverList, key=itemgetter('points'), reverse=True)
            totaldrivers = len(season_sortdriverList) + 1
            #pprint(driverList)
            #print(driverList, sortdriverList)
            
            positions = {'filename': file,
                         'positions': []}
            
            print("SEASON POSITIONS")
            for item in season_driverList:
                if (item['races'] > 4):
                    #print(item)
                    item['classimg'] = ''
                    db.SeasonDrivers.update_one({'steamID': item['steamid']}, {'$set': {'classimg': ''}})
                else:
                    item['points'] = 0
                    item['classimg'] = c_images['not_ranked']
                    db.SeasonDrivers.update_one({'steamID': item['steamid']}, {'$set': {'classimg': c_images['not_ranked']}})
                 
            for i in range(len(season_sortdriverList)):
                #print(i)
                if (season_sortdriverList[i]['classimg'] != c_images['not_ranked']):
                    if (0 <= i <= 15):
                        print(i, 'CHAMPION')
                        db.SeasonDrivers.update_one({
                            'steamID': season_sortdriverList[i]['steamid']}, {'$set': {'classimg': c_images['champion'],
                                                                                 'rank_pos': int(i+1)}})
                        positions['positions'].append({'steamID': season_sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': season_sortdriverList[i]['points']})
                            
                    elif (15 < i <= 31): 
                        print(i, 'CHALLENGER')
                        db.SeasonDrivers.update_one({
                            'steamID': season_sortdriverList[i]['steamid']}, {'$set': {'classimg': c_images['challenger'],
                                                                                 'rank_pos': int(i+1)}})
                        positions['positions'].append({'steamID': season_sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': season_sortdriverList[i]['points']})
                    else:
                        if int(season_sortdriverList[i]['points']) >= 19000:
                            print(i, 'JUNIOR')
                            db.SeasonDrivers.update_one({
                            'steamID': season_sortdriverList[i]['steamid']}, {'$set': {'classimg': c_images['junior'],
                                                                                 'rank_pos': int(i+1)}})
                            positions['positions'].append({'steamID': season_sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': season_sortdriverList[i]['points']})
                        elif 19000 > int(season_sortdriverList[i]['points']) >= 15000:
                            print(i, 'AMATEUR')
                            db.SeasonDrivers.update_one({
                            'steamID': season_sortdriverList[i]['steamid']}, {'$set': {'classimg': c_images['amateur'],
                                                                                 'rank_pos': int(i+1)}})
                            positions['positions'].append({'steamID': season_sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': season_sortdriverList[i]['points']})
                        elif 15000 > int(season_sortdriverList[i]['points']):
                            print(i, 'APPRENTICE')
                            db.SeasonDrivers.update_one({
                            'steamID': season_sortdriverList[i]['steamid']}, {'$set': {'classimg': c_images['apprentice'],
                                                                                 'rank_pos': int(i+1)}})
                            positions['positions'].append({'steamID': season_sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': season_sortdriverList[i]['points']})
                                
    
                
                else:
                    db.SeasonDrivers.update_one({
                                'steamID': season_sortdriverList[i]['steamid']}, {'$set': {'points': 0,
                                                                                 'rank_pos': int(i+1)}})
                    positions['positions'].append({'steamID': season_sortdriverList[i]['steamid'],
                                                         'rank_pos': int(i+1),
                                                         'points': season_sortdriverList[i]['points']})
            if schedrace['official'] == True:
                db.SeasonHistRank.insert_one(positions)
                
                   
        except Exception as e:
            print('error','sortdriverList', str(e))
        
        #Calculate Incident Average of the last 5 races
        
        if schedrace['official'] == True:
            print('Calculating Incident Average for last 5 races!')
            for stid in name_id_pos_stpos_laplist_fulltime_userid_bestlap_lapsled_finishstat_content[1]:
               
                #print(stid)    
                histinc = db.HistIncident.find({'result.steamID':stid}).sort([('filename', DESCENDING)])
                season_histinc = db.SeasonHistIncident.find({'result.steamID':stid}).sort([('filename', DESCENDING)])
                #for item in histinc:
                    #for result in item['result']:
                        #if result['steamID'] == stid:
                           # print(result)
                c = 0
                sc = 0
                season_average = float(0)
                average = float(0)
                for i in histinc:
                    for j in i['result']:
                        if stid == j['steamID']:
                            if c < 5:
                                average += float(j['raceincidents'])
                                #print(stid, average, c)
                                c += 1
                
                for i in season_histinc:
                    for j in i['result']:
                        if stid == j['steamID']:
                            if c < 5:
                                season_average += float(j['raceincidents'])
                                #print(stid, average, c)
                                sc += 1
                                        
                try:
                    races_done = db.Drivers.find_one({'steamID': stid})['races_done']
                    #print(races_done)
                except: 
                    races_done = 0
                try:
                    season_races_done = db.SeasonDrivers.find_one({'steamID': stid})['races_done']
                except:
                    season_races_done = 0
                    #print('exc', races_done)
                if races_done == 0:
                    average = 0
                elif 0 < races_done < 4:
                    if average > 0:
                        average = average/races_done
                else:
                    if average > 0:
                        average = average/5
                
                if season_races_done == 0:
                    average = 0
                elif 0 < races_done < 4:
                    if average > 0:
                        average = average/season_races_done
                else:
                    if season_average > 0:
                        season_average = season_average/5
                
                #print(races_done, average, stid)
                db.Drivers.update_one({'steamID':stid}, {'$set': {'incident_ave': average}})
                db.SeasonDrivers.update_one({'steamID':stid}, {'$set': {'incident_ave': average}})
        
    #Delete Drivers documents IF user account does not exist!
    if file.endswith('R1.xml'):
        driver_cursor = db.Drivers.find()
        user_cursor = dbusers.users.find()
        for driver in driver_cursor:
            if not dbusers.users.find_one({'steam_id': driver['steamID']}):
                db.Drivers.delete_one({'steamID': driver['steamID']})
                db.HistIncident.update_one({'filename': file}, {'$pull': {
                        'result': {'steamID': driver['steamID']}}})
                db.HistRating.update_one({'filename': file}, {'$pull': {
                        'result': {'steamID': driver['steamID']}}})
                db.HistRank.update_one({'filename': file}, {'$pull': {
                        'result': {'steamID': driver['steamID']}}})
                
    #Delete Season Drivers documents IF user account does not exist!
    if file.endswith('R1.xml'):
        season_driver_cursor = db.SeasonDrivers.find()
        user_cursor = dbusers.users.find()
        for driver in season_driver_cursor:
            if not dbusers.users.find_one({'steam_id': driver['steamID']}):
                db.SeasonDrivers.delete_one({'steamID': driver['steamID']})
                db.SeasonHistIncident.update_one({'filename': file}, {'$pull': {
                        'result': {'steamID': driver['steamID']}}})
                db.SeasonHistRating.update_one({'filename': file}, {'$pull': {
                        'result': {'steamID': driver['steamID']}}})
                db.SeasonHistRank.update_one({'filename': file}, {'$pull': {
                        'result': {'steamID': driver['steamID']}}})
            
            
    
    
    #FINISH EVERYTHING
    f.close()
    print('This session parsing is Done')
    return tableDict
                    
                
                #print('FINISHED DRIVER UPDATE')
                #print('----------------------------------------------')
    

def update_records():
    while True:
        try:
            print('-------------------------------')
            print('Starting to Update the track records')
            dbusers = client.users
                
            raceresults = db.RaceResult.find()
            
            print('Querying results from database')
            for item in raceresults: #itera em cada resultado
                racerecord = {}
                racerecord['lap'] = {}
                racerecord['track'] = item['srvsettings']['tracks']
                racerecord['car'] = item['srvsettings']['cars']
                if item['rated']: #se o resultado tiver sido rankeado
                    race = item['race']
                    racerecord['resultid'] = item['_id']
                    for result in race: #itera em cada piloto presente no resultado
                        laps = result['laps']
                        for lap in laps: #itera em cada volta do piloto
                            if lap['bestlap']: #vê se foi a melhor volta do piloto na corrida
                                steamID = result['steamID']
                                userid = result['userid']
                                s1 = lap['s1']
                                s2 = lap['s2']
                                s3 = lap['s3']
                                laptime = lap['laptime']
                                racedate = (item['srvsettings']['date']+' '+item['srvsettings']['time'])
                                #start comparing to other in the same race
                                if userid != '':
                                    user = dbusers.users.find_one({'_id':userid})
                                    username = user['username']
                                    if 'laptime' not in racerecord['lap']: #se não houver voltas no json de record
                                        racerecord['lap'] = {
                                        'racedate' :racedate,
                                        's1': s1,
                                        's2': s2,
                                        's3': s3,
                                        'laptime': laptime,
                                        'steamID': steamID,
                                        'userid': userid,
                                        'username': username}
                                    elif laptime < racerecord['lap']['laptime']: #tem volta, mas a volta da iteração é melhor que a volta salva
                                        racerecord['lap'] = {
                                        'racedate' :racedate,
                                        's1': s1,
                                        's2': s2,
                                        's3': s3,
                                        'laptime': laptime,
                                        'steamID': steamID,
                                        'userid': userid,
                                        'username': username}
                                else:
                                    continue
                    
                    if db.RaceRecord.count_documents({'car': racerecord['car'],
                                          'track': racerecord['track']}) > 0: #Tem record salvo no DB
                        #print(racerecord['car'], racerecord['track'])
                        record  = db.RaceRecord.find_one({'car': racerecord['car'],
                                                          'track': racerecord['track']})
                        if racerecord['lap']['laptime'] < record['laprecord'][len(record['laprecord'])-1]['laptime']:
                                    record['laprecord'].append(racerecord['lap'])
                                    #print(record['laprecord'])
                                    db.RaceRecord.update_one({
                                            '_id': record['_id']},
                                            {
                                            '$set':{
                                                    'laprecord': record['laprecord']}})
                                    print('A new record has been stabilished by ' + racerecord['username'])
                        
                                            
                            
                    else: #não tem record salvo no db
                        db.RaceRecord.insert_one({
                                
                                'car': racerecord['car'],
                                'track': racerecord['track'],
                                'laprecord': [racerecord['lap']],
                                'resultid': racerecord['resultid']
                                
                                })
            print('Updating the Records -- DONE!')
            break
        except Exception as e:
            print('Something Went wrong while updating Records! We will try again in 20 seconds')
            print(str(e))
            time.sleep(20)
#########################
#################################
#########################################
##############################
#################
#######
#


while True:
    sleep = 60
    try:
        if db.ScheduledRace.find_one():
            race = db.ScheduledRace.find().sort([('timestamp', ASCENDING)])[0]
            done = race['Done']
        else:
            done = True
    except Exception as e:
        while True:
            try:
                done = None
                client = MongoClient("mongodb+srv://public:publicpassword@brazilavrank-2ccxo.mongodb.net/test") #EDIT THIS
                db = client.ValleyAlliance
                dbusers = client.users
                cursor = db.RaceResult.find()
                rating_cursor = db.Drivers.find()
                print(str(e))
                print('1 Connection to database timed out...trying again in ' + str(sleep) + ' seconds')
                break
            except Exception as e:
                print(str(e))
    if done == True:
        print('Please schedule a new race!')
        time.sleep(sleep)
    while done == False:
        while True:
            try:
                race = db.ScheduledRace.find().sort([('timestamp', ASCENDING)])[0]
                agenda_time = datetime.strptime(race['date'] + ' ' + race['time'], '%d-%m-%Y %H:%M')
                now = datetime.now()
                print('Race is Schedule. Server will open at ' + agenda_time.ctime())
                print('Local time is ' + now.ctime())
                print('-'*20)
                break
            except Exception as e:
                print(str(e))
                print('2 Connection to database timed out...trying again in ' + str(sleep) + ' seconds')
                try:
                    client = MongoClient("mongodb+srv://public:publicpassword@brazilavrank-2ccxo.mongodb.net/test") #EDIT THIS
                    db = client.ValleyAlliance
                    dbusers = client.users
                    cursor = db.RaceResult.find()
                    rating_cursor = db.Drivers.find()
                except Exception as e:
                    print(str(e))
                    print('3 Connection to database timed out...trying again in '+ str(sleep) + ' seconds')
                time.sleep(sleep)
        if agenda_time - timedelta(seconds=(sleep/2)) <= now  :
            print('start', datetime.now().ctime())
            serverconfig(race)
            try:
                server = subprocess.Popen('AMS Dedicated.exe +profile "DedicatedServer" +oneclick' )
                db.ScheduledRace.update_one({'_id': race['_id']}, {'$set': {'Started': True, 'Online': True}})
            except Exception as e:
                print(e)
                print('4 Connection to database timed out...trying again in '+ str(sleep) + ' seconds')
                
                
            while server:
            #while True:
                #time.sleep(1)
                race = db.ScheduledRace.find_one({'_id': ObjectId(race['_id'])})
                if race['Close'] == True:
                    try:
                        server.terminate()
                        print('finish', datetime.now().ctime())
                        server = None
                        db.ScheduledRace.delete_one({'_id': ObjectId(race['_id'])})
                        if db.ScheduledRace.find_one():
                            race = db.ScheduledRace.find().sort([('timestamp', ASCENDING)])[0]
                            done = race['Done']
                        else: 
                            done = True
                    except Exception as e:
                        print(str(e))
                        print('error while closing the SERVER. Line: 2048')
                        time.sleep(sleep/2)
                        
                after = dict([(f, None) for f in os.listdir(path_to_watch)])
                new = [f for f in after if not f in before]
                if new:
                    print(new)
                for file in new:
                    if file.endswith('P1.xml'):
                        while True:
                            try:
                                before = after
                                tableDict = xmlparser(file)
                                race = db.ScheduleRace.find_one({'_id': ObjectId(race['_id'])})
                                
                                break
                            except Exception as e:
                                print(str(e))
                                print('P1 - Connection to database timed out...trying again in ' + str(sleep/2) + ' seconds')
                                time.sleep(sleep/2)
                                
                            
                        
    #############################################################################################
    #////////////////////////////////////////////////////////////////////////////////////////////
    #############################################################################################
    
                    if file.endswith('Q1.xml'):
                        while True:
                            try:
                                tableDict = {**tableDict, **xmlparser(file)}
                                before = after
                                break
                            except Exception as e:
                                print(str(e))
                                print('Q1 - Connection to database timed out...trying again in ' + str(sleep/2) + ' seconds')
                                time.sleep(sleep/2)
                        
                        
    
    #############################################################################################
    #////////////////////////////////////////////////////////////////////////////////////////////
    #############################################################################################
    
                    if file.endswith('R1.xml'):
                        while True:
                            try:
                                before = after
                                time.sleep(30)
                                server.terminate()
                                server = None
                                
                                tableDict = {**tableDict, **xmlparser(file)}
                                tableDict['srvsettings'] = race
                                db.ScheduledRace.delete_one({'_id':race['_id']})
                                if db.ScheduledRace.find_one():
                                    race = db.ScheduledRace.find().sort([('timestamp', ASCENDING)])[0]
                                    done = race['Done']
                                else: 
                                    done = True
                                print('finish', datetime.now().ctime())
                                if 'race' in tableDict:
                                    db.RaceResult.insert_one(tableDict)
                                    nextracetime = datetime.utcfromtimestamp(race['timestamp']) - datetime.now()
                                    nextracetimetup = divmod(nextracetime.days * 86400 + nextracetime.seconds, 60)
                                    if nextracetimetup <= (60, 0):
                                        update_records()
                                    break                                     
                            except Exception as e:
                                print(str(e))
                                print('R1 - Connection to database timed out...trying again in ' + str(sleep/2) + ' seconds')
                                time.sleep(sleep/2)
                    
                    

        else:
            time.sleep(sleep)
                
    
    

