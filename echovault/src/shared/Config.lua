-- ModuleScript → ReplicatedStorage > Shared > Config
return {
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
}
