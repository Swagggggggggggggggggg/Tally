-- LocalScript → StarterPlayer > StarterPlayerScripts (Rojo: src/client/Hud.client.luau)
-- UI + keybinds only. All game logic is on the server.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local actionRemote = ReplicatedStorage:WaitForChild("LoopAction")
local plr = Players.LocalPlayer

local gui = Instance.new("ScreenGui")
gui.Name = "EchoVaultHud"
gui.ResetOnSpawn = false
gui.Parent = plr:WaitForChild("PlayerGui")

local function frame(size, pos, anchor)
	local f = Instance.new("Frame")
	f.Size, f.Position, f.AnchorPoint = size, pos, anchor
	f.BackgroundColor3 = Color3.fromRGB(18, 18, 28)
	f.BackgroundTransparency = 0.2
	Instance.new("UICorner", f).CornerRadius = UDim.new(0, 12)
	local stroke = Instance.new("UIStroke", f)
	stroke.Color = Color3.fromRGB(90, 220, 255)
	stroke.Transparency = 0.6
	f.Parent = gui
	return f
end

local function text(parent, size, pos, txt, ts)
	local l = Instance.new("TextLabel")
	l.Size, l.Position, l.Text, l.TextSize = size, pos, txt, ts
	l.BackgroundTransparency = 1
	l.TextColor3 = Color3.new(1, 1, 1)
	l.Font = Enum.Font.GothamBold
	l.Parent = parent
	return l
end

local top = frame(UDim2.fromOffset(360, 64), UDim2.new(0.5, 0, 0, 12), Vector2.new(0.5, 0))
local timeLbl = text(top, UDim2.new(0.4, 0, 1, 0), UDim2.new(0, 0, 0, 0), "", 30)
local infoLbl = text(top, UDim2.new(0.6, 0, 1, 0), UDim2.new(0.4, 0, 0, 0), "", 16)
infoLbl.TextColor3 = Color3.fromRGB(150, 230, 255)

local msg = text(gui, UDim2.fromOffset(500, 50), UDim2.new(0.5, -250, 0.25, 0), "", 28)
msg.TextColor3 = Color3.fromRGB(255, 215, 0)
msg.TextStrokeTransparency = 0.5

local bar = frame(UDim2.fromOffset(480, 54), UDim2.new(0.5, 0, 1, -16), Vector2.new(0.5, 1))
local layout = Instance.new("UIListLayout", bar)
layout.FillDirection = Enum.FillDirection.Horizontal
layout.HorizontalAlignment = Enum.HorizontalAlignment.Center
layout.VerticalAlignment = Enum.VerticalAlignment.Center
layout.Padding = UDim.new(0, 8)

local function button(label, action, key)
	local b = Instance.new("TextButton")
	b.Size = UDim2.fromOffset(150, 38)
	b.BackgroundColor3 = Color3.fromRGB(40, 50, 75)
	b.TextColor3 = Color3.new(1, 1, 1)
	b.Font = Enum.Font.GothamBold
	b.TextSize = 14
	b.Text = ("%s [%s]"):format(label, key.Name)
	Instance.new("UICorner", b).CornerRadius = UDim.new(0, 8)
	b.Parent = bar
	b.MouseEnter:Connect(function()
		TweenService:Create(b, TweenInfo.new(0.12), { BackgroundColor3 = Color3.fromRGB(70, 100, 150) }):Play()
	end)
	b.MouseLeave:Connect(function()
		TweenService:Create(b, TweenInfo.new(0.12), { BackgroundColor3 = Color3.fromRGB(40, 50, 75) }):Play()
	end)
	b.Activated:Connect(function() actionRemote:FireServer(action) end)
	return key, action
end

local binds = {}
for _, def in { { "Keep + Loop", "keep", Enum.KeyCode.E }, { "Discard", "discard", Enum.KeyCode.R },
	{ "Reset Level", "reset", Enum.KeyCode.T } } do
	local key, action = button(def[1], def[2], def[3])
	binds[key] = action
end
UserInputService.InputBegan:Connect(function(input, processed)
	if not processed and binds[input.KeyCode] then actionRemote:FireServer(binds[input.KeyCode]) end
end)

local function refresh()
	timeLbl.Text = tostring(plr:GetAttribute("TimeLeft") or "")
	infoLbl.Text = ("Level %d\nEchoes: %d"):format(plr:GetAttribute("Level") or 1, plr:GetAttribute("Ghosts") or 0)
	msg.Text = plr:GetAttribute("Message") or ""
end
for _, a in { "TimeLeft", "Level", "Ghosts", "Message" } do
	plr:GetAttributeChangedSignal(a):Connect(refresh)
end
refresh()
