-- LocalScript → StarterPlayer > StarterPlayerScripts (Rojo: src/client/Hud.client.lua)
-- UI only: shows round status, current level, and the speed-upgrade button.
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage.Shared.Config)
local buyRemote = ReplicatedStorage:WaitForChild("BuySpeed")
local plr = Players.LocalPlayer

local gui = Instance.new("ScreenGui")
gui.Name = "RisingTideHud"
gui.ResetOnSpawn = false
gui.Parent = plr:WaitForChild("PlayerGui")

local function label(size, pos, textSize)
	local l = Instance.new("TextLabel")
	l.Size, l.Position = size, pos
	l.AnchorPoint = Vector2.new(0.5, 0)
	l.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
	l.BackgroundTransparency = 0.25
	l.TextColor3 = Color3.new(1, 1, 1)
	l.Font = Enum.Font.GothamBold
	l.TextSize = textSize
	Instance.new("UICorner", l).CornerRadius = UDim.new(0, 10)
	l.Parent = gui
	return l
end

local statusLbl = label(UDim2.fromOffset(340, 44), UDim2.new(0.5, 0, 0, 12), 22)
local levelLbl = label(UDim2.fromOffset(160, 36), UDim2.new(0.5, 0, 0, 62), 18)

local shop = Instance.new("TextButton")
shop.Size = UDim2.fromOffset(220, 44)
shop.Position = UDim2.new(1, -240, 1, -64)
shop.BackgroundColor3 = Color3.fromRGB(60, 200, 120)
shop.TextColor3 = Color3.new(1, 1, 1)
shop.Font = Enum.Font.GothamBold
shop.TextSize = 16
Instance.new("UICorner", shop).CornerRadius = UDim.new(0, 10)
shop.Parent = gui

local function refresh()
	statusLbl.Text = workspace:GetAttribute("Status") or ""
	levelLbl.Text = "Level " .. (plr:GetAttribute("Level") or 0)
	local lvl = plr:GetAttribute("SpeedLevel") or 0
	local up = Config.SpeedUpgrade
	shop.Text = lvl >= up.Max and "Speed MAX" or ("Speed +  (" .. up.Cost(lvl) .. " coins)")
end

workspace:GetAttributeChangedSignal("Status"):Connect(refresh)
plr:GetAttributeChangedSignal("Level"):Connect(refresh)
plr:GetAttributeChangedSignal("SpeedLevel"):Connect(refresh)
shop.Activated:Connect(function() buyRemote:InvokeServer() end)
refresh()
