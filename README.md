# gpesports-discordbot
Bot for reading mysql


Prequali:
===============================
1. Automatically publish 24 hours before race and send DM
2. $prequali ($check): returns list of current timetrial submissions for this week
3. $prequali -final ($manual): publish prequali list and assigns role
4. $prequali -setrole @gp3-quali: defines the role to assign to prequali submissions
5. $prequali -setchannel
6. $prequali -remind (publish list of all users to remind)
7. $prequali -reminddm (sends reminder to all users in the list)
8. $prequali -clean: return list of users whose role was removed

Parc Ferme:
===============================
1. $parcferme: manually publishes list of pending users without videos in corresponding channel and DM users
2. $parcferme -nodm: manually publishes list of pending users without videos in corresponding channel, but doesnt send DM
2. Automatically publish list according to config file


Backend
===============================
1. Users with no discord ID: if any error is thrown because a user doesnt have a discordID send to backendchannel
2. Backendchannel: Add in config a channel to publish bot internal stuff, errors, confirmations, wte
3. $status command: uptime, current time, amount of current entries in list, 
4. When sending batch DMs, post users who where sent a DM to backendchannel
