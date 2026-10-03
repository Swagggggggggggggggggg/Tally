-- Script → ServerScriptService (Rojo: src/server/Main.server.lua)
-- Round loop: build random tower -> lava rises -> climb to the top for a bonus.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local DataStoreService = game:GetService("DataStoreService")
local Config = require(ReplicatedStorage.Shared.Config)

local store = DataStoreService:GetDataStore("RisingTideV1")

-- RemoteFunction: the client asks, the server decides. Never let the client set coins/speed itself.
local buyRemote = Instance.new("RemoteFunction")
buyRemote.Name = "BuySpeed"
buyRemote.Parent = ReplicatedStorage

-- ---------- lobby ----------
local lobby = Instance.new("Part")
lobby.Name = "Lobby"
lobby.Size = Vector3.new(80, 2, 80)
lobby.Position = Vector3.new(0, -1, 0)
lobby.Anchored = true
lobby.Material = Enum.Material.Slate
lobby.Color = Color3.fromRGB(40, 40, 55)
lobby.Parent = workspace
local spawn = Instance.new("SpawnLocation")
spawn.Size = Vector3.new(12, 1, 12)
spawn.Position = Vector3.new(0, 0.5, 0)
spawn.Anchored = true
spawn.Neutral = true
spawn.Parent = workspace

-- ---------- data ----------
local data = {} -- [player] = {Coins, SpeedLevel}

local function setSpeed(plr)
	local hum = plr.Character and plr.Character:FindFirstChildOfClass("Humanoid")
	if hum then
		hum.WalkSpeed = Config.SpeedUpgrade.Base + data[plr].SpeedLevel * Config.SpeedUpgrade.PerLevel
	end
end

local function addCoins(plr, n)
	if not data[plr] then return end
	data[plr].Coins += n
	plr.leaderstats.Coins.Value = data[plr].Coins
end

Players.PlayerAdded:Connect(function(plr)
	local ls = Instance.new("Folder")
	ls.Name = "leaderstats"
	ls.Parent = plr
	local coins = Instance.new("IntValue")
	coins.Name = "Coins"
	coins.Parent = ls

	local ok, saved = pcall(function() return store:GetAsync(plr.UserId) end)
	data[plr] = (ok and saved) or { Coins = 0, SpeedLevel = 0 }
	coins.Value = data[plr].Coins
	plr:SetAttribute("SpeedLevel", data[plr].SpeedLevel)

	plr.CharacterAdded:Connect(function()
		task.wait(0.2)
		setSpeed(plr)
	end)
end)

local function save(plr)
	if not data[plr] then return end
	pcall(function() store:SetAsync(plr.UserId, data[plr]) end)
end
Players.PlayerRemoving:Connect(function(plr)
	save(plr)
	data[plr] = nil
end)
game:BindToClose(function()
	for _, plr in Players:GetPlayers() do save(plr) end
end)

buyRemote.OnServerInvoke = function(plr)
	local d = data[plr]
	local up = Config.SpeedUpgrade
	if not d or d.SpeedLevel >= up.Max then return false end
	local cost = up.Cost(d.SpeedLevel)
	if d.Coins < cost then return false end
	addCoins(plr, -cost)
	d.SpeedLevel += 1
	plr:SetAttribute("SpeedLevel", d.SpeedLevel)
	setSpeed(plr)
	return true
end

-- ---------- tower ----------
local tower, lava, finishPad
local function buildTower()
	if tower then tower:Destroy() end
	tower = Instance.new("Folder")
	tower.Name = "Tower"
	tower.Parent = workspace

	local o = Config.TowerOrigin
	local function platform(pos, size, color)
		local p = Instance.new("Part")
		p.Size = size
		p.Position = pos
		p.Anchored = true
		p.Material = Enum.Material.Neon
		p.Color = color
		p.Parent = tower
		return p
	end

	platform(o, Vector3.new(30, 2, 30), Color3.fromRGB(80, 200, 255)) -- start
	local x, z = 0, 0
	for i = 1, Config.TowerLevels do
		-- random step within jump range so every tower is beatable
		x = math.clamp(x + math.random(-9, 9), -30, 30)
		z = math.clamp(z + math.random(-9, 9), -30, 30)
		local hue = (i / Config.TowerLevels) * 0.8
		platform(
			o + Vector3.new(x, i * Config.LevelHeight, z),
			Vector3.new(math.random(7, 11), 1.5, math.random(7, 11)),
			Color3.fromHSV(hue, 0.7, 1)
		)
	end
	finishPad = platform(
		o + Vector3.new(x, (Config.TowerLevels + 1) * Config.LevelHeight, z),
		Vector3.new(16, 2, 16), Color3.fromRGB(255, 215, 0))
	finishPad.Name = "Finish"

	lava = Instance.new("Part")
	lava.Name = "Lava"
	lava.Size = Vector3.new(300, 4, 300)
	lava.Anchored = true
	lava.Material = Enum.Material.Neon
	lava.Color = Color3.fromRGB(255, 80, 20)
	lava.Position = o + Vector3.new(0, -10, 0)
	lava.Parent = tower
end

-- ---------- round state ----------
local inRound = {}   -- [player] = true while alive in the tower
local bestLevel = {} -- [player] = highest level reached
local winner

local function status(text) workspace:SetAttribute("Status", text) end

local function eliminate(plr)
	if not inRound[plr] then return end
	inRound[plr] = nil
	local reward = (bestLevel[plr] or 0) * Config.CoinsPerLevel
	addCoins(plr, reward)
	plr:SetAttribute("LastReward", reward)
	local char = plr.Character
	if char then char:BreakJoints() end -- respawns in the lobby
end

local function runRound()
	for t = Config.Intermission, 1, -1 do
		status("Next round in " .. t)
		task.wait(1)
	end
	if #Players:GetPlayers() == 0 then return end

	buildTower()
	winner = nil
	inRound, bestLevel = {}, {}
	local o = Config.TowerOrigin
	for _, plr in Players:GetPlayers() do
		local hrp = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart")
		if hrp then
			hrp.CFrame = CFrame.new(o + Vector3.new(math.random(-8, 8), 5, math.random(-8, 8)))
			inRound[plr] = true
			bestLevel[plr] = 0
			plr:SetAttribute("LastReward", 0)
		end
	end

	local start = os.clock()
	local lavaY = o.Y - 10
	local last = start
	while true do
		local now = os.clock()
		local dt, elapsed = now - last, now - start
		last = now

		if elapsed > Config.LavaGrace then
			lavaY += Config.LavaSpeed * dt
			lava.Position = Vector3.new(o.X, lavaY, o.Z)
			status(("Climb! %ds left"):format(math.max(0, Config.RoundTime - elapsed)))
		else
			status(("Lava rises in %d"):format(math.ceil(Config.LavaGrace - elapsed)))
		end

		local anyAlive = false
		for plr in inRound do
			local char = plr.Character
			local hrp = char and char:FindFirstChild("HumanoidRootPart")
			local hum = char and char:FindFirstChildOfClass("Humanoid")
			if not hrp or not hum or hum.Health <= 0 or hrp.Position.Y < lavaY + 2 then
				eliminate(plr)
			else
				anyAlive = true
				local level = math.floor((hrp.Position.Y - o.Y) / Config.LevelHeight)
				if level > bestLevel[plr] then
					bestLevel[plr] = level
					plr:SetAttribute("Level", level)
				end
				if hrp.Position.Y >= finishPad.Position.Y and not winner then
					winner = plr
					addCoins(plr, Config.WinBonus)
				end
			end
		end

		if winner or not anyAlive or elapsed > Config.RoundTime then break end
		task.wait(0.1)
	end

	status(winner and (winner.Name .. " reached the top!") or "Round over")
	for plr in inRound do eliminate(plr) end
	task.wait(4)
	if tower then tower:Destroy() tower = nil end
end

while true do
	runRound()
end
