-- ModuleScript → ReplicatedStorage > Shared > Config
return {
	Intermission = 10,
	RoundTime = 150,
	LavaGrace = 8,
	LavaSpeed = 2.2, -- studs/sec
	TowerLevels = 40,
	LevelHeight = 9,
	TowerOrigin = Vector3.new(0, 0, 400),
	CoinsPerLevel = 5,
	WinBonus = 100,
	SpeedUpgrade = { Base = 16, PerLevel = 2, Max = 10, Cost = function(lvl) return 50 * (lvl + 1) end },
}
