-- Script → ServerScriptService (Rojo: src/server/Main.server.luau)
-- ECHO VAULT: a time-loop puzzle. Doors only open while something stands on their plate.
-- Record a loop standing on a plate -> your "echo" replays it forever -> next loop you walk through the door.
-- Level N needs N-1 echoes. Every player gets a private arena so nobody interferes.
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local DataStoreService = game:GetService("DataStoreService")
local Config = require(ReplicatedStorage.Shared.Config)

local store = DataStoreService:GetDataStore("EchoVaultV1")

-- RemoteEvent: client -> server requests. Server whitelists the action string.
local actionRemote = Instance.new("RemoteEvent")
actionRemote.Name = "LoopAction"
actionRemote.Parent = ReplicatedStorage

Players.RespawnTime = 1

local sessions, data, usedSlots = {}, {}, {}
local PLATE_REACH, GOAL_REACH = 4.5, 5

local function near(a, b, reach)
	return math.abs(a.X - b.X) < reach and math.abs(a.Z - b.Z) < reach and math.abs(a.Y - b.Y) < 7
end

local function part(parent, size, pos, color, mat)
	local p = Instance.new("Part")
	p.Size, p.Position, p.Color = size, pos, color
	p.Anchored = true
	p.Material = mat or Enum.Material.SmoothPlastic
	p.Parent = parent
	return p
end

-- ---------- level building ----------
local function loadLevel(s, n)
	if s.folder then s.folder:Destroy() end
	s.folder = Instance.new("Folder")
	s.folder.Name = s.plr.Name .. "_Arena"
	s.folder.Parent = workspace
	s.level, s.ghosts, s.plates, s.doors = n, {}, {}, {}

	local o, z0, gap = s.origin, Config.FirstPlateZ, Config.LevelSpacing
	local zmax = z0 + gap * n + 14
	part(s.folder, Vector3.new(40, 2, zmax + 10), o + Vector3.new(0, -1, (zmax - 10) / 2),
		Color3.fromRGB(35, 35, 50))

	for i = 1, n do
		local color = Color3.fromHSV(i / 6, 0.75, 1)
		local pz = z0 + gap * (i - 1)
		local plate = part(s.folder, Vector3.new(8, 0.4, 8),
			o + Vector3.new(i % 2 == 1 and -12 or 12, 0.2, pz), color, Enum.Material.Neon)
		local door = part(s.folder, Vector3.new(44, 10, 2),
			o + Vector3.new(0, 5, pz + gap / 2), color, Enum.Material.Neon)
		door.Transparency = 0.25
		s.plates[i], s.doors[i] = plate, door
	end
	s.goal = part(s.folder, Vector3.new(12, 0.4, 12), o + Vector3.new(0, 0.2, z0 + gap * n),
		Color3.fromRGB(255, 215, 0), Enum.Material.Neon)

	s.plr:SetAttribute("Level", n)
	s.plr:SetAttribute("Ghosts", 0)
end

-- ---------- loop control ----------
local function startLoop(s)
	local hrp = s.plr.Character and s.plr.Character:FindFirstChild("HumanoidRootPart")
	if not hrp then s.active = false return end
	s.t, s.acc, s.rec, s.active = 0, 0, {}, true
	local pos = s.origin + Vector3.new(0, 4, 0)
	hrp.AssemblyLinearVelocity = Vector3.zero
	hrp.CFrame = CFrame.lookAt(pos, pos + Vector3.zAxis)
end

local function keepLoop(s)
	if #s.rec > 1 and #s.ghosts < Config.MaxGhosts then
		local g = part(s.folder, Vector3.new(2, 5, 1), s.rec[1],
			Color3.fromHSV((#s.ghosts * 0.13) % 1, 0.4, 1), Enum.Material.Neon)
		g.Transparency = 0.5
		g.CanCollide = false
		table.insert(s.ghosts, { rec = s.rec, part = g })
		s.plr:SetAttribute("Ghosts", #s.ghosts)
	end
	startLoop(s)
end

local function addCoins(plr, n)
	local d = data[plr]
	d.Coins += n
	plr.leaderstats.Coins.Value = d.Coins
end

local function completeLevel(s)
	s.active = false
	local n = s.level
	local extra = math.max(0, #s.ghosts - (n - 1)) -- ghosts beyond the minimum cost you
	local reward = math.max(10, Config.BaseReward + Config.RewardPerLevel * n - Config.ExtraGhostPenalty * extra)
	addCoins(s.plr, reward)
	local d = data[s.plr]
	d.Best = math.max(d.Best, n)
	s.plr.leaderstats.Cleared.Value = d.Best
	s.plr:SetAttribute("Message", ("Level %d cleared! +%d coins"):format(n, reward))
	task.delay(2, function()
		if not sessions[s.plr] then return end
		s.plr:SetAttribute("Message", "")
		loadLevel(s, n >= Config.MaxLevel and 1 or n + 1)
		startLoop(s)
	end)
end

-- ---------- per-frame simulation ----------
RunService.Heartbeat:Connect(function(dt)
	for plr, s in sessions do
		local char = plr.Character
		local hrp = char and char:FindFirstChild("HumanoidRootPart")
		if not s.active or not hrp then continue end

		s.t += dt
		s.acc += dt
		while s.acc >= Config.SampleRate do
			s.acc -= Config.SampleRate
			s.rec[#s.rec + 1] = hrp.Position
		end

		-- echoes replay their recording, then freeze on their last sample
		local idx = math.floor(s.t / Config.SampleRate) + 1
		local positions = { hrp.Position }
		for _, g in s.ghosts do
			local p = g.rec[math.min(idx, #g.rec)]
			g.part.Position = p
			positions[#positions + 1] = p
		end

		for i, plate in s.plates do
			local pressed = false
			for _, p in positions do
				if near(p, plate.Position, PLATE_REACH) then pressed = true break end
			end
			s.doors[i].CanCollide = not pressed
			s.doors[i].Transparency = pressed and 0.9 or 0.25
			plate.Transparency = pressed and 0.5 or 0
		end

		if near(hrp.Position, s.goal.Position, GOAL_REACH) then
			completeLevel(s)
		elseif hrp.Position.Y < s.origin.Y - 25 then
			char:FindFirstChildOfClass("Humanoid").Health = 0 -- respawn restarts the loop
		elseif s.t >= Config.LoopTime then
			keepLoop(s) -- timeout auto-keeps the loop
		end
		plr:SetAttribute("TimeLeft", math.ceil(Config.LoopTime - s.t))
	end
end)

-- ---------- player lifecycle ----------
local function save(plr)
	if data[plr] then pcall(function() store:SetAsync(plr.UserId, data[plr]) end) end
end

Players.PlayerAdded:Connect(function(plr)
	local slot = 0
	while usedSlots[slot] do slot += 1 end
	usedSlots[slot] = true

	local ls = Instance.new("Folder")
	ls.Name = "leaderstats"
	ls.Parent = plr
	local cleared = Instance.new("IntValue")
	cleared.Name = "Cleared"
	cleared.Parent = ls
	local coins = Instance.new("IntValue")
	coins.Name = "Coins"
	coins.Parent = ls

	local ok, saved = pcall(function() return store:GetAsync(plr.UserId) end)
	data[plr] = (ok and saved) or { Coins = 0, Best = 0 }
	coins.Value, cleared.Value = data[plr].Coins, data[plr].Best

	local s = {
		plr = plr, slot = slot,
		origin = Vector3.new(slot * Config.ArenaSpacing, Config.ArenaHeight, 0),
		active = false,
	}
	sessions[plr] = s
	loadLevel(s, math.min(data[plr].Best + 1, Config.MaxLevel))

	plr.CharacterAdded:Connect(function()
		task.wait(0.2)
		startLoop(s)
	end)
end)

Players.PlayerRemoving:Connect(function(plr)
	save(plr)
	local s = sessions[plr]
	if s then
		usedSlots[s.slot] = nil
		s.folder:Destroy()
	end
	sessions[plr], data[plr] = nil, nil
end)
game:BindToClose(function()
	for _, plr in Players:GetPlayers() do save(plr) end
end)

actionRemote.OnServerEvent:Connect(function(plr, action)
	local s = sessions[plr]
	if not s or not s.active then return end
	if action == "keep" then
		keepLoop(s)
	elseif action == "discard" then
		startLoop(s)
	elseif action == "reset" then
		loadLevel(s, s.level)
		startLoop(s)
	end
end)
