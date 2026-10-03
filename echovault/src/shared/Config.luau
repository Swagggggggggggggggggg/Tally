-- ModuleScript → ReplicatedStorage > Shared > Config
local Config = {
	LoopTime = 25,       -- seconds per loop
	SampleRate = 0.05,   -- how often your position is recorded
	MaxLevel = 5,
	MaxGhosts = 8,
	FirstPlateZ = 10,
	LevelSpacing = 22,   -- distance between plate/door pairs
	ArenaSpacing = 160,  -- distance between players' private arenas
	ArenaHeight = 100,
	BaseReward = 50,
	RewardPerLevel = 25,
	ExtraGhostPenalty = 10,
	LaserFromSegment = 3, -- lasers appear in corridor segments >= this (levels 3+)
	LaserPeriod = 3,
	LaserOn = 1.2,
	LaserWarn = 0.4,      -- orange telegraph before the beam fires
}

-- Pure function of loop time: an echo replays in sync, so it sees exactly what it saw when recorded.
function Config.LaserState(t: number, phase: number): string
	local c = (t + phase) % Config.LaserPeriod
	if c < Config.LaserOn then return "on" end
	if c > Config.LaserPeriod - Config.LaserWarn then return "warn" end
	return "off"
end

return Config
