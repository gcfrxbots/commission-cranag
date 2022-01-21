# Important stuff and commands for Cranag's RPG Bot

Commands:

!reset - Resets the player progress back to the first area in the first room, and wipes any other saved progress.


World.xlsx:

A "Room" is one single scene a player can be in. Every time you give a different description with different options, you go to a different room.

Areas are groups of rooms, for organization. Each area has a description a title so you can separate different areas and clusters of rooms. An infinite number of areas can be made, 50 generate with the bot.
You can add more areas by duplicating an empty area worksheet and simply renaming it to whatever you want the area to be called.

Each room links to a different room by means of a *Room Option* and a *Room ID.* The room option is what a user will vote on, and the ID is an invisible ID tied to that room. 

For example, the room startRoom might have the description "You are in a wooden shack, holding a torch." You may have the option "Light the torch", and that option's ID would link to a different room, perhaps named startRoom_Torchlit. Then that new room would have more options, and so on.

Instead of providing a room ID, you can instead provide a modifier. Each modifier is configurable, must follow a certain format, and does other stuff. A list is below:

$AREA Areaname Roomname  -  Adding this will move the player to the provided Roomname in the new provided Areaname. For example, $AREA Desert startDesert would move the player to the Desert area, and the startDesert room in that area.



