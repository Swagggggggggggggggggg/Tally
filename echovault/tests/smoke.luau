-- Lune headless test: run with `lune run tests/smoke`
local Config = require("../src/shared/Config")

local function check(cond, msg)
	if not cond then error("FAIL: " .. msg, 0) end
end

check(Config.LoopTime > 0, "LoopTime must be positive")
check(Config.SampleRate > 0 and Config.SampleRate < Config.LoopTime, "SampleRate out of range")
check(Config.MaxGhosts >= Config.MaxLevel - 1, "MaxGhosts too low to finish the last level")
check(Config.ExtraGhostPenalty * Config.MaxGhosts > 0, "penalty sanity")

-- Headless sim of the echo mechanic: a recording replays then freezes on its last sample.
local rec = {}
for i = 1, 10 do rec[i] = i end
local function sampleAt(idx) return rec[math.min(idx, #rec)] end
check(sampleAt(3) == 3, "replay mid-recording")
check(sampleAt(999) == 10, "replay freezes on last sample")

-- Lasers: deterministic, telegraph before firing, and a gap exists to slip through.
check(Config.LaserState(0, 0) == "on", "laser on at start of cycle")
check(Config.LaserState(Config.LaserOn + 0.1, 0) == "off", "laser off after on-window")
check(Config.LaserState(Config.LaserPeriod - 0.1, 0) == "warn", "laser warns before firing")
check(Config.LaserState(1.7, 0.5) == Config.LaserState(1.7 + Config.LaserPeriod, 0.5), "laser is periodic")
check(Config.LaserPeriod - Config.LaserOn - Config.LaserWarn > 0.5, "gap wide enough to cross")

print("smoke tests passed")
