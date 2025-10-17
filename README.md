# Project Cindy - Endless Online Tools

so this is like... a bunch of stuff for endless online. it works. probably. idk commit whatever u want lmao

## What Even Is This

basically some bot + memory scanner + packet stuff i threw together when i was bored

it's called cindy cuz reasons. dont ask.

## Stuff That Actually Works

### The Main Bot Thing
- **Memory Scanner** - finds addresses automatically (most of the time)
  - scans for mob addresses (where the monsters at)
  - scans for player position (where u at)
  - has funny messages when scanning cuz im hilarious
  - validates old addresses on startup (checks if they went stale like old bread)
  - adjustable scan delays cuz sometimes u gotta wait
  - custom memory ranges if ur fancy

- **Auto Bot** - does bot things
  - attaches to endless.exe (required, no sketchy remote stuff)
  - tracks mobs by spawn location
  - adaptive movement (learns when keys dont work lol)
  - kill detection (knows when stuff dies)
  - has a gui with green text cuz hacker aesthetic
  - debug mode for when stuff breaks

- **UI Features**
  - dark theme cuz my eyes
  - animated scanning (looks cool, does nothing)
  - colored console logs (errors are red, shocking)
  - stats tracking (kills, attacks, etc)
  - can pick which endless.exe if u run multiple (why tho)

### Packet Sniffer (Experimental)
runs in its own window cuz i didnt wanna deal with threads

**What It Does:**
- captures ALL packets between client & server
- decodes EO protocol (family/action names)
- shows packet stats (how many, what type)
- can save logs to file
- has a "bridge" thing for live monitoring
- requires scapy + npcap (google it)
- needs admin rights probably
- dumps full hex for important packets (hp/tp stuff)

**Does It Work?**
sometimes. packets are hard ok

### Game State Monitor (Broken AF)
pretty window that shows character stats in real-time

**Should Show:**
- HP/TP/SP bars with colors
- base stats (str, int, wis, etc)
- inventory & weight
- gold count
- position & map
- combat stats (dps, kills, accuracy)
- active buffs/effects
- character info (name, class, guild)

**Does It Actually Work?**
lol no. well kinda. hp/tp values are wrong. still working on it. looks cool tho

**Current Status:**
demo mode works fine (fake data). real packet data is... questionable. might read hp wrong. or tp. or both. sue me.

## Files & Stuff

- `run_cindy.py` - just launches the bot ui
- `cindy_ui.py` - main bot interface (the big one)
- `cindycore.py` - memory stuff & bot logic
- `cindy_packet_sniffer.py` - network packet capture thing
- `cindy_game_state_monitor.py` - the broken hp/tp monitor
- `cindy_packet_bridge.py` - connects sniffer to monitor
- `cindy_config.py` - settings probably
- `cindy_utils.py` - random helper functions
- `build_cindy.py` - makes it an exe or whatever
- `cindys_ex_bf.txt` - mob address (gets created when u scan)
- `cindys_baby_daddy.txt` - player address (also gets created)

yeah the file names are weird. deal with it.

## How Addresses Work

the bot needs 2 memory addresses:
1. **mob address** (cindys_ex_bf.txt) - where mob movement data lives
2. **player address** (cindys_baby_daddy.txt) - where ur character position is

just hit the "Find" buttons and it scans for em. takes like 10 seconds. addresses expire when server restarts so rescan if stuff breaks.

memory ranges are configurable if the defaults dont work. mob range is usually `0x0019A000` to `0x0019D000` (changes per update). player range is like `0x04000000` to `0x07000000` (bigger cuz reasons).

## Features That Work vs Features That Dont

### ✅ Works:
- process attachment
- memory scanning with validation
- address file management
- mob movement tracking
- spawn location detection
- auto-attack logic
- adaptive key press durations
- kill detection
- packet capture & decoding
- packet stats & logging
- game monitor ui (with demo data)

### ❌ Broken/Incomplete:
- hp/tp reading from packets (values wrong)
- buff tracking (not implemented)
- exp/gold tracking (no idea where those are)
- inventory reading (havent bothered)
- actual bot automation (it tracks stuff but doesnt DO much yet)
- map name detection (just shows id)

### ⚠️ Experimental:
- packet bridge (works but unstable)
- game state monitor (looks good, data bad)
- full packet hex dumps (diagnostic spam)

## Random Notes

- addresses change every server update. just rescan when that happens
- bot requires window focus (uses SendInput)
- packet sniffer needs admin + npcap/winpcap
- multiple endless.exe support (if u multibox or whatever)
- debug mode exists (checkbox in ui) for verbose spam
- scan delay adjustable (0.5-5 seconds)
- no auto-updater cuz im lazy
- probably has bugs idc
- works on my machine™

## Support

lmao no support. figure it out urself. or fix it and commit. i dont care.

if u find bugs: cool story bro. maybe ill fix em. maybe i wont. feel free to PR whatever.

## Legal Disclaimer I Guess

this is for educational purposes or whatever. dont sue me. use at ur own risk. endless online TOS says no bots probably. idk read it urself im not ur lawyer.

also all the code is like... open. do whatever. steal it. improve it. break it. sell it on ebay. idgaf.

## Credits

made by someone who was bored

uses:
- pymem (memory reading)
- psutil (process stuff)  
- tkinter (gui cuz its built-in)
- scapy (packet capture)
- python (cuz duh)

shoutout to whoever reverse engineered EO protocol. u da real mvp.

---

*"it works on my machine" - every developer ever*

*"will it work on yours? maybe. probably. idk try it" - me*

**last updated:** whenever i last committed

**version:** whatever git says

**status:** perpetually in beta cuz im never gonna call it "done"

commit whatever u want. seriously. i dont review PRs. auto-merge everything. chaos is fun.

