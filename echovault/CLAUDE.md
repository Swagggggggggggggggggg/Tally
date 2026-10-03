# Echo Vault — project notes

Roblox time-loop puzzle. Doors open only while a player or an "echo" (replay of a past loop) stands on the matching plate.

## Layout
- `src/server/Main.server.luau` → ServerScriptService (arenas, loop recording, plates, rewards, DataStore)
- `src/client/Hud.client.luau` → StarterPlayerScripts (HUD + E/R/T keybinds; UI only)
- `src/shared/Config.luau` → ReplicatedStorage.Shared.Config (all tuning numbers)
- `default.project.json` is the Rojo map. Code lives in files, never paste into Studio.
- `check.ps1` runs lune tests, luau-lsp type-check, then builds `builds/EchoVault_NNN.rbxl`. Run it before telling the user anything works.

## Rules
- Spencer is learning Roblox: briefly explain any new concept, and state script type + location.
- Server is authoritative: the client only sends "keep" / "discard" / "reset" via the LoopAction RemoteEvent.
- Use task.wait/task.spawn, wrap DataStore calls in pcall, keep Luau idiomatic and lean.
- Test in Studio via the Studio MCP (play, read Output, screenshots) instead of asking the user to test.

## Gotchas
- Each player gets a private arena at X = slot * ArenaSpacing, Y = ArenaHeight; falling 25 studs below kills.
- Ghosts freeze on their last recorded sample (that's how they hold a plate forever).
- DataStore needs "Enable Studio Access to API Services" in Game Settings > Security.

- Lasers (segments >= Config.LaserFromSegment) cycle on/off as a pure function of loop time (Config.LaserState), so echoes replay safely. Touching a live beam discards your current loop.

## Ideas queue
Co-op shared arena; moving lasers; echo-only plates.
