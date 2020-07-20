import os
import os.path as pathChecker
import shutil
 # GUI
import tkinter as tk
import tkinter.font as tkFont
import tkinter.messagebox as msgBox
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilenames
 # Threading
import threading
 # Pausing
import time
 


 ### - Constants - ###

WIDTH = 400
HEIGHT = 700
TITLE = "Playlist Sync"

LINES_THICKNESS = 2
BUTTON_BG_COLOUR = "#7ec7d2"
BUTTON_FG_COLOUR = "#424242"
BUTTON_FONT = "Helvetica 10"
SYNC_BUTTON_FONT = "Helvetica 16"
TEXTBOX_FONT_NORMAL = "Helvetica 9"
TEXTBOX_FONT_NEW = "Helvetica 10 bold"

BEFORE_SYNC_DELAY = 0.5
AFTER_SYNC_PLAYLIST_DELAY = 0.5


 ### - Data - ###

playlistPathsList = []



 ### - Functions - ###

 # Load when open program
def loadData():
      # IF save file exists, load
     if pathChecker.exists( "Files/SavedData.csv" ):
           # Get save file and its lines
          f = open( "Files/SavedData.csv", "r" )
          lines = f.readlines()
          for i in range( len(lines) ):
               line = lines[i].strip()
                # Get Get first line to load destination/device
               if i == 0:
                    destinationEntry.insert( 0, line )
                # Get rest to load playlists
               else:
                    playlistsListbox.insert( "end", line[ line.rfind('/') + 1 : -4 ] )
                    playlistPathsList.append( line )
                    



 # Save when close program
def saveData():
      # IF 'Files' directory doesn't exist, create and make hidden
     if not pathChecker.exists( "Files/" ):
          os.mkdir( "Files/" )
      # Open 'SavedData.csv'
     f = open( "Files/SavedData.csv", "w" )
      # Write destination/device
     f.write( destinationEntry.get() + "\n" )
      # Write each playlist
     for playlist in playlistPathsList:
          f.write( playlist + "\n"  )
      # Close 'SavedData.csv' and make hidden
     f.close()

 # Method run before application closes
def onClosing():
     saveData()
     root.destroy()
 
 # To insert log information for each output box
def outputBoxUpdate( inBox, inText ):
      # Unlock box
     inBox.config( state = "normal" )
      # Insert text
     inBox.insert( tk.INSERT, inText )
      # Delete old tag, make new tag for newly added line
     inBox.tag_delete( "lastLineBold" )
     inBox.tag_add( "lastLineBold", "insert linestart", "insert lineend" )
     inBox.tag_config( "lastLineBold", font = TEXTBOX_FONT_NEW )
      # Lock text and scroll to bottom
     inBox.config( state = "disabled" )
     inBox.see( "end" )

def outputBoxUpdateLast( inBox, inText ):
      # Unlock box
     inBox.config( state = "normal" )
      # Delete last line
     inBox.delete( "end-1c linestart", "end" )
      # Insert new text
     outputBoxUpdate( inBox, inText )
     

def outputBoxReset( inBox, inText ):
     inBox.config( state = "normal" )
     inBox.delete( "1.0", "end" )
     outputBoxUpdate( inBox, inText )
     inBox.config( state = "disabled" )


 # Lock/Unlock all widgets
def setWdigetsState( inState ):
     destinationEntry['state'] = inState
     chooseDestButton['state'] = inState
     playlistsListbox['state'] = inState
     addPlaylistButton['state'] = inState
     removePlaylistButton['state'] = inState
     syncButton['state'] = inState



 ### - Button Functions - ###


 # User selects destination folder
def chooseDestination():
      # Prompt choose folder
     path = askdirectory( title = 'Select Folder' )
      # IF NOT click cancel, set to entry
     if not path == "":
          destinationEntry.delete( 0, "end" )
          destinationEntry.insert( 0, path ) 


 # Add playlist to list of playlists to be synced
def addPlaylist():
     # User selects one or more playlists
     playlistSelections = askopenfilenames (
                                                  title='select', 
                                                  filetypes = [ ("M3U playlist", ".m3u") ]
                                        )
     # FOR EACH playlist selected, add title to playlistsListBox and save full path to pathsList
     for playlistPath in playlistSelections:
          # IF playlist already exists, error
          if playlistPath in playlistPathsList:
               msgBox.showwarning( "Oops!", "Playlist already exists in your selections!" )
          # ELSE add playlist
          else:
               playlistsListbox.insert( "end", playlistPath[ playlistPath.rfind('/') + 1 : -4 ] )
               playlistPathsList.append( playlistPath )


 # Remove playlist from list of playlists to be synced
def removePlaylist():
     # Remove from array of playlist paths (as only one selection can be made, get first selction from tuple)
     playlistPathsList.pop( playlistsListbox.curselection()[0] )
     # Remove from Listbox (do this after getting the listbox selection)
     playlistsListbox.delete( playlistsListbox.curselection() )


 # So 'Sync' runs in separate thread so text boxes update properly
def syncThread():
     tempThread = threading.Thread( target = sync )
     tempThread.daemon = True
     tempThread.start()

 # Sync selected playlists to selected destination
def sync():

      # Variables
     destPath = destinationEntry.get()

      # IF destination doesn't exist, error
     if not pathChecker.exists( destPath ):
          msgBox.showwarning( "Oops!", "Destination/device does not exist!\nThe folder may not exist, or the device is not connected." )
      # ELSE sync

     else:

           # Set syncButton text
          syncButton.configure( text = "Syncing..." )

           # Lock all widgets
          setWdigetsState( "disabled" )

          # Reset output boxes
          outputBoxReset( playlistsOutputBox, "|| Playlists ||")
          outputBoxReset( songsOutputBox, "|| Songs ||" )

          # Wait a second before start
          time.sleep( BEFORE_SYNC_DELAY )

          # For each playlist, sync
          for origPlaylistPath in playlistPathsList:

               try:

                    # Get playlist name
                    playlistName = origPlaylistPath[ origPlaylistPath.rfind('/') + 1 : -4 ]
                    # Update output boxes
                    outputBoxUpdate( playlistsOutputBox, "\n= = = = = =\nSyncing:\n" + playlistName )
                    outputBoxUpdate( songsOutputBox, "\n= = = = = =" )

                    # IF destination doesn't have folder, create it (then only does 'addSongs', 'removeSongs' doesn't do anything)
                    destPlaylistFolder = destPath + "/" + playlistName
                    if not pathChecker.exists( destPlaylistFolder ):
                         os.mkdir( destPlaylistFolder )

                    # Remove any songs deleted from original (remove first, just incase error in removing, at least all added afterwards)
                    removeSongs( origPlaylistPath, destPlaylistFolder )
                    # Add any songs that aren't at destination
                    addSongs( origPlaylistPath, destPlaylistFolder )

               except UnicodeDecodeError:
                    outputBoxUpdate( playlistsOutputBox, "\nPlaylist name contains bad characters!" )
                    time.sleep( 2 )
               except FileNotFoundError:
                    outputBoxUpdate( playlistsOutputBox, "\nPlaylist not found!" )
                    time.sleep( 2 )



          outputBoxUpdate( playlistsOutputBox, "\n= = = = = =\n|| All done! ||" )
          outputBoxUpdate( songsOutputBox, "\n= = = = = =\n|| All done! ||" )

           # Unlock all widgets
          setWdigetsState( "normal" )

           # Reset syncButton text
          syncButton.configure( text = "Sync" )



 # Remove any songs that aren't in playlist
def removeSongs( inOriginalPlaylist, inDestFolder ):

      # Variables
     numRemovedSongs = 0

      # Output box
     outputBoxUpdate( songsOutputBox, "\nRemoving..." )
     time.sleep( 0.5 )

      # Get original playlists' lines/songs
     originalPlaylist = open( inOriginalPlaylist, "r", encoding="utf8" )
     origSongs = originalPlaylist.readlines()

      # Get destination playlist folder's files/songs
     destSongs = os.listdir( inDestFolder )

      # Replace original playlist's song paths with just song name & extension
     for i in range( len(origSongs) ):
          origSongs[i] = origSongs[i][ origSongs[i].rfind('\\') + 1 : ].strip()

      # For each song in destination
     for song in destSongs:

           # IF destination\s song isn't in playlist (includes if just random file), remove song from destination
          if song not in origSongs:
                ##### IF song doesn't actually exist due to unsupported chars, add to unremoved songs list
               if not pathChecker.exists( inDestFolder + "/" + song ):
                    errorFilePath = "C:\\Users\\{}\\Desktop\\Playlist Sync Adding Errors.txt".format( os.getlogin() )
                    errorFile = open( errorFilePath, "a" )
                    errorFile.write( "= = = = = =\nERROR REMOVING FROM:\n{}\nSONG:\n{}\n= = = = = =\n".format( inOriginalPlaylist, song ) )
                    errorFile.close
                    continue
               else:
                     # Output box
                    numRemovedSongs += 1
                    if numRemovedSongs == 1:
                         outputBoxUpdateLast( songsOutputBox, "\nRemoved 1 song!" )
                    else:
                         outputBoxUpdateLast( songsOutputBox, "\nRemoved {} songs!".format( numRemovedSongs ) )
                    destSongPath = inDestFolder + "/" + song
                    os.remove( destSongPath )

      # Final output
     if numRemovedSongs == 0:
          outputBoxUpdateLast( songsOutputBox, "\nNo songs removed!" )

     time.sleep( AFTER_SYNC_PLAYLIST_DELAY )



 # Add any songs that aren't at destination
def addSongs( inOriginalPlaylist, inDestFolder ):

      # Variables
     numAddedSongs = 0

      # Output box
     outputBoxUpdate( songsOutputBox, "\nAdding..." )
     time.sleep( 0.5 )

      # Get original playlists' lines/songs
     originalPlaylist = open( inOriginalPlaylist, "r", encoding="utf8" )
     origSongs = originalPlaylist.readlines()

      # Get destination playlist folder's files/songs
     destSongs = os.listdir( inDestFolder )

      # For each song in original playlist
     for songPath in origSongs:

           # Replace songPath symbols to work for Python, and remove new line
          songPath = songPath.replace( "\\", "/" ).strip()

           # Get song's name
          song = songPath[ songPath.rfind('/') + 1 : ].strip()

           # IF song isn't at destination, copy song to destination
          if song not in destSongs:

                # IF song doesn't actually exist due to unsupported chars, print error to file on desktop
               if not pathChecker.exists( songPath ):
                    errorFilePath = "C:\\Users\\{}\\Desktop\\Playlist Sync Adding Errors.txt".format( os.getlogin() )
                    errorFile = open( errorFilePath, "a" )
                    errorFile.write( "= = = = = =\nERROR ADDING FROM:\n{}\nSONG:\n{}\n= = = = = =\n".format( inOriginalPlaylist, song ) )
                    errorFile.close
                    continue
               else:
                     # Output box
                    numAddedSongs += 1
                    if numAddedSongs == 1:
                         outputBoxUpdateLast( songsOutputBox, "\nAdded 1 song!" )
                    else:
                         outputBoxUpdateLast( songsOutputBox, "\nAdded {} songs!".format( numAddedSongs ) )

                    destSongPath = inDestFolder + "/" + song
                    shutil.copyfile( songPath, destSongPath )

      # Final output
     if numAddedSongs == 0:
          outputBoxUpdateLast( songsOutputBox, "\nNo songs added!" )

     time.sleep( AFTER_SYNC_PLAYLIST_DELAY )



 ### - Elements - ###

 # Window
root = tk.Tk()
root.resizable( False, False )
root.title( TITLE )

 # Closing event
root.protocol("WM_DELETE_WINDOW", onClosing)

 # Canvas
canvas = tk.Canvas(root, width = WIDTH, height = HEIGHT)
canvas.pack()

 # Frames
headerFrame = tk.Frame( canvas )#, highlightbackground="black", highlightthickness = 1 )
playlistsFrame = tk.Frame( canvas )#, highlightbackground="blue", highlightthickness = 1 )
syncFrame = tk.Frame( canvas )#, highlightbackground="red", highlightthickness = 1 )


 ### - Positioning Frames - ###

 # Constants
framesWidth = 0.8
framesLeft = (1 - framesWidth) / 2
frameGaps = 0.02

headFrTop = 0.02
headFrHeight = 0.2

playlistsFrameTop = headFrTop + headFrHeight + frameGaps
playlistsFrameHeight = 0.4

syncFrameTop = playlistsFrameTop + playlistsFrameHeight + frameGaps
syncFrameHeight = 0.3

 # Positioning
headerFrame.place (
                      relx=framesLeft, rely = headFrTop,
                      relwidth=framesWidth, relheight=headFrHeight
                  )
playlistsFrame.place (
                         relx=framesLeft, rely = playlistsFrameTop,
                         relwidth=framesWidth, relheight=playlistsFrameHeight
                     )
syncFrame.place (
                    relx=framesLeft, rely = syncFrameTop,
                    relwidth=framesWidth, relheight=syncFrameHeight
                )


 ### - Creating & Positioning Lines - ###

 # Constants
linesLeft = (framesLeft*WIDTH) - 10
linesRight = (framesLeft*WIDTH) + (framesWidth*WIDTH) + 10

line1Y = (headFrTop*HEIGHT) + (headFrHeight*HEIGHT) + (frameGaps*HEIGHT) / 2
line2Y = ((playlistsFrameTop*HEIGHT) + (playlistsFrameHeight*HEIGHT) + (frameGaps*HEIGHT) / 2) + 1 # Potition correction
#line3Y = (syncFrameTop*HEIGHT) + (syncFrameHeight*HEIGHT) + (frameGaps*HEIGHT) / 2

 # Positioning
canvas.create_line( linesLeft, line1Y, linesRight, line1Y, width = LINES_THICKNESS )
canvas.create_line( linesLeft, line2Y, linesRight, line2Y, width = LINES_THICKNESS )



 ### - Frame 1 Elements - ###

 # Constants
desinationLabelTop = 0.07
desinationLabelWidth = 0.8

destinationEntryTop = 0.35
destinationEntryWidth = 0.8

chooseDestButtonTop = 0.66
chooseDestButtonWidth = 0.22

 # Label
desinationLabel = tk.Label( headerFrame, text = "Destination / Device", font = "Helvetica 12" )
desinationLabel.place(
                        relx = 0.5 - (desinationLabelWidth/2), rely = desinationLabelTop,
                        relwidth = desinationLabelWidth, relheight = 0.2
                     )

 # Entry
destinationEntry = tk.Entry( headerFrame, font = "Helvetica 9", exportselection=0 )
destinationEntry.place (
                            relx = 0.5 - (destinationEntryWidth/2), rely = destinationEntryTop,
                            relwidth = destinationEntryWidth, relheight = 0.2
                       )

 # Choose Button
chooseDestButton = tk.Button ( 
                                headerFrame,
                                text = "Choose",
                                bg = BUTTON_BG_COLOUR,
                                fg = BUTTON_FG_COLOUR,
                                font = BUTTON_FONT,
                                command = chooseDestination
                             )
chooseDestButton.place (
                            relx = 0.5 - (chooseDestButtonWidth/2), rely = chooseDestButtonTop,
                            relwidth = chooseDestButtonWidth, relheight = 0.2
                       )



 ### - Frame 2 Elements - ###

 # Constants
playlistsListboxWidth = 0.5
playlistsListboxHeight = 0.8
playlistsListboxLeft = 0.05

playlistButtonsGap = 0.05
playlistButtonsWidth = 0.3
playlistButtonsHeight = 0.1
playlistButtonsLeft = playlistsListboxLeft + playlistsListboxWidth + ( ( 1 - ( playlistsListboxLeft + playlistsListboxWidth ) ) / 2 ) - playlistButtonsWidth / 2

 # Listbox
playlistsListbox = tk.Listbox( playlistsFrame, font = "Helvetica 11", activestyle = "none" )
playlistsListbox.place (
                            relx = playlistsListboxLeft, rely = (1 - playlistsListboxHeight) / 2,
                            relwidth = playlistsListboxWidth, relheight = playlistsListboxHeight 
                       )

 # 'Add' button
addPlaylistButton = tk.Button ( 
                                playlistsFrame,
                                text = "Add Playlist",
                                bg = BUTTON_BG_COLOUR,
                                fg = BUTTON_FG_COLOUR,
                                font = BUTTON_FONT,
                                command = addPlaylist
                              )
addPlaylistButton.place (
                            relx = playlistButtonsLeft, rely = 0.5 - playlistButtonsHeight - ( playlistButtonsGap / 2 ),
                            relwidth = playlistButtonsWidth, relheight = playlistButtonsHeight
                        )

 # 'Remove' button
removePlaylistButton = tk.Button ( 
                                   playlistsFrame,
                                   text = "Rem Playlist",
                                   bg = BUTTON_BG_COLOUR,
                                   fg = BUTTON_FG_COLOUR,
                                   font = BUTTON_FONT,
                                   command = removePlaylist
                                )
removePlaylistButton.place (
                              relx = playlistButtonsLeft, rely = 0.5 + ( playlistButtonsGap / 2 ),
                              relwidth = playlistButtonsWidth, relheight = playlistButtonsHeight
                           )



 ### - Frame 3 Elements - ###

  # Constants
syncButtonWidth = 0.38
syncButtonHeight = 0.25

outputBoxEdgeGaps = 0.02
outputBoxMiddleGap = 0.08
outputBoxBottomGap = 0
outputBoxTop = 0.4
outputBoxWidth = 0.5 - ( outputBoxMiddleGap / 2 ) - outputBoxEdgeGaps
outputBoxHeight = 1 - outputBoxTop - outputBoxBottomGap

playlistsOutputBoxLeft = outputBoxEdgeGaps
songsOutputBoxLeft     = outputBoxEdgeGaps + outputBoxWidth + outputBoxMiddleGap

 # Sync Button
syncButton = tk.Button ( 
                              syncFrame,
                              text = "Sync",
                              bg = BUTTON_BG_COLOUR,
                              fg = BUTTON_FG_COLOUR,
                              font = SYNC_BUTTON_FONT,
                              command = syncThread
                       )
syncButton.place (
                         relx = 0.5 - ( syncButtonWidth / 2 ), rely = 0.05,
                         relwidth = syncButtonWidth, relheight = syncButtonHeight
                 )

 # Ouput boxes
playlistsOutputBox = tk.Text (
                                   syncFrame,
                                   bg = "white",
                                   font = TEXTBOX_FONT_NORMAL,
                                   state = "disabled"
                            )

playlistsOutputBox.place (
                              relx = playlistsOutputBoxLeft, rely = outputBoxTop,
                              relwidth = outputBoxWidth, relheight = outputBoxHeight
                        )
outputBoxUpdate( playlistsOutputBox, "|| Playlists ||" )

songsOutputBox = tk.Text (
                              syncFrame,
                              bg = "white",
                              font = TEXTBOX_FONT_NORMAL,
                              state = "disabled"
                         )
songsOutputBox.place (
                              relx = songsOutputBoxLeft, rely = outputBoxTop,
                              relwidth = outputBoxWidth, relheight = outputBoxHeight
                        )
outputBoxUpdate( songsOutputBox, "|| Songs ||" )



 ### - Load - ###

loadData()


 ### - Run - ###

root.mainloop()